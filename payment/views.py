from django.shortcuts import render
from cart.cart import Cart 
from payment.forms import ShippingForm 
from payment.models import ShippingAddress
from django.contrib import messages 
from django.http import HttpResponseRedirect
from django.urls import reverse


# def checkout(request):
#     #get cart
#     cart = Cart(request)
#     cart_products = cart.get_prods
#     quantities = cart.get_quants
#     totals = cart.cart_total()

#     if request.user.is_authenticated:
#         #checkout as logged in user
#         #shipping user
#         shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
#         #shipping form
#         shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
#         return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals, "shipping_form": shipping_form })

#     else:
#         #checkout as guest 
#         shipping_form = ShippingForm(request.POST or None)
#         return render(request, "payment/checkout.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals, "shipping_form": shipping_form})


def checkout(request):
    # Get cart information
    cart = Cart(request)
    cart_products = cart.get_prods()  # Ensure to call the method
    quantities = cart.get_quants()

    # Calculate total
    totals = cart.cart_total()

    # Check if the total is less than £50
    if totals < 50:
        messages.error(request, "Minimum order amount is £50. Please add more items to your cart.")
        return HttpResponseRedirect(reverse('cart_summary'))

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Checkout as a logged-in user
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
    else:
        # Checkout as a guest
        shipping_form = ShippingForm(request.POST or None)

    # Render the checkout page with context data
    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form
    })


def payment_success(request):
    return render(request, "payment/payment_success.html", {})