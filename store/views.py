from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, ContactForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from django.views.generic import FormView


class ContactFormView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'
    def get_context_data(self, **kwargs):
        context = super(ContactFormView, self).get_context_data(**kwargs)
        context.update({'title':'Contact Us'})
        return context
    
    def form_valid(self, form):
        form.send_mail()
        messages.success(self.request, 'Successfully sent the enquiry')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.warning(self.request, 'Unable to send the enquiry') 
        return super().form_invalid(form)
    
    def get_success_url(self):
        return self.request.path

def search(request):
        #determine if they filled out form
        if request.method == "POST":
            searched = request.POST['searched'] #gets the input box with the name of 'searched'
            #query products database model
            searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched)) #icontains allow for search that is not case sensitive
            #test for null
            if not searched:
                    messages.success(request, "That Product Does Not Exist, Please Try Again")
                    return render(request, "search.html", {})
            else:
                return render(request, "search.html", {'searched':searched})
        else:
            return render(request, "search.html", {})


def update_info(request):
    if request.user.is_authenticated:
        #get profile from database that has id of whoever is requesting --> request.user.id = current user that is logged in
        current_user = Profile.objects.get(user__id=request.user.id)
        #get current user's shipping info 
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #when user goes on to profile page, it will already have their current information on there
        #get original user form 
        form = UserInfoForm(request.POST or None, instance=current_user)
        #get user's shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() or shipping_form.is_valid():
            #save original form 
            form.save()
            #save shipping form
            shipping_form.save()

            messages.success(request, "Your Info Has Been Updated!")
            return redirect('home')
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!")
        return redirect('home')
    




def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        #Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            #is form valoid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated")
                login(request, current_user)
                return redirect('update_user')
            else: 
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In To View That Page!")
        return redirect('home')

def update_user(request):
    if request.user.is_authenticated:
        #get user from database that has id of whoever is requesting --> request.user.id = current user that is logged in
        current_user = User.objects.get(id=request.user.id)
        #when user goes on to profile page, it will already have their current information on there
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            login(request, current_user)
            messages.success(request, "User Has Been Updated!")
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!")
        return redirect('home')




def category_summary(request):
    #grab everything from category model
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories})


def category(request, foo):
    #replace hyphens with spaces
    foo = foo.replace('-', ' ')
    #grab category from url
    try:
        #look up category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except:
        messages.success(request, ("That category does not exist"))
        return redirect('home')


def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product' :product})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products' :products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                #shopping cart
                current_user = Profile.objects.get(user__id=request.user.id)
                #get their saved cart from database
                saved_cart = current_user.old_cart
                #convert database string to python dictionary
                #is there anything saved in database and check if something is in there
                if saved_cart:
                    #convert to dictionary using JSON
                    converted_cart = json.loads(saved_cart)
                    #add loaded cart dictionary to cart session
                    cart = Cart(request)
                    #loop through the cart and add the items from the database
                    for key,value in converted_cart.items(): #grab each item from dictionary and loop through and grab key and value for each one
                        cart.db_add(product=key, quantity=value) #create new function called db_add because adding from database

                messages.success(request, ("You have been logged in"))
                return redirect('home')
            else:
                messages.success(request, ("There was an error, please try again"))
                return redirect('login')
        else:
            return render(request, 'login.html', {})
        

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #log user in
            user = authenticate(username=username, password=password)
            login(request, user)
            #instead of just registering user, redirect them to fill out the user info form so that it's like a continuous sign up.
            messages.success(request, ("Username Created, Please Fill Out Your User Information Below...!"))
            return redirect('update_info')
        else:
            messages.success(request, ("There Was A Problem Registering, Please Try Again!"))
            return redirect('register')
    else: 
        return render(request, 'register.html', {'form':form})

     