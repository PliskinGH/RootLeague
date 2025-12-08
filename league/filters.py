
from django import forms
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from django_filters.widgets import RangeWidget, SuffixedMultiWidget

from misc.filters import ModalFormFilterMixin

class NumberRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = (forms.NumberInput, forms.NumberInput)
        SuffixedMultiWidget.__init__(self, widgets, attrs)

class LeaderboardFilter(ModalFormFilterMixin, filters.FilterSet):
    html_title = _("Leaderboard filters")
    html_id = "leaderboardFiltersModal"

    total = filters.RangeFilter(label=_("Threshold of games"),
                                widget=NumberRangeWidget())