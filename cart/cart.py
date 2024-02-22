from store.models import Product


class Cart():
    def __init__(self, request):
        self.session = request.session

        #get current session key if exists
        cart = self.session.get('session_key')

        #if user new, no session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        
        #make sure cqart is available on all pages of site
        self.cart = cart 

    def add(self, product):
        product_id = str(product.id)

        #logic 
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = {'price': str(product.price)}

        self.session.modified = True

    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        #get ids from cart 
        product_ids = self.cart.keys()
        #use ids to look up products in database model
        products = Product.objects.filter(id__in=product_ids)
        #return those looked up products
        return products