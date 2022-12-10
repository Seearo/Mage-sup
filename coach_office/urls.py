from django.urls import path
from coach_office.views import AvailableTimeAsStudentView, \
AvailableTimeChangeFormView, \
AvailableTimeDeleteView, AvailableTimeFormView, AvailableTimeView, \
CoachOfficeView, SettingsView

urlpatterns = [
    path('available_time_as_student.html', AvailableTimeAsStudentView.as_view()),
    path('available_time_change_<int:available_time_id>', AvailableTimeChangeFormView.as_view()),
    path('available_time_delete_<int:available_time_id>', AvailableTimeDeleteView.as_view()),
    path('available_time_form', AvailableTimeFormView.as_view()),
    path('available_time.html', AvailableTimeView.as_view()),
    path('settings', SettingsView.as_view()),
    path('user_id<int:user_id>', CoachOfficeView.as_view()),

]