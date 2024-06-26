from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def shoppingcart_summary(request):
    #get cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {"cart_products": cart_products, "quantities": quantities, "totals": totals})

def shoppingcart_add(request):
    #get the cart
    cart = Cart(request)
    #test for POST
    if request.POST.get('action') == 'post':
        # get product id and quantity
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        #lookup product in database
        product = get_object_or_404(Product, id=product_id)
        #save to session
        cart.add(product=product, quantity=product_qty)

        #get cart quantity 
        cart_quantity = cart.__len__()
        #return response
        # response = JsonResponse({'Product Name: ': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product Added To Cart!"))
        return response


def shoppingcart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        #get stuff
        product_id = int(request.POST.get('product_id'))
        #call delete function in cart
        cart.delete(product=product_id)

        response = JsonResponse({'product':product_id})
        messages.success(request, ("Item Deleted From Shopping Cart!"))
        return response



def shoppingcart_update(request):
    #create instance of cart object
    cart = Cart(request)

    #check if request method is POST and the action is post 
    if request.POST.get('action') == 'post':
        # get id, quantity
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        #update cart with new quantity for specified product
        cart.update(product=product_id, quantity=product_qty)

        #create JSON response with updated quantity 
        response = JsonResponse({'qty':product_qty})

        #display a success message
        messages.success(request, ("Your Cart Has Been Updated!"))
        return response




