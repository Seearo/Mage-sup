from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from six import text_type


def rename_photo(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>
    # default max length of 100 characters.
    return 'photos/user_{0}'.format(instance.user.id)


# достижения
class Achievement(models.Model):
    name = models.CharField(max_length=50, unique=True)
    text = models.TextField(max_length=100, blank=True)
    points = models.PositiveIntegerField(default=0)
    is_coach = models.BooleanField(default=0)

    def __str__(self):
        return self.name

# названия игр
class Game(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# направление - pve, pvp, экономика
class Direction(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


# регион - Европа, США, Азия
class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Profile(models.Model):

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
    games = models.ManyToManyField(Game, blank=True, related_name='favorite_games')
    directions = models.ManyToManyField(Direction, blank=True,
                                        related_name='favorite_directions')
    regions = models.ManyToManyField(Region, blank=True, related_name='favorite_regions')      

    achievements_points = models.PositiveIntegerField(default=0)
    achievements = models.ManyToManyField(Achievement, blank=True,
                                        related_name='user_achievements')

    # Наставник или нет
    coach = models.BooleanField(default=0)

    # profile.is_coach True/False
    @property
    def is_coach(self):
        return bool(self.coach)

    # https://stackoverflow.com/questions/4279905/access-django-model-fields-label-and-help-text
    def __get_help_text(self, field):
        return text_type(self._meta.get_field(field).help_text)

    @property
    def photo_help_text(self):
        return self.__get_help_text('photo')
    
    # https://qna.habr.com/q/71870
    User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])

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

