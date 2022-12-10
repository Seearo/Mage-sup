'''Страницы, доступные только админам'''

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User
from account.models import Profile
from django.core.paginator import Paginator
from superuser.forms import ChangeLessonsCapForm, ChangeRegistrationsPeriodForm, \
ChangeStarsLevelForm
from superuser.models import Settings


class AdminMenuView(View):

    '''Страница меню при нажатии кнопки Админ в Профиле'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                context = dict()
                context['trademark'] = settings.TRADEMARK
                context['current_year'] = datetime.now().strftime('%Y')
                user = User.objects.get(username=request.user)
                context['user'] = user
                return render(request,
                'superuser/menu.html', context=context)
            else:
                return redirect('account/profile.html/user_id{0}'.format(request.user.id))
        else:
            return redirect('../index.html')


class ChangeLessonsCapView(View):

    '''Передача данных об изменении максимально допустимого числа предстоящих записей на уроки на странице Настройки в меню Админ'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            form = ChangeLessonsCapForm(request.POST, instance=Settings.objects.get(id=1))
            if form.is_valid():
                if request.POST.get('registrations_cap'):
                    settings = Settings.objects.get(id=1)
                    settings.registrations_cap = int(request.POST.get('registrations_cap'))
                    settings.save()
            return redirect('settings.html')
        else:
            return redirect('../../index.html')


class ChangeRegistrationsPeriodView(View):

    '''Передача данных об изменении максимального числа дней вперёд, на которые можно записаться, для студента на странице Настройки в меню Админ'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            form = ChangeRegistrationsPeriodForm(request.POST, instance=Settings.objects.get(id=1))
            if form.is_valid():
                if request.POST.get('registrations_period'):
                    settings = Settings.objects.get(id=1)
                    settings.registrations_period = int(request.POST.get('registrations_period'))
                    settings.save()
            return redirect('settings.html')
        else:
            return redirect('../../index.html')


class ChangeStarsLevelView(View):

    '''Передача данных об изменении уровня звёзд Наставника на странице Наставники в меню Админ'''

    def post(self, request, coach_id, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            coach = User.objects.get(id=coach_id)
            form = ChangeStarsLevelForm(request.POST)
            if form.is_valid():
                if request.POST.get('stars'):
                    coach.coach_profile.star_level_id = int(request.POST.get('stars')) - 1
                    coach.save()
            return redirect('../list_of_coaches.html/1')
        else:
            return redirect('../../index.html')


class ListOfCoachesView(View):

    '''Страница со списком Наставников'''

    def get(self, request, page, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            profiles = Profile.objects.filter(coach=1)
            coaches = [profile.user for profile in profiles]
            paginator = Paginator(coaches, 50)  # How many coaches per page
            context['coaches'] = paginator.get_page(page)
            context['stars_form'] = ChangeStarsLevelForm()
            return render(request, 'superuser/list_of_coaches.html', context=context)
        else:
            return redirect('../../index.html')


class SettingsView(View):

    '''Страница Настройки'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                context = dict()
                context['trademark'] = settings.TRADEMARK
                context['current_year'] = datetime.now().strftime('%Y')
                user = User.objects.get(username=request.user)
                context['user'] = user
                context['change_lessons_cap_form'] = ChangeLessonsCapForm(instance=Settings.objects.get(id=1))
                context['change_registrations_period_form'] = ChangeRegistrationsPeriodForm(instance=Settings.objects.get(id=1))
                return render(request,
                'superuser/settings.html', context=context)
            else:
                return redirect('account/profile.html/user_id{0}'.format(request.user.id))
        else:
            return redirect('../index.html')


class WantsToCoachView(View):

    '''Страница назначения Наставников'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            profiles = Profile.objects.filter(wants_to_coach=1)
            context['wannabes'] = [profile.user for profile in profiles]
            return render(request, 'superuser/wants_to_coach.html', context=context)
        else:
            return redirect('../../index.html')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            for name in request.POST:
                if name == 'csrfmiddlewaretoken':
                    continue
                user = User.objects.get(username=name)
                if request.POST[name] == 'y':
                    user.profile.coach = 1
                    # создание профиля CoachProfile из app coach_office
                    # при user.profile.coach and user.profile.wants_to_coach
                    user.save()
                    user.profile.wants_to_coach = 0
                    user.save()
                elif request.POST[name] == 'n':
                    user.profile.wants_to_coach = 0
                    user.save()
            return redirect('wants_to_coach.html')
        else:
            return redirect('../../index.html')