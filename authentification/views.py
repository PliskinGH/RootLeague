from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from . import forms

# Create your views here.

class PlayerLoginView(SuccessMessageMixin, LoginView):
    form_class = forms.PlayerLoginForm
    template_name='misc/basic_form.html'
    redirect_authenticated_user=True
    success_message = _("Log in successful!")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Log in")}

class PlayerSignUpView(SuccessMessageMixin, CreateView):
    model = get_user_model()
    template_name='misc/basic_form.html'
    success_url = reverse_lazy('auth:login')
    form_class = forms.PlayerRegisterForm
    success_message = _("Your player account was successfully created. \
                         You can now log in.")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Register")}

class PlayerPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = forms.PlayerPasswordChangeForm
    template_name='misc/basic_form.html'
    success_url = reverse_lazy('index')
    success_message = _("Password changed successfully!")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Change Password")}