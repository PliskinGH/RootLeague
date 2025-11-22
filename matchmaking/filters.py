
from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Match, Participant
from league.constants import LANDMARKS, HIRELINGS

class MatchFilterMethodsMixin(object):
    def filter_coalition(self, queryset, name, value):
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
    participants__coalition = filters.BooleanFilter(method='filter_coalition')

    tournament__name = filters.CharFilter(lookup_expr='icontains')

    landmark = filters.ChoiceFilter(label="Landmark", choices=LANDMARKS, method='filter_landmark')
    hirelings = filters.ChoiceFilter(label="Hirelings", choices=HIRELINGS, method='filter_hirelings')

    class Meta:
        model = Match
        fields = {'date_closed' : ['gte', 'lte'],
                  'date_modified' : ['gte', 'lte'],
                  'board_map' : ['exact'],
                  'deck' : ['exact'],
                  'turn_timing' : ['exact'],
                  'game_setup' : ['exact'],
                  'tournament' : ['exact'],
                  'participants__faction' : ['exact'],
                  'participants__dominance' : ['exact'],
                  }

class ParticipantFilter(MatchFilterMethodsMixin, filters.FilterSet):
    coalition = filters.BooleanFilter(method='filter_coalition')

    # landmark = filters.ChoiceFilter(label="Landmark", choices=LANDMARKS, method='filter_landmark')
    # hirelings = filters.ChoiceFilter(label="Hirelings", choices=HIRELINGS, method='filter_hirelings')

    class Meta:
        model = Participant
        fields = {'player' : ['exact'],
                  'match__date_closed' : ['gte', 'lte'],
                  'match__date_modified' : ['gte', 'lte'],
                  'match__board_map' : ['exact'],
                  'match__deck' : ['exact'],
                  'match__turn_timing' : ['exact'],
                  'faction' : ['exact'],
                  'dominance' : ['exact'],
                  }