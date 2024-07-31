from django.forms import ModelForm, ChoiceField, BooleanField, BaseInlineFormSet
from django.db.models import Q
from django.core.exceptions import ValidationError
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
            Row(Column("tournament", css_class='col-6'), Column("game_setup", css_class='col-4'), Column("closed", css_class='col-2')),
            Row(Column("table_talk", css_class='col-3'), Column("table_talk_url")),
            Row(Column("deck"), Column("board_map"), Column("random_suits"), Column("undrafted_faction")),
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
                        'tournament_score'],
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
                   'game_setup',
                   'undrafted_faction',
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
            'tournament_score'
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
        self.helper = ModalEditFormHelper()
        self.helper.layout = ModalEditLayout(
            'turn_order',
            'player',
            'faction',
            'game_score',
            'dominance',
            'coalitioned_player',
            'tournament_score'
        )

    def has_changed(self):
        """
        Overriding this, as the initial data passed to the form does not get noticed, 
        and so does not get saved, unless it actually changes
        """
        changed_data = super(ParticipantForm, self).has_changed()
        return bool(self.initial or changed_data)

class ParticipantFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        try:
            forms = [f for f in self.forms
                       if  f.cleaned_data
                       # This next line filters out inline objects that did exist
                       # but will be deleted if we let this form validate --
                       # obviously we don't want to count those if our goal is to
                       # enforce a min or max number of related objects.
                       and not f.cleaned_data.get('DELETE', False)]
            errors = []
            nb_participants = len(forms)
            if (self.instance.tournament is not None):
                max_nb_participants = self.instance.tournament.max_players_per_game
                if (max_nb_participants is not None):
                    if (nb_participants > max_nb_participants):
                        errors.append(
                            ValidationError(
                            _("This tournament does not allow more than %(max_nb)d players per game."),
                            code="error_max_nb",
                            params={'max_nb' : max_nb_participants}))
                min_nb_participants = self.instance.tournament.min_players_per_game
                if (min_nb_participants is not None):
                    if (nb_participants < min_nb_participants):
                        errors.append(
                            ValidationError(
                            _("This tournament does not allow fewer than %(min_nb)d players per game."),
                            code="error_min_nb",
                            params={'min_nb' : min_nb_participants})) 
                coalition_allowed = self.instance.tournament.coalition_allowed
                three_coal_allowed = self.instance.tournament.three_coalition_allowed
                coals = 0
                if (coalition_allowed is False or three_coal_allowed is False):
                    for f in forms:
                        if (f.cleaned_data.get('coalitioned_player', None) not in [None, '']):
                            coals += 1
                    if (coals >= 1 and coalition_allowed is False):
                        errors.append(
                            ValidationError(
                            _("This tournament does not allow coalitions."),
                            code="error_coal")) 
                    if (coals >= 2 and three_coal_allowed is False):
                        errors.append(
                            ValidationError(
                            _("This tournament does not allow three-way coalitions."),
                            code="error_three_coal")) 
            if (len(errors)):
                raise ValidationError(errors)
        except AttributeError:
            pass
        
