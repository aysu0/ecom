from django.shortcuts import render, redirect
from cart.cart import Cart 
from payment.forms import ShippingForm, PurchaseForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages 
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from store.models import Product, Customer, Profile
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import stripe
import random
import json
from django.views import View
from django.core.mail import send_mail

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
    if request.user.is_authenticated:
        user = request.user

        #check if user already has customer record
        customer = Customer.objects.filter(email=user.email).first()

        if not customer:
            #if user has no customer record, create one
            customer.objects.create(
                email=user.email
            )
        else: 
            pass
        
        #generate ref id for customer
        client_ref_id = createCustref(user)

    else: 
        client_ref_id=None

    #get cart information
    cart = Cart(request)
    cart_products = cart.get_prods()  #ensure to call the method
    quantities = cart.get_quants()

    #calculate total
    totals = cart.cart_total()
    session_id = request.GET.get('session_id')

    # Retrieve shipping information from session
    shipping_information = request.session.get('shipping', {})
    #clear cart if payment is successful
    cart.clear()
    
    return render(request, "payment/payment_success.html", {
        "shipping_information": shipping_information,
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "client_ref_id": client_ref_id,
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
            #iterate over cart products to create order items
            for product in cart_products():
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                for key,value in quantities().items():
                    if int(key)== product.id:
                        createorder_item=OrderItem(order_id=order_id, products_id=product_id, user=user, quantity=value, price=price)
                        createorder_item.save()
                        #add order details to order dictionary 
                        orderDict[product_id]= {'price': price, 'quantity':value, 'product_id' :product_id, 'name': product.name}
            #display success message
            messages.success(request, "Order Placed!")
        
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
        #return order details dictionary
        return orderDict
        

    else:
        messages.success(request, "Access Denied")
        return redirect('home')



def createStripePayment(request):
    if request.user.is_authenticated:
        user=request.user
        client_ref_id = createCustref(user)
    else: 
        client_ref_id = None #anonymous users 

    orderDict = handle_order(request)
    user = request.user
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
            'quantity': val['quantity'],
                    
        }
        line_items.append(line_item)

    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        client_reference_id = client_ref_id,
        payment_method_types=['card'],
        currency= 'GBP',      
        line_items=line_items,
        mode='payment',

        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('payment_failed')),
    )
    print(session)
    return redirect(session.url, code=303)


def createCustref(user):
    #check if user already has a customer record
    customer = Customer.objects.filter(email=user.email).first()

    if customer: 
        #if the customer already has an existing record, display their existing client_ref_id
        return customer.client_ref_id
    
    #generate new client_ref_id for user
    client_ref = 'Cust'
    while True:
        client_ref_id = f'{client_ref}_{random.getrandbits(4)}'
        #check if customer with generated client_ref_id exists
        if not Customer.objects.filter(client_ref_id=client_ref_id).exists():
            break

    if user.is_authenticated:
        #check if user has profile
        profile = Profile.objects.filter(user=user).first()

        if profile: 
            #if user has a profile, create or update the associated customer record
            customer, created = Customer.objects.get_or_create(
                first_name=user.first_name,
                last_name=user.last_name,
                phone=profile.phone,
                email=user.email,
                defaults={'client_ref_id': client_ref_id}
            )
            if not created:
                #if custoner record already exists, update client_ref_id
                customer.client_ref_id = client_ref_id
                customer.save()

    return client_ref_id
        

