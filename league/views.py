from django.db.models import Sum, Count, Q, F
from django.utils.translation import gettext_lazy as _
from django.core.validators import EMPTY_VALUES
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from django.core.exceptions import FieldDoesNotExist

from decimal import Decimal

from .models import League, Tournament
from .forms import PlayerInStatsForm
from authentification.models import Player
from matchmaking.models import Participant
from misc.views import SearchableElidedListView
from .constants import FACTIONS, TURN_ORDERS, VAGABOND

# Create your views here.

def leaderboard(request,
                league = None,
                tournament = None,
                players = None,
                title = None,
                ordering = None,
                number_per_page = 15):
    if (league in EMPTY_VALUES and
        tournament not in EMPTY_VALUES):
        league = tournament.league

    min_games = 1
    if (players is None):
        players = Player.objects.filter(is_active=True)
    if (tournament not in EMPTY_VALUES):
        players = players.annotate(total=Count('participations', distinct=True,
                                               filter=~Q(participations__match__date_closed=None) &
                                                       Q(participations__match__tournament=tournament)))
        if (tournament.min_games not in EMPTY_VALUES):
            min_games = max(tournament.min_games, min_games)
    elif (league not in EMPTY_VALUES):
        players = players.annotate(total=Count('participations', distinct=True, 
                                               filter=~Q(participations__match__date_closed=None) &
                                                       Q(participations__match__tournament__league=league)))
        if (league.min_games not in EMPTY_VALUES):
            min_games = max(league.min_games, min_games)
    else:
        players = players.annotate(total=Count('participations', distinct=True,
                                               filter=~Q(participations__match__date_closed=None)))
    players = players.exclude(Q(total=None) | Q(total__lt=min_games))

    if (tournament not in EMPTY_VALUES):
        players = players.annotate(score=Sum('participations__tournament_score',
                                             filter=~Q(participations__match__date_closed=None) &
                                                     Q(participations__match__tournament=tournament)))
    elif (league not in EMPTY_VALUES):
        players = players.annotate(score=Sum('participations__tournament_score',
                                             filter=~Q(participations__match__date_closed=None) &
                                                     Q(participations__match__tournament__league=league)))
    else:
        players = players.annotate(score=Sum('participations__tournament_score',
                                             filter=~Q(participations__match__date_closed=None)))
    players = players.exclude(Q(score=None) | Q(score__lt=1))

    players = players.annotate(relative_score=F('score')/F('total')*100)

    if (title in EMPTY_VALUES):
        title = get_title(tournament=tournament,
                          league=league)
    
    extra_context = get_dropdown_menu(tournament=tournament,
                                      league=league)
    extra_context['min_games'] = min_games
    extra_context['global_url'] = 'league:global_leaderboard'

    if (ordering is None):
        ordering = ['-relative_score', '-score', '-total']
    ordering += ['in_game_name', 'in_game_id', 'pk']
    
    return SearchableElidedListView.as_view(model=Player,
                                            queryset=players,
                                            template_name='league/leaderboard.html',
                                            paginate_by=number_per_page,
                                            title=title,
                                            ordering=ordering,
                                            extra_context=extra_context
                                           )(request)

def league_leaderboard(request,
                       league_id = None,
                       ordering = None,
                       number_per_page = 15):
    league = get_league(league_id)
    return leaderboard(request, league=league,
                       ordering=ordering,
                       number_per_page=number_per_page)

def tournament_leaderboard(request,
                           tournament_id = None,
                           ordering = None,
                           number_per_page = 15):
    tournament = get_tournament(tournament_id)
    return leaderboard(request, tournament=tournament,
                       ordering=ordering,
                       number_per_page=number_per_page)

