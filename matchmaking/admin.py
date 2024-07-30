from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionMixin
from import_export.fields import Field
from datetime import datetime 

from .models import Match, Participant

# Mixn
class AdminURLMixin(object):
    def get_admin_url(self, obj, app = "matchmaking"):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:"+app+"_%s_change" % (
            content_type.model),
            args=(obj.id,))

# Register your models here.

class ParticipantResource(resources.ModelResource):
    game_id = Field(attribute='game_id', column_name="GameID")
    timestamp = Field(attribute='timestamp', column_name="Timestamp")
    player = Field(attribute='player', column_name="Player")
    faction = Field(attribute='faction', column_name="Faction")
    turn_order = Field(attribute='turn_order', column_name="Turn Order")
    game_score = Field(attribute='game_score', column_name="Game Score")
    league_score = Field(attribute='league_score', column_name="Tournament Score")
    board_map = Field(attribute='board_map', column_name="Map")
    clearing_distribution = Field(attribute='clearing_distribution', column_name="Clearing Distribution")
    deck = Field(attribute='deck', column_name="Deck")
    undrafted_faction = Field(attribute='undrafted_faction', column_name="Undrafted Faction")
    dom_coal = Field(attribute='dom_coal', column_name="Dom/Coal")
    season = Field(attribute='season', column_name="Season")

    def get_export_order(self):
        return ('game_id', 'timestamp', 'player', 'faction', 'turn_order',
                'game_score', 'league_score', 'board_map',
                'clearing_distribution', 'deck', 'undrafted_faction',
                'dom_coal', 'season')

    class Meta:
        model = Participant

    def dehydrate_game_id(self, participant):
        game_id = 0
        match = getattr(participant, "match", None)
        if (match is not None):
            game_id = getattr(match, "id", 0)
        return game_id

    def dehydrate_timestamp(self, participant):
        date_registered = datetime.now()
        match = getattr(participant, "match", None)
        if (match is not None):
            date_registered = getattr(match, "date_registered", date_registered)
        return date_registered

    def dehydrate_player(self, participant):
        return participant.__str__(mention_match=False)

    def dehydrate_faction(self, participant):
        return participant.get_faction_display()

    def dehydrate_board_map(self, participant):
        board_map = ""
        match = getattr(participant, "match", None)
        if (match is not None):
            board_map = match.get_board_map_display()
        return board_map

    def dehydrate_clearing_distribution(self, participant):
        distribution = ""
        match = getattr(participant, "match", None)
        if (match is not None):
            random_suits = getattr(match, "random_suits", False)
            if (random_suits):
                distribution = "Random"
        return distribution

    def dehydrate_deck(self, participant):
        deck = ""
        match = getattr(participant, "match", None)
        if (match is not None):
            deck = match.get_deck_display()
        return deck

    def dehydrate_undrafted_faction(self, participant):
        undrafted_faction = ""
        match = getattr(participant, "match", None)
        if (match is not None):
            undrafted_faction = match.get_undrafted_faction_display()
        return undrafted_faction

    def dehydrate_dom_coal(self, participant):
        dom_coal = ""
        coalition = getattr(participant, "coalition", None)
        dominance = getattr(participant, "dominance", None)
        if (coalition is not None):
            dom_coal = "Coalition"
        elif (dominance not in [None, '']):
            dom_coal = "Dominance"
        return dom_coal

    def dehydrate_season(self, participant):
        season = ""
        match = getattr(participant, "match", None)
        if (match is not None):
            tournament = getattr(match, "tournament", None)
            if (tournament is not None):
                season = getattr(tournament, "name", season)
        return season


@admin.register(Participant)
class ParticipantAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    search_fields = ['player__username', 'player__in_game_name',
                     'player__discord_name', 'player__email']
    autocomplete_fields = ['player']
    resource_classes = [ParticipantResource]

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

class MatchResource(resources.ModelResource):
    class Meta:
        model = Match

@admin.register(Match)
class MatchAdmin(ImportExportMixin, ExportActionMixin, admin.ModelAdmin):
    inlines = [ParticipantInline,] # list of participants in the match
    search_fields = ['title', 'participants__player__username',
                     'participants__player__in_game_name',
                     'participants__player__discord_name',
                     'participants__player__email']
    list_filter = ['date_registered', 'date_closed',
                   'tournament',
                   'board_map', 'deck', 'random_suits']
    readonly_fields = ["date_registered"]
    resource_classes = [MatchResource]