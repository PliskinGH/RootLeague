from django.test import TestCase
from django.urls import reverse

from .models import Player

# Create your tests here.

class LoginTestCase(TestCase):
    
    def setUp(self):
        self.user = Player.objects.create_user('TestUser', 'test@test.com', 'test')

from contextlib import contextmanager
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

import requests

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from .backends import EmailBackend
from .forms import (
    PlayerLoginForm,
    PlayerPasswordChangeForm,
    PlayerPasswordResetForm,
    PlayerPasswordResetConfirmForm,
    PlayerProfileEditForm,
    PlayerRegisterForm,
)
from .models import Player, Role


class PlayerModelTestCase(TestCase):

    def test_string_uses_in_game_identity(self):
        player = Player.objects.create_user('player', 'player@test.com', 'test', in_game_name='Warrior', in_game_id=42)
        self.assertEqual(str(player), 'Warrior+42')

    def test_string_falls_back_to_username_without_in_game_name(self):
        player = Player.objects.create_user('player', 'player@test.com', 'test', in_game_name='')
        self.assertEqual(str(player), 'player')

    def test_string_omits_missing_in_game_id(self):
        player = Player.objects.create_user('player', 'player@test.com', 'test', in_game_name='Warrior', in_game_id=None)
        self.assertEqual(str(player), 'Warrior')

    def test_roles_are_optional(self):
        player = Player.objects.create_user('player', 'player@test.com', 'test')
        role = Role.objects.create(name='Champion')
        player.roles.add(role)
        self.assertEqual(list(player.roles.all()), [role])

    def test_duplicate_case_insensitive_in_game_identity_is_rejected(self):
        Player.objects.create_user('first', 'first@test.com', 'test', in_game_name='Warrior', in_game_id=42)
        duplicate = Player(username='second', email='second@test.com', in_game_name='warrior', in_game_id=42)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class AuthenticationBackendTestCase(TestCase):

    def setUp(self):
        self.user = Player.objects.create_user('BackendUser', 'backend@test.com', 'test')
        self.backend = EmailBackend()
        self.request = RequestFactory().get('/')

    def test_authenticates_by_username(self):
        user = self.backend.authenticate(self.request, username='BackendUser', password='test')
        self.assertEqual(user, self.user)

    def test_authenticates_by_exact_email(self):
        user = self.backend.authenticate(self.request, username='backend@test.com', password='test')
        self.assertEqual(user, self.user)

    def test_email_lookup_is_case_sensitive(self):
        user = self.backend.authenticate(self.request, username='BACKEND@TEST.COM', password='test')
        self.assertIsNone(user)

    def test_invalid_credentials_return_none(self):
        user = self.backend.authenticate(self.request, username='BackendUser', password='wrong')
        self.assertIsNone(user)

    def test_inactive_user_cannot_authenticate(self):
        self.user.is_active = False
        self.user.save()
        user = self.backend.authenticate(self.request, username='BackendUser', password='test')
        self.assertIsNone(user)

    def test_unknown_email_and_missing_username_return_none(self):
        self.assertIsNone(self.backend.authenticate(self.request, username='unknown@test.com', password='test'))
        self.assertIsNone(self.backend.authenticate(self.request, username=None, password='test'))


