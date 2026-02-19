from rest_framework.serializers import ModelSerializer

from .models import Player


class PlayerRegistrationSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ["discord_name", "in_game_name", "in_game_id"]
