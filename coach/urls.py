# -*- coding: utf-8 -*-
from django.urls import path
from coach.views import DefaultView, CoachView, CoachStandardsView, DocView, \
IndexView, PartnershipView, PlatformStandardsView, RandomView, TeamView

urlpatterns = [
    path('', DefaultView.as_view()),
    path('coach.html', CoachView.as_view()),
    path('coach-standards.html', CoachStandardsView.as_view()),
    path('doc.html', DocView.as_view()),
    path('index.html', IndexView.as_view()),
    path('partnership.html', PartnershipView.as_view()),
    path('platform-standards.html', PlatformStandardsView.as_view()),
    path('random.html', RandomView.as_view()),
    path('team.html', TeamView.as_view()),
]
