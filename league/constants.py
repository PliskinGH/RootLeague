from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
from datetime import timedelta

# Constants subject to change

MAX_EDIT_TIMEFRAME = timedelta(days=1)

MAX_NUMBER_OF_PLAYERS_IN_MATCH = 6
DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH = 4
WIN_GAME_SCORE = 30

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
VAGABOND = "vb_"
VAGABOND_RANGER = VAGABOND + "ranger"
VAGABOND_THIEF = VAGABOND + "thief"
VAGABOND_TINKER = VAGABOND + "tinker"
VAGABOND_VAGRANT = VAGABOND + "vagrant"
VAGABOND_ARBITER = VAGABOND + "arbiter"
VAGABOND_SCOUNDREL = VAGABOND + "scoundrel"
VAGABOND_ADVENTURER = VAGABOND + "adventurer"
VAGABOND_RONIN = VAGABOND + "ronin"
VAGABOND_HARRIER = VAGABOND + "harrier"
FACTIONS = [
    (FACTION_CATS, _("Marquise de Cat")),
    (FACTION_BIRDS, _("Eyrie Dynasties")),
    (FACTION_ALLIANCE, _("Woodland Alliance")),
    (FACTION_OTTERS, _("Riverfolk Company")),
    (FACTION_LIZARDS, _("Lizard Cult")),
    (FACTION_MOLES, _("Underground Duchy")),
    (FACTION_CROWS, _("Corvid Conspiracy")),
    (FACTION_RATS, _("Lord of the Hundreds")),
    (FACTION_BADGERS, _("Keepers in Iron")),
    (VAGABOND_RANGER, _("Vagabond (Ranger)")),
    (VAGABOND_THIEF, _("Vagabond (Thief)")),
    (VAGABOND_TINKER, _("Vagabond (Tinker)")),
    (VAGABOND_VAGRANT, _("Vagabond (Vagrant)")),
    (VAGABOND_ARBITER, _("Vagabond (Arbiter)")),
    (VAGABOND_SCOUNDREL, _("Vagabond (Scoundrel)")),
    (VAGABOND_ADVENTURER, _("Vagabond (Adventurer)")),
    (VAGABOND_RONIN, _("Vagabond (Ronin)")),
    (VAGABOND_HARRIER, _("Vagabond (Harrier)")),
    ]

def invert_faction(full_name):
    if (full_name == "Marquise de Cat"):
        return FACTION_CATS
    if (full_name == "Eyrie Dynasties"):
        return FACTION_BIRDS
    if (full_name == "Woodland Alliance"):
        return FACTION_ALLIANCE
    if (full_name == "Riverfolk Company"):
        return FACTION_OTTERS
    if (full_name == "Lizard Cult"):
        return FACTION_LIZARDS
    if (full_name == "Underground Duchy"):
        return FACTION_MOLES
    if (full_name == "Corvid Conspiracy"):
        return FACTION_CROWS
    if (full_name == "Lord of the Hundreds"):
        return FACTION_RATS
    if (full_name == "Keepers in Iron"):
        return FACTION_BADGERS
    if (full_name == "Vagabond (Ranger)"):
        return VAGABOND_RANGER
    if (full_name == "Vagabond (Thief)"):
        return VAGABOND_THIEF
    if (full_name == "Vagabond (Tinker)"):
        return VAGABOND_TINKER
    if (full_name == "Vagabond (Vagrant)"):
        return VAGABOND_VAGRANT
    if (full_name == "Vagabond (Arbiter)"):
        return VAGABOND_ARBITER
    if (full_name == "Vagabond (Scoundrel)"):
        return VAGABOND_SCOUNDREL
    if (full_name == "Vagabond (Adventurer)"):
        return VAGABOND_ADVENTURER
    if (full_name == "Vagabond (Ronin)"):
        return VAGABOND_RONIN
    if (full_name == "Vagabond (Harrier)"):
        return VAGABOND_HARRIER
    return ""

FACTIONS_URLS = {}
for (faction, value) in FACTIONS:
    FACTIONS_URLS[faction] = static('league/assets/img/' + faction + '_24.png')

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

def invert_map(full_name):
    if (full_name == "Autumn"):
        return MAP_AUTUMN
    if (full_name == "Winter"):
        return MAP_WINTER
    if (full_name == "Mountain"):
        return MAP_MOUNTAIN
    if (full_name == "Lake"):
        return MAP_LAKE
    return ""

MAPS_URLS = {}
for (map, value) in MAPS:
    MAPS_URLS[map] = static('league/assets/img/' + map + '_24.png')

DECK_STANDARD = "standard"
DECK_EP = "e&p"
DECKS = [
    (DECK_STANDARD, _("Standard")),
    (DECK_EP, _("Exiles and Partisans")),
    ]

DECKS_URLS = {}
for (deck, value) in DECKS:
    DECKS_URLS[deck] = static('league/assets/img/' + deck + '_24.png')

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

TURN_TIMING_LIVE = "live"
TURN_TIMING_ASYNC = "async"
TURN_TIMING_TYPES = [
    (TURN_TIMING_LIVE, _("Live")),
    (TURN_TIMING_ASYNC, _("Async")),
    ]

TURN_TIMING_URLS = {}
for (timing, value) in TURN_TIMING_TYPES:
    TURN_TIMING_URLS[timing] = static('league/assets/img/' + timing + '_24.png')

SETUP_ADSET = "adset"
SETUP_STANDARD = "standard"
SETUP_TYPES = [
    (SETUP_ADSET, _("Advanced")),
    (SETUP_STANDARD, _("Standard")),
    ]