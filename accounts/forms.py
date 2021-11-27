from django import forms
from .models import userInfo

class UserData(forms.ModelForm):
    class Meta:
        model= userInfo
        fields= ["fullname", "email", "contact", "password"]

class LoginUser(forms.ModelForm):
    class Meta:
        model= userInfo
        fields= ["email", "password"]

class StockData(forms.Form):
    stock = forms.CharField()
