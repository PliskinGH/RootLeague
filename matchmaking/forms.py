from django.forms import Form, ModelForm, ChoiceField, BooleanField, BaseInlineFormSet, NumberInput
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Fieldset, Layout, Row, HTML
from crispy_formset_modal.helper import ModalEditFormHelper
from crispy_formset_modal.layout import ModalEditLayout, ModalEditFormsetLayout

from .models import Match, Participant
from league.constants import MAX_NUMBER_OF_PLAYERS_IN_MATCH, VAGABOND, WIN_GAME_SCORE, TURN_TIMING_URLS, DECKS_URLS, MAPS_URLS
from league.models import Tournament
from authentification.forms import PlayerWidget
from misc.forms import NonPrimarySubmit, IconSelect

PLAYERS_SEATS = [(i,i) for i in range(1, MAX_NUMBER_OF_PLAYERS_IN_MATCH + 1)]
PLAYERS_SEATS = [(None, '------')] + PLAYERS_SEATS

class MatchForm(ModelForm):
    closed = BooleanField(required=False, initial=True, label=_("Final Results"))
    submit_text = _("Register match")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.instance and (self.fields['tournament'].queryset.count() >= 1)):
            self.fields['tournament'].queryset = Tournament.objects.exclude(Q(active_in_league = None) & ~Q(league = None))
        if ('hirelings_a' in self.fields):
            self.fields['hirelings_a'].label = False
        if ('hirelings_b' in self.fields):
            self.fields['hirelings_b'].label = False
        if ('hirelings_c' in self.fields):
            self.fields['hirelings_c'].label = False
        if ('landmark_a' in self.fields):
            self.fields['landmark_a'].label = False
        if ('landmark_b' in self.fields):
            self.fields['landmark_b'].label = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("title", css_class='col-md-8'), Column("tournament", css_class='col-md-4')),
            Row(Column("game_setup", css_class='col-md-6'), Column("undrafted_faction", css_class='col-md-6')),
            Row(Column("turn_timing", css_class='col-md-3'), Column("table_talk_url", css_class='col-md-9')),
            Row(Column("deck", css_class='col-md-4'), Column("board_map", css_class='col-md-4'), Column("random_suits", css_class='col-md-4')),
            Fieldset("Hirelings", Row(Column("hirelings_a", css_class='col-md-4'), Column("hirelings_b", css_class='col-md-4'), Column("hirelings_c", css_class='col-md-4')))
            if ('hirelings_a' in self.fields or 'hirelings_b' in self.fields or 'hirelings_c' in self.fields) else HTML(""),
            Fieldset("Landmarks", Row(Column("landmark_a", css_class='col-md-6'), Column("landmark_b", css_class='col-md-6')))
            if ('landmark_a' in self.fields or 'landmark_b' in self.fields) else HTML(""),
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
            Row(Column(NonPrimarySubmit("submit", self.submit_text, css_class="btn-outline-secondary"), css_class='col'), Column("closed", css_class='col'), css_class='row-cols-auto'),
        )

    def clean(self):
        super().clean()
        tournament = self.cleaned_data.get('tournament', None)
        is_closed = self.cleaned_data.get('closed', False)
        game_setup = self.cleaned_data.get('game_setup', '')
        board_map = self.cleaned_data.get('board_map', '')
        deck = self.cleaned_data.get('deck', '')
        if (is_closed):
            # Required fields for closed games
            if (board_map in EMPTY_VALUES):
                self.add_error('board_map',
                               ValidationError(
                                _("A map is required for closed games.")))
            if (deck in EMPTY_VALUES):
                self.add_error('deck',
                               ValidationError(
                                _("A deck is required for closed games.")))
        if (tournament is not None):
            tournament_setup = getattr(tournament, 'game_setup', '')
            tournament_map = getattr(tournament, 'board_map', '')
            tournament_deck = getattr(tournament, 'deck', '')
            if (tournament_setup not in EMPTY_VALUES and
                game_setup != tournament_setup):
                self.add_error('game_setup',
                               ValidationError(
                                _("The setup chosen is different from \
                                  the one of the tournament (%(setup)s)."),
                                  params={'setup' : tournament.get_game_setup_display()}))
            if (tournament_map not in EMPTY_VALUES and
                board_map != tournament_map):
                self.add_error('board_map',
                               ValidationError(
                                _("The chosen map is different from \
                                  the one of the tournament (%(map)s)."),
                                  params={'map' : tournament.get_board_map_display()}))
            if (tournament_deck not in EMPTY_VALUES and
                deck != tournament_deck):
                self.add_error('deck',
                               ValidationError(
                                _("The chosen deck is different from \
                                  the one of the tournament (%(deck)s)."),
                                  params={'deck' : tournament.get_deck_display()}))
    
    class Meta:
        model = Match
        fields = [
                   'title',
                   'tournament',
                   'turn_timing',
                   'table_talk_url',
                   'game_setup',
                   'undrafted_faction',
                   'deck',
                   'board_map',
                   'random_suits',
                #    'hirelings_a',
                #    'hirelings_b',
                #    'hirelings_c',
                #    'landmark_a',
                #    'landmark_b',
                  ]
        # widgets = {
        #     'turn_timing' : IconSelect(choices_urls=TURN_TIMING_URLS),
        #     'deck' : IconSelect(choices_urls=DECKS_URLS),
        #     'board_map' : IconSelect(choices_urls=MAPS_URLS)
        #     }

