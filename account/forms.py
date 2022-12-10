from django import forms
from account.models import Profile, Game, Direction, Friendship, Message, Region
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


class DiarySortingForm(forms.Form):

    SORTING_CHOICES =   [(1, "обновлённым"),
                        (2, "занятиям в качестве Наставника по имени студента"),
                        (3, "занятиям в качестве Наставника по дате"),
                        (4, "занятиям в качестве студента по имени Наставника"),
                        (5, "занятиям в качестве студента по дате")]

    diary_sorting = forms.ChoiceField(choices=SORTING_CHOICES)

    # https://stackoverflow.com/questions/6325681/passing-a-user-request-to-forms
    # In your view: form = MyForm(..., request=request)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields['diary_sorting'].initial = DiarySortingForm.SORTING_CHOICES[self.get_current_sorting() - 1]

    def get_current_sorting(self):
        user = User.objects.get(username=self.request.user)
        return user.profile.diary_sorting # small integer, default = 1


class FriendsCommentingForm(forms.ModelForm):

    class Meta:
        model = Friendship
        fields = ['comment']


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


class MessagesSortingForm(forms.Form):

    SORTING_CHOICES =   [(1, "Новые"),
                        (2, "Все полученные"),
                        (3, "От друзей"),
                        (4, "От Наставников"),
                        (5, "От команды сайта"),
                        (6, "Все отправленные")]

    ms_sorting = forms.ChoiceField(choices=SORTING_CHOICES)

    # https://stackoverflow.com/questions/6325681/passing-a-user-request-to-forms
    # In your view: form = MyForm(..., request=request)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields['ms_sorting'].initial = MessagesSortingForm.SORTING_CHOICES[self.get_current_sorting() - 1]

    def get_current_sorting(self):
        user = User.objects.get(username=self.request.user)
        return user.profile.messages_sorting # small integer, default = 1


class MessageWritingForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ['text']


class RegistrationForm(forms.Form):
    '''Форма при записи на урок к Наставнику по кнопке Запись в Закладках или Профиле при сортировке На определённую дату'''

    def __init__(self, *args, **kwargs):
        datetimes = kwargs.pop("datetimes", None)  # не могу раздельно время и дату, как обновить страницу после выбора даты для нового списка времени
        current_game = kwargs.pop("game", None)
        current_direction = kwargs.pop("direction", None)
        current_region = kwargs.pop("region", None)
        self.request = kwargs.pop("request", None)
        user = User.objects.get(username=self.request.user) if self.request else None

        super(RegistrationForm, self).__init__(*args, **kwargs)
        datetime_choices = self.make_datetimes_tuples(datetimes) if datetimes else []
        self.fields['datetime'] = forms.ChoiceField(choices=datetime_choices, required=True,
                                initial=datetime_choices[0] if datetime_choices else None)
        self.fields['game'] = forms.ModelChoiceField(queryset=Game.objects.all(),
                                                             initial=current_game,
                                                             required=False,
                                                             empty_label="Не выбрано")
        self.fields['direction'] = forms.ModelChoiceField(queryset=Direction.objects.all(),
                                                           initial=current_direction,
                                                           required=False,
                                                           empty_label="Не выбрано")
        self.fields['region'] = forms.ModelChoiceField(queryset=Region.objects.all(),
                                                             initial=current_region,
                                                             required=False,
                                                             empty_label="Не выбрано")
        self.fields['email'] = forms.EmailField(max_length=75, label='Email', required=False,
                                initial=user.email if user else None)
        self.fields['phone_number'] = forms.CharField(max_length=15, label='Телефонный номер', required=False,
                                initial=user.profile.phone_number if user else None)
        self.fields['contacts'] = forms.CharField(max_length=200, required=False, widget=forms.Textarea,
                                    initial=user.profile.contacts if user else None)

    # преобразовать список кортежей дат и времени [(2021,12,25,12,0)] в список кортежей [("2021-12-25-12-0", "25.12.2021 12:00 - 12:45")]
    @staticmethod
    def make_datetimes_tuples(datetimes):
        res = [("", "Выберите дату и время")]
        for year, month, day, hour, minute in datetimes:
            res.append((f"{year}-{month}-{day}-{hour}-{minute}", f"{day}.{month}.{year} {hour}:00 - {hour}:45 МСК"))
        return res


class RegistrationGameForm(forms.Form):
    '''Выбор игры, направления и региона при записи на урок к Наставнику по кнопке Запись в Закладках или Профиле при сортировке На все даты'''

    # https://stackoverflow.com/questions/55357658/set-default-value-for-a-django-modelchoicefield
    # widget=forms.Select(attrs={'class': 'form-control'})  -- на всю строку
    def __init__(self, *args, **kwargs):
        current_game = kwargs.pop("game", None)
        current_direction = kwargs.pop("direction", None)
        current_region = kwargs.pop("region", None)

        super(RegistrationGameForm, self).__init__(*args, **kwargs)
        self.fields['game'] = forms.ModelChoiceField(queryset=Game.objects.all(),
                                                             initial=current_game,
                                                             required=False,
                                                             empty_label="Не выбрано")
        self.fields['direction'] = forms.ModelChoiceField(queryset=Direction.objects.all(),
                                                           initial=current_direction,
                                                           required=False,
                                                           empty_label="Не выбрано")
        self.fields['region'] = forms.ModelChoiceField(queryset=Region.objects.all(),
                                                             initial=current_region,
                                                             required=False,
                                                             empty_label="Не выбрано")


class RegistrationSortingForm(forms.Form):
    '''Выбор типа сортировки на странице Запись по кнопке Запись в Закладках или Профиле Наставника'''

    SORTING_CHOICES =   [(1, "на определённую дату"),
                        (2, "на все даты")]

    reg_sorting = forms.ChoiceField(choices=SORTING_CHOICES)

    # https://stackoverflow.com/questions/6325681/passing-a-user-request-to-forms
    # In your view: form = MyForm(..., request=request)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.fields['reg_sorting'].initial = RegistrationSortingForm.SORTING_CHOICES[self.get_current_sorting() - 1]

    def get_current_sorting(self):
        user = User.objects.get(username=self.request.user)
        return user.profile.registration_sorting # small integer, default = 1


class SettingsForm(forms.ModelForm):
    '''Страница Настройки Профиля'''

    first_name = forms.CharField(max_length = 30, label='Имя', required=False)
    last_name = forms.CharField(max_length = 30, label='Фамилия', required=False)

    game = forms.ModelChoiceField(Game.objects.all(), required=False, empty_label="Не выбрано")
    direction = forms.ModelChoiceField(Direction.objects.all(), required=False, empty_label="Не выбрано")
    region = forms.ModelChoiceField(Region.objects.all(), required=False, empty_label="Не выбрано")

    email = forms.EmailField(max_length=75, label='Email', required=False)
    phone_number = forms.CharField(max_length=15, label='Телефонный номер', required=False)

    class Meta:
        model = Profile
        fields = ['photo', 'nickname', 'contacts']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        user = User.objects.get(username=self.request.user) if self.request else None
        super(SettingsForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone_number'].initial = user.profile.phone_number
            self.fields['nickname'].initial = user.profile.nickname
            self.fields['contacts'].initial = user.profile.contacts
            try:
                gamedirection = user.profile.gamedirections.get(number=1)
            except:
                gamedirection = None
            if gamedirection:
                self.fields['game'].initial = gamedirection.game
                self.fields['direction'].initial = gamedirection.direction
                self.fields['region'].initial = gamedirection.region


class UploadPhotoForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['photo']