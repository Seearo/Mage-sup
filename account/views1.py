'''Страницы, доступные из Профиля для зарегистрированных пользователей'''

from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User
from account.forms import BookmarksSortingForm, FriendsSortingForm, SettingsForm, UploadPhotoForm
from account.models import GameDirection, Game, Direction, Friendship, Region, LevelUp
from login.forms import MySignupForm, MyLoginForm
from django.core.paginator import Paginator


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


class AddToBookmarksView(View):
    '''Кнопка В Закладки при просмотре чужого профиля Наставника

    Сюда попадают только зарегистрированные пользователи, у которых
    этого Наставника нет в Закладках, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            watched_user = User.objects.get(id=watched_user_id)
            if watched_user.profile.coach and watched_user not in user.profile.bookmarks.all():
                user.profile.bookmarks.add(watched_user)
                user.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class AddToFriendsView(View):
    '''Кнопка В друзья при просмотре чужого профиля

    Сюда попадают только зарегистрированные пользователи, у которых
    этого пользователя нет в Друзьях, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            watched_user = User.objects.get(id=watched_user_id)
            if watched_user.profile not in user.profile.friends.all():
                user.profile.friends.add(watched_user.profile)  # status = 0 - отправил заявку
                user.save()
            if user.profile not in watched_user.profile.friends.all():
                watched_user.profile.friends.add(user.profile, through_defaults={'status':3})  # получил заявку
                watched_user.save()
            else:
                fs = Friendship.objects.get(user=watched_user.profile, friend=user.profile)
                if fs.status != 3:  # 3 - рассматривает мою заявку, прочие статусы некорректны, кроме 2 - невзаимный друг
                    fs.status = 1  # взаимные друзья
                    fs.save()
                    fs2 = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                    fs2.status = 1
                    fs2.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class BookmarksSortingView(View):
    '''Выбор типа сортировки закладок на странице Закладки Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            # https://qna.habr.com/q/71870
            form = BookmarksSortingForm(request.POST, request=request)
            if form.is_valid():
                if request.POST.get('bm_sorting'):
                    user.profile.bookmarks_sorting = request.POST.get('bm_sorting')
                    user.save()
            return redirect('bookmarks.html')

        else:
            return redirect('index.html')


class BookmarksView(View):
    '''Страница Закладки Профиля'''

    def get(self, request, page=None, *args, **kwargs):
        if not page:
            page = 1
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            bookmarks_sorting = user.profile.bookmarks_sorting
            if bookmarks_sorting not in [1, 2, 3, 4]:
                bookmarks_sorting = 1
            if bookmarks_sorting == 1:  # по новым
                bookmarks = user.profile.bookmarks.all()[::-1]
            elif bookmarks_sorting == 2:  # по имени
                bookmarks = sorted(user.profile.bookmarks.all(),
                                key=lambda bookmark: (bookmark.first_name or "") + (bookmark.profile.nickname or bookmark.username) + (bookmark.last_name or ""))
            elif bookmarks_sorting == 3:  # звёзды -, т.е. по убыванию
                bookmarks = sorted(user.profile.bookmarks.all(),
                                key = lambda bookmark: bookmark.coach_profile.star_level.number, reverse=True)
            elif bookmarks_sorting == 4:  # звёзды +, т.е. по возрастанию
                bookmarks = sorted(user.profile.bookmarks.all(),
                                key = lambda bookmark: bookmark.coach_profile.star_level.number)
            paginator = Paginator(bookmarks, 20)  # How many bookmarks per page
            context['bookmarks'] = paginator.get_page(page)
            context['bookmarks_sorting_form'] = BookmarksSortingForm(request=request)
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


class FriendsSortingView(View):
    '''Выбор типа сортировки друзей на странице Друзья Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            # https://qna.habr.com/q/71870
            form = FriendsSortingForm(request.POST, request=request)
            if form.is_valid():
                if request.POST.get('fr_sorting'):
                    user.profile.friends_sorting = request.POST.get('fr_sorting')
                    user.save()
            return redirect('friends.html')

        else:
            return redirect('index.html')


