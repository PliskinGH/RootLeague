from django.db import models
from django.utils import timezone

from authentification.models import Player

# Constants subject to change
MAX_NUMBER_OF_PLAYERS_IN_MATCH = 4

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
    (FACTION_CATS, "Marquise de Cat"),
    (FACTION_BIRDS, "Eyrie Dynasties"),
    (FACTION_ALLIANCE, "Woodland Alliance"),
    (FACTION_OTTERS, "Riverfolk"),
    (FACTION_LIZARDS, "Lizard Cult"),
    (FACTION_MOLES, "Underground Duchy"),
    (FACTION_CROWS, "Corvid Conspiracy"),
    (FACTION_RATS, "Lord of the Hundreds"),
    (FACTION_BADGERS, "Keepers in Iron"),
    (VAGABOND_RANGER, "Vagabond: Ranger"),
    (VAGABOND_THIEF, "Vagabond: Thief"),
    (VAGABOND_TINKER, "Vagabond: Tinker"),
    (VAGABOND_VAGRANT, "Vagabond: Vagrant"),
    (VAGABOND_ARBITER, "Vagabond: Arbiter"),
    (VAGABOND_SCOUNDREL, "Vagabond: Scoundrel"),
    (VAGABOND_ADVENTURER, "Vagabond: Adventurer"),
    (VAGABOND_RONIN, "Vagabond: Ronin"),
    (VAGABOND_HARRIER, "Vagabond: Harrier"),
    ]

MAP_AUTUMN = "autumn"
MAP_WINTER = "winter"
MAP_MOUNTAIN = "mountain"
MAP_LAKE = "lake"
MAPS = [
    (MAP_AUTUMN, "Autumn"),
    (MAP_WINTER, "Winter"),
    (MAP_MOUNTAIN, "Mountain"),
    (MAP_LAKE, "Lake"),
    ]

TURN_ORDERS = [(i,i) for i in range(1, MAX_NUMBER_OF_PLAYERS_IN_MATCH + 1)]
    
# Create your models here.

class Match(models.Model):
    """
    Model for matches registered in the league database.
    A match holds all the common information on a unique game,
    and holds a OneToMany relation to participants.
    """
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True, default=timezone.now)
    closed = models.BooleanField(default=False)
    
    board_map = models.CharField(max_length=20, choices=MAPS, blank=True)
    random_suits = models.BooleanField(default=True, blank=True, null=True)
    
    def __str__(self, mention_participants=True):
        result = ""
        if (self.title not in [None, ""]):
            result = self.title
        else:
            result = "Match" + str(self.id)
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
                               blank=False, related_name="participations")
    match = models.ForeignKey(Match, on_delete=models.CASCADE,
                              related_name="participants")
    
    faction = models.CharField(max_length=100, choices=FACTIONS,
                               blank=True)
    
    winner = models.BooleanField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    dominance = models.BooleanField(blank=True, null=True)
    
    turn_order = models.PositiveSmallIntegerField(choices=TURN_ORDERS,
                                                  blank=True, null=True)
    
    def __str__(self, mention_match=True):
        result = ""
        if (self.player is not None):
            result = self.player.__str__()
            if (mention_match and self.match is not None):
                result = result + " in " + self.match.__str__(mention_participants=False)
        else:
            result = "UnknownParticipant" + str(self.id)
        return result