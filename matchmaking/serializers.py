from django.core.validators import EMPTY_VALUES
from rest_framework.serializers import ModelSerializer, StringRelatedField, MultipleChoiceField, PrimaryKeyRelatedField

from .models import Match, Participant
from league.constants import HIRELINGS, LANDMARKS
from league.models import Tournament

class CoalitionedPlayerField(StringRelatedField):
    def to_representation(self, value):
        rep = None
        if (value not in EMPTY_VALUES and
            value.player not in EMPTY_VALUES):
            rep = str(value.player)
        return rep


class TournamentField(PrimaryKeyRelatedField):
    def to_representation(self, value):
        return str(value)


class ParticipantSerializer(ModelSerializer):
    player = StringRelatedField()
    player_id = PrimaryKeyRelatedField(source="player", read_only=True)
    coalition = CoalitionedPlayerField()

    class Meta:
        model = Participant
        exclude = ('match',)

class MatchSerializer(ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    tournament = TournamentField(queryset=Tournament.objects.all())
    hirelings = MultipleChoiceField(choices=HIRELINGS, required=False)
    landmarks = MultipleChoiceField(choices=LANDMARKS, required=False)

    class Meta:
        model = Match
        exclude = ('submitted_by',)
