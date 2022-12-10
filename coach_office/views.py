'''Страницы, доступные только Наставникам'''

from django.shortcuts import render, redirect
from django.conf import settings
import datetime
from django.views import View
from django.contrib.auth.models import User
from coach_office.forms import SettingsForm
from account.models import GameDirection, Game, Direction, Message, Region
from account.views import available_times_to_datetimes, get_new_diary, level_up
from coach_office.models import GameAccount, AvailableTime
from coach_office.forms import AvailableTimeChangeForm, AvailableTimeForm


def same_day_of_week(day1, day2):
    day1 = int(day1)
    day2 = int(day2)
    if day1 == 7 and day2 in [0, 1, 2, 3, 4]:
        return True
    if day1 == 8 and day2 in [5, 6]:
        return True
    if day1 == 9:
        return True
    if day1 == day2:
        return True
    return False


# при выводе на странице всё актуализировано на сегодняшний день
# дни от сегодня и далее, end больше start
def same_period(start_day1, start_day2, end_day1, end_day2):
    if not end_day1 and start_day1 <= start_day2:
        return True
    if not end_day2:
        if start_day1 <= start_day2:
            return True
        return False
    if start_day1 <= start_day2 and end_day1 >= end_day2:
        return True
    return False


class AvailableTimeAsStudentView(View):
    '''Страница по кнопке Просмотеть расписание доступного времени как студент на странице Доступного времени по кнопке в Расписании Профиля Наставника'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            registrations = get_new_diary(user)
            context['new_diary'] = len(registrations)
            available_datetimes, period = available_times_to_datetimes(user, None)
            context['available_datetimes'] = available_datetimes
            context['period'] = period
            return render(request, 'coach_office/available_time_as_student.html', context=context)
        else:
            return redirect('../index.html')


class AvailableTimeChangeFormView(View):
    '''Изменение даты окончания расписания доступного времени по кнопке в Расписании в Профиле у Наставников'''

    def post(self, request, available_time_id, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('coach_profile').get(username=request.user)
            if not user.profile.coach:
                return redirect('../account/profile.html/user_id{0}'.format(user.id))
            form = AvailableTimeChangeForm(request.POST)
            if form.is_valid():
                available_time = AvailableTime.objects.get(id=available_time_id)
                if request.POST.get('start_day'):
                    start_day = datetime.datetime.strptime(request.POST.get('start_day'), "%d.%m.%Y").date()
                    if start_day < datetime.datetime.today().date() + datetime.timedelta(days=1):
                        start_day = datetime.datetime.today().date() + datetime.timedelta(days=1)
                    available_time.start_day = start_day
                    available_time.save()
                if request.POST.get('end_day'):
                    end_day = datetime.datetime.strptime(request.POST.get('end_day'), "%d.%m.%Y").date()
                    if end_day >= available_time.start_day:  # start_day не раньше завтра, уже проверено при get-запросе
                        available_time.end_day = end_day
                        available_time.save()
                else:
                    available_time.end_day = None
                    available_time.save()
            return redirect('../coach_office/available_time.html')
        else:
            return redirect('index.html')


class AvailableTimeDeleteView(View):
    '''Кнопка удаления расписания доступного времени по кнопке в Расписании в Профиле у Наставников'''

    def post(self, request, available_time_id, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('coach_profile').get(username=request.user)
            if not user.profile.coach:
                return redirect('../account/profile.html/user_id{0}'.format(user.id))
            available_time = AvailableTime.objects.get(id=available_time_id)
            available_time.delete()
            return redirect('../coach_office/available_time.html')
        else:
            return redirect('index.html')


class AvailableTimeFormView(View):

    '''Отправка данных на странице Доступное время Наставника по кнопке в Расписании в Профиле у Наставников'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('coach_profile').get(username=request.user)
            if not user.profile.coach:
                return redirect('../account/profile.html/user_id{0}'.format(user.id))
            form = AvailableTimeForm(request.POST, instance=user.coach_profile)
            if form.is_valid():
                available_time = AvailableTime()  # not saved yet
                need_to_save = False  # если повтор, то не сохраним
                available_time.coach = user.coach_profile
                if request.POST.get('day_of_week') and request.POST.get('start_time') \
                    and request.POST.get('end_time'):
                    available_time.day_of_week = int(request.POST.get('day_of_week'))
                    available_time.start_time = datetime.datetime.strptime(request.POST.get('start_time'), "%H").time()
                    end_time = datetime.datetime.strptime(request.POST.get('end_time'), "%H").time()
                    if end_time > available_time.start_time or request.POST.get('end_time') == "00":
                        available_time.end_time = end_time
                        need_to_save = True
                if request.POST.get('start_day'):
                    start_day = datetime.datetime.strptime(request.POST.get('start_day'), "%d.%m.%Y").date()
                    if start_day < datetime.datetime.today().date() + datetime.timedelta(days=1):
                        start_day = datetime.datetime.today().date() + datetime.timedelta(days=1)
                    available_time.start_day = start_day
                if request.POST.get('end_day'):
                    end_day = datetime.datetime.strptime(request.POST.get('end_day'), "%d.%m.%Y").date()
                    if end_day > available_time.start_day:
                        available_time.end_day = end_day
                    else:
                        need_to_save = False
                if need_to_save:
                    available_times = AvailableTime.objects.filter(coach=user.coach_profile)
                    for av_time in available_times:
                        if av_time.start_time == available_time.start_time and \
                            av_time.end_time == available_time.end_time and \
                            same_day_of_week(av_time.day_of_week, available_time.day_of_week) and \
                            same_period(av_time.start_day, available_time.start_day,
                                        av_time.end_day, available_time.end_day):
                            need_to_save = False
                            break
                if need_to_save:
                    available_time.save()
            return redirect('../coach_office/available_time.html')
        else:
            return redirect('index.html')


