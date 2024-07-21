from django.forms import ModelForm, ChoiceField, BooleanField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Fieldset, Layout, Row, Submit
from crispy_formset_modal.helper import ModalEditFormHelper
from crispy_formset_modal.layout import ModalEditLayout, ModalEditFormsetLayout

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH
from league.models import Tournament

PLAYERS_SEATS = [(i,i) for i in range(1, MAX_NUMBER_OF_PLAYERS_IN_MATCH + 1)]
PLAYERS_SEATS = [(None, '------')] + PLAYERS_SEATS

class MatchForm(ModelForm):
    closed = BooleanField(required=False, initial=True, label=_("Closed"))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.instance and (self.fields['tournament'].queryset.count() >= 1)):
            self.fields['tournament'].queryset = Tournament.objects.exclude(Q(active_in_league = None) & ~Q(league = None))
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("title")),
            Row(Column("tournament", css_class='col-10'), Column("closed", css_class='col-2')),
            Row(Column("table_talk", css_class='col-3'), Column("table_talk_url")),
            Row(Column("deck"), Column("board_map"), Column("random_suits")),
            Fieldset(
                "Participants",
                ModalEditFormsetLayout(
                    "ParticipantInline",
                    list_display=[
                        'turn_order',
                        'player',
                        'faction',
                        'game_score',
                        'dominance',
                        'coalitioned_player',
                        'league_score'],
                ),
            ),
            Submit("submit", _("Register match"), css_class="btn btn-secondary"),
        )
    
    class Meta:
        model = Match
        fields = [
                   'title',
                   'tournament',
                   'table_talk',
                   'table_talk_url',
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
        model = Participant
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
        # self.fields["turn_order"].disabled = True
        self.helper = ModalEditFormHelper()
        self.helper.layout = ModalEditLayout(
            'turn_order',
            'player',
            'faction',
            'game_score',
            'dominance',
            'coalitioned_player',
            'league_score'
        )

    def has_changed(self):
        """
        Overriding this, as the initial data passed to the form does not get noticed, 
        and so does not get saved, unless it actually changes
        """
        changed_data = super(ParticipantForm, self).has_changed()
        return bool(self.initial or changed_data)