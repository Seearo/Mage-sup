'''Страницы, доступные из Профиля для зарегистрированных пользователей'''

from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from account.forms import BookmarksSortingForm, DiarySortingForm, \
    FriendsCommentingForm, \
    FriendsSortingForm, MessagesSortingForm, MessageWritingForm, \
    RegistrationForm, RegistrationGameForm, RegistrationSortingForm, SettingsForm, \
    UploadPhotoForm
from account.models import GameDirection, Game, Direction, Friendship, Message, \
    Profile, Region, Registration, LevelUp
from coach_office.models import AvailableTime
from superuser.models import Settings
from login.forms import MySignupForm, MyLoginForm
from django.core.paginator import Paginator
from django.db.models import Q


# imported in coach_office_views
# перевод доступного времени из исходного формата в конкретные даты и время на ближайшие дни
def available_times_to_datetimes(coach, student):
            available_times = AvailableTime.objects.filter(coach=coach.coach_profile)
            # актуализируем доступное время Наставника
            to_remove = []
            available_times = list(available_times)
            for available_time in available_times:
                if available_time.start_day < datetime.today().date() + timedelta(days=1):
                    available_time.start_day = datetime.today().date() + timedelta(days=1)
                    available_time.save()
                if available_time.end_day and available_time.start_day > available_time.end_day:
                    available_time.delete()
                    to_remove.append(available_time)
            for available_time in to_remove:
                available_times.remove(available_time)
            # выводим доступные даты и время на ближайшие две недели
            period = Settings.objects.get(id=1).registrations_period
            available_datetimes = set()
            for available_time in available_times:
                # определим все даты на ближайшие две недели
                days = []
                for i in range(period):
                    days.append(datetime.today().date() + timedelta(days=i + 1))
                # отсеем даты, не подходящие в период доступного времени
                to_remove = []
                for day in days:
                    if available_time.start_day > day or (available_time.end_day and day > available_time.end_day):
                        to_remove.append(day)
                for day in to_remove:
                    days.remove(day)
                if not days:
                    continue
                # отсеем даты, не подходящие по дням недели
                if available_time.day_of_week == 7:
                    days_of_week = [0, 1, 2, 3, 4]
                elif available_time.day_of_week == 8:
                    days_of_week = [5, 6]
                elif available_time.day_of_week == 9:
                    days_of_week = [0, 1, 2, 3, 4, 5, 6]
                elif available_time.day_of_week in [0, 1, 2, 3, 4, 5, 6]:
                    days_of_week = [available_time.day_of_week]
                else:  # данные повреждены, удаляем
                    # available_times.remove(available_time) # не нужно, не используем дальше available_times
                    available_time.delete()
                    continue
                to_remove = []
                for day in days:
                    if day.weekday() not in days_of_week:
                        to_remove.append(day)
                for day in to_remove:
                    days.remove(day)
                if not days:
                    continue
                # определим доступное время начала урока в эти дни
                for day in days:
                    hours = []
                    current_time = available_time.start_time.hour
                    if available_time.end_time != datetime.strptime('00', "%H").time():
                        end_time = available_time.end_time.hour
                        while current_time < end_time:
                            hours.append(current_time)
                            #current_time = (datetime(year=2000, month=1, day=1,
                            #                        hour=current_time,
                            #                        minute=0) + timedelta(hours=1)).time().hour
                            current_time += 1
                    else:
                        #end_time = datetime.strptime('23', "%H").time().hour  # баг, долго грузится
                        end_time = 23
                        while current_time <= end_time:
                            hours.append(current_time)
                            #current_time = (datetime(year=2000, month=1, day=1,
                            #                        hour=current_time,
                            #                        minute=0) + timedelta(hours=1)).time().hour
                            current_time += 1
                    if not hours:
                        continue
                    # проверим, что на это время пока что никто не записался - баг, не работает для 9 или 10 утра, в зависимости от того, hours - set или list
                    # hours = list(hours)
                    # for hour in hours:
                    #     registrations = Registration.objects.filter(date=day, time=hour)
                    #     if registrations:
                    #         hours.remove(hour)
                    # соберём полученный объект datetime
                    hours.sort()
                    for hour in hours:
                        available_datetimes.add((str(day.year), f"{day.month:02d}",
                                                f"{day.day:02d}", f"{hour:02d}", f"{0:02d}"))

            # проверим, записался ли кто на это время и что студент не записан на это время
            available_datetimes = list(available_datetimes)
            res = []
            for available_datetime in available_datetimes:
                year, month, day, hour, minute = (int(i) for i in available_datetime)
                date = datetime(year=year, month=month, day=day).date()
                time = datetime(year=2000, month=1, day=1, hour=hour, minute=minute).time()
                registrations_coach = Registration.objects.filter(coach=coach.profile, date=date, time=time)
                registrations_student = Registration.objects.filter(student=student.profile, date=date, time=time) if student else None
                registrations_coach2 = Registration.objects.filter(student=coach.profile, date=date, time=time)
                registrations_student2 = Registration.objects.filter(coach=student.profile, date=date, time=time) if student else None
                if not registrations_coach and not registrations_student  and not registrations_coach2 and not registrations_student2:
                    res.append(available_datetime)
            # отсортируем полученные datetime
            available_datetimes = res
            available_datetimes.sort()
            return available_datetimes, period