class AvailableTimeView(View):

    '''Страница Доступное время Наставника по кнопке в Расписании у Наставников'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user)
            if user.profile.coach:
                context = dict()
                context['trademark'] = settings.TRADEMARK
                context['current_year'] = datetime.datetime.now().strftime('%Y')
                context['user'] = user
                context['available_time_form'] = AvailableTimeForm()
                new_messages = Message.objects.filter(recipient=user.profile, status=0)
                context['new_messages'] = len(new_messages)
                registrations = get_new_diary(user)
                context['new_diary'] = len(registrations)
                available_times = AvailableTime.objects.filter(coach=user.coach_profile)
                to_remove = []
                for available_time in available_times:
                    if available_time.start_day < datetime.datetime.today().date() + datetime.timedelta(days=1):
                        available_time.start_day = datetime.datetime.today().date() + datetime.timedelta(days=1)
                        available_time.save()
                    if available_time.end_day and available_time.start_day > available_time.end_day:
                        available_time.delete()
                        to_remove.append(available_time)
                for available_time in to_remove:
                    available_times.remove(available_time)
                context['available_times'] = available_times
                context['available_time_change_form'] = AvailableTimeChangeForm()
                context['midnight'] = datetime.datetime.strptime('00', "%H").time()
                return render(request, 'coach_office/available_time.html', context=context)
            else:
                return redirect('../profile.html/user_id{0}'.format(user.id))
        else:
            return redirect('index.html')


class CoachOfficeView(View):

    '''Страница Наставник в Профиле у Наставников'''

    def get(self, request, user_id, *args, **kwargs):
        requested_user = User.objects.filter(id=user_id)[0]
        if not requested_user:
            return redirect('index.html')
        if requested_user.profile.coach:
            if request.user.is_authenticated:
                context = dict()
                context['trademark'] = settings.TRADEMARK
                context['current_year'] = datetime.datetime.now().strftime('%Y')
                user = User.objects.select_related('profile').get(username=request.user)
                context['user'] = user
                if request.user.id == user_id:
                    context['settings_form'] = SettingsForm()
                    context['level_up'] = level_up(user.profile.level)
                    context['value_now'] = round(user.profile.level / context['level_up'] * 100)
                    new_messages = Message.objects.filter(recipient=user.profile, status=0)
                    context['new_messages'] = len(new_messages)
                    registrations = get_new_diary(user)
                    context['new_diary'] = len(registrations)
                    return render(request, 'coach_office/coach-office.html', context=context)
                else:
                    return render(request, 'coach_office/other/coach_office.html', context=context)
            else:
                return render(request, 'coach_office/other/coach_office.html', context={'trademark': settings.TRADEMARK, 'current_year': datetime.now().strftime('%Y')})
        else:
            return redirect('index.html')

class SettingsView(View):

    '''Отправка данных на странице Наставник в Профиле у Наставников'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user)
            form = SettingsForm(request.POST, request.FILES, instance=request.user.profile)
            if form.is_valid():
                if request.POST.get('game1') or request.POST.get('direction1') or request.POST.get('region1'):
                    gamedirection = GameDirection()
                    gamedirection.number = 2
                    if request.POST.get('game1'):
                        gamedirection.game = Game.objects.get(id = request.POST.get('game1'))
                    if request.POST.get('direction1'):
                        gamedirection.direction = Direction.objects.get(id = request.POST.get('direction1'))
                    if request.POST.get('region1'):
                        gamedirection.region = Region.objects.get(id = request.POST.get('region1'))
                    gamedirection.save()
                    for obj in user.profile.gamedirections.filter(number=2):
                        user.profile.gamedirections.remove(obj)
                        obj.delete()
                    user.profile.gamedirections.add(gamedirection)
                if request.POST.get('game2') or request.POST.get('direction2') or request.POST.get('region2'):
                    gamedirection = GameDirection()
                    gamedirection.number = 3
                    if request.POST.get('game2'):
                        gamedirection.game = Game.objects.get(id = request.POST.get('game2'))
                    if request.POST.get('direction2'):
                        gamedirection.direction = Direction.objects.get(id = request.POST.get('direction2'))
                    if request.POST.get('region2'):
                        gamedirection.region = Region.objects.get(id = request.POST.get('region2'))
                    gamedirection.save()
                    for obj in user.profile.gamedirections.filter(number=3):
                        user.profile.gamedirections.remove(obj)
                        obj.delete()
                    user.profile.gamedirections.add(gamedirection)
                if request.POST.get('game3') or request.POST.get('direction3') or request.POST.get('region3'):
                    gamedirection = GameDirection()
                    gamedirection.number = 4
                    if request.POST.get('game3'):
                        gamedirection.game = Game.objects.get(id = request.POST.get('game3'))
                    if request.POST.get('direction3'):
                        gamedirection.direction = Direction.objects.get(id = request.POST.get('direction3'))
                    if request.POST.get('region3'):
                        gamedirection.region = Region.objects.get(id = request.POST.get('region3'))
                    gamedirection.save()
                    for obj in user.profile.gamedirections.filter(number=4):
                        user.profile.gamedirections.remove(obj)
                        obj.delete()
                    user.profile.gamedirections.add(gamedirection)
                if request.POST.get('contacts'):
                    user.coach_profile.contacts = request.POST.get('contacts')
                if request.POST.get('description'):
                    user.coach_profile.description = request.POST.get('description')
                if request.POST.get('strengths'):
                    user.coach_profile.strengths = request.POST.get('strengths')
                if request.POST.get('which_photo'):
                    user.coach_profile.which_photo = request.POST.get('which_photo')
                if request.POST.get('show_button'):
                    user.coach_profile.show_button = request.POST.get('show_button')
                if request.POST.get('game_accounts'):
                    for obj in user.coach_profile.game_accounts.all():
                        user.coach_profile.game_accounts.remove(obj)
                        obj.delete()
                    game_account = GameAccount()
                    game_account.url = request.POST.get('game_accounts')
                    user.coach_profile.game_accounts.add(game_account)
                if request.POST.get('nickname_flag_checked') or request.POST.get('nickname_flag_not_checked'):
                    user.coach_profile.nickname_flag = 1
                else:
                    user.coach_profile.nickname_flag = 0
                if request.POST.get('search_flag_checked') or request.POST.get('search_flag_not_checked'):
                    user.coach_profile.search_flag = 1
                else:
                    user.coach_profile.search_flag = 0
                if request.POST.get('inactive_flag_checked') or request.POST.get('inactive_flag_not_checked'):
                    user.coach_profile.inactive_flag = 1
                else:
                    user.coach_profile.inactive_flag = 0
                user.save()
            return redirect('../account/profile.html/user_id{0}'.format(user.id))

        else:
            return redirect('index.html')