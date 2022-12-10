from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm

default_context = {'trademark': settings.TRADEMARK,
                   'current_year': datetime.now().strftime('%Y'),
                   'form': UserCreationForm()}

class DefaultView(View):

    def get(self, request, *args, **kwargs):
        return redirect("index.html")


class CoachView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/coach.html', context=default_context)

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')


class CoachStandardsView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/coach-standards.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            


class DocView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/doc.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            


class IndexView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/index.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            


class PartnershipView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/partnership.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            


class PlatformStandardsView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/platform-standards.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            

class ProfileView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/profile.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            


class RandomView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/random.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            


class TeamView(View):

    def get(self, request, *args, **kwargs):
        return render(request,
            'coach/team.html', context=default_context)
            
    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('coach/profile.html')            