def check_past_and_blacklist(registrations, user):
            '''проверить, какие записи на уроки уже прошли, а какие идут сейчас'''

            to_remove = []
            for registration in registrations:
                reg_datetime = datetime(year=registration.date.year, month=registration.date.month,
                                        day=registration.date.day, hour=registration.time.hour,
                                        minute=registration.time.minute)
                if reg_datetime <= datetime.today():
                    if reg_datetime + timedelta(minutes=45) <= datetime.today():
                        registration.past = 2
                    else:
                        registration.past = 1
                        to_remove.append(registration)
                    registration.save()
                elif registration.coach.user in user.profile.blacklist.all() or user in registration.coach.blacklist.all():
                    registration.delete()
                    to_remove.append(registration)
            for registration in to_remove:
                    registrations.remove(registration)
            return registrations


# принять полученную заявку в друзья
def friendship_accept(friendship):
    if friendship.status != 3:  # 3 - получена заявка в друзья
        return
    user = Profile.objects.get(id=friendship.user_id)
    friend = Profile.objects.select_related('user').get(id=friendship.friend_id)
    # if friend not in user.friends.all():
    #     return
    if friend.user in user.blacklist.all():
        user.friends.remove(friend)
        if user in friend.friends.all():
            friendship2 = Friendship.objects.get(user=friend, friend=user)
            if friendship2.status != 3:  # 3 - рассматривает мою заявку
                friendship2.status = 2  # у него невзаимный друг
                friendship2.save()
        return
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


'''когда Наставник подтвердил, что урок прошёл'''
def on_confirm_lesson_coach(registration):
    registration.unread_student = 1
    # студент получает 1000 опыта и, возможно, уровень
    registration.student.experience += 1000
    current_level = registration.student.level
    current_exp = registration.student.experience
    if current_exp >= level_up(current_level):
        registration.student.experience -= level_up(current_level)
        registration.student.level += 1
    registration.student.save()
    registration.save()


'''когда студент подтвердил, что урок прошёл'''
def on_confirm_lesson_student(registration):
    registration.unread_coach = 1
    registration.coach.experience += 1000
    current_level = registration.coach.level
    current_exp = registration.coach.experience
    if current_exp >= level_up(current_level):
        registration.coach.experience -= level_up(current_level)
        registration.coach.level += 1
    registration.coach.save()
    registration.save()


