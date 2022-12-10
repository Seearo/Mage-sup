# -*- coding: utf-8 -*-
'''Страницы, доступные из Профиля для зарегистрированных пользователей'''

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User
from account.forms import UploadPhotoForm, SettingsForm
from account.models import GameDirection, Game, Direction, Region, LevelUp


# used also in coach_office.views
def level_up(current_level):
    '''How much experience needed for the next level'''

    # взяв лвл, экспа считается с 0
    cur_exp = LevelUp.objects.filter(to_level=current_level + 1)[0]
    if cur_exp:
        return cur_exp.experience
    else:
        # далее по 10 процентов шаг или около того
        max_lvl = LevelUp.objects.latest()  # by 'to_level'
        return round(max_lvl.experience * 1.1 ** (current_level + 1 - max_lvl.to_level))


class AccountView(View):
    '''Страница Настройки Профиля'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            if user.profile.photo:
                context['photo'] = user.profile.photo.url
            else:
                context['photo'] = ''
            context['settings_form'] = SettingsForm()
            return render(request, 'account/account.html', context=context)
        else:
            return redirect('index.html')


class AchievementsView(View):
    '''Страница Достижения'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request, 'account/achievements.html', context=context)
        else:
            return redirect('index.html')


class BookmarksView(View):
    '''Страница Закладки Профиля'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request, 'account/bookmarks.html', context=context)
        else:
            return redirect('index.html')


class ChatidView(View):
    '''Страница чата'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request, 'account/chatid1598737bi.html', context=context)
        else:
            return redirect('index.html')


class DiaryView(View):
    '''Страница Дневник Профиля'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request, 'account/diary.html', context=context)
        else:
            return redirect('index.html')


class FriendsView(View):
    '''Страница Друзья Профиля'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request, 'account/friends.html', context=context)
        else:
            return redirect('index.html')


class MessageView(View):
    '''Страница Сообщения Профиля'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            return render(request, 'account/message.html', context=context)
        else:
            return redirect('index.html')


class ProfileView(View):
    '''Страница Профиль'''

    def get(self, request, user_id, *args, **kwargs):
        context = dict()
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        watched_user = User.objects.get(id=user_id)  # кого смотрим
        context['watched_user'] = watched_user
        context['level_up'] = level_up(watched_user.profile.level)
        context['value_now'] = round(watched_user.profile.level / context['level_up'] * 100)
        if watched_user.profile.photo:
            context['photo'] = watched_user.profile.photo.url
        else:
            context['photo'] = ''
        context['gamedirection1'] = watched_user.profile.gamedirections.filter(number=1)[0] if watched_user.profile.gamedirections.filter(number=1) else None
        if watched_user.profile.coach:
            context['num_stars'] = '1' * watched_user.coach_profile.star_level.number
            context['no_stars'] = '1' * (5 - watched_user.coach_profile.star_level.number)
            context['gamedirection2'] = watched_user.profile.gamedirections.filter(number=2)[0] if watched_user.profile.gamedirections.filter(number=2) else None
            context['gamedirection3'] = watched_user.profile.gamedirections.filter(number=3)[0] if watched_user.profile.gamedirections.filter(number=3) else None
            context['gamedirection4'] = watched_user.profile.gamedirections.filter(number=4)[0] if watched_user.profile.gamedirections.filter(number=4) else None            
        if request.user.is_authenticated: # кто смотрит
            # https://stackoverflow.com/questions/17312831/what-does-request-user-refer-to-in-django
            user = User.objects.get(username=request.user)
            context['user'] = user
            if request.user.id == user_id:  # смотрит сам себя
                context['upload_photo_form'] = UploadPhotoForm()
                if user.profile.coach:
                    return render(request, 'account/coach_profile.html', context=context)
                else:
                    return render(request, 'account/profile.html', context=context)
            else:
                if watched_user.profile.coach:
                    return render(request, 'account/other/coach_profile.html', context=context)
                return render(request, 'account/other/profile.html', context=context)
        else:  # смотрит гость
            context['user'] = None
            if watched_user.profile.coach:
                return render(request, 'account/other/coach_profile.html', context=context)
            return render(request, 'account/other/profile.html', context=context)

    
class SettingsView(View):
    '''Отправка данных на странице Настройки Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            form = SettingsForm(request.POST, request.FILES, instance=request.user.profile)
            if form.is_valid():
                if request.FILES.get('photo'):
                    user.profile.photo = request.FILES.get('photo')
                if request.POST.get('first_name'):
                    user.first_name = request.POST.get('first_name')
                if request.POST.get('last_name'):
                    user.last_name = request.POST.get('last_name')
                if request.POST.get('nickname'):
                    user.profile.nickname = request.POST.get('nickname')
                if request.POST.get('game') or request.POST.get('direction') or request.POST.get('region'):
                    gamedirection = GameDirection()
                    gamedirection.number = 1  # default
                    if request.POST.get('game'):
                        gamedirection.game = Game.objects.get(id = request.POST.get('game'))
                    if request.POST.get('direction'):
                        gamedirection.direction = Direction.objects.get(id = request.POST.get('direction'))
                    if request.POST.get('region'):
                        gamedirection.region = Region.objects.get(id = request.POST.get('region'))
                    # https://docs.djangoproject.com/en/3.1/ref/models/relations/
                    gamedirection.save()
                    for obj in user.profile.gamedirections.filter(number=1):
                        user.profile.gamedirections.remove(obj)
                        obj.delete()
                    user.profile.gamedirections.add(gamedirection)
                if request.POST.get('contacts'):
                    user.profile.contacts = request.POST.get('contacts')
                user.save()
            return redirect('../account/profile.html/user_id{0}'.format(user.id))

        else:
            return redirect('index.html')


class UploadPhotoView(View):
    '''Загрузка фото на странице Настройки Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            # https://qna.habr.com/q/71870
            form = UploadPhotoForm(request.FILES, instance=request.user.profile)
            if form.is_valid():
                if request.FILES.get('photo'):
                    user.profile.photo = request.FILES.get('photo')
                    user.save()
            return redirect('profile.html/user_id{0}'.format(user.id))

        else:
            return redirect('index.html')

class WantsToCoachView(View):
    '''Кнопка Стать Наставником на странице Настройки Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            if user.profile.coach == 0 and user.profile.wants_to_coach == 0:
                user.profile.wants_to_coach = 1
                user.save()
            return redirect('profile.html/user_id{0}'.format(user.id))
        else:
            return redirect('index.html')