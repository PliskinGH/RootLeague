from django.core.validators import EMPTY_VALUES
from rest_framework.serializers import ModelSerializer, StringRelatedField, MultipleChoiceField, PrimaryKeyRelatedField

from .models import Match, Participant
from league.constants import HIRELINGS, LANDMARKS

class CoalitionedPlayerField(StringRelatedField):
    def to_representation(self, value):
        rep = None
        if (value not in EMPTY_VALUES and
            value.player not in EMPTY_VALUES):
            rep = str(value.player)
        return rep

class ParticipantSerializer(ModelSerializer):
    player = StringRelatedField()
    player_id = PrimaryKeyRelatedField(source="player", read_only=True)
    coalition = CoalitionedPlayerField()

    class Meta:
        model = Participant
        exclude = ('match',)

class MatchSerializer(ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    tournament = StringRelatedField()
    hirelings = MultipleChoiceField(choices=HIRELINGS)
    landmarks = MultipleChoiceField(choices=LANDMARKS)

    class Meta:
        model = Match
        exclude = ('submitted_by',)
