'''Страницы, доступные из главного меню'''

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from datetime import datetime
from login.forms import MySignupForm, MyLoginForm
from django.contrib.auth.models import User

default_context = {'signup_form': MySignupForm(),
                   'login_form': MyLoginForm()}

class DefaultView(View):

    '''Страница по умолчанию'''

    def get(self, request, *args, **kwargs):
        return redirect("index.html")


class CoachView(View):

    '''Страница Наставники главного меню'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/coach.html', context=context)
        else:
            return render(request,
            'coach/coach.html', context=context)


class CoachStandardsView(View):

    '''Страница Правила и стандарты Наставника GTL'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/coach-standards.html', context=context)
        else:
            return render(request,
            'coach/coach-standards.html', context=context)


class DocView(View):

    '''Страница Описание работы платформы'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/doc.html', context=context)
        else:
            return render(request,
            'coach/doc.html', context=context)


class IndexView(View):

    '''Главная страница главного меню'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/index.html', context=context)
        else:
            return render(request,
            'coach/index.html', context=context)


class PartnershipView(View):

    '''Страница Партнёрская программа'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/partnership.html', context=context)
        else:
            return render(request,
            'coach/partnership.html', context=context)


class PlatformStandardsView(View):

    '''Страница Правила и стандарты сервиса GTL'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/platform-standards.html', context=context)
        else:
            return render(request,
            'coach/platform-standards.html', context=context)


class RandomView(View):

    '''Страница Случайный поиск главного меню'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/random.html', context=context)
        else:
            return render(request,
            'coach/random.html', context=context)


class TeamView(View):

    '''Страница Наша команда'''

    def get(self, request, *args, **kwargs):
        context = default_context
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request,
            'coach/account/team.html', context=context)
        else:
            return render(request,
            'coach/team.html', context=context)
