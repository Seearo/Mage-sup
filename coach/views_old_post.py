from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from datetime import datetime
from login.views import MySignupForm, MyLoginForm

default_context = {'trademark': settings.TRADEMARK,
                   'current_year': datetime.now().strftime('%Y'),
                   'signup_form': MySignupForm(),
                   'login_form': MyLoginForm()}

class DefaultView(View):
    def get(self, request, *args, **kwargs):
        return redirect("index.html")


class CoachView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/coach.html', context=default_context)


class CoachStandardsView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/coach-standards.html', context=default_context)


class DocView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/doc.html', context=default_context)


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/index.html', context=default_context)


class PartnershipView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/partnership.html', context=default_context)


class PlatformStandardsView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/platform-standards.html', context=default_context)


class RandomView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/random.html', context=default_context)


class TeamView(View):
    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/team.html', context=default_context)

