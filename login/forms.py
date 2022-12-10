# -*- coding: utf-8 -*-
from django import forms
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MySignupForm(forms.ModelForm):
    email = forms.EmailField(max_length=75, required=True)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('username',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Пароли не совпадают.")
        return cd['password2']

'''
class MySignupForm(UserCreationForm):

    # уже есть: имя пользователя, пароль, подтверждение пароля
    email = forms.EmailField(max_length=75, required=True)

    # class Meta:
    #    model = User
    #    fields = ('username', 'email', 'password1', 'password2', )
'''

class MyLoginForm(forms.ModelForm):

    #username = forms.CharField(max_length=30, label='Логин')
    #password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('username', 'password')