def timedelta_to_string(reg_timedelta):
                    if reg_timedelta.days:
                        if reg_timedelta.days % 10 == 1 and reg_timedelta.days != 11:
                            reg_timedelta_string = f"{reg_timedelta.days} день"
                        elif reg_timedelta.days % 10 in [2, 3, 4] and reg_timedelta.days not in [12, 13, 14]:
                            reg_timedelta_string = f"{reg_timedelta.days} дня"
                        else:
                            reg_timedelta_string = f"{reg_timedelta.days} дней"
                    elif reg_timedelta.seconds >= 3600:
                            hours = reg_timedelta.seconds // 3600
                            if hours % 10 == 1 and hours != 11:
                                reg_timedelta_string = f"{hours} час"
                            elif hours % 10 in [2, 3, 4] and hours not in [12, 13, 14]:
                                reg_timedelta_string = f"{hours} часа"
                            else:
                                reg_timedelta_string = f"{hours} часов"
                    elif reg_timedelta.seconds >= 60:
                            minutes = reg_timedelta.seconds // 60
                            if minutes % 10 == 1 and minutes != 11:
                                reg_timedelta_string = f"{minutes} минуту"
                            elif minutes % 10 in [2, 3, 4] and minutes not in [12, 13, 14]:
                                reg_timedelta_string = f"{minutes} минуты"
                            else:
                                reg_timedelta_string = f"{minutes} минут"
                    else:
                            seconds = reg_timedelta.seconds
                            if seconds % 10 == 1 and seconds != 11:
                                reg_timedelta_string = f"{seconds} секунду"
                            elif seconds % 10 in [2, 3, 4] and seconds not in [12, 13, 14]:
                                reg_timedelta_string = f"{seconds} секунды"
                            else:
                                reg_timedelta_string = f"{seconds} секунд"
                    return reg_timedelta_string


def validate_phone_number(phone_number):
    for s in phone_number:
        if s not in '1234567890()+-–':
            return False
    return True


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
            context['settings_form'] = SettingsForm(request=request)
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            return render(request, 'account/account.html', context=context)
        else:
            return redirect('../index.html')


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
            return redirect('../index.html')


class AddToBlacklistView(View):
    '''Пункт меню В чёрный список на вкладках Сообщения, Закладки, Друзья,
        в чужом профиле, написании сообщения или комментария

    Сюда попадают только зарегистрированные пользователи, у которых
    этого пользователя нет в чёрном списке, но проверку сделаем на всякий случай

    '''

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            try:
                user = User.objects.select_related("profile").get(username=request.user)
                watched_user = User.objects.select_related("profile").get(id=watched_user_id)
            except User.DoesNotExist:
                raise Http404
            if watched_user.id == user.id:
                return redirect(next_url)
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

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user)
            watched_user = User.objects.select_related('profile').get(id=watched_user_id)
            if watched_user.profile.coach and watched_user not in user.profile.bookmarks.all() and \
                watched_user not in user.profile.blacklist.all():
                user.profile.bookmarks.add(watched_user)
                user.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class AddToFriendsView(View):
    '''Кнопка В друзья при просмотре чужого профиля

    Сюда попадают только зарегистрированные пользователи, у которых
    этого пользователя нет в Друзьях, но проверку сделаем на всякий случай
    Делаю проверку своего чёрного списка, хотя для этого случая кнопка невидима
    Делаю проверку чужого списка

    '''

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user)
            watched_user = User.objects.select_related('profile').get(id=watched_user_id)
            if watched_user in user.profile.blacklist.all():
                return redirect(next_url)
            if watched_user.profile not in user.profile.friends.all():
                user.profile.friends.add(watched_user.profile)  # status = 0 - отправил заявку
                user.save()
            if user.profile not in watched_user.profile.friends.all():
                if watched_user.profile.friends_auto == 2 or user in watched_user.profile.blacklist.all():  # он всегда отклоняет заявки либо добавил в чёрный список
                    fs = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                    fs.status = 2  # невзаимный друг
                    fs.save()
                elif watched_user.profile.friends_auto == 1:  # он всегда принимает заявки
                    watched_user.profile.friends.add(user.profile, through_defaults={'status':1})  # взаимные друзья
                    watched_user.save()
                    fs = Friendship.objects.get(user=user.profile, friend=watched_user.profile)
                    fs.status = 1  # взаимные друзья
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
            return redirect('../index.html')


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
            return redirect('../index.html')


class BookmarksView(View):
    '''Страница Закладки Профиля

    Не делаю проверку чёрного списка, их не должно быть в Закладках'''

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
                                key=lambda bookmark: ((bookmark.first_name or "") + (bookmark.profile.nickname or bookmark.username) + (bookmark.last_name or "")).lower())
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
            return redirect('../index.html')


# class ChatidView(View):
#     '''Страница чата'''

#     def get(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             context = dict()
#             context['trademark'] = settings.TRADEMARK
#             context['current_year'] = datetime.now().strftime('%Y')
#             user = User.objects.get(username=request.user)
#             context['user'] = user
#             return render(request, 'account/chatid1598737bi.html', context=context)
#         else:
#             return redirect('index.html')


