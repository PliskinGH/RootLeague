from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from import_export import resources
from import_export.admin import ImportMixin, ExportActionMixin
from import_export.fields import Field
from import_export.widgets import DateTimeWidget, CharWidget, IntegerWidget, DecimalWidget
from datetime import datetime 
from django_admin_inline_paginator.admin import TabularInlinePaginated

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
    tournament_score = Field(attribute='tournament_score', column_name="Tournament Score")
    board_map = Field(attribute='board_map', column_name="Map")
    clearing_distribution = Field(attribute='clearing_distribution', column_name="Clearing Distribution")
    deck = Field(attribute='deck', column_name="Deck")
    undrafted_faction = Field(attribute='undrafted_faction', column_name="Undrafted Faction")
    dom_coal = Field(attribute='dom_coal', column_name="Dom/Coal")
    season = Field(attribute='season', column_name="Season")

    def get_export_order(self):
        return ('game_id', 'timestamp', 'player', 'faction', 'turn_order',
                'game_score', 'tournament_score', 'board_map',
                'clearing_distribution', 'deck', 'undrafted_faction',
                'dom_coal', 'season')

    class Meta:
        model = Participant

    def dehydrate_game_id(self, participant):
        game_id = 0
        match = getattr(participant, "match", None)
        if (match is not None):
            game_id = getattr(match, "id", 0)
        return "DbInput!" + str(game_id)

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
class ParticipantAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = ['player__username', 'player__in_game_name',
                     'player__discord_name', 'player__email']
    autocomplete_fields = ['player']
    resource_classes = [ParticipantResource]

class ParticipantInline(TabularInlinePaginated, AdminURLMixin):
    model = Participant
    extra = 0
    readonly_fields = ['participant_link']
    fields = ['participant_link', 'faction', 'turn_order',
              'game_score','dominance', 'coalition','tournament_score']
    def participant_link(self, participant):
        url = self.get_admin_url(participant)
        title_link = participant.__str__()
        return mark_safe("<a href='{}'>{}</a>".format(url, title_link))

class ParticipationInline(ParticipantInline):
    per_page = 3
    verbose_name = "Participation"
    verbose_name_plural = "Participations"

class MatchResource(resources.ModelResource):
    timestamp = Field(attribute='timestamp', column_name="Timestamp",
                      widget=DateTimeWidget(format='%Y-%m-%d %H:%M'))
    first_player = Field(attribute='first_player', column_name="First Player",
                         widget=CharWidget())
    second_player = Field(attribute='second_player', column_name="Second Player",
                          widget=CharWidget())
    third_player = Field(attribute='third_player', column_name="Third Player",
                         widget=CharWidget())
    fourth_player = Field(attribute='fourth_player', column_name="Fourth Player",
                          widget=CharWidget())
    first_faction = Field(attribute='first_faction', column_name="First Player Faction",
                          widget=CharWidget())
    second_faction = Field(attribute='second_faction', column_name="Second Player Faction",
                           widget=CharWidget())
    third_faction = Field(attribute='third_faction', column_name="Third Player Faction",
                          widget=CharWidget())
    fourth_faction = Field(attribute='fourth_faction', column_name="Fourth Player Faction",
                           widget=CharWidget())
    unselected_faction = Field(attribute='unselected_faction', column_name="Unselected Faction",
                               widget=CharWidget())
    first_game_score = Field(attribute='first_game_score', column_name="First Player Game Score",
                               widget=CharWidget())
    second_game_score = Field(attribute='second_game_score', column_name="Second Player Game Score",
                              widget=CharWidget())
    third_game_score = Field(attribute='third_game_score', column_name="Third Player Game Score",
                             widget=CharWidget())
    fourth_game_score = Field(attribute='fourth_game_score', column_name="Fourth Player Game Score",
                              widget=CharWidget())
    first_league_score = Field(attribute='first_league_score', column_name="First Player League Score",
                               widget=DecimalWidget())
    second_league_score = Field(attribute='second_league_score', column_name="Second Player League Score",
                                widget=DecimalWidget())
    third_league_score = Field(attribute='third_league_score', column_name="Third Player League Score",
                               widget=DecimalWidget())
    fourth_league_score = Field(attribute='fourth_league_score', column_name="Fourth Player League Score",
                                widget=DecimalWidget())
    board_map = Field(attribute='board_map', column_name="Map",
                      widget=CharWidget())
    deck = Field(attribute='deck', column_name="Deck",
                 widget=CharWidget())
    clearing_distribution = Field(attribute='clearing_distribution', column_name="Clearing Distribution",
                                  widget=CharWidget())
    timing = Field(attribute='timing', column_name="Timing",
                   widget=CharWidget())
    discord_link = Field(attribute='discord_link', column_name="Discord Link",
                         widget=CharWidget())

    def get_import_order(self):
        return ('timestamp', 'first_player', 'second_player', 'third_player', 'fourth_player',
                'first_faction', 'second_faction', 'third_faction', 'fourth_faction', 'unselected_faction',
                'first_game_score', 'second_game_score', 'third_game_score', 'fourth_game_score',
                'first_league_score', 'second_league_score', 'third_league_score', 'fourth_league_score',
                'board_map', 'deck', 'clearing_distribution', 'timing', 'discord_link')
    
    def import_instance(self, instance, row, **kwargs):
        player_fields = [self.first_player, self.second_player, self.third_player, self.fourth_player]
        faction_fields = [self.first_faction, self.second_faction, self.third_faction, self.fourth_faction]
        game_score_fields = [self.first_game_score, self.second_game_score, self.third_game_score, self.fourth_game_score]
        league_score_fields = [self.first_league_score, self.second_league_score, self.third_league_score, self.fourth_league_score]

        for i in range(4):
            player_field = player_fields[i]
            faction_field = faction_fields[i]
            game_score_field = game_score_fields[i]
            league_score_field = league_score_fields[i]
            
        pass

    class Meta:
        model = Match
        force_init_instance = True

@admin.register(Match)
class MatchAdmin(ImportMixin, admin.ModelAdmin):
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