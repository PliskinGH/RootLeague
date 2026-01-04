
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.validators import EMPTY_VALUES
from django_filters import rest_framework as filters

from .models import Match, Participant
from league import constants
from league.models import Tournament
from authentification.models import Player
from authentification.widgets import PlayerMultipleWidget
from misc.filters import ModalFormFilterMixin
from misc.widgets import DateTimeWidget, FullWidthSelect2MultipleWidget

AND_FILTER_HELP_TEXT = _("This filter uses AND logic.")
FACTIONS_FILTER_CHOICES = constants.FACTIONS + [(constants.VAGABOND_PREFIX, _("Any Vagabond"))]
REGEX_PROMOTED_HIRELING = r'{}[a-z]+{}'.format(constants.HIRELING_PREFIX, constants.HIRELING_PROMOTED_SUFFIX)
REGEX_DEMOTED_HIRELING = r'{}[a-z]+{}'.format(constants.HIRELING_PREFIX, constants.HIRELING_DEMOTED_SUFFIX)
HIRELINGS_FILTER_CHOICES = constants.HIRELINGS +\
                           [(constants.HIRELING_PREFIX, _("Any Hireling")),
                            (REGEX_PROMOTED_HIRELING, _("Any Promoted Hireling")),
                            (REGEX_DEMOTED_HIRELING, _("Any Demoted Hireling"))]
LANDMARKS_FILTER_CHOICES = constants.LANDMARKS +\
                           [(constants.LANDMARK_PREFIX, _("Any Landmark"))]

class MatchFilterMethodsMixin(object):
    def filter_isnotnull(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        method = queryset.filter if value else queryset.exclude
        return method(**{lookup: False}).distinct()

class MatchDRFFilter(MatchFilterMethodsMixin, filters.FilterSet):
    participants__player = filters.ModelMultipleChoiceFilter(queryset=Player.objects.all().order_by('username'),
                                                             widget=PlayerMultipleWidget,)
    tournament = filters.ModelMultipleChoiceFilter(queryset=Tournament.objects.all().order_by('start_date', 'name'))
    board_map = filters.MultipleChoiceFilter(choices=constants.MAPS)
    deck = filters.MultipleChoiceFilter(choices=constants.DECKS)
    turn_timing = filters.MultipleChoiceFilter(choices=constants.TURN_TIMING_TYPES)
    game_setup = filters.MultipleChoiceFilter(choices=constants.SETUP_TYPES)
    participants__faction = filters.MultipleChoiceFilter(choices=constants.FACTIONS)
    participants__dominance = filters.MultipleChoiceFilter(choices=constants.DOMINANCE_SUITS)
    participants__coalition = filters.BooleanFilter(method='filter_isnotnull')

    tournament__name = filters.CharFilter(lookup_expr='icontains')

    landmarks = filters.MultipleChoiceFilter(choices=constants.LANDMARKS, lookup_expr="contains", label=_("Landmarks"))
    hirelings = filters.MultipleChoiceFilter(choices=HIRELINGS_FILTER_CHOICES, lookup_expr="regex", label=_("Hirelings"))

    class Meta:
        model = Match
        fields = {'date_closed' : ['gte', 'lte'],
                  'date_modified' : ['gte', 'lte'],
                  'participants__player' : ['exact'],
                  'tournament' : ['exact'],
                  'board_map' : ['exact'],
                  'deck' : ['exact'],
                  'turn_timing' : ['exact'],
                  'game_setup' : ['exact'],
                  'participants__faction' : ['exact'],
                  'participants__dominance' : ['exact'],
                  'hirelings' : ['exact'],
                  'landmarks' : ['exact'],
                  }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': filters.DateTimeFilter,
                'extra': lambda f: {
                    'widget': DateTimeWidget(),
                }
            }
        }

