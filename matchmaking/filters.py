
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from crispy_forms.layout import Layout, Div, Button, Submit

from .models import Match, Participant
from league import constants
from league.models import Tournament
from authentification.models import Player
from authentification.forms import PlayerMultipleWidget
from misc.forms import DateTimeWidget

class MatchFilterMethodsMixin(object):
    def filter_isnotnull(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        method = queryset.filter if value else queryset.exclude
        return method(**{lookup: False}).distinct()

    def filter_landmark(self, queryset, name, value):
        lookup_a = '_'.join([name, 'a'])
        lookup_b = '_'.join([name, 'b'])
        return queryset.filter(Q(**{lookup_a: value}) | Q(**{lookup_b: value})).distinct()

    def filter_hirelings(self, queryset, name, value):
        lookup_a = '_'.join([name, 'a'])
        lookup_b = '_'.join([name, 'b'])
        lookup_c = '_'.join([name, 'c'])
        return queryset.filter(Q(**{lookup_a: value}) | Q(**{lookup_b: value}) | Q(**{lookup_c: value})).distinct()

class MatchFilter(MatchFilterMethodsMixin, filters.FilterSet):
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

    landmark = filters.ChoiceFilter(label="Landmark", choices=constants.LANDMARKS, method='filter_landmark')
    hirelings = filters.ChoiceFilter(label="Hirelings", choices=constants.HIRELINGS, method='filter_hirelings')

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
                  }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': filters.DateTimeFilter,
                'extra': lambda f: {
                    'widget': DateTimeWidget(),
                }
            }
        }

class ParticipantFilter(MatchFilterMethodsMixin, filters.FilterSet):
    player = filters.ModelMultipleChoiceFilter(queryset=Player.objects.all().order_by('username'),
                                               widget=PlayerMultipleWidget,)
    match__tournament = filters.ModelMultipleChoiceFilter(queryset=Tournament.objects.all().order_by('start_date', 'name'))
    match__board_map = filters.MultipleChoiceFilter(choices=constants.MAPS)
    match__deck = filters.MultipleChoiceFilter(choices=constants.DECKS)
    match__turn_timing = filters.MultipleChoiceFilter(choices=constants.TURN_TIMING_TYPES)
    match__game_setup = filters.MultipleChoiceFilter(choices=constants.SETUP_TYPES)
    faction = filters.MultipleChoiceFilter(choices=constants.FACTIONS)
    dominance = filters.MultipleChoiceFilter(choices=constants.DOMINANCE_SUITS)
    coalition = filters.BooleanFilter(method='filter_isnotnull')
    closed = filters.BooleanFilter(field_name='match__date_closed',
                                   label='Match closed',
                                   method='filter_isnotnull')

    @property
    def form(self):
        form = super().form

        layout_components = list(form.fields.keys())
        form.helper.layout = Layout(
            Div(*layout_components, css_class="modal-body"),
            Div(Button("close", _("Close"), css_class="btn btn-secondary", data_bs_dismiss="modal"),
                Submit("confirm", _("Confirm"), css_class="btn-default"),
                css_class="modal-footer")
        )

        return form

    # landmark = filters.ChoiceFilter(label="Landmark", choices=LANDMARKS, method='filter_landmark')
    # hirelings = filters.ChoiceFilter(label="Hirelings", choices=HIRELINGS, method='filter_hirelings')

    class Meta:
        model = Participant
        fields = {'player' : ['exact'],
                  'match__tournament' : ['exact'],
                  'match__date_modified' : ['gte', 'lte'],
                  'match__board_map' : ['exact'],
                  'match__deck' : ['exact'],
                  'match__turn_timing' : ['exact'],
                  'match__game_setup' : ['exact'],
                  'faction' : ['exact'],
                  'dominance' : ['exact'],
                  }
        filter_overrides = {
            models.DateTimeField: {
                'filter_class': filters.DateTimeFilter,
                'extra': lambda f: {
                    'widget': DateTimeWidget(),
                }
            }
        }