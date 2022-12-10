from django.contrib import admin
from account.models import Achievement, Game, Direction, Region, LevelUp


class AchievementAdmin(admin.ModelAdmin):
    pass


class GameAdmin(admin.ModelAdmin):
    fields = ('name', 'number')


class DirectionAdmin(admin.ModelAdmin):
    fields = ('name', 'number')


class RegionAdmin(admin.ModelAdmin):
    fields = ('name', 'number')


class LevelUpAdmin(admin.ModelAdmin):
    pass


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Direction, DirectionAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(LevelUp, LevelUpAdmin)