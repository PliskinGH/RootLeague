from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from authentification.models import Player
from matchmaking.views import ElidedListView

# Create your views here.

def leaderboard(request, players = None, title = _("All players"),
            number_per_page = 10):
    if (players is None):
        players = Player.objects.annotate(score=Sum('participations__tournament_score')).exclude(score=None)
    return ElidedListView.as_view(model=Player,
                                  queryset=players,
                                  template_name='league/leaderboard.html',
                                  paginate_by=number_per_page,
                                  title=title,
                                  ordering="-score"
                                  )(request)
