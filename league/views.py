from django.db.models import Sum, Count, Q, F
from django.utils.translation import gettext_lazy as _

from authentification.models import Player
from matchmaking.views import ElidedListView

# Create your views here.

def leaderboard(request, players = None, title = _("All players"),
                ordering = '-relative_score', number_per_page = 15):
    if (players is None):
        players = Player.objects.all()
    players = players.annotate(total=Count('participations')).exclude(Q(total=None) | Q(total__lt=1)) \
                     .annotate(score=Sum('participations__tournament_score')).exclude(score=None) \
                     .annotate(relative_score=F('score')/F('total')*100)
    return ElidedListView.as_view(model=Player,
                                  queryset=players,
                                  template_name='league/leaderboard.html',
                                  paginate_by=number_per_page,
                                  title=title,
                                  ordering=ordering
                                  )(request)