class DiaryConfirmRegistrationView(View):
    '''Кнопка Подтвердить, что урок прошёл на странице Дневник Профиля'''

    def post(self, request, registration_id, next_url, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                user_profile = User.objects.select_related('profile').get(username=request.user).profile
                registration = Registration.objects.get(id=registration_id)
            except:
                return redirect(next_url)
            if registration.coach == user_profile:
                registration.confirmation_coach = 1
                on_confirm_lesson_coach(registration)
            elif registration.student == user_profile:
                registration.confirmation_student = 1
                on_confirm_lesson_student(registration)
            registration.save()
            return redirect(next_url)
        else:
            return redirect(next_url)


class DiarySortingView(View):
    '''Выбор типа сортировки на странице Дневник Профиля'''

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            # https://qna.habr.com/q/71870
            form = DiarySortingForm(request.POST, request=request)
            if form.is_valid():
                if request.POST.get('diary_sorting'):
                    user.profile.diary_sorting = request.POST.get('diary_sorting')
                    user.save()
            return redirect('diary.html')
        else:
            return redirect('../index.html')


class DiaryView(View):
    '''Страница Дневник Профиля'''

    def get(self, request, page=1, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            diary_sorting = user.profile.diary_sorting
            context['diary_sorting'] = diary_sorting
            num_pages = 10
            if user.profile.coach:
                # Выведем прошедшие занятия Наставника, в т.ч. в чёрном списке
                registrations = Registration.objects.filter(~Q(past=1), coach=user.profile)  # будущие и текущие занятия
                registrations = list(registrations) if registrations else []
                # проверим, может, какие-то уже прошли
                check_past_and_blacklist(registrations, user)
            # Выведем прошедшие занятия студента, в т.ч. в чёрном списке
            registrations = Registration.objects.filter(~Q(past=1), student=user.profile)  # будущие и текущие занятия
            registrations = list(registrations) if registrations else []
            # проверим, может, какие-то уже прошли
            check_past_and_blacklist(registrations, user)
            if diary_sorting not in [1, 2, 3, 4, 5]:
                diary_sorting = 1
            if diary_sorting == 1:  # по обновлённым
                registrations = Registration.objects.filter(coach=user.profile, past=1, unread_coach=1)
                registrations = list(registrations) if registrations else []
                registrations2 = Registration.objects.filter(student=user.profile, past=1, unread_student=1)
                registrations2 = list(registrations2) if registrations2 else []
                registrations.extend(registrations2)
                num_pages = 1
            elif diary_sorting == 2:  # по занятиям в качестве Наставника по имени студента
                registrations = Registration.objects.filter(coach=user.profile, past=1)  # занятия прошли
                registrations = list(registrations) if registrations else []
                registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                            day=registration.date.day, hour=registration.time.hour,
                                            minute=registration.time.minute), reverse=True)
                registrations.sort(key = lambda registration:  ((registration.student.user.first_name or '') + \
                                                                (registration.student.nickname or registration.student.user.username) + \
                                                                (registration.student.user.last_name or '')).lower())
            elif diary_sorting == 3:  # по занятиям в качестве Наставника по дате
                registrations = Registration.objects.filter(coach=user.profile, past=1)  # занятия прошли
                registrations = list(registrations) if registrations else []
                registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                            day=registration.date.day, hour=registration.time.hour,
                                            minute=registration.time.minute), reverse=True)
            elif diary_sorting == 4:  # по занятиям в качестве студента по имени Наставника
                registrations = Registration.objects.filter(student=user.profile, past=1)
                registrations = list(registrations) if registrations else []
                registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                            day=registration.date.day, hour=registration.time.hour,
                                            minute=registration.time.minute), reverse=True)
                registrations.sort(key = lambda registration:  ((registration.coach.user.first_name or '') + \
                                                                (registration.coach.nickname or registration.coach.user.username) + \
                                                                (registration.coach.user.last_name or '')).lower())
            elif diary_sorting == 5:  # по занятиям в качестве студента по дате
                registrations = Registration.objects.filter(student=user.profile, past=1)
                registrations = list(registrations) if registrations else []
                registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                            day=registration.date.day, hour=registration.time.hour,
                                            minute=registration.time.minute), reverse=True)
            paginator = Paginator(registrations, num_pages)  # How many registrations per page
            context['registrations'] = paginator.get_page(page)
            # Теперь выведенные в Обновлённых записи являются прочтёнными
            if diary_sorting == 1:
                for registration in paginator.get_page(page):
                    if registration.coach == user.profile:
                        registration.unread_coach = 0
                    else:
                        registration.unread_student = 0
                    registration.save()
            context['diary_sorting_form'] = DiarySortingForm(request=request)
            return render(request, 'account/diary.html', context=context)
        else:
            return redirect('../index.html')


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
                friendship_accept(friendship)  # проверяет на чёрный список
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
    '''Отправка комментария к другу на странице Друзья Профиля

    Проверка на дружбу, так что не требуется проверять чёрный список'''

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
            return redirect('../index.html')