class PlayerFormTestCase(TestCase):

    def valid_registration_data(self, **overrides):
        data = {
            'username': 'RegisteredUser',
            'email': 'registered@test.com',
            'in_game_name': 'Registered',
            'in_game_id': '100',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        data.update(overrides)
        return data

    def test_registration_form_accepts_valid_data(self):
        form = PlayerRegisterForm(data=self.valid_registration_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_registration_form_requires_email(self):
        form = PlayerRegisterForm(data=self.valid_registration_data(email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_registration_form_has_no_discord_name_field(self):
        form = PlayerRegisterForm(data=self.valid_registration_data(discord_name='typed_by_hand'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('discord_name', form.fields)

    def test_registration_form_rejects_duplicate_email(self):
        Player.objects.create_user('ExistingUser', 'registered@test.com', 'test')
        form = PlayerRegisterForm(data=self.valid_registration_data())
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_profile_form_updates_player(self):
        player = Player.objects.create_user('ProfileUser', 'profile@test.com', 'test',
                                            discord_name='kept_discord')
        form = PlayerProfileEditForm(instance=player, data={
            'username': 'UpdatedProfileUser',
            'email': 'updated-profile@test.com',
            'in_game_name': 'UpdatedProfile',
            'in_game_id': '200',
        })
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertEqual(updated.username, 'UpdatedProfileUser')
        self.assertEqual(updated.discord_name, 'kept_discord')

    def test_login_form_accepts_username(self):
        player = Player.objects.create_user('LoginUser', 'login@test.com', 'test')
        form = PlayerLoginForm(data={'username': player.username, 'password': 'test'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_form_rejects_invalid_password(self):
        Player.objects.create_user('InvalidLogin', 'invalid-login@test.com', 'test')
        form = PlayerLoginForm(data={'username': 'InvalidLogin', 'password': 'wrong'})
        self.assertFalse(form.is_valid())

    def test_password_change_form_rejects_mismatched_passwords(self):
        player = Player.objects.create_user('ChangeFormUser', 'change-form@test.com', 'test')
        form = PlayerPasswordChangeForm(user=player, data={
            'old_password': 'test',
            'new_password1': 'NewStrongPassword123!',
            'new_password2': 'DifferentPassword123!',
        })
        self.assertFalse(form.is_valid())

    def test_password_reset_confirm_form_rejects_mismatched_passwords(self):
        player = Player.objects.create_user('ConfirmFormUser', 'confirm-form@test.com', 'test')
        form = PlayerPasswordResetConfirmForm(user=player, data={
            'new_password1': 'NewStrongPassword123!',
            'new_password2': 'DifferentPassword123!',
        })
        self.assertFalse(form.is_valid())

    def test_password_reset_form_matches_email_case_insensitively(self):
        player = Player.objects.create_user('ResetUser', 'reset@test.com', 'test')
        form = PlayerPasswordResetForm(data={'email': 'RESET@TEST.COM'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(list(form.get_users('RESET@TEST.COM')), [player])

    def test_password_reset_form_excludes_inactive_and_unknown_users(self):
        inactive = Player.objects.create_user('InactiveReset', 'inactive-reset@test.com', 'test')
        inactive.is_active = False
        inactive.save()
        form = PlayerPasswordResetForm()
        self.assertEqual(list(form.get_users('inactive-reset@test.com')), [])
        self.assertEqual(list(form.get_users('unknown-reset@test.com')), [])


class AuthenticationViewTestCase(TestCase):

    def setUp(self):
        self.user = Player.objects.create_user('ViewUser', 'view@test.com', 'test')

    def test_login_by_email(self):
        response = self.client.post(reverse('auth:login'), {
            'username': 'view@test.com',
            'password': 'test',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_authenticated_user_is_redirected_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('auth:login'))
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('auth:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/', response['Location'])

    def test_profile_updates_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:profile'), {
            'username': 'UpdatedViewUser',
            'email': 'updated-view@test.com',
            'discord_name': 'updated_view',
            'in_game_name': 'UpdatedView',
            'in_game_id': '300',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'UpdatedViewUser')

    def test_password_change_requires_login(self):
        response = self.client.get(reverse('auth:password_change'))
        self.assertEqual(response.status_code, 302)

    def test_password_change_updates_password(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:password_change'), {
            'old_password': 'test',
            'new_password1': 'NewStrongPassword123!',
            'new_password2': 'NewStrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPassword123!'))

    def test_api_token_requires_login(self):
        response = self.client.post(reverse('auth:api-token'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Token.objects.exists())

    def test_api_token_is_created_once(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:api-token'))
        self.assertEqual(response.status_code, 302)
        token = Token.objects.get(user=self.user)
        self.client.post(reverse('auth:api-token'))
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Token.objects.get(user=self.user), token)

    def test_profile_hides_existing_token(self):
        token = Token.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse('auth:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, token.key)

    def test_profile_shows_token_only_with_show_token_param(self):
        token = Token.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.get(f"{reverse('auth:profile')}?show_token=1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, token.key)

    def test_api_token_is_displayed_after_generation_redirect(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:api-token'))
        self.assertEqual(response.status_code, 302)
        token = Token.objects.get(user=self.user)
        self.assertIn('show_token=1', response['Location'])
        response = self.client.get(response['Location'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, token.key)

    def test_api_token_message_reports_new_token(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:api-token'), follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('new API token', str(messages[0]))

    def test_api_token_message_reports_existing_token(self):
        Token.objects.create(user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:api-token'), follow=True)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('already existed', str(messages[0]))
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)

    def test_registration_creates_player_and_redirects_to_login(self):
        response = self.client.post(reverse('auth:register'), {
            'username': 'NewRegisteredUser',
            'email': 'new-registered@test.com',
            'in_game_name': 'NewRegistered',
            'in_game_id': '400',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('auth:login'))
        self.assertTrue(Player.objects.filter(username='NewRegisteredUser').exists())


class AuthenticationAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.active = Player.objects.create_user('ActiveApiUser', 'active-api@test.com', 'test', discord_name='active_api')
        self.inactive = Player.objects.create_user('InactiveApiUser', 'inactive-api@test.com', 'test', discord_name='inactive_api')
        self.inactive.is_active = False
        self.inactive.save()

    def test_player_api_lists_active_players_only(self):
        response = self.client.get(reverse('player-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['discord_name'], 'active_api')

    def test_player_registration_api_looks_up_discord_name(self):
        response = self.client.get(reverse('registration-detail', args=('active_api',)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['in_game_name'], self.active.in_game_name)

    def test_player_registration_api_hides_inactive_players(self):
        response = self.client.get(reverse('registration-detail', args=('inactive_api',)))
        self.assertEqual(response.status_code, 404)

    def test_player_api_detail_returns_404_for_unknown_player(self):
        response = self.client.get(reverse('player-detail', args=(999999,)))
        self.assertEqual(response.status_code, 404)

    def test_player_api_is_read_only(self):
        response = self.client.post(reverse('player-list'), {'discord_name': 'new_api'})
        self.assertEqual(response.status_code, 405)

    def test_player_detail_write_methods_are_not_allowed(self):
        url = reverse('player-detail', args=(self.active.pk,))
        self.assertEqual(self.client.patch(url, {'in_game_name': 'Changed'}).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)


@override_settings(DISCORD_CLIENT_ID='test-client-id',
                   DISCORD_CLIENT_SECRET='test-client-secret')
class DiscordLinkingTestCase(TestCase):

    def setUp(self):
        self.user = Player.objects.create_user('DiscordUser', 'discord@test.com', 'test')

    def set_session_state(self, state='valid-state'):
        session = self.client.session
        session['discord_oauth_state'] = state
        session.save()

    def set_session_pending(self, discord_name='verified_user'):
        session = self.client.session
        session['discord_oauth_pending'] = {'discord_name': discord_name}
        session.save()

    @contextmanager
    def discord_api(self, username='verified_user', post_side_effect=None):
        token_response = Mock()
        token_response.raise_for_status.return_value = None
        token_response.json.return_value = {'access_token': 'access-token'}
        user_response = Mock()
        user_response.raise_for_status.return_value = None
        user_response.json.return_value = {'id': '987654321098765432', 'username': username}
        with patch('authentification.discord.requests.post', return_value=token_response,
                   side_effect=post_side_effect) as post_mock, \
             patch('authentification.discord.requests.get', return_value=user_response) as get_mock:
            yield post_mock, get_mock

    def test_connect_redirects_to_discord_authorization(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('auth:discord_connect'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('https://discord.com/oauth2/authorize?'))
        params = parse_qs(urlsplit(response['Location']).query)
        self.assertEqual(params['client_id'], ['test-client-id'])
        self.assertEqual(params['response_type'], ['code'])
        self.assertEqual(params['scope'], ['identify'])
        self.assertEqual(params['redirect_uri'], ['http://testserver/auth/discord/callback/'])
        self.assertEqual(self.client.session['discord_oauth_state'], params['state'][0])

    def test_connect_uses_configured_redirect_uri(self):
        self.client.force_login(self.user)
        with override_settings(DISCORD_REDIRECT_URI='https://rootleague.example/auth/discord/callback/'):
            response = self.client.post(reverse('auth:discord_connect'))
        params = parse_qs(urlsplit(response['Location']).query)
        self.assertEqual(params['redirect_uri'],
                         ['https://rootleague.example/auth/discord/callback/'])

    def test_connect_is_post_only(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('auth:discord_connect')).status_code, 405)

    def test_connect_returns_404_when_not_configured(self):
        self.client.force_login(self.user)
        with override_settings(DISCORD_CLIENT_ID=None, DISCORD_CLIENT_SECRET=None):
            response = self.client.post(reverse('auth:discord_connect'))
        self.assertEqual(response.status_code, 404)

    def test_connect_is_allowed_for_anonymous_users(self):
        response = self.client.post(reverse('auth:discord_connect'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('discord_oauth_state', self.client.session)

    def test_callback_links_discord_account_to_logged_in_player(self):
        self.client.force_login(self.user)
        self.set_session_state()
        with self.discord_api() as (post_mock, get_mock):
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'code': 'auth-code', 'state': 'valid-state'},
                                       follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.discord_name, 'verified_user')
        self.assertNotIn('discord_oauth_state', self.client.session)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('successfully linked' in str(message) for message in messages_list))
        self.assertEqual(post_mock.call_args.kwargs['data']['code'], 'auth-code')
        self.assertEqual(get_mock.call_args.kwargs['headers']['Authorization'],
                         'Bearer access-token')

    def test_callback_rejects_invalid_state(self):
        self.client.force_login(self.user)
        self.set_session_state('valid-state')
        with self.discord_api():
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'code': 'auth-code', 'state': 'forged-state'},
                                       follow=True)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.discord_name)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('failed' in str(message) for message in messages_list))

    def test_callback_handles_discord_api_failure(self):
        self.client.force_login(self.user)
        self.set_session_state()
        with self.discord_api(post_side_effect=requests.ConnectionError('boom')):
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'code': 'auth-code', 'state': 'valid-state'},
                                       follow=True)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.discord_name)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('failed' in str(message) for message in messages_list))

    def test_callback_reports_conflict_and_leaves_player_unchanged(self):
        Player.objects.create_user('OtherUser', 'other@test.com', 'test',
                                   discord_name='verified_user')
        self.client.force_login(self.user)
        self.set_session_state()
        with self.discord_api():
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'code': 'auth-code', 'state': 'valid-state'},
                                       follow=True)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.discord_name)
        messages_list = list(response.context['messages'])
        self.assertTrue(any('contact the administrators' in str(message)
                            for message in messages_list))

    def test_callback_allows_relinking_the_same_discord_name(self):
        self.user.discord_name = 'verified_user'
        self.user.save()
        self.client.force_login(self.user)
        self.set_session_state()
        with self.discord_api():
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'code': 'auth-code', 'state': 'valid-state'},
                                       follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.discord_name, 'verified_user')
        messages_list = list(response.context['messages'])
        self.assertTrue(any('successfully linked' in str(message) for message in messages_list))

    def test_callback_reports_cancellation(self):
        self.client.force_login(self.user)
        self.set_session_state()
        with self.discord_api() as (post_mock, get_mock):
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'error': 'access_denied'}, follow=True)
        post_mock.assert_not_called()
        get_mock.assert_not_called()
        self.user.refresh_from_db()
        self.assertIsNone(self.user.discord_name)

    def test_callback_stores_pending_link_for_anonymous_users(self):
        self.set_session_state()
        with self.discord_api():
            response = self.client.get(reverse('auth:discord_callback'),
                                       {'code': 'auth-code', 'state': 'valid-state'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('auth:register'))
        self.assertEqual(self.client.session['discord_oauth_pending'],
                         {'discord_name': 'verified_user'})