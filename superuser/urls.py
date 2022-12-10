from django.urls import path, re_path
from superuser.views import AdminMenuView, ChangeLessonsCapView, \
ChangeRegistrationsPeriodView, ChangeStarsLevelView, ListOfCoachesView, \
SettingsView, WantsToCoachView

urlpatterns = [
    path('change_lessons_cap', ChangeLessonsCapView.as_view()),
    path('change_registrations_period', ChangeRegistrationsPeriodView.as_view()),
    re_path('change_stars_level/(?P<coach_id>[^/]*)/?', ChangeStarsLevelView.as_view()),
    re_path('list_of_coaches.html/(?P<page>[^/]*)/?', ListOfCoachesView.as_view()),
    path('settings.html', SettingsView.as_view()),
    path('wants_to_coach', WantsToCoachView.as_view()),
    path('wants_to_coach.html', WantsToCoachView.as_view()),
    path('', AdminMenuView.as_view()),
]