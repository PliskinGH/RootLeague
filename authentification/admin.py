from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from more_admin_filters.filters import MultiSelectRelatedFilter
from rest_framework.authtoken.admin import TokenAdmin

from .models import Player
from matchmaking.admin import ParticipationInline
from reports.admin import FiledReportInline, ReferencedReportInline, ReportedPlayerInline
from reports.models import Report

# Register your models here.

@admin.register(Player)
class PlayerAdmin(UserAdmin):
    inlines = [ParticipationInline, ReportedPlayerInline,
               FiledReportInline, ReferencedReportInline,]
    report_inline_fk_names = {
        ReportedPlayerInline: 'reported_player',
        FiledReportInline: 'reporter',
        ReferencedReportInline: 'reference_player',
    }
    search_fields = ['username', 'in_game_name', 'discord_name', 'email']
    list_display = ("username", "email", "in_game_name", "in_game_id", "discord_name", "is_staff")
    list_filter = ['date_joined', 'is_active', 'is_staff',
                   ('groups', MultiSelectRelatedFilter),
                   ]
    readonly_fields = ('auth_token',)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email", "in_game_name", "in_game_id", "discord_name")}),
        (_("API"), {"fields": ("auth_token",)}),
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

    def get_inline_instances(self, request, obj=None):
        instances = super().get_inline_instances(request, obj)
        if obj is not None and obj.pk is not None:
            instances = [inline for inline in instances
                         if self.report_inline_fk_names.get(inline.__class__) is None
                         or Report.objects.filter(
                             **{self.report_inline_fk_names[inline.__class__]: obj}).exists()]
        return instances

TokenAdmin.autocomplete_fields = ['user']