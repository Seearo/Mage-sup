# -*- coding: utf-8 -*-
from django import forms
from account.models import Game, Direction, Region
from coach_office.models import CoachProfile


class SettingsForm(forms.ModelForm):

    game1 = forms.ModelChoiceField(Game.objects.all(), required=False, empty_label="Выбирайте...")
    direction1 = forms.ModelChoiceField(Direction.objects.all(), required=False, empty_label="Выбирайте...")
    region1 = forms.ModelChoiceField(Region.objects.all(), required=False, empty_label="Выбирайте...")

    game2 = forms.ModelChoiceField(Game.objects.all(), required=False, empty_label="Выбирайте...")
    direction2 = forms.ModelChoiceField(Direction.objects.all(), required=False, empty_label="Выбирайте...")
    region2 = forms.ModelChoiceField(Region.objects.all(), required=False, empty_label="Выбирайте...")

    game3 = forms.ModelChoiceField(Game.objects.all(), required=False, empty_label="Выбирайте...")
    direction3 = forms.ModelChoiceField(Direction.objects.all(), required=False, empty_label="Выбирайте...")
    region3 = forms.ModelChoiceField(Region.objects.all(), required=False, empty_label="Выбирайте...")

    contacts = forms.Textarea(attrs={'placeholder': 'Ваши контактные данные видны только модераторам и ученикам'})

    PHOTO_CHOICES = [
                    ('', 'Показывать на фото...'),
                    (1, 'Показывать основное фото профиля'),
                    (2, 'Показывать стандартное изображение (девушка)'),
                    (3, 'Показывать стандартное изображение (парень)'),
                    ]
    which_photo = forms.ChoiceField(choices=PHOTO_CHOICES, required=False)

    BUTTON_CHOICES = [
                    ('', 'Выбирайте...'),
                    (1, 'Отсутствует'),
                    (2, 'Только для учеников'),
                    (3, 'Для всех'),
                    ]
    show_button = forms.ChoiceField(choices=BUTTON_CHOICES, required=False)

    game_accounts = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'Вставляйте ссылку на профиль сюда', 'size': 240}), required=False)

    nickname_flag_checked = forms.BooleanField(required=False,
                               widget=forms.CheckboxInput({
                                   'class': 'form-check-input',
                                   'id': 'exampleCheck1',
                                   'checked' : ''}))
    nickname_flag_not_checked = forms.BooleanField(required=False,
                               widget=forms.CheckboxInput({
                                   'class': 'form-check-input',
                                   'id': 'exampleCheck1'}))

    search_flag_checked = forms.BooleanField(required=False,
                               widget=forms.CheckboxInput({
                                   'class': 'form-check-input',
                                   'id': 'exampleCheck2',
                                   'checked' : ''}))
    search_flag_not_checked = forms.BooleanField(required=False,
                               widget=forms.CheckboxInput({
                                   'class': 'form-check-input',
                                   'id': 'exampleCheck2'}))

    inactive_flag_checked = forms.BooleanField(required=False,
                               widget=forms.CheckboxInput({
                                   'class': 'form-check-input',
                                   'id': 'exampleCheck3',
                                   'checked' : ''}))
    inactive_flag_not_checked = forms.BooleanField(required=False,
                               widget=forms.CheckboxInput({
                                   'class': 'form-check-input',
                                   'id': 'exampleCheck3'}))


    class Meta:
        model = CoachProfile
        fields = ['description', 'strengths']
