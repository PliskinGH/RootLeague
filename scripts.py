# Scripts file
import csv
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str

from authentification.models import Player
from league.models import League, Tournament
from league.constants import FACTION_OTTERS
from matchmaking.models import Match, Participant

def import_users(csv_file_name, test_run = True, ignore_failures=False):
    players = []
    errors = {}
    with open(csv_file_name, newline='') as csvfile:
        reader_test = csv.DictReader(csvfile)
        nbrows = 0
        for row in reader_test:
            if (test_run):
                if (nbrows >= 10):
                    break
                print(row['Discord'], row['IGN'], row['Email'])
            nbrows+=1
    with open(csv_file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player = Player()
            discord_name = str(row['Discord']).strip()
            if (discord_name not in EMPTY_VALUES):
                player.username = discord_name
                player.discord_name = discord_name
            ign = str(row['IGN']).strip()
            ign_split = ign.split('+')
            try:
                in_game_name = str(ign_split[0]).strip()
                player.in_game_name = in_game_name
            except Exception as e:
                errors[ign] = ValidationError(force_str(e), code="invalid")
            try:
                in_game_id = int(ign_split[1])
                player.in_game_id = in_game_id
            except Exception as e:
                errors[ign] = ValidationError(force_str(e), code="invalid")
            try:
                email = str(row['Email'])
                if (email not in EMPTY_VALUES):
                    player.email = email
            except Exception as e:
                errors[ign] = ValidationError(force_str(e), code="invalid")
            player.set_unusable_password()
            players.append(player)
    if (errors and not(ignore_failures)):
        raise ValidationError(errors)
    else:
        print(len(players), "players could be imported.", "\n")
        if (not(test_run)):
            nbImported = 0
            for player in players:
                try:
                    player.save()
                    nbImported += 1
                except Exception as e:
                    errors[str(player.username)] = ValidationError(force_str(e), code="invalid")
            print(nbImported, "players imported.", "\n")
        if (errors):
            print("Errors:\n", errors)

def increment_turn_order(league_name="Legacy", test_run = True):
    leagues = League.objects.filter(name__icontains=league_name)
    if (len(leagues) != 1):
        raise ValidationError("League not found!", code="invalid")
    league = leagues[0]
    seasons = league.seasons.all()
    if (len(seasons) < 1):
        raise ValidationError("Seasons not found!", code="invalid")
    nbModifications = 0
    nbToModif = 0
    errors = {}
    for season in seasons:
        matches = season.matches.all()
        for match in matches:
            participants = match.participants.all()
            for participant in participants:
                if (not(test_run)):
                    try:
                        participant.turn_order += 1
                        participant.save()
                        nbModifications += 1
                    except Exception as e:
                        errors[str(match.title)] = ValidationError(force_str(e), code="invalid")
                nbToModif += 1
    if (test_run):
        print(nbToModif, "participant turn orders could be fixed.\n")
    else:
        print(nbModifications, "participants turn orders were fixed out of", nbToModif, "possible.\n")
    if (errors):
        print(errors)

def fix_empty_factions(league_name="Legacy", faction=FACTION_OTTERS, test_run=True):
    leagues = League.objects.filter(name__icontains=league_name)
    if (len(leagues) != 1):
        raise ValidationError("League not found!", code="invalid")
    league = leagues[0]
    seasons = league.seasons.all()
    if (len(seasons) < 1):
        raise ValidationError("Seasons not found!", code="invalid")
    nbModifications = 0
    nbToModif = 0
    errors = {}
    for season in seasons:
        matches = season.matches.all()
        for match in matches:
            participants = match.participants.all()
            for participant in participants:
                if (participant.faction not in EMPTY_VALUES):
                    continue
                if (not(test_run)):
                    try:
                        participant.faction = faction
                        participant.save()
                        nbModifications += 1
                    except Exception as e:
                        errors[str(match.title)] = ValidationError(force_str(e), code="invalid")
                nbToModif += 1
    if (test_run):
        print(nbToModif, "participant factions could be fixed.\n")
    else:
        print(nbModifications, "participants factions were fixed out of", nbToModif, "possible.\n")
    if (errors):
        print(errors)

def find_wrong_turn_orders():
    print("#### Starting script ####\n")
    matches = Match.objects.all()
    wrong_matches = set()
    for match in matches:
        participants = match.participants.all()
        turn_orders = set()
        for participant in participants:
            turn_orders.add(getattr(participant, "turn_order", None))
        nbParticipants = participants.count()
        legal_turn_orders = {i for i in range(1, nbParticipants+1)}
        if (legal_turn_orders != turn_orders):
            wrong_matches.add(match)
    nbWrongMatches = len(wrong_matches)
    if (nbWrongMatches):
        print(nbWrongMatches, "matches have wrong turn orders:")
        for match in wrong_matches:
            print(getattr(match, "id", "Unknown"), " : ", getattr(match, "title", ""))
    else:
        print("No match with wrong turn orders was found. All good!")
    print("\n#### Script ended ####")

def find_wrong_factions():
    print("#### Starting script ####\n")
    matches = Match.objects.all()
    wrong_matches = set()
    for match in matches:
        participants = match.participants.all()
        factions = set()
        for participant in participants:
            factions.add(getattr(participant, "faction", None))
        nbParticipants = participants.count()
        if (len(factions) != nbParticipants):
            wrong_matches.add(match)
    nbWrongMatches = len(wrong_matches)
    if (nbWrongMatches):
        print(nbWrongMatches, "matches have wrong factions:")
        for match in wrong_matches:
            print(getattr(match, "id", "Unknown"), " : ", getattr(match, "title", ""))
    else:
        print("No match with wrong factions was found. All good!")
    print("\n#### Script ended ####")

def find_wrong_players():
    print("#### Starting script ####\n")
    matches = Match.objects.all()
    wrong_matches = set()
    for match in matches:
        participants = match.participants.all()
        players = set()
        for participant in participants:
            players.add(getattr(participant, "player", None))
        nbParticipants = participants.count()
        if (len(players) != nbParticipants):
            wrong_matches.add(match)
    nbWrongMatches = len(wrong_matches)
    if (nbWrongMatches):
        print(nbWrongMatches, "matches have wrong players:")
        for match in wrong_matches:
            print(getattr(match, "id", "Unknown"), " : ", getattr(match, "title", ""))
    else:
        print("No match with wrong players was found. All good!")
    print("\n#### Script ended ####")

