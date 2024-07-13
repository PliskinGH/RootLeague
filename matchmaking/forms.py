from django.forms import ModelForm, ChoiceField, BooleanField, formset_factory
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib import admin
from django.utils.translation import gettext as _

from . import models

PLAYERS_SEATS = [(i,i) for i in range(1, models.MAX_NUMBER_OF_PLAYERS_IN_MATCH + 1)]
PLAYERS_SEATS = [(None, '------')] + PLAYERS_SEATS

class MatchForm(ModelForm):
    closed = BooleanField(required=False, initial=True, label=_("Closed"))
    
    class Meta:
        model = models.Match
        fields = [
                   'title',
                   'deck',
                   'board_map',
                   'random_suits',
                  ]

class ParticipantForm(ModelForm):
    coalitioned_player = ChoiceField(required=False, choices=PLAYERS_SEATS,
                                     label=_('Coalition with'))
    
    class Meta:
        model = models.Participant
        fields = [
            'turn_order',
            'player',
            'faction',
            'game_score',
            'dominance',
            'league_score'
            ]
        exclude = [
            'match',
            'coalition',
            ]
        widgets = {
            'player' : AutocompleteSelect(models.Participant._meta.get_field('player'), admin.site)
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["turn_order"].disabled = True
        
ParticipantsFormSet = formset_factory(ParticipantForm,
                                      extra = models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                      max_num=models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                      absolute_max=models.MAX_NUMBER_OF_PLAYERS_IN_MATCH)