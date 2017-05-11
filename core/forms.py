from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm 
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from core.models import EmployeeDocument

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username', 'placeholder': 'Username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password', 'placeholder': 'Password'}))


class DocumentForm(forms.Form):
	employee_id = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control'}))
	class Meta:
		model = EmployeeDocument

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("There is no user registered with the specified email address!")

        return email




		
	