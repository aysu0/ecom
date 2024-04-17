from django.shortcuts import render, redirect
from .models import Product, Category
from django.contrib import messages 
from .forms import ContactForm
from django.db.models import Q
from django.views.generic import FormView
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class ContactFormView(FormView):
    #define form class to be user
    form_class = ContactForm
    template_name = 'contact.html' #the template to render and connect 

    def get_context_data(self, **kwargs):
        #call parent method to get initial context
        context = super(ContactFormView, self).get_context_data(**kwargs)
        context.update({'title':'Contact Us'}) #add title to context
        return context
    
    #handle valid form submission
    def form_valid(self, form):
        print(form.data) #print form data
        form.send_mail() #send email using form data
        messages.success(self.request, 'Successfully sent the enquiry! We will be in touch!') #display success message
        return super().form_valid(form)
    
    #handle invalid form submission
    def form_invalid(self, form):
        messages.warning(self.request, 'Unable to send the enquiry!') #display warning message
        return super().form_invalid(form)
    
    #specify URL to redirect after successful form submission
    def get_success_url(self):
        return self.request.path

def search_product(request):
        #determine if they filled out form
        if request.method == "POST":
            searched_item = request.POST['searched'] #gets the input box with the name of 'searched'
            #query products database model
            searched_results = Product.objects.filter(Q(name__icontains=searched_item) | Q(description__icontains=searched_item)) #icontains allow for search that is not case sensitive
            #test for null
            if not searched_item:
                    #if searched item doesnt exist, display message, prompt user to try again
                    messages.success(request, "No Matching Products Found, Please Try Again")
                    return render(request, "search.html", {})
            else:
                #if item exists, display item on search page 
                return render(request, "search.html", {'searched': searched_results, 'searched_item': searched_item})
        else:
            return render(request, "search.html", {})
        

# def search_product(request):
#     # Get the searched item from the form submission
#     if request.method == "POST":
#         searched_item = request.POST.get('searched', None)
#         if searched_item:
#             # Query products database model
#             searched_results = Product.objects.filter(Q(name__icontains=searched_item) | Q(description__icontains=searched_item))
#             # Paginate the search results
#             paginator = Paginator(searched_results, 4)  # 10 items per page
#             page_number = request.GET.get('page')
#             try:
#                 searched_results = paginator.page(page_number)
#             except PageNotAnInteger:
#                 searched_results = paginator.page(1)
#             except EmptyPage:
#                 searched_results = paginator.page(paginator.num_pages)
#             # Pass the paginated results to the template
#             return render(request, "search.html", {'searched': searched_results, 'searched_item': searched_item})
#         else:
#             # If no search term provided, return an empty search page
#             return render(request, "search.html", {})
#     else:
#         return render(request, "search.html", {})


def category_summary(request):
    #grab everything from category model
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories})

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product' :product})

def home(request):
    products_list = Product.objects.all()
    paginator = Paginator(products_list, 10)  #show 10 prods per page

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        #if page not integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        #if page out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {'products': products})


def about(request):
    return render(request, 'about.html', {})        

    
def category(request, bar):
    #replace hyphens with spaces
    bar = bar.replace('-', ' ')
    #grab category from url
    try:
        #look up category
        category = Category.objects.get(name=bar)
        #get products associated with category 
        items = Product.objects.filter(category=category)
        
        #pagination
        paginator = Paginator(items, 10)  #10 items per page
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            #if page not integer, deliver first page.
            products = paginator.page(1)
        except EmptyPage:
            #if page out of range (e.g. 9999), deliver last page of results.
            products = paginator.page(paginator.num_pages)
        
        #combines category page with products and category objects
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        #if category does not exist, display message and send user to homepage
        messages.error(request, "That category does not exist")
        return redirect('home')