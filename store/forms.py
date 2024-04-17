from django import forms
from django.core.mail import send_mail

class ContactForm(forms.Form):
    #define fields, name, email, subject and message
	name = forms.CharField(max_length=50)
	email = forms.EmailField()
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget= forms.Textarea)

	#method to send email using form data
	def send_mail(self):
        #create email by connecting the subject and sender's name 
		send_mail(self.cleaned_data.get('subject') + ', sent on behalf of ' + self.cleaned_data.get('name'), 
		self.cleaned_data.get('message'), 
		self.cleaned_data.get('email'), ['zrnyldz@gmail.com'])#the email messages get sent with send_mail function


