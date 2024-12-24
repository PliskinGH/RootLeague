from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Player
from matchmaking.admin import ParticipationInline

# Register your models here.

@admin.register(Player)
class PlayerAdmin(UserAdmin):
    inlines = [ParticipationInline,] # list of participants in the match
    search_fields = ['username', 'in_game_name', 'discord_name', 'email']
    list_display = ("username", "email", "in_game_name", "in_game_id", "discord_name", "is_staff")
    list_filter = ['date_joined', 'is_active', 'is_staff']
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email", "in_game_name", "in_game_id", "discord_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "groups",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2"),
            },
        ),
        (_("Personal info"), {"fields": ("email", "in_game_name", "in_game_id", "discord_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "groups",
                ),
            },
        ),
    )
