from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from rest_framework.test import APIClient

from . import models
from .forms import MatchForm, ParticipantForm, ParticipantFormSet, UpdateMatchForm
from .filters import MatchFilter, MatchDRFFilter, ParticipantFilter
from .serializers import CoalitionedPlayerField, MatchSerializer, TournamentField
from .views import MatchDetailView, listing
from authentification.models import Player
from league.models import Tournament
from league.constants import MAP_WINTER

# Create your tests here.

class MatchModelTestCase(TestCase):

    def setUp(self):
        self.user = Player.objects.create_user('ModelUser', 'model@test.com', 'test')
        self.other_user = Player.objects.create_user('OtherModelUser', 'other-model@test.com', 'test')
        self.match = models.Match.objects.create(submitted_by=self.user)

    def test_submitter_can_edit_an_open_match(self):
        self.assertTrue(self.match.is_editable_by(self.user))

    def test_participant_can_edit_an_open_match(self):
        participant = models.Participant.objects.create(match=self.match, player=self.other_user)
        self.assertTrue(self.match.is_editable_by(self.other_user))
        participant.delete()

    def test_unrelated_user_cannot_edit(self):
        self.assertFalse(self.match.is_editable_by(self.other_user))

    def test_anonymous_user_cannot_edit(self):
        self.assertFalse(self.match.is_editable_by(None))

    def test_old_closed_match_cannot_be_edited(self):
        self.match.date_closed = timezone.now() - timedelta(days=30)
        self.match.save()
        self.assertFalse(self.match.is_editable_by(self.user))


