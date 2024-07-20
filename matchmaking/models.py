from django.db import models
from django.utils.translation import gettext_lazy as _

from authentification.models import Player
from league.models import Tournament

# Constants subject to change
MAX_NUMBER_OF_PLAYERS_IN_MATCH = 4
DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH = 4

FACTION_CATS = "cats"
FACTION_BIRDS = "birds"
FACTION_ALLIANCE = "alliance"
FACTION_VAGABOND = "vagabond"
FACTION_OTTERS = "otters"
FACTION_LIZARDS = "lizards"
FACTION_MOLES = "moles"
FACTION_CROWS = "crows"
FACTION_RATS = "rats"
FACTION_BADGERS = "badgers"
VAGABOND_RANGER = "vb_ranger"
VAGABOND_THIEF = "vb_thief"
VAGABOND_TINKER = "vb_tinker"
VAGABOND_VAGRANT = "vb_vagrant"
VAGABOND_ARBITER = "vb_arbiter"
VAGABOND_SCOUNDREL = "vb_scoundrel"
VAGABOND_ADVENTURER = "vb_adventurer"
VAGABOND_RONIN = "vb_ronin"
VAGABOND_HARRIER = "vb_harrier"
FACTIONS = [
    (FACTION_CATS, _("Marquise de Cat")),
    (FACTION_BIRDS, _("Eyrie Dynasties")),
    (FACTION_ALLIANCE, _("Woodland Alliance")),
    (FACTION_OTTERS, _("Riverfolk")),
    (FACTION_LIZARDS, _("Lizard Cult")),
    (FACTION_MOLES, _("Underground Duchy")),
    (FACTION_CROWS, _("Corvid Conspiracy")),
    (FACTION_RATS, _("Lord of the Hundreds")),
    (FACTION_BADGERS, _("Keepers in Iron")),
    (VAGABOND_RANGER, _("Vagabond: Ranger")),
    (VAGABOND_THIEF, _("Vagabond: Thief")),
    (VAGABOND_TINKER, _("Vagabond: Tinker")),
    (VAGABOND_VAGRANT, _("Vagabond: Vagrant")),
    (VAGABOND_ARBITER, _("Vagabond: Arbiter")),
    (VAGABOND_SCOUNDREL, _("Vagabond: Scoundrel")),
    (VAGABOND_ADVENTURER, _("Vagabond: Adventurer")),
    (VAGABOND_RONIN, _("Vagabond: Ronin")),
    (VAGABOND_HARRIER, _("Vagabond: Harrier")),
    ]

MAP_AUTUMN = "autumn"
MAP_WINTER = "winter"
MAP_MOUNTAIN = "mountain"
MAP_LAKE = "lake"
MAPS = [
    (MAP_AUTUMN, _("Autumn")),
    (MAP_WINTER, _("Winter")),
    (MAP_MOUNTAIN, _("Mountain")),
    (MAP_LAKE, _("Lake")),
    ]

DECK_STANDARD = "standard"
DECK_EP = "e&p"
DECKS = [
    (DECK_STANDARD, _("Standard")),
    (DECK_EP, _("Exiles and Partisans")),
    ]

SUIT_BIRD = "bird"
SUIT_FOX = "fox"
SUIT_MOUSE = "mouse"
SUIT_RABBIT = "rabbit"
DOMINANCE_SUITS = [
    (SUIT_BIRD, _("Bird dominance")),
    (SUIT_FOX, _("Fox dominance")),
    (SUIT_MOUSE, _("Mouse dominance")),
    (SUIT_RABBIT, _("Rabbit dominance")),
    ]

SCORE_WIN = 1.0
SCORE_COALITION = 0.5
SCORE_LOSS = 0.0
SCORES = [
    (SCORE_WIN, 1),
    (SCORE_COALITION, 0.5),
    (SCORE_LOSS, 0),
    ]

TURN_ORDERS = [(i,i) for i in range(1, MAX_NUMBER_OF_PLAYERS_IN_MATCH + 1)]

TABLETALK_LIVE = "live"
TABLETALK_ASYNC = "async"
TABLETALK_TYPES = [
    (TABLETALK_LIVE, _("Live")),
    (TABLETALK_ASYNC, _("Async")),
    ]
    
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
                                   related_name="matches",
                                   verbose_name=_('tournament'))
    
    table_talk = models.CharField(max_length=20,
                                  blank=True, default=TABLETALK_ASYNC,
                                  choices=TABLETALK_TYPES,
                                  verbose_name=_('table talk'))
    
    deck = models.CharField(max_length=200, choices=DECKS,
                            blank=True, default=DECK_EP,
                            verbose_name=_('deck'))
    board_map = models.CharField(max_length=20, choices=MAPS,
                                 blank=True, default=MAP_AUTUMN,
                                 verbose_name=_('map'))
    random_suits = models.BooleanField(default=True, blank=True, null=True,
                                       verbose_name=_('random suits'))
    
    class Meta:
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
    league_score = models.DecimalField(max_digits=2, decimal_places=1,
                                       choices = SCORES,
                                       blank=True, null=True,
                                       verbose_name=_('league score'))
    
    turn_order = models.PositiveSmallIntegerField(choices=TURN_ORDERS,
                                                  blank=True, null=True,
                                                  verbose_name=_('turn order'))
    
    def __str__(self, mention_match=True):
        result = ""
        if (self.player is not None):
            result = self.player.__str__()
            if (mention_match and self.match is not None):
                result = result + _(" in ") + self.match.__str__(mention_participants=False)
        else:
            result = _("UnknownPlayer") + str(self.id)
        return result