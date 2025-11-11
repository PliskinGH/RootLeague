from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from . import forms

# Create your views here.

class PlayerLoginView(SuccessMessageMixin, LoginView):
    form_class = forms.PlayerLoginForm
    template_name='authentification/player_login_form.html'
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

class PlayerProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    template_name='authentification/player_profile_edit_form.html'
    success_url = reverse_lazy('home')
    form_class = forms.PlayerProfileEditForm
    success_message = _("Your profile was successfully updated.")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Profile")}

@login_required
def profileEditView(request):
    return PlayerProfileEditView.as_view()(request, pk=request.user.pk)

class PlayerPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = forms.PlayerPasswordChangeForm
    template_name='misc/basic_form.html'
    success_url = reverse_lazy('home')
    success_message = _("Password changed successfully!")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Change Password")}

class PlayerPasswordResetView(SuccessMessageMixin, PasswordResetView):
    form_class = forms.PlayerPasswordResetForm
    template_name='misc/basic_form.html'
    email_template_name='authentification/password_reset_email.html' 
    success_url = reverse_lazy('home')
    success_message = _("Confirmation email sent! Please follow the confirmation link to reset your password.")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Reset Password")}

class PlayerPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    form_class = forms.PlayerPasswordResetConfirmForm
    template_name='authentification/player_password_reset_form.html'
    success_url = reverse_lazy('home')
    success_message = _("Password changed successfully!")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Reset Password")}