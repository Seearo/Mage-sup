from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from six import text_type


def rename_photo(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>
    # default max length of 100 characters.
    return 'photos/user_{0}'.format(instance.user.id)


# поля number завела как id, планируя делать to_field, но потом передумала
# оставила на случай, если пригодятся
# достижения
class Achievement(models.Model):
    name = models.CharField(max_length=50, unique=True)
    text = models.TextField(max_length=100, blank=True)
    points = models.PositiveIntegerField(default=0)
    is_coach = models.BooleanField(default=0)
    number = models.PositiveIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

# class Bookmark(models.Model):
#     '''Закладки, в которые добавляем Наставников на страницу Закладки в Профиле'''

#     # https://docs.djangoproject.com/en/3.2/ref/models/fields/#arguments про CASCADE
#     # при удалении Наставника должны удаляться все закладки на него
#     # при ссылке на User выдавал ошибку, делаю ссылку на Profile, вдруг захотим закладки любых пользователей в будущем
#     coach = models.ForeignKey(
#         'Profile', on_delete=models.CASCADE, related_name = 'bookmarks',
#     )
#     number = models.PositiveSmallIntegerField(default=1)  # 0 to 32767

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = 'Закладка'
#         verbose_name_plural = 'Закладки'

# направление - pve, pvp, экономика...
class Direction(models.Model):
    name = models.CharField(max_length=30, unique=True)
    number = models.PositiveIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'


# названия игр
class Game(models.Model):
    name = models.CharField(max_length=50, unique=True)
    number = models.PositiveIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Игру'
        verbose_name_plural = 'Игры'


# регион - Европа, США, Азия
class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)
    number = models.PositiveIntegerField(blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


# игра со своим направлением и регионом
class GameDirection(models.Model):
    game = models.ForeignKey(
        'Game', blank=True, null=True,
        on_delete=models.SET_NULL, related_name = 'gamedirections',
    )
    direction = models.ForeignKey(
        'Direction', blank=True, null=True,
        on_delete=models.SET_NULL, related_name = 'gamedirections',
    )
    region = models.ForeignKey(
        'Region', blank=True, null=True,
        on_delete=models.SET_NULL, related_name = 'gamedirections',
    )

    # в настройках аккаунта меняем только 1й, наставник имеет ещё 3
    number = models.PositiveSmallIntegerField(default=1)  # 0 to 32767


# сколько опыта нужно, чтобы подняться с предыдущего уровня на указанный
class LevelUp(models.Model):
    to_level = models.PositiveSmallIntegerField(unique=True)
    experience = models.PositiveIntegerField()

    def __str__(self):
        return str(self.to_level)

    class Meta:
        verbose_name = 'Опыт до уровня'
        verbose_name_plural = 'Уровни'
        get_latest_by = "to_level"


class Profile(models.Model):

    # в User уже хранится:

    # логин username, 30 символов, required
    # Usernames may contain alphanumeric, _, @, +, . and - characters.

    # имя first_name, 30 символов
    # фамилия last_name, 30 символов
    # email - got to be required but not unique through form validation

    # password, required
    # Django doesn’t store the raw password.
    # Raw passwords can be arbitrarily long and can contain any character.

    # groups, user_permissions
    # is_staff, is_active (False is deleted account), is_superuser

    # last_login, date_joined - automatically

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    nickname = models.CharField(max_length=30, blank=True)

    level = models.PositiveSmallIntegerField(default=1)  # 0 to 32767
    experience = models.PositiveIntegerField(default=0)

    contacts = models.TextField(max_length=200, blank=True)
    photo = models.ImageField(upload_to=rename_photo, width_field='image_width',
                              height_field='image_height', blank=True, null=True,
                              help_text=u"Загрузить фото")
    image_width = models.PositiveSmallIntegerField(default=0)
    image_height = models.PositiveSmallIntegerField(default=0)

    # для пустых str(user.profile.games) == 'account.Game.None'
    # про related_name: https://qna.habr.com/q/551262
    # SET_NULL: https://django.fun/docs/django/ru/2.2/ref/models/fields/
    gamedirections = models.ManyToManyField(
        'GameDirection', blank=True,
        related_name="profiles",
    )

    achievements_points = models.PositiveIntegerField(default=0)
    achievements = models.ManyToManyField(Achievement, blank=True,
                                        related_name='user_achievements')

    blacklist = models.ManyToManyField(User, blank=True,
                                        related_name='user_blacklist')

    bookmarks = models.ManyToManyField(User, blank=True,
                                        related_name='user_bookmarks')

    # 1, 2, 3, 4 - number of choice in the menu on Bookmarks page of Profile
    bookmarks_sorting = models.PositiveSmallIntegerField(default=1)

    #https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.choices
    # class BookmarksSorting(models.TextChoices):
    #     NEW = '1', _('новым')
    #     NAME = '2', _('имени')
    #     STARS_DESC = '3', _('звёздам -')
    #     STARS_ASC = '4', _('звёздам +')

    # bookmarks_sorting = models.CharField(
    #     max_length=1,
    #     choices=BookmarksSorting.choices,
    #     default=BookmarksSorting.NEW,
    # )

    # 1, 2, 3, 4, 5 - number of choice in the menu on Diary page of Profile
    diary_sorting = models.PositiveSmallIntegerField(default=1)

    # https://www.djbook.ru/rel1.9/ref/models/fields.html
    # Если вам не нужна симметричность для связи многое-ко-многим к self, установите symmetrical в False.
    friends = models.ManyToManyField("self", blank=True, through='Friendship',
                                    through_fields=('user', 'friend'),
                                    symmetrical=False,
                                    related_name='user_friends')

    # автоматическая обработка заявок в друзья
    # 0 - нет,
    # 1 - всегда принимать,
    # 2 - всегда отклонять
    friends_auto = models.PositiveSmallIntegerField(default=0)

    # 1, 2, 3, 4, 5 - number of choice in the menu on Friends page of Profile
    friends_sorting = models.PositiveSmallIntegerField(default=1)

    messages = models.ManyToManyField("self", blank=True, through='Message',
                                    through_fields=('recipient', 'author'),
                                    symmetrical=False)

    # 1, 2, 3, 4, 5, 6 - number of choice in the menu on Messages page of Profile
    messages_sorting = models.PositiveSmallIntegerField(default=1)

    # номер телефона в Настройках профиля
    # user.email
    phone_number = models.CharField(max_length=15, blank=True)

    # 1, 2 - number of choice in the menu on Registration page по кнопке Запись в Закладках или Профиле Наставника
    registration_sorting = models.PositiveSmallIntegerField(default=1)

    # Наставник 1 или нет 0
    coach = models.BooleanField(default=0)

    # profile.is_coach True/False
    @property
    def is_coach(self):
        return bool(self.coach)

    # нажал кнопку «Стать Наставником» в Настройках аккаунта
    wants_to_coach = models.BooleanField(default=0)

    # https://stackoverflow.com/questions/4279905/access-django-model-fields-label-and-help-text
    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    @property
    def photo_help_text(self):
        return self.__get_help_text('photo')

    # https://qna.habr.com/q/71870
    User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])


