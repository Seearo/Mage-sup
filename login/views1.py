'''Отправка данных регистрации и авторизации пользователей'''

from django.views import View
from django.shortcuts import redirect
from login.forms import MySignupForm
from django.contrib.auth import authenticate, login


class MySignupView(View):

    '''Отправка данных регистрации нового пользователя'''

    def post(self, request, *args, **kwargs):
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
            user_id = user.id
            return redirect('/account/profile.html/user_id{0}'.format(user_id))
        else:
            return redirect('/')

class MyLoginView(View):

    '''Отправка данных при логине пользователя'''

    def post(self, request, *args, **kwargs):
        # user_form = MyLoginForm(request.POST)
        # if user_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
                if user.is_active:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    user_id = user.id
                    return redirect('/account/profile.html/user_id{0}'.format(user_id))
                else:
                    # Return a 'disabled account' error message
                    return redirect('/')
        else:
                # Return an 'invalid login' error message.
                return redirect('/')