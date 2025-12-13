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

def get_short_name(full_name, tuple_list=FACTIONS):
    for (key, value) in tuple_list:
        if (full_name == value):
            return key
    return ""

def invert_faction(full_name):
    return get_short_name(full_name)

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
    return get_short_name(full_name, tuple_list=MAPS)

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

LANDMARK_BM = "lm_bm"
LANDMARK_ET = "lm_et"
LANDMARK_FERRY = "lm_ferry"
LANDMARK_LF = "lm_lf"
LANDMARK_LC = "lm_lc"
LANDMARK_TOWER = "lm_tower"
LANDMARKS = [
    (LANDMARK_BM, _("Black Market")),
    (LANDMARK_ET, _("Elder Treetop")),
    (LANDMARK_FERRY, _("The Ferry")),
    (LANDMARK_LF, _("Legendary Forge")),
    (LANDMARK_LC, _("Lost City")),
    (LANDMARK_TOWER, _("The Tower")),
]

HIRELINGS_BADGERS_P = "h_badgers_p"
HIRELINGS_BADGERS_D = "h_badgers_d"
HIRELINGS_BAND_P = "h_band_p"
HIRELINGS_BAND_D = "h_band_d"
HIRELINGS_BANDITS_P = "h_bandits_p"
HIRELINGS_BANDITS_D = "h_bandits_d"
HIRELINGS_CROWS_P = "h_crows_p"
HIRELINGS_CROWS_D = "h_crows_d"
HIRELINGS_LIZARDS_P = "h_lizards_p"
HIRELINGS_LIZARDS_D = "h_lizards_d"
HIRELINGS_MOLES_P = "h_moles_p"
HIRELINGS_MOLES_D = "h_moles_d"
HIRELINGS_BIRDS_P = "h_birds_p"
HIRELINGS_BIRDS_D = "h_birds_d"
HIRELINGS_CATS_P = "h_cats_p"
HIRELINGS_CATS_D = "h_cats_d"
HIRELINGS_PROTECTOR_P = "h_protector_p"
HIRELINGS_PROTECTOR_D = "h_protector_d"
HIRELINGS_RATS_P = "h_rats_p"
HIRELINGS_RATS_D = "h_rats_d"
HIRELINGS_OTTERS_P = "h_otters_p"
HIRELINGS_OTTERS_D = "h_otters_d"
HIRELINGS_VAGABOND_P = "h_vb_p"
HIRELINGS_VAGABOND_D = "h_vb_d"
HIRELINGS_ALLIANCE_P = "h_alliance_p"
HIRELINGS_ALLIANCE_D = "h_alliance_d"
HIRELINGS = [
    (HIRELINGS_BADGERS_P, _("Vault Keepers")),
    (HIRELINGS_BADGERS_D, _("Badger Bodyguards")),
    (HIRELINGS_BAND_P, _("Popular Band")),
    (HIRELINGS_BAND_D, _("Street Band")),
    (HIRELINGS_BANDITS_P, _("Highway Bandits")),
    (HIRELINGS_BANDITS_D, _("Bandit Gangs")),
    (HIRELINGS_CROWS_P, _("Corvid Spies")),
    (HIRELINGS_CROWS_D, _("Raven Sentries")),
    (HIRELINGS_LIZARDS_P, _("Warm Sun Prophets")),
    (HIRELINGS_LIZARDS_D, _("Lizard Envoys")),
    (HIRELINGS_MOLES_P, _("Warm Sun Prophets")),
    (HIRELINGS_MOLES_D, _("Lizard Envoys")),
    (HIRELINGS_BIRDS_P, _("Last Dynasty")),
    (HIRELINGS_BIRDS_D, _("Bluebird Nobles")),
    (HIRELINGS_CATS_P, _("Forest Patrol")),
    (HIRELINGS_CATS_D, _("Feline Physicians")),
    (HIRELINGS_PROTECTOR_P, _("Furious Protector")),
    (HIRELINGS_PROTECTOR_D, _("Stoic Protector")),
    (HIRELINGS_RATS_P, _("Flame Bearers")),
    (HIRELINGS_RATS_D, _("Rat Smugglers")),
    (HIRELINGS_OTTERS_P, _("Riverfolk Flotilla")),
    (HIRELINGS_OTTERS_D, _("Otter Divers")),
    (HIRELINGS_VAGABOND_P, _("The Exile")),
    (HIRELINGS_VAGABOND_D, _("The Brigand")),
    (HIRELINGS_ALLIANCE_P, _("Spring Uprising")),
    (HIRELINGS_ALLIANCE_D, _("Rabbit Scouts")),
]