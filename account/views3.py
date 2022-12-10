'''Страницы, доступные из Профиля для зарегистрированных пользователей'''

from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User
from account.forms import BookmarksSortingForm, FriendsCommentingForm, \
    FriendsSortingForm, MessagesSortingForm, MessageWritingForm, SettingsForm, \
    UploadPhotoForm
from account.models import GameDirection, Game, Direction, Friendship, Message, \
    Profile, Region, LevelUp
from login.forms import MySignupForm, MyLoginForm
from django.core.paginator import Paginator


# принять полученную заявку в друзья
def friendship_accept(friendship):
    if friendship.status != 3:  # 3 - получена заявка в друзья
        return
    user = Profile.objects.get(id=friendship.user_id)
    friend = Profile.objects.get(id=friendship.friend_id)
    # if friend not in user.friends.all():
    #     return
    if user not in friend.friends.all():
        friendship.status = 2  # у меня невзаимный друг
        friendship.save()
    else:
        friendship2 = Friendship.objects.get(user=friend, friend=user)
        if friendship2.status == 3:  # 3 - рассматривает мою заявку
            friendship.status = 0  # 0 - моя заявка на рассмотрении
            friendship.save()
        else:  # все статусы некорректны, кроме 0 - отправил мне заявку
            friendship.status = 1  # взаимные друзья
            friendship.save()
            friendship2.status = 1
            friendship2.save()


# отклонить полученную заявку в друзья
def friendship_reject(friendship):
    if friendship.status != 3:  # 3 - получена заявка в друзья
        return
    user = Profile.objects.get(id=friendship.user_id)
    friend = Profile.objects.get(id=friendship.friend_id)
    user.friends.remove(friend)
    user.save()
    if user in friend.friends.all():
        friendship2 = Friendship.objects.get(user=friend, friend=user)
        if friendship2.status != 3:  # 3 - рассматривает мою заявку, все статусы некорректны, кроме 0 - отправил мне заявку
            friendship2.status = 2  # я его невзаимный друг
            friendship2.save()


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
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            if user.profile.photo:
                context['photo'] = user.profile.photo.url
            else:
                context['photo'] = ''
            context['settings_form'] = SettingsForm()
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
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


