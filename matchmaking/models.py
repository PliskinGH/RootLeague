from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from authentification.models import Player
from league.models import Tournament
from league.constants import *
    
# Create your models here.

class Match(models.Model):
    """
    Model for matches registered in the league database.
    A match holds all the common information on a unique game,
    and holds a OneToMany relation to participants.
    """
    title = models.CharField(max_length=200, blank=True,
                             verbose_name=_('title'))
    date_registered = models.DateTimeField(auto_now_add=True,
                                           verbose_name=_('date registered'))
    date_closed = models.DateTimeField(blank=True, null=True,
                                       verbose_name=_('date closed'))
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL,
                                   null=True, blank=False,
                                   default=Tournament.get_default_pk,
                                   related_name="matches",
                                   verbose_name=_('tournament'))
    
    table_talk = models.CharField(max_length=20,
                                  blank=True, default=TABLETALK_ASYNC,
                                  choices=TABLETALK_TYPES,
                                  verbose_name=_('table talk'))
    table_talk_url = models.URLField(blank=True, null=True,
                                     help_text=_("E.g. Discord thread."),
                                     verbose_name=_('table talk URL'))
    
    game_setup = models.CharField(max_length=20,
                                  blank=True, default=SETUP_ADSET,
                                  choices=SETUP_TYPES,
                                  verbose_name=_('setup'))
    undrafted_faction = models.CharField(max_length=100, choices=FACTIONS,
                                         blank=True,
                                         help_text=_("Only in advanced setup."),
                                         verbose_name=_('undrafted faction'))
    
    deck = models.CharField(max_length=200, choices=DECKS,
                            blank=True, default=DECK_EP,
                            verbose_name=_('deck'))
    board_map = models.CharField(max_length=20, choices=MAPS,
                                 blank=True, default=MAP_AUTUMN,
                                 verbose_name=_('map'))
    random_suits = models.BooleanField(default=True, blank=True, null=True,
                                       verbose_name=_('random suits'))

    class Meta:
        verbose_name = _("match")
        ordering = ['-date_registered']

    
    def __str__(self, mention_participants=True):
        result = ""
        if (self.title not in [None, ""]):
            result = self.title
        else:
            result = _("Match") + str(self.id)
        participants = self.participants.all()
        if (mention_participants and len(participants) >= 1):
            result = result + " (" + \
            ", ".join([participant.__str__(mention_match=False) for participant in participants]) + \
                ")"
        return result
    
class Participant(models.Model):
    """
    Model for participants in a given match.
    This model holds all the individual information (score, etc)
    on a participant, and keeps a ManyToOne relation to the relevant match.
    Also holds a ManyToOne relation to a player in the league
    if the participant is already registered.
    """
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True,
                               blank=True, related_name="participations",
                               verbose_name=_('player'))
    match = models.ForeignKey(Match, on_delete=models.CASCADE,
                              related_name="participants",
                              verbose_name=_('match'))
    
    faction = models.CharField(max_length=100, choices=FACTIONS,
                               blank=True,
                               verbose_name=_('faction'))
    
    game_score = models.IntegerField(blank=True, null=True,
                                     verbose_name=_('game score'))
    dominance = models.CharField(max_length=100, choices=DOMINANCE_SUITS,
                                 blank=True,
                                 verbose_name=_('dominance'))
    coalition = models.OneToOneField('Participant', on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     verbose_name=_('coalition'))
    tournament_score = models.DecimalField(max_digits=3, decimal_places=2,
                                           null=True,
                                           verbose_name=_('tournament score'))
    
    turn_order = models.PositiveSmallIntegerField(choices=TURN_ORDERS,
                                                  null=True,
                                                  verbose_name=_('turn order'))

    class Meta:
        verbose_name = _("participant")
    
    def __str__(self, mention_match=True):
        result = ""
        if (self.player is not None):
            result = self.player.__str__()
            if (mention_match and self.match is not None):
                result = result + _(" in ") + self.match.__str__(mention_participants=False)
        else:
            result = _("UnknownPlayer") + str(self.id)
        return result