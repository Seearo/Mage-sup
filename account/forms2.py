from django import forms
from account.models import Profile, Game, Direction, Region
from django.contrib.auth.models import User


class BookmarksSortingForm(forms.Form):

    SORTING_CHOICES =   [(1, "новым"),
                        (2, "имени"),
                        (3, "звёздам -"),
                        (4, "звёздам +")]

    #https://stackoverflow.com/questions/68071627/how-to-store-the-default-value-for-a-django-form-in-the-database/68073938#68073938
    bm_sorting = forms.ChoiceField(choices=SORTING_CHOICES)

    # https://stackoverflow.com/questions/6325681/passing-a-user-request-to-forms
    # In your view: form = MyForm(..., request=request)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields['bm_sorting'].initial = BookmarksSortingForm.SORTING_CHOICES[self.get_current_sorting() - 1]

    def get_current_sorting(self):
        user = User.objects.get(username=self.request.user)
        return user.profile.bookmarks_sorting # small integer, default = 1


class FriendsSortingForm(forms.Form):

    SORTING_CHOICES =   [(1, "новым"),
                        (2, "имени"),
                        (3, "на рассмотрении"),
                        (4, "взаимные"),
                        (5, "полученные заявки")]

    fr_sorting = forms.ChoiceField(choices=SORTING_CHOICES)

    # https://stackoverflow.com/questions/6325681/passing-a-user-request-to-forms
    # In your view: form = MyForm(..., request=request)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields['fr_sorting'].initial = FriendsSortingForm.SORTING_CHOICES[self.get_current_sorting() - 1]

    def get_current_sorting(self):
        user = User.objects.get(username=self.request.user)
        return user.profile.friends_sorting # small integer, default = 1


class SettingsForm(forms.ModelForm):

    first_name = forms.CharField(max_length = 30, label='Имя', required=False)
    last_name = forms.CharField(max_length = 30, label='Фамилия', required=False)

    game = forms.ModelChoiceField(Game.objects.all(), required=False, empty_label="Не выбрано")
    direction = forms.ModelChoiceField(Direction.objects.all(), required=False, empty_label="Не выбрано")
    region = forms.ModelChoiceField(Region.objects.all(), required=False, empty_label="Не выбрано")


    class Meta:
        model = Profile
        fields = ['photo', 'nickname', 'contacts']


class UploadPhotoForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['photo']

    '''
    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields['games'].empty_label = "Не выбрано"
        # following line needed to refresh widget copy of choice list
        # https://stackoverflow.com/questions/739260/customize-remove-django-select-box-blank-option
        self.fields['games'].widget.choices = self.fields['games'].choices
        self.fields['directions'].empty_label = "Не выбрано"
        self.fields['directions'].widget.choices = self.fields['directions'].choices
        self.fields['regions'].empty_label = "Не выбрано"
        self.fields['regions'].widget.choices = self.fields['regions'].
    '''

    '''
    # много галочек http://www.joshuakehn.com/2013/6/23/django-m2m-modelform.html
    def __init__ (self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields["games"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["games"].help_text = ""
        self.fields["games"].queryset = Game.objects.all()
    '''