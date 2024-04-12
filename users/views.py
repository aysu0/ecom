from django.shortcuts import render
from users.forms import CustomPasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView
from django.urls import reverse_lazy


class CustomPasswordResetView(PasswordResetView):   
    form_class = CustomPasswordResetForm
    template_name = 'password_reset_form.html'  
    success_url = reverse_lazy('password_reset_done')  
    email_template_name = 'password_reset_email.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'



def custom_password_reset_complete(request):
    return render(request, 'password_reset_complete.html')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