class FriendsView(View):
    '''Страница Друзья Профиля

    Не проверяю чёрный список, их там не должно быть'''

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
                    key=lambda friendship: ((friendship.friend.user.first_name or "") + \
                        (friendship.friend.nickname or friendship.friend.user.username) + (friendship.friend.user.last_name or "")).lower())
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
            return redirect('../index.html')


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
            return redirect('../index.html')


class MessageView(View):
    '''Страница Сообщения Профиля

    Показываю, даже если автор в чёрном списке'''

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
            return redirect('../index.html')


class MessageWritingView(View):
    '''Отправка сообщения на странице по кнопке Написать сообщение в чужом
    профиле, на вкладке Закладки, Друзья Профиля

    Обработка чёрного списка - в шаблоне страницы написания сообщения
    и в отправке POST-сообщения, на всякий случай'''

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
            if user.user in recipient.blacklist.all() or recipient.user in user.blacklist.all():
                return redirect(next_url)
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
                #context['upload_photo_form'] = UploadPhotoForm()
                new_messages = Message.objects.filter(recipient=user.profile, status=0)
                context['new_messages'] = len(new_messages)
                # Расписание студента
                registrations = Registration.objects.filter(student=user.profile).exclude(past=1)  # будущие и текущие занятия
                registrations = list(registrations) if registrations else []
                # проверим, может, какие-то уже прошли
                registrations = check_past_and_blacklist(registrations, user)
                registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                            day=registration.date.day, hour=registration.time.hour,
                                            minute=registration.time.minute))
                if not registrations:
                    context['registrations_student'] = []
                else:
                    registration = registrations[0]  # самое раннее занятие, возможно, текущее
                    reg_datetime = datetime(year=registration.date.year, month=registration.date.month,
                                                day=registration.date.day, hour=registration.time.hour,
                                                minute=registration.time.minute)
                    reg_timedelta = reg_datetime - datetime.today()
                    reg_timedelta_string = timedelta_to_string(reg_timedelta)
                    registrations = (registration.past == 2, registration.coach, registration.coach.user.coach_profile.star_level.name, reg_timedelta_string)
                    context['registrations_student'] = (registrations,)  # расписание студента
                if user.profile.coach:
                    # Расписание Наставника
                    registrations = Registration.objects.filter(~Q(past=1), coach=user.profile)  # будущие и текущие занятия
                    registrations = list(registrations) if registrations else []
                    # проверим, может, какие-то уже прошли
                    registrations = check_past_and_blacklist(registrations, user)
                    registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                                day=registration.date.day, hour=registration.time.hour,
                                                minute=registration.time.minute))
                    if not registrations:
                        context['registrations_coach'] = []
                    else:
                        registration = registrations[0]  # самое раннее занятие, возможно, текущее
                        reg_datetime = datetime(year=registration.date.year, month=registration.date.month,
                                                    day=registration.date.day, hour=registration.time.hour,
                                                    minute=registration.time.minute)
                        reg_timedelta = reg_datetime - datetime.today()
                        reg_timedelta_string = timedelta_to_string(reg_timedelta)
                        registrations = (registration.past == 2, registration.student, reg_timedelta_string)
                        context['registrations_coach'] = (registrations,)  # расписание Наставника
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

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = '../profile.html/user_id{0}'.format(watched_user_id)
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            friend = User.objects.select_related('profile').get(id=watched_user_id).profile
            friendship = Friendship.objects.get(user=user, friend=friend)
            friendship_accept(friendship)  # учитывает чёрный список
            return redirect(next_url)
        else:
            return redirect(next_url)


