# -*- coding: utf-8 -*-
from django.urls import path
from login.views import MyLoginView, MySignupView


urlpatterns = [
    path('signup', MySignupView.as_view()),
    path('', MyLoginView.as_view()),
]
