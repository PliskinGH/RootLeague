from decimal import Decimal
from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.http import HttpResponse

from authentification.models import Player
from matchmaking.models import Match, Participant

from .constants import FACTION_CATS, FACTION_BIRDS
from .forms import PlayerInStatsForm
from .admin import TournamentAdmin
from .models import League, Tournament
from .views import get_stats, leaderboard
from .common import get_dropdown_menu, get_league, get_menu_by_pagination, get_title, get_tournament
from .views import faction_stats, stats, turn_order_stats
from .constants import FACTIONS, TURN_ORDERS


class LeagueModelTestCase(TestCase):

	def test_saving_a_default_league_demotes_previous_default(self):
		first = League.objects.create(name='First League', is_default=True)
		second = League.objects.create(name='Second League', is_default=True)
		first.refresh_from_db()
		self.assertFalse(first.is_default)
		self.assertTrue(second.is_default)

	def test_get_default_creates_default_league(self):
		league, created = League.get_default()
		self.assertTrue(created)
		self.assertTrue(league.is_default)
		self.assertEqual(League.objects.filter(is_default=True).count(), 1)

	def test_get_default_reuses_existing_default_league(self):
		league = League.objects.create(name='Existing Default', is_default=True)
		result, created = League.get_default()
		self.assertFalse(created)
		self.assertEqual(result, league)

	def test_get_default_tournament_creates_active_season(self):
		league = League.objects.create(name='Default League', is_default=True)
		tournament, created = Tournament.get_default()
		self.assertTrue(created)
		league.refresh_from_db()
		self.assertEqual(tournament.league, league)
		self.assertEqual(league.active_season, tournament)
		self.assertEqual(Tournament.get_default_pk(), tournament.pk)

	def test_tournament_defaults_to_no_coalition_setting(self):
		tournament = Tournament.objects.create(name='Coalition Tournament', coalition_allowed=True)
		self.assertTrue(tournament.three_coalition_allowed)

	def test_tournament_string_uses_name(self):
		tournament = Tournament.objects.create(name='Named Tournament')
		self.assertEqual(str(tournament), 'Named Tournament')

	def test_existing_active_season_is_reused_as_default_tournament(self):
		league = League.objects.create(name='Season League', is_default=True)
		season = Tournament.objects.create(name='Existing Season', league=league)
		league.active_season = season
		league.save()
		tournament, created = Tournament.get_default()
		self.assertFalse(created)
		self.assertEqual(tournament, season)


class LeagueCommonTestCase(TestCase):

	def setUp(self):
		self.league = League.objects.create(name='Common League', is_default=True, visibility=True)
		self.tournament = Tournament.objects.create(
			name='Common Tournament', league=self.league, visibility=True,
		)

	def test_get_helpers_return_valid_objects_and_default_fallbacks(self):
		self.assertEqual(get_league(self.league.pk), self.league)
		self.assertEqual(get_tournament(self.tournament.pk), self.tournament)
		self.assertEqual(get_league(999999).is_default, True)
		self.assertIsNotNone(get_tournament(999999))

	def test_get_title_prefers_league_then_tournament_then_default(self):
		self.assertEqual(get_title(league=self.league, tournament=self.tournament), self.league.name)
		self.assertEqual(get_title(tournament=self.tournament), self.tournament.name)
		self.assertEqual(get_title(), 'All games')

	def test_menu_infers_league_from_tournament(self):
		menu = get_menu_by_pagination(tournament=self.tournament)
		self.assertEqual(menu['league'], self.league)
		self.assertIn(self.tournament, menu['seasons'])

	def test_dropdown_excludes_hidden_seasons(self):
		hidden = Tournament.objects.create(name='Hidden Common', league=self.league, visibility=False)
		menu = get_dropdown_menu(league=self.league)
		self.assertIn(self.tournament, menu['seasons'])
		self.assertNotIn(hidden, menu['seasons'])


