from django.contrib import admin
from django.core.validators import EMPTY_VALUES

from .models import League, Tournament
from .forms import LeagueAdminForm, TournamentAdminForm

# Register your models here.

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    form = LeagueAdminForm
    search_fields = ['name']

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    form = TournamentAdminForm
    search_fields = ['name', 'league__name']
    autocomplete_fields = ['league']

    def get_changeform_initial_data(self, request):
        initial_data = super().get_changeform_initial_data(request)
        league_id = request.GET.get('league', None)
        leagues = []
        if league_id not in EMPTY_VALUES:
            leagues = League.objects.filter(id=int(league_id))
        league = None
        if leagues not in EMPTY_VALUES and len(leagues) == 1:
            league = leagues.first()
        if league not in EMPTY_VALUES:
            initial_data['league'] = league_id
            initial_data['max_players_per_game'] = league.max_players_per_game
            initial_data['min_players_per_game'] = league.min_players_per_game
            initial_data['coalition_allowed'] = league.coalition_allowed
            initial_data['three_coalition_allowed'] = league.three_coalition_allowed
            initial_data['hirelings'] = league.hirelings
            initial_data['landmarks_required'] = league.landmarks_required
            initial_data['win_score'] = league.win_score
            initial_data['coalition_score_multiplier'] = league.coalition_score_multiplier
            initial_data['total_score_per_game'] = league.total_score_per_game
            initial_data['game_setup'] = league.game_setup
            initial_data['deck'] = league.deck
            initial_data['board_map'] = league.board_map
            initial_data['random_suits'] = league.random_suits
            initial_data['visibility'] = league.visibility
            initial_data['public'] = league.public
        return initial_data