"""
Discord OAuth2 account linking.

This module holds the Discord-specific constants and helpers used by the views.

"""
import requests

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Player

# Discord OAuth2 endpoints
DISCORD_AUTHORIZE_URL = 'https://discord.com/oauth2/authorize'
DISCORD_API_BASE_URL = 'https://discord.com/api/v10'

# Session keys used by the linking flow
DISCORD_STATE_SESSION_KEY = 'discord_oauth_state'
DISCORD_PENDING_SESSION_KEY = 'discord_oauth_pending'

DISCORD_NAME_CONFLICT_MESSAGE = _(
    "This Discord account is already linked to another player. "
    "Please contact the administrators."
)


def discord_oauth_configured():
    """
    Return True when the Discord OAuth2 application credentials are set.

    The linking UI and the connecting views are disabled until this is the
    case.
    """
    return bool(settings.DISCORD_CLIENT_ID and settings.DISCORD_CLIENT_SECRET)


def discord_redirect_uri(request):
    """
    Return the callback URI sent to Discord.

    Prefers the explicitly configured ROOTLEAGUE_DISCORD_REDIRECT_URI (needed
    behind a reverse proxy where the request host cannot be trusted), and
    falls back to building it from the current request.
    """
    return settings.DISCORD_REDIRECT_URI or request.build_absolute_uri(
        reverse('auth:discord_callback'))


def discord_name_is_taken(discord_name, request):
    """
    Return True when another player already holds this Discord username.

    The logged in user's own existing link is always allowed (re-linking).
    """
    conflict = Player.objects.filter(discord_name__iexact=discord_name)
    if request.user.is_authenticated:
        conflict = conflict.exclude(pk=request.user.pk)
    return conflict.exists()


def fetch_discord_name(request, code):
    """
    Exchange the OAuth2 authorization code for an access token and return the
    Discord username of the authenticated user.

    Any network or Discord API error propagates to the caller.
    """
    token_response = requests.post(
        f"{DISCORD_API_BASE_URL}/oauth2/token",
        data={
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': discord_redirect_uri(request),
        },
        timeout=10,
    )
    token_response.raise_for_status()
    access_token = token_response.json()['access_token']
    user_response = requests.get(
        f"{DISCORD_API_BASE_URL}/users/@me",
        headers={'Authorization': f"Bearer {access_token}"},
        timeout=10,
    )
    user_response.raise_for_status()
    return user_response.json()['username']