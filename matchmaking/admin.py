from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from import_export.admin import ImportMixin, ExportActionMixin
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from more_admin_filters.filters import MultiSelectRelatedFilter, MultiSelectFilter, RelatedDropdownFilter
from admin_auto_filters.filters import AutocompleteFilter

from .models import Match, Participant
from .forms import ParticipantAdminForm, MatchAdminForm
from .ressources import ParticipantResource, MatchResource
from misc.admin import MultiSelectChoicesFilter

MATCH_SEARCH_HELP_TEXT = _("Only in title. For other fields, use the filters.")

# Mixn
class AdminURLMixin(object):
    def get_admin_url(self, obj, app = "matchmaking"):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:"+app+"_%s_change" % (
            content_type.model),
            args=(obj.id,))

# Register your models here.

class CoalitionListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("coalition")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "coalition"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("yes", _("Yes")),
            ("no", _("No")),
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == "yes":
            return queryset.filter(~Q(coalition=None))
        if self.value() == "no":
            return queryset.filter(coalition=None)

class PlayerFilter(AutocompleteFilter):
    title = 'Player'
    field_name = 'player'

@admin.register(Participant)
class ParticipantAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = ['match__title']
    search_help_text = MATCH_SEARCH_HELP_TEXT
    fields = ['player', 'match', 'turn_order', 'faction',
              'game_score', 'dominance', 'coalition',
              'tournament_score']
    list_filter = [PlayerFilter,
                   ('faction', MultiSelectChoicesFilter),
                   ('tournament_score', MultiSelectFilter),
                   ('turn_order', MultiSelectChoicesFilter),
                   ('dominance', MultiSelectChoicesFilter),
                   CoalitionListFilter,
                   ('match__tournament', MultiSelectRelatedFilter),
                   ('match__turn_timing', MultiSelectChoicesFilter),
                   ('match__deck', MultiSelectChoicesFilter),
                   ('match__board_map', MultiSelectChoicesFilter),
                   ('match__random_suits', MultiSelectFilter),
                   'match__date_registered', 'match__date_closed',
                   ]
    list_display = ['player', 'match', 'match__date_closed',
                    'faction', 'game_score', 'tournament_score', 'turn_order']
    autocomplete_fields = ['player']
    readonly_fields = ['match']
    resource_classes = [ParticipantResource]
    form = ParticipantAdminForm

class ParticipantInline(TabularInlinePaginated, AdminURLMixin):
    model = Participant
    extra = 0
    readonly_fields = ['participant_link', 'faction', 'turn_order',
                       'game_score','dominance', 'coalition','tournament_score']
    fields = ['participant_link', 'faction', 'turn_order',
              'game_score','dominance', 'coalition','tournament_score']
    def participant_link(self, participant):
        url = self.get_admin_url(participant)
        title_link = participant.__str__()
        return mark_safe("<a href='{}'>{}</a>".format(url, title_link))

class ParticipationInline(ParticipantInline):
    per_page = 3
    verbose_name = "Participation"
    verbose_name_plural = "Participations"

class ParticipantPlayerFilter(AutocompleteFilter):
    title = 'player'
    field_name = 'player'
    rel_model = Participant
    parameter_name = 'participants__player'

@admin.register(Match)
class MatchAdmin(ImportMixin, admin.ModelAdmin):
    inlines = [ParticipantInline,] # list of participants in the match
    search_fields = ['title']
    search_help_text = MATCH_SEARCH_HELP_TEXT
    list_filter = [ParticipantPlayerFilter,
                   ('tournament', MultiSelectRelatedFilter),
                   ('turn_timing', MultiSelectChoicesFilter),
                   ('deck', MultiSelectChoicesFilter),
                   ('board_map', MultiSelectChoicesFilter),
                   ('random_suits', MultiSelectFilter),
                   'date_registered', 'date_modified', 'date_closed',
                   ]
    list_display = ['title', 'date_registered', 'date_closed',
                   'tournament',
                   'turn_timing',
                   'board_map', 'deck', 'random_suits']
    list_editable = ['turn_timing']
    autocomplete_fields = ['submitted_by', 'tournament']
    readonly_fields = ['date_registered', 'date_modified']
    resource_classes = [MatchResource]
    form = MatchAdminForm