def get_stats(rows = None,
              field = None,
              tournament = None,
              league = None,
              player = None,
              totals = [],
              with_game_score = False):
    stats = {}
    if (field in EMPTY_VALUES or rows in EMPTY_VALUES):
        return stats
    
    participations_manager = None
    if (player is not None):
        participations_manager = player.participations
    if (participations_manager is None):
        participations_manager = Participant.objects
    all_participations = participations_manager.exclude(match__date_closed=None)
    if (tournament not in EMPTY_VALUES):
        all_participations = all_participations.filter(match__tournament=tournament)
    elif (league not in EMPTY_VALUES):
        all_participations = all_participations.filter(match__tournament__league=league)
    try:
        for (row, row_name) in rows:
            participations = all_participations.filter(**{field : row})
            total = participations.count()
            if (total < 1):
                row_stats = dict(total=total,
                                 score=None,
                                 relative_score=None,
                                 total_with_game_score=None,
                                 game_score=None,
                                 average_game_score=None)
            else:
                row_stats = participations.exclude(tournament_score=None) \
                                          .aggregate(score=Sum('tournament_score', default=0))
                row_stats['total'] = total
                row_stats['relative_score'] = row_stats['score'] / total * 100
                if (with_game_score):
                    row_game_score_stats = \
                        participations.exclude(Q(game_score=None) | (~Q(dominance=None) & ~Q(dominance="")) | ~Q(coalition=None)) \
                                      .aggregate(total_with_game_score=Count('id'), game_score=Sum('game_score', default=0))
                    row_stats.update(row_game_score_stats)
                    if (row_stats['total_with_game_score'] < 1):
                        row_stats['average_game_score'] = None
                    else:
                        row_stats['average_game_score'] = row_stats['game_score'] / row_stats['total_with_game_score']
            row_stats['name'] = row_name
            stats[row] = row_stats
        for total_key, total_name, summed_rows in totals:
            total = 0
            score = Decimal(0)
            relative_score = Decimal(0)
            total_with_game_score = 0
            game_score = Decimal(0)
            average_game_score = Decimal(0)
            for row in summed_rows:
                total += stats[row]['total']
                if (stats[row]['score'] is not None):
                    score += stats[row]['score']
                if (with_game_score):
                    if (stats[row]['total_with_game_score'] is not None):
                        total_with_game_score += stats[row]['total_with_game_score']
                    if (stats[row]['game_score'] is not None):
                        game_score += stats[row]['game_score']
            if (total >= 1):
                relative_score = score / total * 100
            else:
                score = None
                relative_score = None
            if (total_with_game_score >= 1):
                average_game_score = game_score / total_with_game_score
            else:
                game_score = None
                average_game_score = None
            row_stats = dict(name=total_name,
                             total=total,
                             score=score,
                             relative_score=relative_score,
                             total_with_game_score=total_with_game_score,
                             game_score=game_score,
                             average_game_score=average_game_score)
            stats[total_key] = row_stats
    except (AttributeError, FieldDoesNotExist):
        stats = {}
    return stats

def stats(request,
          league = None,
          tournament = None,
          title = None,
          rows = None,
          field = None,
          stats_name = None,
          totals = [],
          with_game_score = False):
    if (league in EMPTY_VALUES and
        tournament not in EMPTY_VALUES):
        league = tournament.league
        
    player_id = request.GET.get('player', None)
    players = None
    if (player_id not in EMPTY_VALUES):
        players = Player.objects.filter(id=int(player_id))
    player = None
    if (players not in EMPTY_VALUES and len(players) == 1):
        player = players[0]
    
    player_form = PlayerInStatsForm(dict(player=player))

    stats = get_stats(rows=rows,
                      field=field,
                      tournament=tournament,
                      league=league,
                      player=player,
                      totals=totals,
                      with_game_score=with_game_score)
    cleaned_stats = []
    for row in stats.values():
        total = row.get('total', 0)
        if (total >= 1):
            cleaned_stats.append(row)

    if (title in EMPTY_VALUES):
        title = get_title(tournament=tournament,
                          league=league)
        
    extra_context = get_dropdown_menu(tournament=tournament,
                                      league=league)
    
    extra_context['player'] = None
    extra_context['player_get_param'] = ""
    extra_context['player_form'] = player_form
    if (player not in EMPTY_VALUES):
        extra_context['player'] = player
        extra_context['player_get_param'] = "?player=" + str(player.id)
    
    extra_context['stats'] = cleaned_stats
    extra_context['title'] = title
    if (stats_name in EMPTY_VALUES):
        extra_context['stats_title'] = _("Stats")
        extra_context['stats_name'] = ""
    else:
        extra_context['stats_title'] = stats_name + " " + _("stats")
        extra_context['stats_name'] = stats_name
    extra_context['with_game_score'] = with_game_score

    extra_context['league_url'] = 'league:league_' + field + '_stats'
    extra_context['tournament_url'] = 'league:tournament_' + field + '_stats'
    extra_context['global_url'] = 'league:global_' + field + '_stats'

    return TemplateView.as_view(template_name='league/stats.html',
                                extra_context=extra_context
                                )(request)