class AddToBlacklistView(View):
    '''Пункт меню В чёрный список на вкладках Сообщения, Закладки, Друзья,
        в чужом профиле, написании сообщения или комментария

    Сюда попадают только зарегистрированные пользователи, у которых
    этого пользователя нет в чёрном списке, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            try:
                user = User.objects.select_related("profile").get(username=request.user)
                watched_user = User.objects.select_related("profile").get(id=watched_user_id)
            except User.DoesNotExist:
                raise Http404
            if watched_user not in user.profile.blacklist.all():
                user.profile.blacklist.add(watched_user)
                user.save()
            if watched_user.profile in user.profile.friends.all():
                user.profile.friends.remove(watched_user.profile)
                if user.profile in watched_user.profile.friends.all():
                    friendship = Friendship.objects.get(user=watched_user.profile, friend=user.profile)
                    if friendship.status != 3:
                        friendship.status = 2
                        friendship.save()
            if watched_user in user.profile.bookmarks.all():
                user.profile.bookmarks.remove(watched_user)
            return redirect(next_url)
        else:
            return redirect(next_url)


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
                if watched_user.profile.friends_auto == 1:  # он всегда принимает заявки
                    watched_user.profile.friends.add(user.profile, through_defaults={'status':1})  # взаимные друзья
                    watched_user.save()
                elif watched_user.profile.friends_auto == 2:  # он всегда отклоняет заявки
                    fs = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                    fs.status = 2  # невзаимный друг
                    fs.save()
                else:
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


class BlacklistView(View):
    '''Страница Чёрный список Профиля'''

    def get(self, request, page=1, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            blacklist = user.profile.blacklist.all()
            paginator = Paginator(blacklist, 20)  # How many persons per page
            context['blacklist'] = paginator.get_page(page)
            return render(request, 'account/blacklist.html', context=context)
        else:
            return redirect('index.html')


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
            user = User.objects.select_related('profile').get(username=request.user)
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
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
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
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            return render(request, 'account/diary.html', context=context)
        else:
            return redirect('index.html')


class FriendsAcceptAllView(View):
    '''Кнопка Принять все заявки на странице Друзья Профиля при сортировке
    по полученным заявкам и наличии полученных заявок.

    Проверка выбранной сортировки - в функции
    Заново получаю все данные из базы'''

    def post(self, request, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            friendships = Friendship.objects.filter(user=user, status=3)
            if not friendships:
                return redirect(next_url)
            for friendship in friendships:
                friendship_accept(friendship)
            return redirect(next_url)
        else:
            return redirect(next_url)


class FriendsAutoAcceptAllView(View):
    '''Кнопка Всегда принимать все заявки на странице Друзья Профиля при сортировке
    по полученным заявкам и отсутствии полученных заявок.

    Проверка выбранной сортировки не требуется
    '''

    def post(self, request, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            user.friends_auto = 1
            user.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class FriendsAutoRejectAllView(View):
    '''Кнопка Всегда отклонять все заявки на странице Друзья Профиля при сортировке
    по полученным заявкам и отсутствии полученных заявок.

    Проверка выбранной сортировки не требуется
    '''

    def post(self, request, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            user.friends_auto = 2
            user.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class FriendsClearCommentView(View):
    '''Кнопка Очистить комментарий на странице написания комментария по кнопке
    Написать комментарий в Друзьях Профиля'''

    def post(self, request, friend_id, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            friend = User.objects.get(id=friend_id)
            friendship = Friendship.objects.get(user=user.profile, friend=friend.profile)
            if not friendship:
                return redirect(next_url)
            friendship.comment = ''
            friendship.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class FriendsCommentingView(View):
    '''Отправка комментария к другу на странице Друзья Профиля'''

    def get(self, request, friend_id, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.get(username=request.user)
            context['user'] = user
            friend = User.objects.select_related('profile').get(id=friend_id)
            friendship = Friendship.objects.get(user=user.profile, friend=friend.profile)
            if not friendship:
                return redirect('friends.html')
            context['friendship'] = friendship
            form = FriendsCommentingForm(instance=friendship)
            context['friends_commenting_form'] = form
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            return render(request, 'account/friends_comment.html', context=context)
        else:
            return redirect('friends.html')

    def post(self, request, friend_id, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            friend = User.objects.get(id=friend_id)
            friendship = Friendship.objects.get(user=user.profile, friend=friend.profile)
            if not friendship:
                return redirect(next_url)
            form = FriendsCommentingForm(request.POST)
            if form.is_valid():
                if request.POST.get('comment'):
                    friendship.comment = request.POST.get('comment')
                    friendship.save()
            return redirect(next_url)

        else:
            return redirect(next_url)


class FriendsNoAutoView(View):
    '''Кнопка Отменить автоматическую обработку заявок на странице Друзья Профиля при сортировке
    по полученным заявкам и отсутствии полученных заявок.

    Проверка выбранной сортировки не требуется
    '''

    def post(self, request, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            user.friends_auto = 0
            user.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class FriendsRejectAllView(View):
    '''Кнопка Отклонить все заявки на странице Друзья Профиля при сортировке
    по полученным заявкам и наличии полученных заявок.

    Проверка выбранной сортировки - в функции
    Заново получаю все данные из базы'''

    def post(self, request, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            friendships = Friendship.objects.filter(user=user, status=3)
            if not friendships:
                return redirect(next_url)
            for friendship in friendships:
                friendship_reject(friendship)
            return redirect(next_url)
        else:
            return redirect(next_url)


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
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            friends_auto = user.profile.friends_auto
            context['friends_auto'] = friends_auto
            friends_sorting = user.profile.friends_sorting
            context['friends_sorting'] = friends_sorting
            if friends_sorting not in [1, 2, 3, 4, 5]:
                friends_sorting = 1
            if friends_sorting == 1:  # по новым
                friendships = Friendship.objects.filter(user=user.profile)[::-1]
            elif friends_sorting == 2:  # по имени
                friendships = sorted(Friendship.objects.prefetch_related('friend').filter(user=user.profile),
                    key=lambda friendship: (friendship.friend.user.first_name or "") + \
                        (friendship.friend.nickname or friendship.friend.user.username) + (friendship.friend.user.last_name or ""))
                # n (user) + 3
                # friendships = sorted(Friendship.objects.filter(user=user.profile),
                #     key=lambda friendship: (friendship.friend.user.first_name or "") + \
                #         (friendship.friend.nickname or friendship.friend.user.username) + (friendship.friend.user.last_name or ""))
                # 1 (friendship) + 2n (user, profile)
            elif friends_sorting == 3:  # на рассмотрении
                friendships = Friendship.objects.filter(user=user.profile, status=0)
            elif friends_sorting == 4:  # взаимные
                friendships = Friendship.objects.filter(user=user.profile, status=1)
            elif friends_sorting == 5:  # полученные заявки
                friendships = Friendship.objects.filter(user=user.profile, status=3)
            paginator = Paginator(friendships, 20)  # How many friends per page
            context['friendships'] = paginator.get_page(page)

            context['friends_sorting_form'] = FriendsSortingForm(request=request)
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            return render(request, 'account/friends.html', context=context)
        else:
            return redirect('index.html')


class MessagesSortingView(View):
    '''Выбор типа сортировки сообщений на странице Сообщения Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            # https://qna.habr.com/q/71870
            form = MessagesSortingForm(request.POST, request=request)
            if form.is_valid():
                if request.POST.get('ms_sorting'):
                    user.profile.messages_sorting = request.POST.get('ms_sorting')
                    user.save()
            return redirect('message1.html')

        else:
            return redirect('index.html')


