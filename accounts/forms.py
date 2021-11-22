from django import forms
from .models import userInfo

class UserData(forms.ModelForm):
    class Meta:
        model= userInfo
        fields= ["fullname", "email", "contact", "password"]

# class LoginUser(forms.Form):
#     email = forms.CharField(required=True)
#     password = forms.CharField(required=True)

class LoginUser(forms.ModelForm):
    class Meta:
        model= userInfo
        fields= ["email", "password"]