def faction_stats(request,
                  league = None,
                  tournament = None,
                  title = None):
    all_vagabonds = [key for (key, _) in FACTIONS if VAGABOND in key]
    all_factions = [key for (key, _) in FACTIONS]
    totals = []
    totals.append(('vb_total', _('All Vagabonds'), all_vagabonds))
    totals.append(('factions_total', _('All Factions'), all_factions))
    return stats(request,
                 league=league,
                 tournament=tournament,
                 title=title,
                 rows=FACTIONS,
                 field='faction',
                 stats_name=_('Faction'),
                 totals=totals,
                 with_game_score=True)

def tournament_faction_stats(request,
                             tournament_id = None):
    tournament = get_tournament(tournament_id)
    return faction_stats(request, tournament=tournament)

def league_faction_stats(request,
                         league_id = None):
    league = get_league(league_id)
    return faction_stats(request, league=league)

def turn_order_stats(request,
                     league = None,
                     tournament = None,
                     max_number_players = None,
                     title = None):
    turn_orders_list = TURN_ORDERS
    if (max_number_players is not None
        and max_number_players >= 1
        and max_number_players < len(turn_orders_list)):
        turn_orders_list = turn_orders_list[:max_number_players]
    return stats(request,
                 league=league,
                 tournament=tournament,
                 title=title,
                 rows=turn_orders_list,
                 field='turn_order',
                 stats_name=_('Turn order'))

def tournament_turn_order_stats(request,
                                tournament_id = None):
    tournament = get_tournament(tournament_id)
    max_number_players = None
    if (tournament is not None):
        max_number_players = tournament.max_players_per_game
    return turn_order_stats(request, tournament=tournament,
                            max_number_players=max_number_players)

def league_turn_order_stats(request,
                            league_id = None):
    league = get_league(league_id)
    max_number_players = None
    if (league is not None):
        max_number_players = league.max_players_per_game
    return turn_order_stats(request, league=league,
                            max_number_players=max_number_players)

def get_tournament(tournament_id = None):
    tournaments = None
    tournament = None
    if (tournament_id not in EMPTY_VALUES):
        tournaments = Tournament.objects.filter(id=tournament_id)
    if (tournaments not in EMPTY_VALUES and len(tournaments) == 1):
        tournament = tournaments.first()
    if (tournament in EMPTY_VALUES):
        tournament, _ = Tournament.get_default()
    return tournament

def get_league(league_id = None):
    leagues = None
    league = None
    if (league_id not in EMPTY_VALUES):
        leagues = League.objects.filter(id=league_id)
    if (leagues not in EMPTY_VALUES and len(leagues) == 1):
        league = leagues.first()
    if (league in EMPTY_VALUES):
        league, _ = League.get_default()
    return league

def get_title(tournament = None,
              league = None,
              default = _("All games")):
    if (league not in EMPTY_VALUES):
        title = league.name
    elif (tournament not in EMPTY_VALUES):
        title = tournament.name
    else:
        title = default
    return title

def get_menu_by_pagination(league = None,
                           tournament = None):
    if (league in EMPTY_VALUES and
        tournament not in EMPTY_VALUES):
        league = tournament.league
    
    seasons = Tournament.objects.none()
    if (league not in EMPTY_VALUES):
        seasons = league.seasons.all().order_by('-start_date', '-pk')
    season_paginator = Paginator(seasons, 1)
    season_page = None
    season_range = None
    season_position = 0
    if (tournament not in EMPTY_VALUES):
        season_ind = 0
        for season in seasons:
            season_ind += 1
            if (season == tournament):
                season_position = season_ind
                break
    if (season_position >= 1):
        season_page = season_paginator.get_page(season_position)
        season_range = season_paginator.get_elided_page_range(season_position)
    elif (season_paginator.count >= 1):
        season_range = season_paginator.get_elided_page_range(1)
    
    return dict(league=league,
                seasons=seasons,
                season_page=season_page,
                season_range=season_range,
                season_paginator=season_paginator)

def get_dropdown_menu(league = None,
                      tournament = None):
    if (league in EMPTY_VALUES and
        tournament not in EMPTY_VALUES):
        league = tournament.league
    
    seasons = Tournament.objects.none()
    if (league not in EMPTY_VALUES):
        seasons = league.seasons.filter(stats_display=True).order_by('-start_date', '-pk')

    leagues = League.objects.filter(stats_display=True)
    nbLeagues = leagues.count()
    if (nbLeagues > 1 or
        (not(league) and nbLeagues)):
        leagues = leagues.order_by('-start_date', '-pk')
    else:
        leagues = None
    
    return dict(league=league,
                season=tournament,
                seasons=seasons,
                leagues=leagues)