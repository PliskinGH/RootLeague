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
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str

from .models import Match, Participant
from authentification.models import Player
from league.constants import DECK_EP, DECK_STANDARD, SUIT_BIRD, SUIT_FOX, SUIT_MOUSE, SUIT_RABBIT, TURN_TIMING_LIVE, TURN_TIMING_ASYNC, invert_faction, invert_map
from league.models import Tournament

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
        date_closed = datetime.now()
        match = getattr(participant, "match", None)
        if (match is not None):
            date_closed = getattr(match, "date_closed", date_closed)
        return date_closed

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
    readonly_fields = ['participant_link', 'faction', 'turn_order',
                       'game_score','dominance', 'coalition','tournament_score']
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

    # Fields
    timestamp = Field(attribute=None, column_name="Timestamp",
                      widget=DateTimeWidget(format='%Y-%m-%d %H:%M'))
    first_player = Field(attribute=None, column_name="First Player",
                         widget=CharWidget())
    second_player = Field(attribute=None, column_name="Second Player",
                          widget=CharWidget())
    third_player = Field(attribute=None, column_name="Third Player",
                         widget=CharWidget())
    fourth_player = Field(attribute=None, column_name="Fourth Player",
                          widget=CharWidget())
    first_faction = Field(attribute=None, column_name="First Player Faction",
                          widget=CharWidget())
    second_faction = Field(attribute=None, column_name="Second Player Faction",
                           widget=CharWidget())
    third_faction = Field(attribute=None, column_name="Third Player Faction",
                          widget=CharWidget())
    fourth_faction = Field(attribute=None, column_name="Fourth Player Faction",
                           widget=CharWidget())
    unselected_faction = Field(attribute=None, column_name="Unselected Faction",
                               widget=CharWidget())
    first_game_score = Field(attribute=None, column_name="First Player Game Score",
                               widget=CharWidget())
    second_game_score = Field(attribute=None, column_name="Second Player Game Score",
                              widget=CharWidget())
    third_game_score = Field(attribute=None, column_name="Third Player Game Score",
                             widget=CharWidget())
    fourth_game_score = Field(attribute=None, column_name="Fourth Player Game Score",
                              widget=CharWidget())
    first_league_score = Field(attribute=None, column_name="First Player League Score",
                               widget=DecimalWidget())
    second_league_score = Field(attribute=None, column_name="Second Player League Score",
                                widget=DecimalWidget())
    third_league_score = Field(attribute=None, column_name="Third Player League Score",
                               widget=DecimalWidget())
    fourth_league_score = Field(attribute=None, column_name="Fourth Player League Score",
                                widget=DecimalWidget())
    board_map = Field(attribute=None, column_name="Map",
                      widget=CharWidget())
    deck = Field(attribute=None, column_name="Deck",
                 widget=CharWidget())
    clearing_distribution = Field(attribute=None, column_name="Clearing Distribution",
                                  widget=CharWidget())
    timing = Field(attribute=None, column_name="Timing",
                   widget=CharWidget())
    discord_link = Field(attribute=None, column_name="Discord Link",
                         widget=CharWidget())
    tournament = Field(attribute=None, column_name="Tournament",
                         widget=CharWidget())
    setup = Field(attribute=None, column_name="Setup",
                         widget=CharWidget())
    
    # Foreign keys to be saved after match is saved
    participants = []

    class Meta:
        model = Match
        force_init_instance = True
        fields = ('timestamp', 'first_player', 'second_player', 'third_player', 'fourth_player',
                'first_faction', 'second_faction', 'third_faction', 'fourth_faction', 'unselected_faction',
                'first_game_score', 'second_game_score', 'third_game_score', 'fourth_game_score',
                'first_league_score', 'second_league_score', 'third_league_score', 'fourth_league_score',
                'board_map', 'deck', 'clearing_distribution', 'timing', 'discord_link', 'tournament', 'setup',)

    def get_import_order(self):
        return ('timestamp', 'first_player', 'second_player', 'third_player', 'fourth_player',
                'first_faction', 'second_faction', 'third_faction', 'fourth_faction', 'unselected_faction',
                'first_game_score', 'second_game_score', 'third_game_score', 'fourth_game_score',
                'first_league_score', 'second_league_score', 'third_league_score', 'fourth_league_score',
                'board_map', 'deck', 'clearing_distribution', 'timing', 'discord_link', 'tournament', 'setup')
    
    def import_instance(self, instance, row, **kwargs):
        player_fields = [self.fields['first_player'], self.fields['second_player'], self.fields['third_player'], self.fields['fourth_player']]
        faction_fields = [self.fields['first_faction'], self.fields['second_faction'], self.fields['third_faction'], self.fields['fourth_faction']]
        game_score_fields = [self.fields['first_game_score'], self.fields['second_game_score'], self.fields['third_game_score'], self.fields['fourth_game_score']]
        league_score_fields = [self.fields['first_league_score'], self.fields['second_league_score'], self.fields['third_league_score'], self.fields['fourth_league_score']]

        errors = {}
        players = [None, None, None, None]
        factions = [None, None, None, None]
        game_scores = [None, None, None, None]
        league_scores = [None, None, None, None]
        for i in range(4):
            player_field = player_fields[i]
            faction_field = faction_fields[i]
            game_score_field = game_score_fields[i]
            league_score_field = league_score_fields[i]

            try:
                player_field_split = player_field.clean(row, **kwargs).split('+')
            except Exception as e:
                errors[player_field.column_name] = ValidationError(force_str(e), code="invalid")
                continue
            if (len(player_field_split) != 2):
                errors[player_field.column_name] = ValidationError("Invalid name or id", code="invalid")
                continue
            player_in_game_name = ""
            player_in_game_id = None
            try:
                player_in_game_name = str(player_field_split[0])
                player_in_game_id = int(player_field_split[1])
            except:
                pass
            player_qs = Player.objects.filter(in_game_name__iexact=player_in_game_name, in_game_id=player_in_game_id)
            if (len(player_qs) != 1):
                errors[player_field.column_name] = ValidationError("Player name or id not found", code="invalid")
                continue
            players[i] = player_qs[0]

            try:
                faction = faction_field.clean(row, **kwargs)
            except Exception as e:
                errors[faction_field.column_name] = ValidationError(force_str(e), code="invalid")
                continue
            factions[i] = faction

            try:
                game_score = game_score_field.clean(row, **kwargs)
            except Exception as e:
                errors[game_score_field.column_name] = ValidationError(force_str(e), code="invalid")
                continue
            game_scores[i] = game_score

            try:
                league_score = league_score_field.clean(row, **kwargs)
            except Exception as e:
                errors[league_score_field.column_name] = ValidationError(force_str(e), code="invalid")
                continue
            league_scores[i] = league_score

        if errors:
            raise ValidationError(errors)
        
        coalitioned_players = [None, None, None, None]
        dominance_suits = [None, None, None, None]
        for i in range(4):
            if ("Coalition" in game_scores[i]):
                coalitioned_faction = game_scores[i].replace("Coalition w/", "")
                index_coalitioned = factions.index(coalitioned_faction)
                if (index_coalitioned < 0 or index_coalitioned > 3 or index_coalitioned == i):
                    errors[game_score_fields[i].column_name] = ValidationError("Invalid game score", code="invalid")
                    continue
                coalitioned_players[i] = index_coalitioned
            if ("Dom" in game_scores[i]):
                if (game_scores[i] == "Bird Dom"):
                    dominance_suits[i] = SUIT_BIRD
                elif (game_scores[i] == "Bunny Dom"):
                    dominance_suits[i] = SUIT_RABBIT
                elif (game_scores[i] == "Mouse Dom"):
                    dominance_suits[i] = SUIT_MOUSE
                elif (game_scores[i] == "Fox Dom"):
                    dominance_suits[i] = SUIT_FOX
                else:
                    errors[game_score_fields[i].column_name] = ValidationError("Invalid game score", code="invalid")
                    continue

        if errors:
            raise ValidationError(errors)

        participants = [None, None, None, None]
        for i in range(4):
            try:
                participants[i] = Participant(player=players[i], match=instance, faction=invert_faction(factions[i]),
                                              tournament_score=league_scores[i],
                                              turn_order=i+1)
            except Exception as e:
                errors[player_fields[i].column_name] = ValidationError(force_str(e), code="invalid")
                continue

        if errors:
            raise ValidationError(errors)
        
        for i in range(4):
            try:
                if (coalitioned_players[i] is not None):
                    participants[i].coalition = participants[coalitioned_players[i]]
                elif (dominance_suits[i] is not None):
                    participants[i].dominance = dominance_suits[i]
                else:
                    participants[i].game_score = int(game_scores[i])
            except Exception as e:
                errors[game_score_fields[i].column_name] = ValidationError(force_str(e), code="invalid")
                continue
            
        if errors:
            raise ValidationError(errors)
        
        date_closed = None
        try:
            date_closed = self.fields['timestamp'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['timestamp'].column_name] = ValidationError(force_str(e), code="invalid")
        
        tournament = None
        try:
            tournament_name = self.fields['tournament'].clean(row, **kwargs)
            tournament = Tournament.objects.get(name=tournament_name)
        except Exception as e:
            errors[self.fields['tournament'].column_name] = ValidationError(force_str(e), code="invalid")
        
        turn_timing = None
        try:
            turn_timing = self.fields['timing'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['timing'].column_namee] = ValidationError(force_str(e), code="invalid")
        
        table_talk_url = None
        try:
            table_talk_url = self.fields['discord_link'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['discord_link'].column_name] = ValidationError(force_str(e), code="invalid")
        
        game_setup = None
        try:
            game_setup = self.fields['setup'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['setup'].column_name] = ValidationError(force_str(e), code="invalid")
        
        undrafted_faction = None
        try:
            undrafted_faction = self.fields['unselected_faction'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['unselected_faction'].column_name] = ValidationError(force_str(e), code="invalid")
        
        deck = None
        try:
            deck = self.fields['deck'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['deck'].column_name] = ValidationError(force_str(e), code="invalid")
        
        board_map = None
        try:
            board_map = self.fields['board_map'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['board_map'].column_name] = ValidationError(force_str(e), code="invalid")
        
        clearing_distribution = None
        try:
            clearing_distribution = self.fields['clearing_distribution'].clean(row, **kwargs)
        except Exception as e:
            errors[self.fields['clearing_distribution'].column_name] = ValidationError(force_str(e), code="invalid")
            
        if errors:
            raise ValidationError(errors)
        
        instance.title = "Import game " + str(date_closed)
        instance.date_closed = date_closed
        instance.tournament = tournament
        if (turn_timing == "Live"):
            instance.turn_timing = TURN_TIMING_LIVE
        elif (turn_timing == "Async"):
            instance.turn_timing = TURN_TIMING_ASYNC
        instance.table_talk_url = table_talk_url
        instance.game_setup = game_setup
        instance.undrafted_faction = invert_faction(undrafted_faction)
        if (deck == "E&P"):
            instance.deck = DECK_EP
        elif (deck == "Base"):
            instance.deck = DECK_STANDARD
        instance.board_map = invert_map(board_map)
        instance.random_suits = ("Random" in clearing_distribution)

        self.participants = participants

    def after_save_instance(self, instance, row, **kwargs):
        for participant in self.participants:
            if (participant is not None and participant.coalition is None):
                participant.save()
        for participant in self.participants:
            if (participant is not None and participant.coalition is not None):
                participant.save()
        self.participants = []

@admin.register(Match)
class MatchAdmin(ImportMixin, admin.ModelAdmin):
    inlines = [ParticipantInline,] # list of participants in the match
    search_fields = ['title', 'participants__player__username',
                     'participants__player__in_game_name',
                     'participants__player__discord_name',
                     'participants__player__email']
    list_filter = ['date_registered', 'date_modified', 'date_closed',
                   'tournament',
                   'board_map', 'deck', 'random_suits']
    readonly_fields = ['date_registered', 'date_modified']
    resource_classes = [MatchResource]