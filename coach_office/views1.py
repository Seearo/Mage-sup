'''Страницы, доступные только Наставникам'''

from django.shortcuts import render, redirect
from django.conf import settings
from datetime import datetime
from django.views import View
from django.contrib.auth.models import User
from coach_office.forms import SettingsForm
from account.models import GameDirection, Game, Direction, Message, Region
from account.views import level_up
from coach_office.models import GameAccount

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
                context['current_year'] = datetime.now().strftime('%Y')
                user = User.objects.select_related('profile').get(username=request.user)
                context['user'] = user
                if request.user.id == user_id:
                    context['settings_form'] = SettingsForm()
                    context['level_up'] = level_up(user.profile.level)
                    context['value_now'] = round(user.profile.level / context['level_up'] * 100)
                    new_messages = Message.objects.filter(recipient=user.profile, status=0)
                    context['new_messages'] = len(new_messages)
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
            user = User.objects.get(username=request.user)
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