class MatchFormTestCase(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name='Form Tournament')

    def test_open_match_can_be_submitted_with_minimal_data(self):
        form = MatchForm(data={
            'title': 'Open match',
            'tournament': self.tournament.pk,
            'closed': '',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_closed_match_requires_result_fields(self):
        form = MatchForm(data={
            'title': 'Closed match',
            'tournament': self.tournament.pk,
            'closed': 'on',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('game_setup', form.errors)
        self.assertIn('board_map', form.errors)
        self.assertIn('deck', form.errors)
        self.assertIn('turn_timing', form.errors)

    def test_winter_match_requires_random_suits(self):
        form = MatchForm(data={
            'title': 'Winter match',
            'tournament': self.tournament.pk,
            'board_map': MAP_WINTER,
            'random_suits': '',
            'closed': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('random_suits', form.errors)

    def test_duplicate_hirelings_are_rejected(self):
        hireling = models.HIRELINGS[0][0]
        form = MatchForm(data={
            'title': 'Duplicate hireling match',
            'tournament': self.tournament.pk,
            'hirelings': [hireling, hireling],
            'closed': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('hirelings', form.errors)

    def test_update_form_opens_open_match_by_default(self):
        match = models.Match.objects.create(tournament=self.tournament)
        form = UpdateMatchForm(instance=match)
        self.assertFalse(form.fields['closed'].initial)


class ParticipantFormTestCase(TestCase):

    def setUp(self):
        self.active_player = Player.objects.create_user('ActivePlayer', 'active@test.com', 'test')
        self.inactive_player = Player.objects.create_user('InactivePlayer', 'inactive@test.com', 'test')
        self.inactive_player.is_active = False
        self.inactive_player.save()

    def test_only_active_players_are_selectable(self):
        form = ParticipantForm()
        self.assertIn(self.active_player, form.fields['player'].queryset)
        self.assertNotIn(self.inactive_player, form.fields['player'].queryset)


class ParticipantFormSetTestCase(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name='Participant Tournament')
        self.match = models.Match.objects.create(tournament=self.tournament)
        self.player_one = Player.objects.create_user('FormsetOne', 'formset-one@test.com', 'test')
        self.player_two = Player.objects.create_user('FormsetTwo', 'formset-two@test.com', 'test')
        self.formset_class = inlineformset_factory(
            models.Match,
            models.Participant,
            form=ParticipantForm,
            formset=ParticipantFormSet,
            fields=('turn_order', 'player', 'faction', 'game_score', 'dominance', 'tournament_score'),
            extra=0,
        )

    def formset(self, rows, closed=True):
        data = {
            'participants-TOTAL_FORMS': str(len(rows)),
            'participants-INITIAL_FORMS': '0',
            'participants-MIN_NUM_FORMS': '0',
            'participants-MAX_NUM_FORMS': '6',
        }
        if closed:
            data['closed'] = 'on'
        for index, row in enumerate(rows):
            for field, value in row.items():
                data[f'participants-{index}-{field}'] = value
        return self.formset_class(data=data, instance=self.match, prefix='participants')

    def test_closed_participant_requires_player_faction_and_score(self):
        formset = self.formset([{'turn_order': '1'}])
        self.assertFalse(formset.is_valid())
        self.assertTrue(any(error.code == 'error_required_splayer' for error in formset.non_form_errors().data))
        self.assertTrue(any(error.code == 'error_required_faction' for error in formset.non_form_errors().data))
        self.assertTrue(any(error.code == 'error_required_score' for error in formset.non_form_errors().data))

    def test_closed_participants_must_have_unique_players_and_factions(self):
        formset = self.formset([
            {'turn_order': '1', 'player': self.player_one.pk, 'faction': models.FACTION_CATS, 'tournament_score': '5'},
            {'turn_order': '2', 'player': self.player_one.pk, 'faction': models.FACTION_CATS, 'tournament_score': '0'},
        ])
        self.assertFalse(formset.is_valid())
        error_codes = {error.code for error in formset.non_form_errors().data}
        self.assertIn('error_players', error_codes)
        self.assertIn('error_factions', error_codes)

    def test_game_score_cannot_be_combined_with_dominance(self):
        formset = self.formset([{
            'turn_order': '1',
            'player': self.player_one.pk,
            'faction': models.FACTION_CATS,
            'game_score': '30',
            'dominance': models.SUIT_BIRD,
            'tournament_score': '5',
        }])
        self.assertFalse(formset.is_valid())
        self.assertIn('error_score_dom', {error.code for error in formset.non_form_errors().data})

    def test_tournament_minimum_player_limit_is_enforced(self):
        self.tournament.min_players_per_game = 2
        self.tournament.save()
        formset = self.formset([{
            'turn_order': '1',
            'player': self.player_one.pk,
            'faction': models.FACTION_CATS,
            'game_score': '30',
            'tournament_score': '5',
        }])
        self.assertFalse(formset.is_valid())
        self.assertIn('error_min_nb', {error.code for error in formset.non_form_errors().data})


class MatchSerializerTestCase(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name='Serializer Tournament')
        self.player = Player.objects.create_user('SerializerPlayer', 'serializer@test.com', 'test')
        self.match = models.Match.objects.create(tournament=self.tournament, submitted_by=self.player)
        self.participant = models.Participant.objects.create(match=self.match, player=self.player)

    def test_tournament_and_player_representations_are_strings(self):
        self.assertEqual(TournamentField(read_only=True).to_representation(self.tournament), str(self.tournament))
        self.assertEqual(CoalitionedPlayerField().to_representation(self.participant), str(self.player))
        self.participant.player = None
        self.assertIsNone(CoalitionedPlayerField().to_representation(self.participant))

    def test_serializer_update_without_participants_preserves_existing_rows(self):
        serializer = MatchSerializer(instance=self.match, data={'title': 'Renamed'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(self.match.participants.count(), 1)

    def test_serializer_represents_player_id_and_discord_username(self):
        data = MatchSerializer(self.match).data
        participant = data['participants'][0]
        self.assertEqual(participant['player_id'], self.player.pk)
        self.assertEqual(participant['discord_username'], self.player.discord_name)


class MatchFilterTestCase(TestCase):

    def setUp(self):
        self.tournament = Tournament.objects.create(name='Filter Tournament')
        self.open_match = models.Match.objects.create(title='Open filter match', tournament=self.tournament)
        self.closed_match = models.Match.objects.create(
            title='Closed filter match', tournament=self.tournament,
            date_closed='2026-01-01T00:00:00Z',
        )
        self.player = Player.objects.create_user('FilterPlayer', 'filter@test.com', 'test')
        models.Participant.objects.create(match=self.open_match, player=self.player, faction=models.FACTION_CATS)
        models.Participant.objects.create(match=self.closed_match, player=self.player, faction=models.FACTION_CATS)

    def test_match_filter_closed_true_and_false(self):
        closed = MatchFilter({'closed': 'true'}, queryset=models.Match.objects.all()).qs
        open_matches = MatchFilter({'closed': 'false'}, queryset=models.Match.objects.all()).qs
        self.assertIn(self.closed_match, closed)
        self.assertNotIn(self.open_match, closed)
        self.assertIn(self.open_match, open_matches)
        self.assertNotIn(self.closed_match, open_matches)

    def test_participant_filter_by_player(self):
        filtered = ParticipantFilter({'player': [self.player.pk]}, queryset=models.Participant.objects.all()).qs
        self.assertEqual(filtered.count(), 2)

    def test_drf_filter_by_tournament_name(self):
        filtered = MatchDRFFilter({'tournament__name': 'Filter'}, queryset=models.Match.objects.all()).qs
        self.assertCountEqual(filtered, [self.open_match, self.closed_match])


class MatchHtmlAccessTestCase(TestCase):

    def setUp(self):
        self.user = Player.objects.create_user('HtmlUser', 'html@test.com', 'test')
        self.other_user = Player.objects.create_user('OtherHtmlUser', 'other-html@test.com', 'test')
        self.tournament = Tournament.objects.create(name='HTML Tournament')
        self.match = models.Match.objects.create(
            title='HTML match', tournament=self.tournament, submitted_by=self.user,
        )

    def test_anonymous_registration_redirects_to_login(self):
        response = self.client.get(reverse('match:register'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/auth/?next=/match/register/')

    def test_anonymous_update_redirects_to_login(self):
        response = self.client.get(reverse('match:update', args=(self.match.pk,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/auth/?next=/match/update/{self.match.pk}/')

    def test_anonymous_delete_redirects_to_login(self):
        response = self.client.get(reverse('match:delete', args=(self.match.pk,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], f'/auth/?next=/match/delete/{self.match.pk}/')

    def test_other_user_cannot_update_match(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('match:update', args=(self.match.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_other_user_cannot_delete_match(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('match:delete', args=(self.match.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_submitter_can_delete_match(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('match:delete', args=(self.match.pk,)), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('match:submissions'))
        self.assertFalse(models.Match.objects.filter(pk=self.match.pk).exists())

    def test_detail_context_marks_editable_match(self):
        request = RequestFactory().get(reverse('match:detail', args=(self.match.pk,)))
        request.user = self.user
        view = MatchDetailView()
        view.request = request
        view.object = self.match
        context = view.get_context_data()
        self.assertTrue(context['display_edit'])


class MatchListingTestCase(TestCase):

    def setUp(self):
        self.user = Player.objects.create_user('ListingUser', 'listing@test.com', 'test')
        self.tournament = Tournament.objects.create(name='Visible Tournament', visibility=True)
        self.hidden_tournament = Tournament.objects.create(name='Hidden Tournament', visibility=False)
        self.visible_match = models.Match.objects.create(
            title='Visible match', tournament=self.tournament, submitted_by=self.user,
        )
        models.Participant.objects.create(match=self.visible_match, player=self.user)
        self.hidden_match = models.Match.objects.create(
            title='Hidden match', tournament=self.hidden_tournament, submitted_by=self.user,
        )

    def test_listing_filters_invisible_tournaments(self):
        request = RequestFactory().get(reverse('match:listing'))
        request.user = self.user
        with patch('matchmaking.views.ImprovedListView.as_view', return_value=lambda request: HttpResponse(status=204)) as as_view:
            listing(request)
        queryset = as_view.call_args.kwargs['queryset']
        self.assertIn(self.visible_match, queryset)
        self.assertNotIn(self.hidden_match, queryset)

    def test_submitted_listing_uses_current_user(self):
        request = RequestFactory().get(reverse('match:submissions'))
        request.user = self.user
        with patch('matchmaking.views.ImprovedListView.as_view', return_value=lambda request: HttpResponse(status=204)) as as_view:
            listing(request, submitted_by=self.user)
        queryset = as_view.call_args.kwargs['queryset']
        self.assertIn(self.visible_match, queryset)
        self.assertNotIn(self.hidden_match, queryset)

class MatchApiTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Player.objects.create_user('ApiUser', 'api@test.com', 'test')
        self.other_user = Player.objects.create_user('OtherUser', 'other@test.com', 'test')
        self.tournament = Tournament.objects.create(name='API Tournament')
        permissions = Permission.objects.filter(
            content_type__app_label='matchmaking',
            codename__in=('drf_add_match', 'drf_change_match', 'drf_delete_match'),
        )
        self.user.user_permissions.add(*permissions)

    def test_create_requires_add_permission(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(reverse('match-list'), {
            'title': 'API match',
            'tournament': self.tournament.pk,
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_sets_submitter(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('match-list'), {
            'title': 'API match',
            'tournament': self.tournament.pk,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        match = models.Match.objects.get(title='API match')
        self.assertEqual(match.submitted_by, self.user)

    def test_create_uses_default_tournament(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('match-list'), {
            'title': 'API default tournament match',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        match = models.Match.objects.get(title='API default tournament match')
        self.assertEqual(match.tournament_id, Tournament.get_default_pk())

    def test_create_accepts_participants_by_discord_username(self):
        player = Player.objects.create_user('ParticipantUser', 'participant@test.com', 'test')
        player.discord_name = 'participant'
        player.save()
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('match-list'), {
            'title': 'API participants match',
            'tournament': self.tournament.pk,
            'participants': [{'discord_username': 'participant'}],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        match = models.Match.objects.get(title='API participants match')
        self.assertEqual(match.participants.get().player, player)

    def test_update_accepts_participants_by_discord_username(self):
        player = Player.objects.create_user('ParticipantUser', 'participant@test.com', 'test')
        player.discord_name = 'participant'
        player.save()
        match = models.Match.objects.create(
            title='API participants match',
            tournament=self.tournament,
            submitted_by=self.user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse('match-detail', args=(match.pk,)),
            {'participants': [{'discord_username': 'participant'}]},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(match.participants.get().player, player)

    def test_update_requires_editable_match(self):
        match = models.Match.objects.create(
            title='API match',
            tournament=self.tournament,
            submitted_by=self.other_user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse('match-detail', args=(match.pk,)),
            {'title': 'Updated API match'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_update_allowed_for_submitter_with_change_permission(self):
        match = models.Match.objects.create(
            title='API match',
            tournament=self.tournament,
            submitted_by=self.user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse('match-detail', args=(match.pk,)),
            {'title': 'Updated API match'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        match.refresh_from_db()
        self.assertEqual(match.title, 'Updated API match')

    def test_delete_requires_delete_permission(self):
        match = models.Match.objects.create(
            title='API match',
            tournament=self.tournament,
            submitted_by=self.user,
        )
        self.client.force_authenticate(self.other_user)
        response = self.client.delete(reverse('match-detail', args=(match.pk,)))
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('match-detail', args=(match.pk,)))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(models.Match.objects.filter(pk=match.pk).exists())

    def test_open_matches_are_visible_to_change_permission_users(self):
        models.Match.objects.create(title='Open API match', tournament=self.tournament)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.force_authenticate(self.other_user)
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_open_matches_are_visible_to_delete_permission_users(self):
        delete_user = Player.objects.create_user('DeleteUser', 'delete@test.com', 'test')
        delete_permission = Permission.objects.get(
            content_type__app_label='matchmaking',
            codename='drf_delete_match',
        )
        delete_user.user_permissions.add(delete_permission)
        models.Match.objects.create(title='Open API match', tournament=self.tournament)

        self.client.force_authenticate(delete_user)
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)