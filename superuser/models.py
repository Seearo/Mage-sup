from django.db import models

class Settings(models.Model):
    # максимальное число записей на предстоящие уроки
    registrations_cap = models.PositiveSmallIntegerField(default=4)
    # число дней, на которые выводится доступное время для записи на урок
    # если большое, то может вылететь из-за превышения ограничения по оперативной памяти
    registrations_period = models.PositiveSmallIntegerField(default=3)