class MatchFilter(ModalFormFilterMixin, MatchFilterMethodsMixin, filters.FilterSet):
    html_title = _("Match filters")
    html_id = "matchFiltersModal"

    def __init__(self, *args, **kwargs):
        tournament_qs = kwargs.pop("tournament_qs", None)
        super().__init__(*args, **kwargs)
        if (tournament_qs not in EMPTY_VALUES):
            self.filters['tournament'].queryset = tournament_qs.order_by('start_date', 'name')

    title__icontains = filters.CharFilter(field_name='title', lookup_expr='icontains')
    tournament = filters.ModelMultipleChoiceFilter(queryset=Tournament.objects.all().order_by('start_date', 'name'),
                                                   widget=FullWidthSelect2MultipleWidget,)
    players = filters.ModelMultipleChoiceFilter(queryset=Player.objects.all().order_by('username'),
                                                widget=PlayerMultipleWidget,
                                                conjoined=True,
                                                field_name="participants__player",
                                                label=_("Players"),
                                                help_text=AND_FILTER_HELP_TEXT)
    factions = filters.MultipleChoiceFilter(choices=FACTIONS_FILTER_CHOICES, lookup_expr="contains",
                                            conjoined=True,
                                            widget=FullWidthSelect2MultipleWidget,
                                            field_name="participants__faction",
                                            label=_("Factions"),
                                            help_text=AND_FILTER_HELP_TEXT)
    board_map = filters.MultipleChoiceFilter(choices=constants.MAPS,
                                             widget=FullWidthSelect2MultipleWidget)
    deck = filters.MultipleChoiceFilter(choices=constants.DECKS,
                                        widget=FullWidthSelect2MultipleWidget)
    turn_timing = filters.MultipleChoiceFilter(choices=constants.TURN_TIMING_TYPES,
                                               widget=FullWidthSelect2MultipleWidget,)
    game_setup = filters.MultipleChoiceFilter(choices=constants.SETUP_TYPES,
                                              widget=FullWidthSelect2MultipleWidget,)
    hirelings = filters.MultipleChoiceFilter(choices=HIRELINGS_FILTER_CHOICES, lookup_expr="regex", label=_("Hirelings"),
                                             widget=FullWidthSelect2MultipleWidget,)
    hirelings_and = filters.MultipleChoiceFilter(choices=HIRELINGS_FILTER_CHOICES, lookup_expr="regex", label=_("Hirelings"),
                                                 widget=FullWidthSelect2MultipleWidget,
                                                 field_name="hirelings",
                                                 conjoined=True,
                                                 help_text=AND_FILTER_HELP_TEXT)
    landmarks = filters.MultipleChoiceFilter(choices=LANDMARKS_FILTER_CHOICES, lookup_expr="contains", label=_("Landmarks"),
                                             widget=FullWidthSelect2MultipleWidget,)
    landmarks_and = filters.MultipleChoiceFilter(choices=constants.LANDMARKS, lookup_expr="contains", label=_("Landmarks"),
                                                 widget=FullWidthSelect2MultipleWidget,
                                                 field_name="landmarks",
                                                 conjoined=True,
                                                 help_text=AND_FILTER_HELP_TEXT)
    closed = filters.BooleanFilter(field_name='date_closed',
                                   label='Match closed',
                                   method='filter_isnotnull')
    date_closed__gte = filters.DateTimeFilter(field_name='date_closed', lookup_expr='gte', widget=DateTimeWidget)
    date_closed__lte = filters.DateTimeFilter(field_name='date_closed', lookup_expr='lte', widget=DateTimeWidget)
    date_modified__gte = filters.DateTimeFilter(field_name='date_modified', lookup_expr='gte', widget=DateTimeWidget)
    date_modified__lte = filters.DateTimeFilter(field_name='date_modified', lookup_expr='lte', widget=DateTimeWidget)

    class Meta:
        model = Match
        fields = {}

class ParticipantFilter(ModalFormFilterMixin, MatchFilterMethodsMixin, filters.FilterSet):
    html_title = _("Participant filters")
    html_id = "participantFiltersModal"

    player = filters.ModelMultipleChoiceFilter(queryset=Player.objects.all().order_by('username'),
                                               widget=PlayerMultipleWidget,)
    turn_order = filters.MultipleChoiceFilter(choices=constants.TURN_ORDERS,
                                              widget=FullWidthSelect2MultipleWidget,)
    faction = filters.MultipleChoiceFilter(choices=FACTIONS_FILTER_CHOICES, lookup_expr="contains",
                                           label=_("Faction"),
                                           widget=FullWidthSelect2MultipleWidget,)
    tournament_score = filters.AllValuesMultipleFilter(widget=FullWidthSelect2MultipleWidget,)
    dominance = filters.MultipleChoiceFilter(choices=constants.DOMINANCE_SUITS,
                                             widget=FullWidthSelect2MultipleWidget,)
    coalition = filters.BooleanFilter(method='filter_isnotnull')

    class Meta:
        model = Participant
        fields = {}