# https://youtu.be/-HuTlmEVOgU
class Friendship(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friendships1')
    friend = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friendships2')
    # 0 моя заявка отправлена и на рассмотрении, у меня невзаимный друг,
    # 1 мы взаимные друзья,
    # 2 у меня невзаимный друг,
	# 3 я получила заявку и она на рассмотрении
	# 0-2 могу удалить друга, 3 могу принять или отклонить заявку
    status = models.PositiveSmallIntegerField(default=0)
    comment = models.TextField(max_length=200, blank=True)

    class Meta:
        unique_together = [['user', 'friend']]


class Message(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='messages_by_author')
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='messages_by_recipient')
    datetime = models.DateTimeField(auto_now_add=True)  # автоматическое время создания
    text = models.TextField(max_length=500)
    status = models.PositiveSmallIntegerField(default=0) # 0 unread, 1 read


class Registration(models.Model):
    '''Запись на занятие'''

    coach = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='registrations_by_coach')
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='registrations_by_student')
    date = models.DateField()
    time = models.TimeField()
    past = models.PositiveSmallIntegerField(default=0) # 0 in the future, 1 already in the past, 2 in the process
    gamedirection = models.OneToOneField(GameDirection, on_delete=models.SET_NULL, null=True, blank=True)
    contacts = models.TextField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=75, blank=True)
    mark_student = models.SmallIntegerField(default=0) # оценка занятия студентом, 1-5, если оспорена, то -1 - -5
    mark_coach = models.SmallIntegerField(default=0) # оценка студента Наставником, 1-5, если оспорена, то -1 - -5
    feedback_student = models.TextField(max_length=200, blank=True)  # отзыв студента о занятии
    feedback_coach = models.TextField(max_length=200, blank=True)  # отзыв Наставника о студенте на занятии
    confirmation_student = models.PositiveSmallIntegerField(default=0)  # 1 - подтверждение, что урок прошёл
    confirmation_coach = models.PositiveSmallIntegerField(default=0)  # 1 - подтверждение, что урок прошёл
    homework_coach = models.TextField(max_length=500, blank=True)  # домашнее задание для студента
    homework_student = models.TextField(max_length=500, blank=True)  # выполненное домашнее задание студента
    homework_feedback_coach = models.TextField(max_length=200, blank=True)  # отзыв Наставника о решении домашнего задания студентом
    homework_mark_coach = models.SmallIntegerField(default=0) # оценка домашнего задания Наставником, 1-5, если оспорена, то -1 - -5
    homework_mark_student = models.SmallIntegerField(default=0) # оценка домашнего задания студентом, 1-5, если оспорена, то -1 - -5
    unread_coach = models.PositiveSmallIntegerField(default=0)  # флаг 1, что есть непрочтённое Наставником
    unread_student = models.PositiveSmallIntegerField(default=0)  # флаг 1, что есть непрочтённое Наставником
    hidden_coach = models.PositiveSmallIntegerField(default=0)  # флаг, что скрыто Наставником
    hidden_student = models.PositiveSmallIntegerField(default=0)  # флаг, что скрыто студентом

# сигналы для Profile на автоматическое создание/обновление, когда
# мы создаём/обновляем стандартную модель пользователя (User)
# https://tproger.ru/translations/extending-django-user-model/

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()