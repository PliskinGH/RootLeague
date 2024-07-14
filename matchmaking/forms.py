from django.forms import ModelForm, ChoiceField, BooleanField, formset_factory
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms

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

class PlayerWidget(s2forms.ModelSelect2Widget):
    search_fields = ['username__icontains', 'in_game_name__icontains',
                     'discord_name__icontains', 'email__icontains']

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
            'player' : PlayerWidget(attrs={'style': 'width : 100%'})
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["turn_order"].disabled = True
        
ParticipantsFormSet = formset_factory(ParticipantForm,
                                      extra = models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                      max_num=models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                      absolute_max=models.MAX_NUMBER_OF_PLAYERS_IN_MATCH)

class LeagueForm(ModelForm):
    class Meta:
        model = models.League
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(LeagueForm, self).__init__(*args, **kwargs)
        if (self.instance and (self.fields['active_season'].queryset.count() >= 1)):
            self.fields['active_season'].queryset = models.Tournament.objects.filter(league=self.instance)