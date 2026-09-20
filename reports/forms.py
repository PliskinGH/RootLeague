from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Report, ReportEvidence


class ReportMatchForm(forms.ModelForm):
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
        help_texts = {
            'reported_player': _('Match participant, if registered. Leave empty for an '
                                 'unregistered player (but give their discord name in the '
                                 'description) or if the report is about submission errors.'),
            'description': _('Describe what happened. If the reported player is not registered, '
                             'state their discord name here.'),
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
