import secrets
from urllib.parse import urlencode

import requests

from django.conf import settings
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.authtoken.models import Token

from . import forms
from .discord import (
    DISCORD_AUTHORIZE_URL,
    DISCORD_NAME_CONFLICT_MESSAGE,
    DISCORD_PENDING_SESSION_KEY,
    DISCORD_STATE_SESSION_KEY,
    discord_name_is_taken,
    discord_oauth_configured,
    discord_redirect_uri,
    fetch_discord_name,
)
from .models import Player
from .serializers import PlayerSerializer


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
    template_name='authentification/player_register_form.html'
    success_url = reverse_lazy('auth:login')
    form_class = forms.PlayerRegisterForm
    success_message = _("Your player account was successfully created. \
                         You can now log in.")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Register")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['discord_enabled'] = discord_oauth_configured()
        context['pending_discord_name'] = (self.request.session
                                           .get(DISCORD_PENDING_SESSION_KEY, {})
                                           .get('discord_name'))
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        pending = self.request.session.pop(DISCORD_PENDING_SESSION_KEY, None)
        if pending and pending.get('discord_name'):
            if discord_name_is_taken(pending['discord_name'], self.request):
                messages.error(self.request, DISCORD_NAME_CONFLICT_MESSAGE)
            else:
                self.object.discord_name = pending['discord_name']
                self.object.save(update_fields=['discord_name'])
                messages.success(self.request, _("Your Discord account was successfully linked."))
        return response

class PlayerProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    template_name='authentification/player_profile_edit_form.html'
    success_url = reverse_lazy('home')
    form_class = forms.PlayerProfileEditForm
    success_message = _("Your profile was successfully updated.")
    extra_context = {'upper_title' : _("Account"),
                     'lower_title' : _("Profile")}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_token'] = self.request.GET.get('show_token')
        context['discord_enabled'] = discord_oauth_configured()
        return context

@login_required
def profileEditView(request):
    return PlayerProfileEditView.as_view()(request, pk=request.user.pk)

class DiscordConnectView(View):
    """
    Start the Discord OAuth2 flow to link a Discord account.

    Allowed for anonymous users too, so that a Discord account can be
    linked during registration.
    """

    http_method_names = ["post", "options"]

    def post(self, request, *args, **kwargs):
        if not discord_oauth_configured():
            raise Http404(_("Discord account linking is not configured."))
        state = secrets.token_urlsafe(32)
        request.session[DISCORD_STATE_SESSION_KEY] = state
        params = urlencode({
            'client_id': settings.DISCORD_CLIENT_ID,
            'redirect_uri': discord_redirect_uri(request),
            'response_type': 'code',
            'scope': 'identify',
            'state': state,
        })
        return HttpResponseRedirect(f"{DISCORD_AUTHORIZE_URL}?{params}")


class DiscordCallbackView(View):
    """
    Handle the Discord OAuth2 callback: validate the state, exchange the
    authorization code for an access token, fetch the Discord user, then
    link the verified Discord username to the player (or keep it in the
    session until registration is completed).
    """

    http_method_names = ["get", "options"]

    def get(self, request, *args, **kwargs):
        redirect_to = (reverse('auth:profile') if request.user.is_authenticated
                       else reverse('auth:register'))
        if not discord_oauth_configured():
            raise Http404(_("Discord account linking is not configured."))
        state = request.session.pop(DISCORD_STATE_SESSION_KEY, None)
        if request.GET.get('error'):
            messages.error(request, _("Discord account linking was cancelled."))
            return HttpResponseRedirect(redirect_to)
        code = request.GET.get('code')
        if (not code or not state
                or not secrets.compare_digest(request.GET.get('state', ''), state)):
            messages.error(request, _("Discord account linking failed. Please try again."))
            return HttpResponseRedirect(redirect_to)
        try:
            discord_name = fetch_discord_name(request, code)
        except (requests.RequestException, KeyError, ValueError):
            messages.error(request, _("Discord account linking failed. Please try again."))
            return HttpResponseRedirect(redirect_to)
        if discord_name_is_taken(discord_name, request):
            messages.error(request, DISCORD_NAME_CONFLICT_MESSAGE)
            return HttpResponseRedirect(redirect_to)
        if request.user.is_authenticated:
            request.user.discord_name = discord_name
            request.user.save(update_fields=['discord_name'])
            messages.success(request, _("Your Discord account was successfully linked."))
        else:
            request.session[DISCORD_PENDING_SESSION_KEY] = {'discord_name': discord_name}
            messages.success(request, _("Your Discord account has been verified. \
                                         It will be linked to your player account once you register."))
        return HttpResponseRedirect(redirect_to)


class DiscordDisconnectView(LoginRequiredMixin, View):
    """
    Unlink the Discord account from the logged in player.
    """

    http_method_names = ["post", "options"]

    def post(self, request, *args, **kwargs):
        request.user.discord_name = None
        request.user.save(update_fields=['discord_name'])
        messages.success(request, _("Your Discord account was unlinked."))
        return HttpResponseRedirect(reverse('auth:profile'))

class PlayerAPITokenGenerateView(LoginRequiredMixin, View):
    """
    Generate API token for a user.
    """

    http_method_names = ["post", "options"]

    def post(self, request, *args, **kwargs):
        """Token generation done via POST."""
        token, created = Token.objects.get_or_create(user=request.user)
        if created:
            message = _("A new API token has been generated.")
        else:
            message = _("An API token already existed.")
        messages.success(request, message)
        redirect_to = f"{reverse('auth:profile')}?show_token=1"
        return HttpResponseRedirect(redirect_to)

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
    
class PlayerViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerSerializer
    lookup_value_converter = 'int'
 
    def get_queryset(self):
        return Player.objects.filter(is_active=True)

# API ViewSet for checking whether a particular Player, with the specified Discord Username, is registered for league
class PlayerRegistrationViewSet(PlayerViewSet):
    lookup_field = "discord_name"
    lookup_value_converter = 'str'