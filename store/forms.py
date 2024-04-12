from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm, PasswordResetForm
from django import forms
from .models import Profile
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

class ChangePasswordForm(SetPasswordForm):
    #define form fields, the passwords
    new_password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        help_text='<ul class="form-text text-muted small">'
                  '<li>Your password can\'t be too similar to your other personal information.</li>'
                  '<li>Your password must contain at least 8 characters.</li>'
                  '<li>Your password can\'t be a commonly used password.</li>'
                  '<li>Your password can\'t be entirely numeric.</li>'
                  '</ul>'
    )
    new_password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        help_text='<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
    )

    class Meta:
        #define model and fields
        model = User
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)


class UpdateUserForm(UserChangeForm):
    #hide password
    password = None
    
    #define other fields, email, first and last name
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        required=False
    )
    first_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        required=False
    )
    last_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        required=False
    )

    class Meta:
        #specify model and fields
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

		#change behaviour and appearance of field 
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'


class RegisterForm(UserCreationForm): 
    #define form fields for email, first and last name 
    email = forms.EmailField(
        label="", 
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'})
    )
    first_name = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'})
    )
    last_name = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'})
    )

    class Meta:
        #specify model and the fields
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

		#change appearance and behaviour of form fields
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'User Name'})
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class UserInfoForm(forms.ModelForm):
	phone = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}), required=False)
	address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address 1'}), required=False)
	address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address 2'}), required=False)
	city = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}), required=False)
	postcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postcode'}), required=False)
	country = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}), required=False)

	class Meta: 
		model = Profile 
		fields = ('phone', 'address1', 'address2', 'city', 'postcode', 'country', )
          