class MessageView(View):
    '''Страница Сообщения Профиля'''

    def get(self, request, page=None, *args, **kwargs):
        if not page:
            page = 1
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            context['messages_sorting_form'] = MessagesSortingForm(request=request)
            messages_sorting = user.profile.messages_sorting
            context['messages_sorting'] = messages_sorting
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            if messages_sorting not in [1, 2, 3, 4, 5, 6]:
                messages_sorting = 1
            if messages_sorting == 1:  # новые
                messages = new_messages[::-1]
            elif messages_sorting == 2:  # все полученные
                messages = Message.objects.filter(recipient=user.profile)[::-1]
            elif messages_sorting == 3:  # от друзей
                messages1 = Message.objects.filter(recipient=user.profile)[::-1]
                messages = []
                for message in messages1:
                    if message.author in user.profile.friends.all():
                        messages.append(message)
            elif messages_sorting == 4:  # от Наставников
                messages1 = Message.objects.filter(recipient=user.profile)[::-1]
                messages = []
                for message in messages1:
                    if message.author.coach:
                        messages.append(message)
            elif messages_sorting == 5:  # от команды сайта
                messages1 = Message.objects.filter(recipient=user.profile)[::-1]
                messages = []
                for message in messages1:
                    if message.author.user.is_superuser:
                        messages.append(message)
            elif messages_sorting == 6:  # все отправленные
                messages = Message.objects.filter(author=user.profile)[::-1]
            paginator = Paginator(messages, 20)  # How many messages per page
            current_messages = paginator.get_page(page)
            if messages_sorting != 6:
                for message in current_messages:
                    if message.status == 0 and message.recipient == user.profile:
                        message.status = 1  # read
                        message.save()
            data = []
            for message in current_messages:
                try:
                    if messages_sorting == 6:
                        friendship = Friendship.objects.get(user=user.profile, friend=message.recipient)
                    else:
                        friendship = Friendship.objects.get(user=user.profile, friend=message.author)
                except Friendship.DoesNotExist:
                    friendship = None
                data.append((message, friendship))
            context['messages'] = data
            return render(request, 'account/message.html', context=context)
        else:
            return redirect('index.html')


class MessageWritingView(View):
    '''Отправка сообщения на странице по кнопке Написать сообщение в чужом
    профиле, на вкладке Закладки, Друзья Профиля'''

    def get(self, request, recipient_id, page=None, *args, **kwargs):
        if not page:
            page = 1
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            recipient = User.objects.select_related('profile').get(id=recipient_id).profile
            context['recipient'] = recipient
            friendship = Friendship.objects.get(user=user.profile, friend=recipient)
            if not friendship:
                context['friendship'] = None
            else:
                context['friendship'] = friendship
            form = MessageWritingForm()
            context['message_writing_form'] = form
            messages = list(Message.objects.filter(author=user.profile, recipient=recipient))
            messages.extend(list(Message.objects.filter(author=recipient, recipient=user.profile)))
            messages.sort(key=lambda message: message.datetime)
            messages = messages[::-1]
            paginator = Paginator(messages, 20)  # How many messages per page
            current_messages = paginator.get_page(page)
            for message in current_messages:
                if message.status == 0 and message.author == recipient:
                    message.status = 1  # read
                    message.save()
            context['messages'] = current_messages
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            return render(request, 'account/write_message.html', context=context)
        else:
            return redirect('../profile.html/user_id{0}'.format(recipient_id))

    def post(self, request, recipient_id, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            recipient = User.objects.select_related('profile').get(id=recipient_id).profile
            form = MessageWritingForm(request.POST)
            if form.is_valid():
                if request.POST.get('text'):
                    Message.objects.create(author=user, recipient=recipient,
                                            text=request.POST.get('text'))
                    # no need to save()
                    #https://stackoverflow.com/questions/26672077/django-model-vs-model-objects-create
            return redirect(next_url)

        else:
            return redirect(next_url)


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
            user = User.objects.select_related('profile').get(username=request.user)
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
                new_messages = Message.objects.filter(recipient=user.profile, status=0)
                context['new_messages'] = len(new_messages)
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
            user = User.objects.select_related('profile').get(username=request.user).profile
            friend = User.objects.select_related('profile').get(id=watched_user_id).profile
            friendship = Friendship.objects.get(user=user, friend=friend)
            friendship_accept(friendship)
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
            user = User.objects.select_related('profile').get(username=request.user).profile
            friend = User.objects.select_related('profile').get(id=watched_user_id).profile
            friendship = Friendship.objects.get(user=user, friend=friend)
            friendship_reject(friendship)
            return redirect(next_url)
        else:
            return redirect(next_url)


class RemoveFromBlacklistView(View):
    '''Кнопка Удалить из чёрного списка на вкладке Чёрный список

    Сюда попадают только зарегистрированные пользователи, у которых
    этот пользователь есть в Чёрном списке, но проверку сделаем на всякий случай

    '''

    def get(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            try:
                user = User.objects.select_related('profile').get(username=request.user)
                watched_user = User.objects.get(id=watched_user_id)
            except User.DoesNotExist:
                raise Http404
            if watched_user in user.profile.blacklist.all():
                user.profile.blacklist.remove(watched_user)
                user.save()
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
            user = User.objects.select_related('profile').get(username=request.user)
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