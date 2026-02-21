from rest_framework.serializers import ModelSerializer

from .models import Player

class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ["id", "discord_name", "in_game_name", "in_game_id"]
