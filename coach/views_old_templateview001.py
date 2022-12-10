# from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views import View
from django.conf import settings
from datetime import datetime

default_context = {'trademark': settings.TRADEMARK,
                   'current_year': datetime.now().strftime('%Y')}

class DefaultView(View):
    def get(self, request, *args, **kwargs):
        return redirect("index.html")


class CoachView(TemplateView):
    template_name = "coach/coach.html"
    def get_context_data(self, **kwargs):
        return default_context


class CoachStandardsView(TemplateView):
    template_name = "coach/coach-standards.html"
    def get_context_data(self, **kwargs):
        return default_context


class DocView(TemplateView):
    template_name = "coach/doc.html"
    def get_context_data(self, **kwargs):
        return default_context


class IndexView(TemplateView):
    template_name = "coach/index.html"
    def get_context_data(self, **kwargs):
        return default_context


class PartnershipView(TemplateView):
    template_name = "coach/partnership.html"
    def get_context_data(self, **kwargs):
        return default_context


class PlatformStandardsView(TemplateView):
    template_name = "coach/platform-standards.html"
    def get_context_data(self, **kwargs):
        return default_context


class RandomView(TemplateView):
    template_name = "coach/random.html"
    def get_context_data(self, **kwargs):
        return default_context


class TeamView(TemplateView):
    template_name = "coach/team.html"
    def get_context_data(self, **kwargs):
        return default_context
