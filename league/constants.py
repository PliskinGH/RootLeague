from django.utils.translation import gettext_lazy as _

# Constants subject to change

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
    (FACTION_OTTERS, _("Riverfolk")),
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

SETUP_ADSET = "adset"
SETUP_STANDARD = "standard"
SETUP_TYPES = [
    (SETUP_ADSET, _("Advanced")),
    (SETUP_STANDARD, _("Standard")),
    ]