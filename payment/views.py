from django.shortcuts import render, redirect
from cart.cart import Cart 
from payment.forms import ShippingForm, PurchaseForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages 
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from store.models import Product
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import stripe
import random

def checkout(request):

    #get cart information
    cart = Cart(request)
    cart_products = cart.get_prods()  # Ensure to call the method
    quantities = cart.get_quants()

    #calculate total
    totals = cart.cart_total()

    #check if total is less than £50
    if totals < 50:
        messages.error(request, "Minimum order amount is £50. Please add more items to your cart.")
        return HttpResponseRedirect(reverse('cart_summary'))

    #check if user is authenticated
    if request.user.is_authenticated:
        #checkout as logged-in user
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
    else:
        #checkout as guest
        shipping_form = ShippingForm(request.POST or None)

    #render checkout page with context data
    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form,
    })


def user_billing_information(request):

    if request.POST:

        #get cart information
        cart = Cart(request)
        cart_products = cart.get_prods()  #ensure to call the method
        quantities = cart.get_quants()
        #calculate total
        totals = cart.cart_total()

        #create a session with shipping information
        shipping = request.POST
        request.session['shipping'] = shipping

        # Store shipping information in session
        request.session['shipping'] = {
            'shipping_full_name': shipping['shipping_full_name'],
            'shipping_email': shipping['shipping_email'],
            'shipping_address1': shipping['shipping_address1'],
            'shipping_address2': shipping['shipping_address2'],
            'shipping_city': shipping['shipping_city'],
            'shipping_postcode': shipping['shipping_postcode'],
            'shipping_country': shipping['shipping_country'],
        }

        #check to see if user is logged in
        if request.user.is_authenticated:
            #get billing form 
            billing = PurchaseForm()
            #display product info and shipping info
            return render(request, "payment/user_billing_information.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_information": request.POST,
            "billing": billing,
          

        })
        else: 
            #get billing form 
            billing = PurchaseForm()
            #not logged in
            #display product info and shipping info
            return render(request, "payment/user_billing_information.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_information": request.POST,
            "billing": billing,

        })
        

        shipping_form = request.POST

        return render(request, "payment/user_billing_information.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_form": shipping_form
        })
    else: 
        #if users tries access without having anything in their cart, denies access
        messages.success(request, "Access Denied")
        return redirect('home')



def payment_success(request):
    # #get cart information
    # client_ref = 'Cust'
    # client_ref_id = f'{client_ref}_{random.getrandbits(4)}'
    cart = Cart(request)
    cart_products = cart.get_prods()  #ensure to call the method
    quantities = cart.get_quants()
    #calculate total
    totals = cart.cart_total()

    # Retrieve shipping information from session
    shipping_information = request.session.get('shipping', {})
    
    return render(request, "payment/payment_success.html", {
        "shipping_information": shipping_information,
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        # "client_ref_id": client_ref_id,
    })


def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})

def handle_order(request):

    if request.POST:
        #get cart information
        cart = Cart(request)
        cart_products = cart.get_prods # Ensure to call the method
        quantities = cart.get_quants
        #calculate total
        totals = cart.cart_total()
        orderDict = {}

        #get billing info
        payment = PurchaseForm(request.POST or None)
        #get shipping data
        shipping = request.session.get('shipping')

        full_name= shipping['shipping_full_name']
        email= shipping['shipping_email']
        shipping_address = f"{shipping['shipping_address1']}\n{shipping['shipping_address2']}\n{shipping['shipping_city']}\n{shipping['shipping_postcode']}\n{shipping['shipping_country']}\n"
        amount_paid=totals

        #create shipping address from session info

        if request.user.is_authenticated:
            user = request.user
            #create order
            createorder = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            createorder.save()

            order_id = createorder.pk

            for product in cart_products():
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for key,value in quantities().items():
                    if int(key)== product.id:
                        createorder_item=OrderItem(order_id=order_id, products_id=product_id, user=user, quantity=value, price=price)
                        # print(createorder_item)
                        createorder_item.save()
                        orderDict[product_id]= {'price': price, 'quantity':value, 'product_id' :product_id, 'name': product.name}




            messages.success(request, "Order Placed!")
            # return redirect('home')
        
        else: 
            #not logged in
            createorder = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            createorder.save()

            order_id = createorder.pk
            for product in cart_products():
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for key,value in quantities().items():
                        
                        if int(key)== product.id:
                            createorder_item=OrderItem(order_id=order_id, products_id=product_id, quantity=value, price=price)
                            createorder_item.save()
                            orderDict[product_id]= {'price': price, 'quantity':value, 'product_id' :product_id, 'name': product.name}



       
        return orderDict
        

    else:
        messages.success(request, "Access Denied")
        return redirect('home')



def createStripePayment(request):
    orderDict = handle_order(request)

    stripe.api_key = settings.STRIPE_PRIVATE_KEY

    line_items = []

    for item, val in orderDict.items():
        line_item = {
            'price_data': {
            'currency': 'gbp',
            'product_data': {
                'name': val['name'],
                },
                'unit_amount': int(val['price']*100),
            },
            'quantity': 1,
                    
        }
        line_items.append(line_item)

    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        client_reference_id = createCustref(request),
        payment_method_types=['card'],
        currency= 'GBP',      
        line_items=line_items,
        mode='payment',

        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('payment_failed')),
    )
    print(session)
    return redirect(session.url, code=303)


def createCustref(request):
        
        client_ref = 'Cust'
        client_ref_id = f'{client_ref}_{random.getrandbits(4)}'
        return client_ref_id
        print(client_ref_id)