class RegisterToLessonView(View):
    '''Запись на урок на странице Записи на урок к Наставнику по кнопке Запись чужого Профиля Наставника или в Закладках

    Сюда попадают после проверки на доступность этого времени, но делаю её снова

    '''
    def post(self, request, coach_id, year, month, day, hour, minute, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            coach = User.objects.select_related('profile').get(id=coach_id).profile
            appointment = datetime(year=int(year), month=int(month), day=int(day),
                                    hour=int(hour), minute=int(minute))
            if not user or not coach or not appointment or user.id == coach.id \
                        or coach.user in user.blacklist.all() or user.user in coach.blacklist.all():  # нельзя записаться к самому себе
                return redirect(f"registration.html_coach_id{coach_id}")
            date = appointment.date()
            time = appointment.time()
            appointment_datetime = (str(date.year), f"{date.month:02d}",
                                                 f"{date.day:02d}", f"{time.hour:02d}", f"{time.minute:02d}")
            available_datetimes, period = available_times_to_datetimes(coach.user, user.user)
            if appointment_datetime not in available_datetimes:
                return redirect(f"registration.html_coach_id{coach_id}")
            reg = Registration()
            reg.coach = coach
            reg.student = user
            reg.date = date
            reg.time = time
            form = RegistrationGameForm(request.POST, game=None, direction=None, region=None)
            gamedirection = GameDirection()
            to_save = False
            if form.is_valid():
                if request.POST.get('game'):
                    gamedirection.game = Game.objects.get(id = request.POST.get('game'))
                    to_save = True
                if request.POST.get('direction'):
                    gamedirection.direction = Direction.objects.get(id = request.POST.get('direction'))
                    to_save = True
                if request.POST.get('region'):
                    gamedirection.region = Region.objects.get(id = request.POST.get('region'))
                    to_save = True
            if to_save:
                gamedirection.save()
                reg.gamedirection = gamedirection
            reg.save()
            return redirect(f"registration.html_coach_id{coach_id}")
        else:
            return redirect(f"registration.html_coach_id{coach_id}")


class RegisterToLesson2View(View):
    '''Запись на урок на странице Записи на урок к Наставнику по кнопке Запись чужого Профиля Наставника или в Закладках
    Вариант при выборе сортировки на определённый день

    Сюда попадают после проверки на доступность этого времени, но делаю её снова

    '''
    def post(self, request, coach_id, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.select_related('profile').get(username=request.user).profile
            coach = User.objects.select_related('profile').get(id=coach_id).profile
            if not user or not coach or user.id == coach.id \
                    or coach.user in user.blacklist.all() or user.user in coach.blacklist.all():  # нельзя записаться к самому себе
                return redirect(f"registration.html_coach_id{coach_id}")
            #form = RegistrationForm(request.POST, datetimes=None, game=None,
            #                        direction=None,
            #                        region=None,
            #                        request=request)
            reg = Registration()
            to_save = False
            #if form.is_valid():   # не проходит, возможно, из-за datetimes=None
            if request.POST.get('datetime'):  # формат "2021-12-25-12-0"
                    reg_datetime = request.POST.get('datetime')
                    year, month, day, hour, minute = (int(i) for i in reg_datetime.split("-"))
                    appointment_datetime = (str(year), f"{month:02d}",
                                                 f"{day:02d}", f"{hour:02d}", f"{minute:02d}")
                    available_datetimes, period = available_times_to_datetimes(coach.user, user.user)
                    if appointment_datetime not in available_datetimes:
                        return redirect(f"registration.html_coach_id{coach_id}")
                    appointment = datetime(year=int(year), month=int(month), day=int(day),
                                    hour=int(hour), minute=int(minute))
                    reg.date = appointment.date()
                    reg.time = appointment.time()
                    to_save = True
            gamedirection = GameDirection()
            to_save2 = False
            if request.POST.get('game'):
                    gamedirection.game = Game.objects.get(id = request.POST.get('game'))
                    to_save2 = True
            if request.POST.get('direction'):
                    gamedirection.direction = Direction.objects.get(id = request.POST.get('direction'))
                    to_save2 = True
            if request.POST.get('region'):
                    gamedirection.region = Region.objects.get(id = request.POST.get('region'))
                    to_save2 = True
            if to_save2:
                    gamedirection.save()
                    reg.gamedirection = gamedirection
            if request.POST.get('email'):
                    reg.email = request.POST.get('email')
            if request.POST.get('phone_number'):
                    phone_number = request.POST.get('phone_number')
                    if validate_phone_number(phone_number):
                        reg.phone_number = phone_number
            if request.POST.get('contacts'):
                    reg.contacts = request.POST.get('contacts')
            reg.coach = coach
            reg.student = user
            #to_save = True
            if to_save:
                reg.save()
            return redirect(f"registration.html_coach_id{coach_id}")
        else:
            return redirect(f"registration.html_coach_id{coach_id}")


class RegistrationSortingView(View):
    '''Выбор типа сортировки на странице Запись по кнопке Запись в Закладках или Профиле'''

    def post(self, request, coach_id, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(username=request.user)
            # https://qna.habr.com/q/71870
            form = RegistrationSortingForm(request.POST, request=request)
            if form.is_valid():
                if request.POST.get('reg_sorting'):
                    user.profile.registration_sorting = request.POST.get('reg_sorting')
                    user.save()
            return redirect(f'registration.html_coach_id{coach_id}')

        else:
            return redirect('../index.html')


class RegistrationView(View):
    '''Страница Запись на урок к Наставнику по кнопке Запись чужого Профиля Наставника или в Закладках'''

    def get(self, request, coach_id, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            coach = User.objects.select_related('profile').get(id=coach_id)
            context['coach'] = coach
            if not coach.profile.coach:
                return redirect('../profile.html/user_id{0}'.format(coach_id))
            # обновим все записи студента
            registrations = Registration.objects.filter(student=user.profile).exclude(past=1)  # будущие и текущие записи
            registrations = list(registrations) if registrations else []
            # проверим, есть ли ещё прошедшие
            registrations = check_past_and_blacklist(registrations, user)
            # проверим, не превышен ли кап предстоящих занятий
            cap = Settings.objects.get(id=1).registrations_cap
            context['cap'] = cap
            context['cap_reached'] = len(registrations) >= cap
            # отсортируем записи студента к этому тренеру
            registrations = Registration.objects.filter(coach=coach.profile, student=user.profile, past=0)
            registrations = list(registrations)
            registrations.sort(key=lambda reg: reg.time)
            registrations.sort(key=lambda reg: reg.date)
            # проверим чёрный список
            if coach in user.profile.blacklist.all() or user in coach.profile.blacklist.all():
                context['available_datetimes'] = []
                for registration in registrations:
                    registration.delete()
                registrations = []
            context['registrations'] = registrations
            # проверка, если кто уже записан на это время (например, к другому Наставнику) делается в функции
            available_datetimes, period = available_times_to_datetimes(coach, user)
            context['available_datetimes'] = available_datetimes  # кортежи строк
            context['period'] = period
            try:
                current_gamedirection = user.profile.gamedirections.get(number=1)
            except:
                current_gamedirection = None
            form = RegistrationGameForm(game=current_gamedirection.game if current_gamedirection and current_gamedirection.game != "Account.Game.None" else None,
                                        direction=current_gamedirection.direction if current_gamedirection and current_gamedirection.direction != "Account.Direction.None" else None,
                                        region=current_gamedirection.region if current_gamedirection and current_gamedirection.region != "Account.Region.None" else None)
            context['registration_game_form'] = form
            form = RegistrationSortingForm(request=request)
            context['registration_sorting_form'] = form
            context['reg_sorting'] = user.profile.registration_sorting
            # проблема с этим вариантом - теряется синхронность даты и времени, списки заполняются при открытии страницы, а не обновляются при выборе даты. Сделала выбор даты и времени одновременно
            form = RegistrationForm(datetimes=available_datetimes, game=current_gamedirection.game if current_gamedirection and current_gamedirection.game != "Account.Game.None" else None,
                                    direction=current_gamedirection.direction if current_gamedirection and current_gamedirection.direction != "Account.Direction.None" else None,
                                    region=current_gamedirection.region if current_gamedirection and current_gamedirection.region != "Account.Region.None" else None,
                                    request=request)
            context['registration_form'] = form
            return render(request, 'account/registration.html', context=context)
        else:
            return redirect('../index.html')


class RejectFromFriendsView(View):
    '''Кнопка Отклонить заявку при просмотре чужого профиля

    Сюда попадают только зарегистрированные пользователи, которым
    этот пользователь подал заявку в Друзья, но проверку сделаем на всякий случай

    '''

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
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

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
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

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
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
    Ни к чему проверять чёрный список

    '''

    def post(self, request, watched_user_id, next_url=None, *args, **kwargs):
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
            form = SettingsForm(request.POST, request.FILES, request=request)
            if form.is_valid():
                if request.FILES.get('photo'):
                    user.profile.photo = request.FILES.get('photo')
                if request.POST.get('first_name'):
                    user.first_name = request.POST.get('first_name')
                if request.POST.get('last_name'):
                    user.last_name = request.POST.get('last_name')
                if request.POST.get('nickname'):
                    user.profile.nickname = request.POST.get('nickname')
                if request.POST.get('email'):
                    user.email = request.POST.get('email')
                if request.POST.get('phone_number'):
                    phone_number = request.POST.get('phone_number')
                    if validate_phone_number(phone_number):
                        user.profile.phone_number = phone_number
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
            return redirect('account.html')

        else:
            return redirect('../index.html')


class TimetableView(View):
    '''Страница Расписание Профиля'''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = dict()
            context['trademark'] = settings.TRADEMARK
            context['current_year'] = datetime.now().strftime('%Y')
            user = User.objects.select_related('profile').get(username=request.user)
            context['user'] = user
            new_messages = Message.objects.filter(recipient=user.profile, status=0)
            context['new_messages'] = len(new_messages)
            # Расписание Наставника
            registrations = Registration.objects.filter(~Q(past=1), coach=user.profile)  # будущие и текущие занятия
            registrations = list(registrations) if registrations else []
            # проверим, может, какие-то уже прошли
            registrations = check_past_and_blacklist(registrations, user)
            registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                        day=registration.date.day, hour=registration.time.hour,
                                        minute=registration.time.minute))
            registrations = [(registration, registration.student, registration.gamedirection, str(registration.date.year),
                            f"{registration.date.month:02d}", f"{registration.date.day:02d}",
                            f"{registration.time.hour:02d}", f"{registration.time.minute:02d}")
                            for registration in registrations]
            context['registrations_coach'] = registrations  # расписание Наставника
            # Расписание студента
            registrations = Registration.objects.filter(student=user.profile).exclude(past=1)  # будущие и текущие занятия
            registrations = list(registrations) if registrations else []
            # проверим, может, какие-то уже прошли
            registrations = check_past_and_blacklist(registrations, user)
            registrations.sort(key = lambda registration: datetime(year=registration.date.year, month=registration.date.month,
                                        day=registration.date.day, hour=registration.time.hour,
                                        minute=registration.time.minute))
            registrations = [(registration.id, registration.coach, registration.gamedirection, str(registration.date.year),
                            f"{registration.date.month:02d}", f"{registration.date.day:02d}",
                            f"{registration.time.hour:02d}", f"{registration.time.minute:02d}")
                            for registration in registrations]
            context['registrations_student'] = registrations  # расписание студента
            return render(request, 'account/timetable.html', context=context)
        else:
            return redirect('../index.html')


class UnregisterView(View):
    '''Кнопка Отписаться на странице Записи к Наставнику по кнопке Запись
    в профиле Наставника или в Закладках
    Также кнопка Отписаться в Расписании - Наставника или студента

    Сюда попадают только зарегистрированные пользователи, и есть запись на урок, но сделаем проверку

    '''

    def post(self, request, registration_id, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = 'timetable.html'
        if request.user.is_authenticated:
            registration = Registration.objects.get(id=registration_id)
            if not registration:
                return redirect(next_url)
            user = User.objects.select_related('profile').get(username=request.user).profile
            if not registration.student.id == user.id and not registration.coach.id == user.id:
                return redirect(next_url)
            registration.delete()
            return redirect(next_url)
        else:
            return redirect(next_url)


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
            return redirect('../index.html')

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
            return redirect('../index.html')