
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from crispy_forms.layout import Layout, Div, Button, Submit

from .models import Match, Participant
from league.constants import LANDMARKS, HIRELINGS
from authentification.models import Player
from authentification.forms import PlayerWidget

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
    participants__coalition = filters.BooleanFilter(method='filter_isnotnull')

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
    player = filters.ModelChoiceFilter(queryset=Player.objects.all().order_by('username'),
                                       empty_label=_("All players"),
                                       widget=PlayerWidget,)
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
                  'match__date_modified' : ['gte', 'lte'],
                  'match__board_map' : ['exact'],
                  'match__deck' : ['exact'],
                  'match__turn_timing' : ['exact'],
                  'match__game_setup' : ['exact'],
                  'match__tournament' : ['exact'],
                  'faction' : ['exact'],
                  'dominance' : ['exact'],
                  }