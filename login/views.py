'''Отправка данных регистрации и авторизации пользователей'''

from django.views import View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from login.forms import MySignupForm, MyLoginForm
from django.conf import settings
from datetime import datetime


DEFAULT_CONTEXT = {'signup_form': MySignupForm(),
                   'login_form': MyLoginForm()}


class LoginPageView(View):

    '''Страница Регистрация/Вход, доступная гостю при нажатии некоторых кнопок'''

    def get(self, request, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = "index.html"
        # if next_url.startswith("profile"):
        #     next_url = '/account/profile.html/user_id{0}'.format(next_url[7:]) # e.g. profile4 -> user_id = 4
        if request.user.is_authenticated:
            return redirect(next_url)
        context = DEFAULT_CONTEXT
        context['trademark'] = settings.TRADEMARK
        context['current_year'] = datetime.now().strftime('%Y')
        context['next_page'] = next_url  # maybe something like profile4 for deciphering later
        return render(request,
            'login/login.html', context=context)


class MyLoginView(View):

    '''Отправка данных при логине пользователя'''

    def post(self, request, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = "index.html"
        if next_url.startswith("profile"):
            next_url = '/account/profile.html/user_id{0}'.format(next_url[7:]) # e.g. profile4 -> user_id = 4
        # user_form = MyLoginForm(request.POST)
        # if user_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
                if user.is_active:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect(next_url)
                else:
                    # Return a 'disabled account' error message
                    return redirect(next_url)
        else:
                # Return an 'invalid login' error message.
                return redirect(next_url)


class MySignupView(View):

    '''Отправка данных регистрации нового пользователя'''

    def post(self, request, next_url=None, *args, **kwargs):
        if not next_url:
            next_url = "index.html"
        if next_url.startswith("profile"):
            next_url = '/account/profile.html/user_id{0}'.format(next_url[7:]) # e.g. profile4 -> user_id = 4
        # if "next=" in next_url:
        #     next_url = next_url.split("next=")[0]
        user_form = MySignupForm(request.POST)
        if user_form.is_valid():

            # https://pocoz.gitbooks.io/django-v-primerah/content/glava-4-sozdanie-social-website/registratsiya-polzovatelei-i-profili-polzovatelei/registratsiya-polzovatelei.html
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.email = user_form.cleaned_data.get('email')
            # Save the User object
            new_user.save()

            # https://kmv-it.ru/django-registraciya
            # Если вы хотите сразу авторизовать пользователя после регистрации
            username = user_form.cleaned_data.get('username')
            my_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=my_password)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(next_url)