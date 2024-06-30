from django.forms import ModelForm, inlineformset_factory
from .models import Match, Participant

class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = [
                   'title',
                   'board_map', 
                   'closed',
                  ]
        
ParticipantsFormSet = inlineformset_factory(Match, Participant, extra=4,
                                            max_num=4, exclude=('match',))