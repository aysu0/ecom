from django.shortcuts import render, redirect
from cart.cart import Cart 
from payment.forms import ShippingForm, PurchaseForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib import messages 
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User


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
        "shipping_form": shipping_form
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
            "billing": billing
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
            "billing": billing

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


def handle_order(request):
    if request.POST:
        #get cart information
        cart = Cart(request)
        cart_products = cart.get_prods()  # Ensure to call the method
        quantities = cart.get_quants()
        #calculate total
        totals = cart.cart_total()

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

            messages.success(request, "Order Placed!")
            return redirect('home')
        
        else: 
            #not logged in
            createorder = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            createorder.save()

            messages.success(request, "Order Placed!")
            return redirect('home')

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def payment_success(request):
    return render(request, "payment/payment_success.html", {})