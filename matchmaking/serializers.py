from django.core.validators import EMPTY_VALUES
from django.db import transaction
from rest_framework.serializers import ModelSerializer, StringRelatedField, MultipleChoiceField, PrimaryKeyRelatedField, SlugRelatedField

from .models import Match, Participant
from league.constants import HIRELINGS, LANDMARKS
from league.models import Tournament
from authentification.models import Player

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
    discord_username = SlugRelatedField(source='player', slug_field='discord_name',
                                         queryset=Player.objects.all(), required=False,
                                         allow_null=True)
    coalition = CoalitionedPlayerField()

    class Meta:
        model = Participant
        exclude = ('match',)

class MatchSerializer(ModelSerializer):
    participants = ParticipantSerializer(many=True, required=False)
    tournament = TournamentField(queryset=Tournament.objects.all(), required=False)
    hirelings = MultipleChoiceField(choices=HIRELINGS, required=False)
    landmarks = MultipleChoiceField(choices=LANDMARKS, required=False)

    class Meta:
        model = Match
        exclude = ('submitted_by',)

    @transaction.atomic
    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        match = super().create(validated_data)
        Participant.objects.bulk_create(
            [Participant(match=match, **participant) for participant in participants]
        )
        return match

    @transaction.atomic
    def update(self, instance, validated_data):
        participants = validated_data.pop('participants', None)
        match = super().update(instance, validated_data)
        if participants is not None:
            match.participants.all().delete()
            Participant.objects.bulk_create(
                [Participant(match=match, **participant) for participant in participants]
            )
        return match
