from django import forms
from coach_office.models import Stars
from superuser.models import Settings


class ChangeLessonsCapForm(forms.ModelForm):
    '''Изменить максимально допустимое число предстоящих записей на уроки на странице Админ-Настройки'''

    class Meta:
        model = Settings
        fields = ['registrations_cap']


class ChangeRegistrationsPeriodForm(forms.ModelForm):
    '''Изменить максимальное число дней вперёд, на которые можно записаться, для студента  на странице Админ-Настройки'''

    class Meta:
        model = Settings
        fields = ['registrations_period']


class ChangeStarsLevelForm(forms.Form):
    '''Изменить уровень звёзд у Наставника на странице Админ - Наставники'''

    stars = forms.ModelChoiceField(Stars.objects.all(), required=False, empty_label="Уровень звёзд")