class LeagueStatsWrapperTestCase(TestCase):

	def setUp(self):
		self.request = RequestFactory().get('/league/')
		self.request.user = self.client.session.get('_auth_user_id') or None

	def test_stats_builds_default_context(self):
		with patch('league.views.ImprovedListView.as_view', return_value=lambda request: HttpResponse(status=204)) as as_view:
			stats(self.request, rows=[('a', 'A')], field='faction')
		context = as_view.call_args.kwargs['extra_context']
		self.assertEqual(context['stats_title'], 'Stats')
		self.assertEqual(context['stats_name'], '')

	def test_stats_uses_named_stats_context(self):
		with patch('league.views.ImprovedListView.as_view', return_value=lambda request: HttpResponse(status=204)) as as_view:
			stats(self.request, rows=[('a', 'A')], field='faction', stats_name='Faction')
		context = as_view.call_args.kwargs['extra_context']
		self.assertEqual(context['stats_title'], 'Faction stats')

	def test_turn_order_stats_truncates_requested_player_count(self):
		with patch('league.views.stats') as stats_view:
			turn_order_stats(self.request, max_number_players=3)
		self.assertEqual(len(stats_view.call_args.kwargs['rows']), 3)

	def test_turn_order_stats_keeps_all_rows_for_nonpositive_limit(self):
		with patch('league.views.stats') as stats_view:
			turn_order_stats(self.request, max_number_players=0)
		self.assertEqual(len(stats_view.call_args.kwargs['rows']), len(TURN_ORDERS))


class LeagueFormTestCase(TestCase):

	def setUp(self):
		self.league = League.objects.create(name='Form League')
		self.tournament = Tournament.objects.create(name='Form Tournament', league=self.league)

	def test_player_stats_form_player_is_optional(self):
		form = PlayerInStatsForm(data={})
		self.assertTrue(form.is_valid())
		self.assertIsNone(form.cleaned_data['player'])


class LeagueStatsTestCase(TestCase):

	def setUp(self):
		self.league = League.objects.create(name='Stats League')
		self.tournament = Tournament.objects.create(name='Stats Tournament', league=self.league)
		self.player = Player.objects.create_user('StatsUser', 'stats@test.com', 'test')
		self.other_player = Player.objects.create_user('OtherStatsUser', 'other-stats@test.com', 'test')
		self.match = Match.objects.create(
			title='Stats match', tournament=self.tournament,
			date_closed='2026-01-01T00:00:00Z',
		)
		Participant.objects.create(
			match=self.match, player=self.player, faction=FACTION_CATS,
			tournament_score=Decimal('5.00'), game_score=30,
		)
		Participant.objects.create(
			match=self.match, player=self.other_player, faction=FACTION_BIRDS,
			tournament_score=Decimal('0.00'), game_score=20,
		)

	def test_get_stats_calculates_score_and_relative_score(self):
		stats = get_stats(
			rows=[(FACTION_CATS, 'Cats'), (FACTION_BIRDS, 'Birds')],
			field='faction',
			tournament=self.tournament,
		)
		self.assertEqual(stats[FACTION_CATS]['total'], 1)
		self.assertEqual(stats[FACTION_CATS]['score'], Decimal('5'))
		self.assertEqual(stats[FACTION_CATS]['relative_score'], Decimal('500'))
		self.assertEqual(stats[FACTION_BIRDS]['score'], Decimal('0'))

	def test_get_stats_calculates_game_score_average(self):
		stats = get_stats(
			rows=[(FACTION_CATS, 'Cats'), (FACTION_BIRDS, 'Birds')],
			field='faction',
			tournament=self.tournament,
			with_game_score=True,
		)
		self.assertEqual(stats[FACTION_CATS]['average_game_score'], Decimal('30'))
		self.assertEqual(stats[FACTION_CATS]['total_with_game_score'], 1)

	def test_get_stats_supports_summed_totals(self):
		stats = get_stats(
			rows=[(FACTION_CATS, 'Cats'), (FACTION_BIRDS, 'Birds')],
			field='faction',
			tournament=self.tournament,
			totals=[('all', 'All factions', [FACTION_CATS, FACTION_BIRDS])],
		)
		self.assertEqual(stats['all']['total'], 2)
		self.assertEqual(stats['all']['score'], Decimal('5'))
		self.assertEqual(stats['all']['relative_score'], Decimal('250'))

	def test_get_stats_returns_empty_for_missing_input(self):
		self.assertEqual(get_stats(), {})
		self.assertEqual(get_stats(rows=[], field='faction'), {})

	def test_get_stats_excludes_open_matches_by_default(self):
		open_match = Match.objects.create(title='Open match', tournament=self.tournament)
		Participant.objects.create(
			match=open_match, player=self.player, faction=FACTION_CATS,
			tournament_score=Decimal('4.00'),
		)
		stats = get_stats(rows=[(FACTION_CATS, 'Cats')], field='faction')
		self.assertEqual(stats[FACTION_CATS]['score'], Decimal('5'))

	def test_get_stats_handles_invalid_fields_and_empty_totals(self):
		self.assertEqual(get_stats(rows=[('x', 'X')], field='not_a_field'), {})
		stats = get_stats(
			rows=[('missing', 'Missing')], field='faction', tournament=self.tournament,
			totals=[('all', 'All', ['missing'])],
		)
		self.assertIsNone(stats['missing']['score'])
		self.assertIsNone(stats['all']['score'])

	def test_get_stats_excludes_dominance_from_game_score_average(self):
		dominance_match = Match.objects.create(
			title='Dominance match', tournament=self.tournament,
			date_closed='2026-01-02T00:00:00Z',
		)
		Participant.objects.create(
			match=dominance_match, player=self.player, faction=FACTION_CATS,
			dominance='bird', game_score=30, tournament_score=Decimal('5.00'),
		)
		stats = get_stats(
			rows=[(FACTION_CATS, 'Cats')], field='faction',
			tournament=self.tournament, with_game_score=True,
		)
		self.assertEqual(stats[FACTION_CATS]['total_with_game_score'], 1)


