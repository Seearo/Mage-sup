from django.urls import path
from login.views import LoginPageView, MyLoginView, MySignupView


urlpatterns = [
    #path('login.html/next=<path:next_url>', LoginPageView.as_view()), # баг: сразу редирект на next_url, если он корректен
    path('login.html/next2=<str:next_url>', LoginPageView.as_view()),
    path('signup/next2=<str:next_url>', MySignupView.as_view()),
    path('signup/next=<path:next_url>', MySignupView.as_view()),
    path('next2=<str:next_url>', MyLoginView.as_view()),
    path('next=<path:next_url>', MyLoginView.as_view()),
]