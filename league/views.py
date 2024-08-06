from django.db.models import Sum, Count, Q, F
from django.utils.translation import gettext_lazy as _
from django.core.validators import EMPTY_VALUES

from .models import League
from authentification.models import Player
from misc.views import ElidedListView

# Create your views here.

def leaderboard(request,
                league = None,
                tournament = None,
                players = None,
                title = None,
                ordering = '-relative_score', number_per_page = 15):
    if (players is None):
        players = Player.objects.all()
    if (tournament not in EMPTY_VALUES):
        players = players.annotate(total=Count('participations', filter=Q(participations__match__tournament=tournament)))
    elif (league not in EMPTY_VALUES):
        players = players.annotate(total=Count('participations', filter=Q(participations__match__tournament__league=league)))
    else:
        players = players.annotate(total=Count('participations'))
    players = players.exclude(Q(total=None) | Q(total__lt=1))

    if (tournament not in EMPTY_VALUES):
        players = players.annotate(score=Sum('participations__tournament_score', filter=Q(participations__match__tournament=tournament)))
    elif (league not in EMPTY_VALUES):
        players = players.annotate(score=Sum('participations__tournament_score', filter=Q(participations__match__tournament__league=league)))
    else:
        players = players.annotate(score=Sum('participations__tournament_score'))
    players = players.exclude(score=None)

    players = players.annotate(relative_score=F('score')/F('total')*100)

    if (title in EMPTY_VALUES):
        if (tournament not in EMPTY_VALUES):
            title = tournament.name
        elif (league not in EMPTY_VALUES):
            title = league.name
        else:
            title = _("All players")
    
    return ElidedListView.as_view(model=Player,
                                  queryset=players,
                                  template_name='league/leaderboard.html',
                                  paginate_by=number_per_page,
                                  title=title,
                                  ordering=ordering
                                  )(request)

def league_leaderboard(request,
                       league_id = None,
                       players = None,
                       ordering = '-relative_score',
                       number_per_page = 15):
    leagues = None
    league = None
    if (league_id not in EMPTY_VALUES):
        leagues = League.objects.filter(id=league_id)
    if (leagues not in EMPTY_VALUES and len(leagues) == 1):
        league = leagues.first()
    if (league in EMPTY_VALUES):
        league, _ = League.get_default()
    return leaderboard(request, league=league,
                       ordering=ordering,
                       number_per_page=number_per_page)

def global_leaderboard(request, players = None,
                       ordering = '-relative_score',
                       number_per_page = 15):
    return leaderboard(request, ordering=ordering,
                       number_per_page=number_per_page)