class LeagueViewTestCase(TestCase):

	def setUp(self):
		self.league = League.objects.create(name='View League', is_default=True)
		self.tournament = Tournament.objects.create(
			name='View Tournament', league=self.league, visibility=True, min_games=1,
		)
		self.player = Player.objects.create_user('ViewPlayer', 'view-player@test.com', 'test')
		self.match = Match.objects.create(
			title='Leaderboard match', tournament=self.tournament,
			date_closed='2026-01-01T00:00:00Z',
		)
		Participant.objects.create(
			match=self.match, player=self.player, faction=FACTION_CATS,
			tournament_score=Decimal('5.00'),
		)

	def test_leaderboard_passes_visible_closed_matches_to_list_view(self):
		request = RequestFactory().get(reverse('league:tournament_leaderboard', args=(self.tournament.pk,)))
		request.user = self.player
		with patch('league.views.ImprovedListView.as_view', return_value=lambda request: HttpResponse(status=204)) as as_view:
			leaderboard(request, tournament=self.tournament, number_per_page=10)
		queryset = as_view.call_args.kwargs['queryset']
		self.assertIn(self.player, queryset)

	def test_leaderboard_filters_players_below_default_minimum_games(self):
		request = RequestFactory().get(reverse('league:global_leaderboard'))
		request.user = self.player
		with patch('league.views.ImprovedListView.as_view', return_value=lambda request: HttpResponse(status=204)) as as_view:
			leaderboard(request, number_per_page=10)
		queryset = as_view.call_args.kwargs['queryset']
		self.assertNotIn(self.player, queryset)

	def test_league_and_tournament_routes_reverse(self):
		self.assertEqual(reverse('league:default_leaderboard'), '/league/')
		self.assertEqual(reverse('league:league_leaderboard', args=(self.league.pk,)), f'/league/{self.league.pk}/')
		self.assertEqual(reverse('league:tournament_leaderboard', args=(self.tournament.pk,)), f'/league/tournament/{self.tournament.pk}/')

	def test_tournament_admin_ignores_invalid_league_query_parameter(self):
		request = RequestFactory().get('/admin/league/tournament/add/?league=invalid')
		initial = TournamentAdmin(Tournament, None).get_changeform_initial_data(request)
		self.assertNotIn('league', initial)

# Create your tests here.
