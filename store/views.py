from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, ContactForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart
from django.views.generic import FormView
from django.core.mail import send_mail
from django.contrib.sessions.models import Session


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
            searched_item = Product.objects.filter(Q(name__icontains=searched_item) | Q(description__icontains=searched_item)) #icontains allow for search that is not case sensitive
            #test for null
            if not searched_item:
                    #if searched item doesnt exist, display message, prompt user to try again
                    messages.success(request, "No Matching Products Found, Please Try Again")
                    return render(request, "search.html", {})
            else:
                #if item exists, display item on search page 
                return render(request, "search.html", {'searched':searched_item})
        else:
            return render(request, "search.html", {})
        

def update_information(request):
    if request.user.is_authenticated:
        #get profile from database that has id of whoever is requesting --> request.user.id = current user that is logged in
        user_profile = Profile.objects.get(user__id=request.user.id)
        #get current user's shipping info 
        user_shipping = ShippingAddress.objects.get(user__id=request.user.id)
        #when user goes on to profile page, it will already have their current information on there
        #get original user form 
        user_form = UserInfoForm(request.POST or None, instance=user_profile)
        #get user's shipping form
        shipping_form = ShippingForm(request.POST or None, instance=user_shipping)

        if user_form.is_valid() or shipping_form.is_valid():
            #save original form 
            user_form.save()
            #save shipping form
            shipping_form.save()

            messages.success(request, "Your Information Has Been Updated Successfully!")
            return redirect('home')
        return render(request, 'update_info.html', {'form': user_form, 'shipping_form': shipping_form})
    else:
        messages.success(request, "You Must Be Logged In To Access This Page!")
        return redirect('home')
    
def update_password(request):
    #check to see if the user is authenticated
    if request.user.is_authenticated:
        current_user = request.user
        #check to see if the user has filled out the form 
        if request.method == 'POST':
            #creating an instance of changepasswordform with current user and form data
            update_password_form = ChangePasswordForm(current_user, request.POST)
            #is form valid?
            if update_password_form.is_valid():
                #save updated password
                update_password_form.save()
                messages.success(request, "Your Password Has Been Updated")
                #log user in with updated password 
                login(request, current_user)
                return redirect('update_user') #redirect to update profile page 
            else: 
                #if form not valid in any way, display error message 
                for error in list(update_password_form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password') #redirect to the update password page
        else:
            update_password_form = ChangePasswordForm(current_user) #if request method is not POST, send user to update password page with form
            return render(request, 'update_password.html', {'form': update_password_form})
    else:
        messages.success(request, "You Must Be Signed In To View That Page!")#if user not authenticated, display message and redirect to the homepage
        return redirect('home')




def update_user(request):
    if request.user.is_authenticated:
        #get user from database that has id of whoever is requesting --> request.user.id = current user that is logged in
        current_user = User.objects.get(id=request.user.id)
        #when user goes on to profile page, it will already have their current information on there
        profile_form = UpdateUserForm(request.POST or None, instance=current_user)

        if profile_form.is_valid():
            #save the updated user information
            profile_form.save()
            #login the user
            login(request, current_user)
            #show success message if update was successful
            messages.success(request, "User Profile Has Been Updated!")
            return redirect('home') #and redirect user to homepage
        return render(request, 'update_user.html', {'user_form': profile_form})
    else:
        #if user not authenticated, display message and redirect to homepage
        messages.success(request, "You Must Be Logged In To Access That Page!")
        return redirect('home')
    
def user_signup(request):
    register_form = RegisterForm()
    #check of request method is post 
    if request.method == "POST":
        #if post, populate registerform with post data
        register_form = RegisterForm(request.POST)
        if register_form.is_valid(): #check if input is valid 
            register_form.save() #save data to create new user 
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password1']
            #log user in
            user = authenticate(username=username, password=password)
            login(request, user)
            #instead of just registering user, redirect them to fill out the user info form so that it's like a continuous sign up.
            messages.success(request, ("Username Created, Please Fill Out Your User Information Below...!"))
            return redirect('update_info')
        else:
            #if form invalid, display error message and redirect to register page 
            messages.success(request, ("There Was A Problem Registering, Please Try Again!"))
            return redirect('register')
    else: 
        return render(request, 'register.html', {'form':register_form}) #if not post, render register.html with register_form

     
def category_summary(request):
    #grab everything from category model
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories})

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product' :product})



def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products' :products})

def login_customer(request):
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                #shopping cart
                current_user = Profile.objects.get(user__id=request.user.id)
                #get their saved cart from database
                stored_cart = current_user.old_cart
                #convert database string to python dictionary
                #is there anything saved in database and check if something is in there
                if stored_cart:
                    #convert to dictionary using JSON
                    converted_cart = json.loads(stored_cart)
                    #add loaded cart dictionary to cart session
                    cart = Cart(request)
                    #loop through the cart and add the items from the database
                    for key,value in converted_cart.items(): #grab each item from dictionary and loop through and grab key and value for each one
                        cart.db_add(product=key, quantity=value) #create new function called db_add because adding from database
                #if credentials match to database, login user in and display message and redirect user to homepage
                messages.success(request, ("You have been logged in"))
                return redirect('home')
            else:
                #if credentials don't match to database, display error message 
                messages.success(request, ("There was an error, please try again"))
                return redirect('login')
        else:
            return render(request, 'login.html', {})
        
def about(request):
    return render(request, 'about.html', {})        

def logout_customer(request):
    logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect('home')

def category(request, bar):
    #replace hyphens with spaces
    bar = bar.replace('-', ' ')
    #grab category from url
    try:
        #look up category
        category = Category.objects.get(name=bar)
        #get products assosciated with category 
        items = Product.objects.filter(category=category)
        #combines category page with products and category objects
        return render(request, 'category.html', {'products':items, 'category':category})
    except:
        #if category does not exist, display message and send user to homepage
        messages.success(request, ("That category does not exist"))
        return redirect('home')
    
