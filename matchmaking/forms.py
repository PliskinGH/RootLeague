from django.forms import ModelForm, inlineformset_factory, ChoiceField
from . import models

PLAYERS_SEATS = [(i,i) for i in range(1, models.MAX_NUMBER_OF_PLAYERS_IN_MATCH + 1)]
PLAYERS_SEATS = [(None, '------')] + PLAYERS_SEATS

class MatchForm(ModelForm):
    class Meta:
        model = models.Match
        fields = [
                   'title',
                   'board_map', 
                   'closed',
                  ]

class ParticipantForm(ModelForm):
    coalitioned_player = ChoiceField(required=False, choices=PLAYERS_SEATS,
                                     label='Coalition with')
    
    class Meta:
        model = models.Participant
        fields = [
            'turn_order',
            'player',
            'faction',
            'winner',
            'score',
            'dominance'
            ]
        exclude = [
            'match',
            'coalition',
            ]
        
ParticipantsFormSet = inlineformset_factory(models.Match, models.Participant,
                                            form=ParticipantForm,
                                            extra = models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                            max_num=models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                            absolute_max=models.MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                                            exclude=('match','coalition'))