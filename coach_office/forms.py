from django import forms
from account.models import Game, Direction, Region
from coach_office.models import AvailableTime, CoachProfile


class AvailableTimeChangeForm(forms.ModelForm):
    class Meta:
        model = AvailableTime
        fields = ['start_day', 'end_day']


class AvailableTimeForm(forms.ModelForm):

    DAY_OF_WEEK_CHOICES =   [(0, "понедельник"),
                        (1, "вторник"),
                        (2, "среда"),
                        (3, "четверг"),
                        (4, "пятница"),
                        (5, "суббота"),
                        (6, "воскресенье"),
                        (7, "все будни"),
                        (8, "все выходные"),
                        (9, "все дни")]
    day_of_week = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES)

    TIME_CHOICES = [('00', "0:00"),
                    ('01', "1:00"),
                    ('02', "2:00"),
                    ('03', "3:00"),
                    ('04', "4:00"),
                    ('05', "5:00"),
                    ('06', "6:00"),
                    ('07', "7:00"),
                    ('08', "8:00"),
                    ('09', "9:00"),
                    ('10', "10:00"),
                    ('11', "11:00"),
                    ('12', "12:00"),
                    ('13', "13:00"),
                    ('14', "14:00"),
                    ('15', "15:00"),
                    ('16', "16:00"),
                    ('17', "17:00"),
                    ('18', "18:00"),
                    ('19', "19:00"),
                    ('20', "20:00"),
                    ('21', "21:00"),
                    ('22', "22:00"),
                    ('23', "23:00"),
                    ('00', "24:00"),
                    ]
    start_time = forms.ChoiceField(choices=TIME_CHOICES[:-1])
    end_time = forms.ChoiceField(choices=TIME_CHOICES[1:])


    class Meta:
        model = AvailableTime
        fields = ['start_day', 'end_day']


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

    # contacts = forms.Textarea(attrs={'placeholder': 'Ваши контактные данные видны только модераторам и ученикам'})

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
        fields = ['description', 'strengths', 'contacts']