class FriendsView(View):
    '''Страница Друзья Профиля'''

    def get(self, request, page=None, *args, **kwargs):
        if not page:
            page = 1
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            friends_sorting = user.profile.friends_sorting
            context['friends_sorting'] = friends_sorting
            # friends3 = list(map(lambda friendship: friendship.friend.user, Friendship.objects.filter(user=user.profile, status=0)))
            # context['friends3'] = friends3
            # friends4 = list(map(lambda friendship: friendship.friend.user, Friendship.objects.filter(user=user.profile, status=1)))
            # context['friends4'] = friends4
            # friends5 = list(map(lambda friendship: friendship.friend.user, Friendship.objects.filter(user=user.profile, status=3)))
            # context['friends5'] = friends5
            # if friends_sorting not in [1, 2, 3, 4, 5]:
            #     friends_sorting = 1
            # if friends_sorting == 1:  # по новым - неправильно сортирует почему-то
            #     friends = user.profile.friends.all()[::-1]
            #     friends = list(map(lambda friend: friend.user, friends))
            # elif friends_sorting == 2:  # по имени
            #     friends = sorted(user.profile.friends.all(),
            #                     key=lambda friend: (friend.user.first_name or "") + (friend.nickname or friend.user.username) + (friend.user.last_name or ""))
            #     friends = list(map(lambda friend: friend.user, friends))
            # elif friends_sorting == 3:  # на рассмотрении
            #     friends = friends3
            # elif friends_sorting == 4:  # взаимные
            #     friends = friends4
            # elif friends_sorting == 5:  # полученные заявки
            #     friends = friends5
            # paginator = Paginator(friends, 20)  # How many friends per page
            # context['friends'] = paginator.get_page(page)

            if friends_sorting not in [1, 2, 3, 4, 5]:
                friends_sorting = 1
            if friends_sorting in [1, 2]:
                friendships = []
            friendships3 = []
            friendships4 = []
            friendships5 = []
            for friendship in Friendship.objects.filter(user=user.profile):
                status = friendship.status
                if status == 0:
                    friendships3.append(friendship)
                elif status == 1:
                    friendships4.append(friendship)
                elif status == 3:
                    friendships5.append(friendship)
                if friends_sorting in [1, 2]:
                    friendships.append(friendship)
            context['friendships3'] = set(friendships3)
            context['friendships4'] = set(friendships4)
            context['friendships5'] = set(friendships5)

            if friends_sorting == 1:  # по новым
                friendships = friendships[::-1]
            elif friends_sorting == 2:  # по имени
                friendships = sorted(friendships,
                    key=lambda friendship: (friendship.friend.user.first_name or "") + (friendship.friend.nickname or friendship.friend.user.username) + (friendship.friend.user.last_name or ""))
            elif friends_sorting == 3:  # на рассмотрении
                friendships = friendships3
            elif friends_sorting == 4:  # взаимные
                friendships = friendships4
            elif friends_sorting == 5:  # полученные заявки
                friendships = friendships5
            paginator = Paginator(friendships, 20)  # How many friends per page
            context['friendships'] = paginator.get_page(page)

            context['friends_sorting_form'] = FriendsSortingForm(request=request)
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
    '''Страница Профиль, в том числе при просмотре с другого аккаунта'''

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
            if watched_user in user.profile.bookmarks.all():  # не добавляю проверку watched_user.profile.coach на случай, если попадёт неНаставник в Закладки
            # if user.profile.bookmarks.get(watched_user):  # cannot unpack non-iterable User object
                context['in_bookmarks'] = True
            else:
                context['in_bookmarks'] = False
            if watched_user.profile in user.profile.friends.all():
                fs = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                if fs.status == 3:
                    context['in_friends'] = 1  # я рассматриваю заявку, могу принять или отклонить
                else:
                    context['in_friends'] = 2  # это мой друг, могу удалить из друзей
            else:
                context['in_friends'] = 0
            if request.user.id == user_id:  # смотрит сам себя
                context['upload_photo_form'] = UploadPhotoForm()
                if user.profile.coach:
                    return render(request, 'account/coach_profile.html', context=context)
                else:
                    return render(request, 'account/profile.html', context=context)
            else:
                return render(request, 'account/other/profile.html', context=context)
        else:  # смотрит гость
            context['user'] = None
            context['signup_form'] = MySignupForm()
            context['login_form'] = MyLoginForm()
            return render(request, 'account/other/profile.html', context=context)