class UpdateMatchForm(MatchForm):
    submit_text = _("Update match")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.instance and self.instance.date_closed is None):
            self.fields['closed'].initial = False

class DeleteMatchForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            NonPrimarySubmit("submit", _("Confirm"), css_class="btn-outline-danger"),
        )

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
            'player' : PlayerWidget,
            'tournament_score' : NumberInput(attrs={'step': 0.5}),
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
        if self.instance and self.instance.pk is not None:
            coalitioned_participant = self.instance.coalition
            match = self.instance.match
            in_coalition = False
            index_coalitioned = 0
            if (coalitioned_participant is not None and match is not None):
                for participant in match.participants.order_by('turn_order'):
                    index_coalitioned += 1
                    if (participant == coalitioned_participant):
                        in_coalition = True
                        break
            if (in_coalition):
                self.fields['coalitioned_player'].initial = index_coalitioned

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

            is_closed = False   
            coalition_allowed = None
            three_coal_allowed = None
            total_score_allowed = None
            win_score = None
            coal_mult = None

            coals = []
            turn_orders = set()
            factions = set()
            players = set()
            for f in forms:
                if (f.data.get('closed', None) == 'on'):
                    is_closed = True
                coal = f.cleaned_data.get('coalitioned_player', None)
                if (coal not in EMPTY_VALUES):
                    coals.append(int(coal))
                turn_order = f.cleaned_data.get('turn_order', None)
                turn_orders.add(turn_order)
                faction = f.cleaned_data.get('faction', None)
                factions.add(faction)
                player = f.cleaned_data.get('player', None)
                players.add(player)

            nb_participants = len(forms)
            legal_turn_orders = {i for i in range(1, nb_participants+1)}
            if (is_closed and turn_orders != legal_turn_orders):
                errors.append(
                    ValidationError(
                    _("Turn orders are wrong.\
                       Please check again that they are consistent and\
                       between %(min_nb_participants)d and %(nb_participants)d."),
                    code="error_turn_order",
                    params={'nb_participants' : nb_participants,
                            'min_nb_participants' : 1}))
            if (is_closed and len(factions) != nb_participants):
                errors.append(
                    ValidationError(
                    _("Factions are wrong.\
                       Please check again that all participants have a defined faction\
                       with no duplicates."),
                    code="error_factions"))
            if (is_closed and len(players) != nb_participants):
                errors.append(
                    ValidationError(
                    _("Something is wrong with the submitted players.\
                       Please check again that they are all defined\
                       with no duplicates."),
                    code="error_players"))

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

            index_f = 0
            total_score = 0
            for f in forms:
                index_f += 1
                player = f.cleaned_data.get('player', None)
                score = f.cleaned_data.get('tournament_score', None)
                if (score not in EMPTY_VALUES):
                    total_score += score
                game_score = f.cleaned_data.get('game_score', None)
                coal = f.cleaned_data.get('coalitioned_player', None)
                in_coal = index_f in coals or coal not in EMPTY_VALUES
                in_3way_coal = index_f in coals and coal not in EMPTY_VALUES
                dominance = f.cleaned_data.get('dominance', None)
                faction = f.cleaned_data.get('faction', None)
                is_vagabond = faction not in EMPTY_VALUES and VAGABOND in faction
                if (player in EMPTY_VALUES and is_closed):
                    # Required field if game closed
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i must be defined, if the game is closed."),
                        code="error_required_splayer",
                        params={'index_player' : index_f}))
                if (score in EMPTY_VALUES and is_closed):
                    # Required field if game closed
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i must have a defined tournament score, if the game is closed."),
                        code="error_required_score",
                        params={'index_player' : index_f}))
                if (faction in EMPTY_VALUES and is_closed):
                    # Required field if game closed
                    errors.append(
                        ValidationError(
                        _("A faction must be defined for player %(index_player)i if the game is closed."),
                        code="error_required_faction",
                        params={'index_player' : index_f}))
                if (game_score in EMPTY_VALUES and
                    dominance in EMPTY_VALUES and
                    coal in EMPTY_VALUES and
                    is_closed):
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i must have a defined game score, coalition or dominance, if the game is closed."),
                        code="error_score_coal_dom",
                        params={'index_player' : index_f}))
                if (game_score not in EMPTY_VALUES):
                    if (coal not in EMPTY_VALUES):
                        errors.append(
                            ValidationError(
                            _("Player %(index_player)i cannot both have a game score and be in a coalition."),
                            code="error_score_coal",
                            params={'index_player' : index_f})) 
                    if (dominance not in EMPTY_VALUES):
                        errors.append(
                            ValidationError(
                            _("Player %(index_player)i cannot both play a dominance and have a game score."),
                            code="error_score_dom",
                            params={'index_player' : index_f})) 
                if (coal not in EMPTY_VALUES and not(is_vagabond)):
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i is not a vagabond and cannot play a coalition."),
                        code="error_vb_coal",
                        params={'index_player' : index_f})) 
                if (dominance not in EMPTY_VALUES and is_vagabond):
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i is a vagabond and cannot play a dominance."),
                        code="error_vb_dom",
                        params={'index_player' : index_f})) 
                actual_win_score = None
                if (win_score not in EMPTY_VALUES):
                    actual_win_score = win_score
                    if (coal_mult is not None and
                        in_coal):
                        actual_win_score *= coal_mult
                if (is_closed and
                    win_score not in EMPTY_VALUES and
                    ((game_score not in EMPTY_VALUES and
                    game_score >= WIN_GAME_SCORE and score != actual_win_score) or
                    (coal not in EMPTY_VALUES and score != actual_win_score and score != 0))):
                    if (coal_mult is not None):
                        coal_win = win_score*coal_mult
                        errors.append(
                            ValidationError(
                            _("Player %(index_player)i does not have a correct tournament score.\
                            Possible scores: 0 (for a loss), %(win_score)0.2f (for a win) and %(coal_win)0.2f (for a win in coalition)."),
                            code="error_score",
                            params={'index_player' : index_f, 'win_score' : win_score, 'coal_win': coal_win})) 
                    else:
                        errors.append(
                            ValidationError(
                            _("Player %(index_player)i does not have a correct tournament score.\
                            Possible scores: 0 (for a loss) and %(win_score)0.2f (for a win)."),
                            code="error_score",
                            params={'index_player' : index_f, 'win_score' : win_score})) 
                if (is_closed and in_coal and coalition_allowed is False):
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i is in a coalition\
                          but this tournament does not allow coalitions."),
                        code="error_coal",
                        params={'index_player' : index_f}))
                if (is_closed and in_3way_coal and three_coal_allowed is False):
                    errors.append(
                        ValidationError(
                        _("Player %(index_player)i is in a three-way coalition\
                          but this tournament does not allow three-way coalitions."),
                        code="error_3way_coal",
                        params={'index_player' : index_f}))

            if (is_closed and
                total_score_allowed not in EMPTY_VALUES and
                total_score != total_score_allowed):
                errors.append(
                    ValidationError(
                    _("The total score should be %(total)0.2f."),
                    code="error_total_score",
                    params={'total' : total_score_allowed})) 
                    
            if (len(errors)):
                raise ValidationError(errors)
        except AttributeError:
            pass

class ParticipantAdminForm(ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.instance and self.instance.pk is not None and self.instance.match.pk is not None):
            self.fields['coalition'].queryset = self.instance.match.participants.exclude(pk=self.instance.pk)
        else:
            self.fields['coalition'].queryset = Participant.objects.none()
        self.fields['player'].widget.can_add_related = False
        self.fields['player'].widget.can_delete_related = False
        self.fields['coalition'].widget.can_add_related = False
        self.fields['coalition'].widget.can_delete_related = False

class MatchAdminForm(ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submitted_by'].widget.can_add_related = False
        self.fields['submitted_by'].widget.can_delete_related = False
        self.fields['tournament'].widget.can_delete_related = False
