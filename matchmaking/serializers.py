from django.core.validators import EMPTY_VALUES
from rest_framework.serializers import ModelSerializer, StringRelatedField

from .models import Match, Participant

class CoalitionedPlayerField(StringRelatedField):
    def to_representation(self, value):
        rep = None
        if (value not in EMPTY_VALUES and
            value.player not in EMPTY_VALUES):
            rep = str(value.player)
        return rep

class ParticipantSerializer(ModelSerializer):
    player = StringRelatedField()
    coalition = CoalitionedPlayerField()

    class Meta:
        model = Participant
        exclude = ('match',)

class MatchSerializer(ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    tournament = StringRelatedField()

    class Meta:
        model = Match
        exclude = ('submitted_by',)