class ReceiveToFriendsView(View):
    '''Кнопка Принять заявку при просмотре чужого профиля

    Сюда попадают только зарегистрированные пользователи, которым
    этот пользователь подал заявку в Друзья, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            watched_user = User.objects.get(id=watched_user_id)
            if watched_user.profile not in user.profile.friends.all():
                user.profile.friends.add(watched_user.profile)  # status = 0 - отправил заявку
                user.save()
            if user.profile not in watched_user.profile.friends.all():
                fs = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                fs.status = 2  # у меня невзаимный друг
                fs.save()
            else:
                fs = Friendship.objects.get(user=watched_user.profile, friend=user.profile)
                if fs.status != 3:  # 3 - рассматривает мою заявку, все статусы некорректны, кроме 0 - отправил мне заявку
                    fs.status = 1  # взаимные друзья
                    fs.save()
                    fs2 = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                    fs2.status = 1
                    fs2.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class RejectFromFriendsView(View):
    '''Кнопка Отклонить заявку при просмотре чужого профиля

    Сюда попадают только зарегистрированные пользователи, которым
    этот пользователь подал заявку в Друзья, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            watched_user = User.objects.get(id=watched_user_id)
            if watched_user.profile in user.profile.friends.all():
                user.profile.friends.remove(watched_user.profile)
                user.save()
            if user.profile in watched_user.profile.friends.all():
                fs = Friendship.objects.get(user=watched_user.profile, friend=user.profile)
                if fs.status != 3:  # некорректные статусы, кроме 0 - отправлена заявка, при 3 - моя заявка на рассмотрении - ничего не делаем
                    fs.status = 2  # я его невзаимный друг
                    fs.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class RemoveFromBookmarksView(View):
    '''Кнопка Удалить из закладок при просмотре чужого профиля Наставника

    Сюда попадают только зарегистрированные пользователи, у которых
    этот Наставник есть в Закладках, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            watched_user = User.objects.get(id=watched_user_id)
            if watched_user in user.profile.bookmarks.all():  # не делаю проверку watched_user_profile.coach, вдруг в закладки попадёт неНаставник
                user.profile.bookmarks.remove(watched_user)
                user.save()
            #return redirect('../profile.html/user_id{0}'.format(watched_user_id))
            return redirect(next_url)
        else:
            return redirect(next_url)


class RemoveFromFriendsView(View):
    '''Кнопка Удалить из друзей при просмотре чужого профиля

    Сюда попадают только зарегистрированные пользователи, у которых
    этот пользователь есть в Друзьях, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            watched_user = User.objects.get(id=watched_user_id)
            #Friendship.objects.filter(user=user.profile, friend=watched_user.profile).status = 5 # молча не работает
            #user.profile.user_friends.get(user=user.profile, friend=watched_user.profile).status=5 # ошибка, показывает поля Profile
            #Friendship.save() # ошибка
            # user.profile.friends.set([watched_user.profile], through_defaults={'status': 5})  # молча не работает
            # user.save()
            # fs = Friendship.objects.get(user=user.profile, friend=watched_user.profile)  # ура, работает!
            # fs.status = 5
            # fs.save()
            if watched_user.profile in user.profile.friends.all():
                user.profile.friends.remove(watched_user.profile)
                user.save()
            if user.profile in watched_user.profile.friends.all():
                fs = Friendship.objects.get(user=watched_user.profile, friend=user.profile)
                if fs.status != 3:  # некорректные статусы, кроме 1 - мы взаимные друзья, при 3 - моя заявка на рассмотрении - ничего не делаем
                    fs.status = 2  # я его невзаимный друг
                    fs.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


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