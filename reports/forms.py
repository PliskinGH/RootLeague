from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from authentification.widgets import PlayerWidget

from .models import Report, ReportEvidence

MAX_DESCRIPTION_LENGTH = 5000


class ReportBaseForm(forms.ModelForm):
    """Shared fields and match-aware validation for report forms."""

    def __init__(self, *args, match=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.match = match
        if match is not None:
            players = match.players
            self.fields['reported_player'].queryset = players
            self.fields['reference_player'].queryset = players

    class Meta:
        model = Report
        fields = ['reported_player', 'reference_player', 'reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_reported_player(self):
        player = self.cleaned_data.get('reported_player')
        if player is not None and self.match is not None:
            if not player.participations.filter(match=self.match).exists():
                raise ValidationError(_('The reported player is not part of this match.'))
        return player

    def clean_reference_player(self):
        player = self.cleaned_data.get('reference_player')
        if player is not None and self.match is not None:
            if not player.participations.filter(match=self.match).exists():
                raise ValidationError(_('The witness is not part of this match.'))
        return player

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise ValidationError(_('Keep the description under %(limit)s characters.')
                                  % {'limit': MAX_DESCRIPTION_LENGTH})
        return description


class ReportMatchForm(ReportBaseForm):
    """Report scoped to the participants of one match."""

    void_match = forms.BooleanField(required=False, label=_('Void the match'),
                                    help_text=_('Only admins can undo a void.'))

    def __init__(self, *args, allow_void=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not allow_void:
            self.fields.pop('void_match', None)


class ReportGeneralForm(ReportBaseForm):
    """Report filed without a match, with roster-wide player autocomplete."""

    class Meta(ReportBaseForm.Meta):
        widgets = dict(ReportBaseForm.Meta.widgets,
                       reported_player=PlayerWidget,
                       reference_player=PlayerWidget)
        help_texts = {
            'reported_player': _('Leave empty if this report is not about a registered '
                                 'player.'),
        }


class ReportEvidenceForm(forms.ModelForm):
    class Meta:
        model = ReportEvidence
        fields = ['url', 'caption']


ReportEvidenceFormSet = inlineformset_factory(
    Report, ReportEvidence,
    form=ReportEvidenceForm,
    extra=3, max_num=3, validate_max=True,
    fk_name='report',
)
