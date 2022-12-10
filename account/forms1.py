# -*- coding: utf-8 -*-
from django import forms
from account.models import Profile
 
class UploadPhotoForm(forms.ModelForm):
 
    class Meta:
        model = Profile
        fields = ['photo']
        
class SettingsForm(forms.ModelForm):

    first_name = forms.CharField(max_length = 30, label='Имя', required=False)
    last_name = forms.CharField(max_length = 30, label='Фамилия', required=False)

    class Meta:
        model = Profile
        fields = ['photo', 'first_name', 'last_name', 'nickname',
                'games', 'directions', 'regions', 'contacts']

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields['games'].empty_label = "Не выбрано"
        # following line needed to refresh widget copy of choice list
        # https://stackoverflow.com/questions/739260/customize-remove-django-select-box-blank-option
        self.fields['games'].widget.choices = self.fields['games'].choices
        self.fields['directions'].empty_label = "Не выбрано"
        self.fields['directions'].widget.choices = self.fields['directions'].choices
        self.fields['regions'].empty_label = "Не выбрано"
        self.fields['regions'].widget.choices = self.fields['regions'].choices        
        
