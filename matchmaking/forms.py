from django.forms import ModelForm, ChoiceField, BooleanField, BaseInlineFormSet
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Fieldset, Layout, Row, Submit
from crispy_formset_modal.helper import ModalEditFormHelper
from crispy_formset_modal.layout import ModalEditLayout, ModalEditFormsetLayout

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH, VAGABOND, WIN_GAME_SCORE
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

    def clean(self):
        super().clean()
        try:
            errors = []
            
            if (len(errors)):
                raise ValidationError(errors)
        except AttributeError:
            pass
        

    def has_changed(self):
        """
        Overriding this, as the initial data passed to the form does not get noticed, 
        and so does not get saved, unless it actually changes
        """
        changed_data = super().has_changed()
        return bool(self.initial or changed_data)

class ParticipantFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        try:
            forms = [f for f in self.forms
                       if  f.cleaned_data
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
                total_score_allowed = self.instance.tournament.total_score_per_game
                win_score = self.instance.tournament.win_score
                coal_mult = self.instance.tournament.coalition_score_multiplier

                coals = []
                for f in forms:   
                    coal = f.cleaned_data.get('coalitioned_player', None)
                    if (coal not in [None, '']):
                        coals.append(coal)

                index_f = 0
                total_score = 0
                for f in forms:
                    index_f += 1
                    score = f.cleaned_data.get('tournament_score', 0)
                    total_score += score
                    game_score = f.cleaned_data.get('game_score', None)
                    coal = f.cleaned_data.get('coalitioned_player', None)
                    in_coal = index_f in coals or coal not in [None, '']
                    dominance = f.cleaned_data.get('dominance', None)
                    faction = f.cleaned_data.get('faction', None)
                    is_vagabond = faction is not None and VAGABOND in faction
                    if (game_score is not None):
                        if (coal not in [None, '']):
                            errors.append(
                                ValidationError(
                                _("Player %(player)i cannot both have a game score and be in a coalition."),
                                code="error_score_coal",
                                params={'player' : index_f})) 
                        if (dominance not in [None, '']):
                            errors.append(
                                ValidationError(
                                _("Player %(player)i cannot both play a dominance and have a game score."),
                                code="error_score_dom",
                                params={'player' : index_f})) 
                    if (coal not in [None, ''] and not(is_vagabond)):
                        errors.append(
                            ValidationError(
                            _("Player %(player)i is not a vagabond and cannot play a coalition."),
                            code="error_vb_coal",
                            params={'player' : index_f})) 
                    if (dominance not in [None, ''] and is_vagabond):
                        errors.append(
                            ValidationError(
                            _("Player %(player)i is a vagabond and cannot play a dominance."),
                            code="error_vb_dom",
                            params={'player' : index_f})) 
                    actual_win_score = None
                    if (win_score is not None):
                        actual_win_score = win_score
                        if (coal_mult is not None and index_f in coals):
                            actual_win_score *= coal_mult
                    if (win_score is not None and
                        game_score not in [None, ''] and
                        game_score >= WIN_GAME_SCORE and score != actual_win_score):
                        if (coal_mult is not None):
                            coal_win = win_score*coal_mult
                            errors.append(
                                ValidationError(
                                _("Player %(player)i does not have a correct tournament score.\
                                Possible scores: 0 (for a loss), %(win_score)0.2f (for a win) and %(coal_win)0.2f (for a win in coalition)."),
                                code="error_score",
                                params={'player' : index_f, 'win_score' : win_score, 'coal_win': coal_win})) 
                        else:
                            errors.append(
                                ValidationError(
                                _("Player %(player)i does not have a correct tournament score.\
                                Possible scores: 0 (for a loss) and %(win_score)0.2f (for a win)."),
                                code="error_score",
                                params={'player' : index_f, 'win_score' : win_score})) 

                if (total_score_allowed is not None and total_score != total_score_allowed):
                    errors.append(
                        ValidationError(
                        _("The total score should be %(total)0.2f."),
                        code="error_total_score",
                        params={'total' : total_score_allowed})) 
                if (coalition_allowed is False or three_coal_allowed is False):
                    if (len(coals) >= 1 and coalition_allowed is False):
                        errors.append(
                            ValidationError(
                            _("This tournament does not allow coalitions."),
                            code="error_coal")) 
                    if (len(coals) >= 2 and three_coal_allowed is False):
                        errors.append(
                            ValidationError(
                            _("This tournament does not allow three-way coalitions."),
                            code="error_three_coal")) 
            if (len(errors)):
                raise ValidationError(errors)
        except AttributeError:
            pass
        
