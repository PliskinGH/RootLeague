from django.contrib import admin

from .models import Player
from matchmaking.admin import ParticipationInline

# Register your models here.

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    inlines = [ParticipationInline,] # list of participants in the match
    search_fields = ['ig_name', 'email']