from .cart import Cart 

#create context processor so cart can work on all pages of site
def cart(request):
    #return default data from the cart 
    return {'cart': Cart(request)}