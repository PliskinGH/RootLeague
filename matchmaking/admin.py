from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from .models import Match, Participant

# Mixn
class AdminURLMixin(object):
    def get_admin_url(self, obj, app = "matchmaking"):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:"+app+"_%s_change" % (
            content_type.model),
            args=(obj.id,))

# Register your models here.

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    search_fields = ['player__username', 'player__in_game_name',
                     'player__discord_name', 'player__email']
    autocomplete_fields = ['player']

class ParticipantInline(admin.TabularInline, AdminURLMixin):
    model = Participant
    extra = 0
    readonly_fields = ['player_link']
    fields = ['player', 'player_link', 'faction', 'turn_order',
              'game_score','dominance', 'coalition','league_score']
    autocomplete_fields = ['player']
    def player_link(self, participant):
        if (participant.player is None):
            url = self.get_admin_url(participant)
            title_link = participant.__str__()
        else:
            url = self.get_admin_url(participant.player, "authentification")
            title_link = participant.player.__str__()
        return mark_safe("<a href='{}'>{}</a>".format(url, title_link))

class ParticipationInline(ParticipantInline):
    readonly_fields = ['match_link']
    fields = ['match', 'match_link', 'faction', 'turn_order',
              'game_score', 'dominance', 'coalition','league_score']
    verbose_name = "Participation"
    verbose_name_plural = "Participations"
    def match_link(self, participant):
        url = self.get_admin_url(participant.match)
        return mark_safe("<a href='{}'>{}</a>".format(url, participant.match.__str__()))

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline,] # list of participants in the match
    search_fields = ['title', 'participants__player__username',
                     'participants__player__in_game_name',
                     'participants__player__discord_name',
                     'participants__player__email']
    list_filter = ['date_registered', 'date_closed',
                   'tournament',
                   'board_map', 'deck', 'random_suits']
    readonly_fields = ["date_registered"]