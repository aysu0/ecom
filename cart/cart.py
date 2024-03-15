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

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        #logic 
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

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
    
    def get_quants(self):
        quantites = self.cart
        return quantites 
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        #get cart
        ourcart = self.cart
        #update dictionary/cart
        ourcart[product_id] = product_qty

        self.session.modified = True
        thing = self.cart
        return thing
    
    def delete(self, product):
        product_id = str(product)
        #delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]
            
        self.session.modified = True 

    def cart_total(self):
        #get product ids
        product_ids = self.cart.keys()
        #look up keys in products database model
        products = Product.objects.filter(id__in=product_ids)
        #get quantites
        quantites = self.cart
        #start counting at 0
        total = 0

        for key, value in quantites.items():
            #convert key string into int to do the sum
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total


    # def has_product(self, product_id):
    #     # Check if the product is already in the cart
    #     return product_id in self.cart