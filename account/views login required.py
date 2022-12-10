from django.shortcuts import render
from django.views import View
from django.conf import settings
from datetime import datetime
from login.forms import MySignupForm, MyLoginForm
from django.contrib.auth.decorators import login_required

default_context = {'trademark': settings.TRADEMARK,
                   'current_year': datetime.now().strftime('%Y'),
                   'signup_form': MySignupForm(),
                   'login_form': MyLoginForm()}


class AccountView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/account.html', context=default_context)


class BookmarksView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/bookmarks.html', context=default_context)


class ChatidView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/chatid1598737bi.html', context=default_context)


class CoachOfficeView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/coach-office.html', context=default_context)


class DiaryView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/diary.html', context=default_context)


class FriendsView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/friends.html', context=default_context)


class MessageView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/message.html', context=default_context)


class ProfileView(View):

    @login_required
    def get(self, request, *args, **kwargs):
        return render(request,
            'account/profile.html', context=default_context)