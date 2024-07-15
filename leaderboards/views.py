from django.views.generic import ListView
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from authentification.models import Player


# Create your views here.

def leaderboard(request, players = None, title = _("All players"),
            number_per_page = 10):
    if (players is None):
        players = Player.objects.annotate(score=Sum('participations__league_score')).order_by("-score")
    return ListView.as_view(model=Player,
                            queryset=players,
                            template_name='leaderboards/leaderboard.html',
                            paginate_by=number_per_page,
                            extra_context={'title' : title}
                     )(request)