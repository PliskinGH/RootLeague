
from django.core.validators import EMPTY_VALUES
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

from .models import League, Tournament

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
        seasons = league.seasons.filter(visibility=True).order_by('-start_date', '-pk')

    leagues = League.objects.filter(visibility=True)
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