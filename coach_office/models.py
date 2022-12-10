from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class GameAccount(models.Model):
    # можно добавить название игры, если будет несколько игровых аккаунтов
    url = models.URLField(blank=True, null=True)  # default length 200

    def __str__(self):
        return self.url


# уровень звёзд - Новичок, 1, 2, 3, 4, 5
class Stars(models.Model):
    name = models.CharField(max_length=20, unique=True)
    number = models.PositiveSmallIntegerField(unique=True)
    price = models.PositiveIntegerField(default=0)  # оплата за урок 45 минут

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Уровень звёзд'
        verbose_name_plural = 'Уровни звёзд'


class CoachProfile(models.Model):

    # не путать user.coach_profile и user.profile.coach
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')

    # не путать user.profile.contacts и user.coach_profile.contacts
    # контактные данные для игр
    contacts = models.TextField(max_length=900, blank=True)

    # описание для карточек в поиске
    description = models.TextField(max_length=350, blank=True)

    # сейчас ссылка на игровой аккаунт одна, но делаю запас на расширение
    game_accounts = models.ManyToManyField(
        'GameAccount', blank=True,
        related_name="users",
    )

    # доход зависит от звёзд, звёзды от киберспорта, будут устанавливаться админом
    # pk: https://stackoverflow.com/questions/32760038/django-model-cannot-serialize-into-migration-files
    # default=Stars.objects.get(number=0).pk  # "Field 'star_level_id' doesn't have a default value"
    # to_field: https://stackoverflow.com/questions/9311996/setting-default-value-for-foreign-key-attribute
    star_level = models.ForeignKey(Stars, to_field='number', default=0,
                on_delete=models.SET_DEFAULT,
                related_name='users')

    # сильные стороны/программа
    strengths = models.TextField(max_length=900, blank=True)

    # число учеников для достижения 10 последователей
    students_number = models.PositiveSmallIntegerField(default=0)

    # флажок, что нужно отключить аккаунт Наставника
    inactive_flag = models.BooleanField(default=0)

    # флажок, что нужно показывать только никнейм
    nickname_flag = models.BooleanField(default=0)

    # флажок, нужно ли показывать в случайном поиске
    search_flag = models.BooleanField(default=1)

    # 1 'Показывать основное фото профиля',
    # 2 'Показывать стандартное изображение (парень)',
    # 3 'Показывать стандартное изображение (девушка)'
    which_photo = models.PositiveSmallIntegerField(default=1)

    # Кнопка на Ваш игровой профиль
    # 1 Отсутствует
    # 2 Только для учеников
    # 3 Для всех
    show_button = models.PositiveSmallIntegerField(default=3)


def tomorrow():
    return datetime.date.today() + datetime.timedelta(days=1)


# Доступное время Наставника в Расписании Профиля Наставника
class AvailableTime(models.Model):

    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE)
    # https://codengineering.ru/q/how-do-i-get-the-day-of-week-given-a-date-in-python-25488
    # datetime: понедельник равен 0, пятница 4, а воскресенье-6, 7 - все будни, 8 - все выходные, 9 - все дни
    day_of_week = models.PositiveSmallIntegerField()
    # в форме разбивка по часам
    start_time = models.TimeField()
    end_time = models.TimeField()
    # на какой период действует это расписание доступного времени
    # today() - пишет, что это фиксированная дата, а не текущая
    start_day = models.DateField(default=tomorrow)
    end_day = models.DateField(blank=True, null=True)


# сигналы для CoachProfile на автоматическое создание/обновление, когда
# мы обновляем стандартную модель пользователя (User)
# https://tproger.ru/translations/extending-django-user-model/

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.profile.coach and instance.profile.wants_to_coach:
        CoachProfile.objects.create(user=instance)
    elif instance.profile.coach:
        instance.coach_profile.save()