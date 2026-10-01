from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    """Player-filed infraction report on a match participant."""

    class Reason(models.TextChoices):
        TIMED_OUT = 'timed_out', _('Timed out on purpose')
        INAPPROPRIATE_RESIGN = 'inappropriate_resign', _('Inappropriately resigned')
        SIDE_CHAT = 'side_chat', _('Participated in private/side chats about game strategy')
        BROKE_RULE_TO_VOID = 'broke_rule_to_void', _('Intentionally broke a league rule in order to void game')
        SUBMITTED_VOID_RESULT = 'submitted_void_result', _('Intentionally submitted a game result that was void')
        GHOSTED = 'ghosted', _('Participated in league game but did not register (i.e., ghosted)')
        COMMUNITY_GUIDELINES = 'community_guidelines', _('Did not comply with the WW Community Guidelines')
        SUBMISSION_ERROR = 'submission_error', _('Match submission contains errors (details in description)')
        OTHER = 'other', _('Other')

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_REVIEW = 'in_review', _('In review')
        RESOLVED = 'resolved', _('Resolved')
        DISMISSED = 'dismissed', _('Dismissed')

    reporter = models.ForeignKey('authentification.Player', on_delete=models.SET_NULL,
                                 null=True, related_name='filed_reports',
                                 verbose_name=_('reporter'))
    reported_player = models.ForeignKey('authentification.Player', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='reports_against',
                                        verbose_name=_('reported player'),
                                        help_text=_('Match participant, if registered. Leave empty for an '
                                                    'unregistered player or if the report is about ' \
                                                    'submission errors.'))
    match = models.ForeignKey('matchmaking.Match', on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='reports',
                              verbose_name=_('match'))
    reference_player = models.ForeignKey('authentification.Player', on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='referenced_in_reports',
                                         verbose_name=_('witness / reference player'),
                                         help_text=_('Player who can corroborate the report.'))
    reason = models.CharField(max_length=30, choices=Reason.choices,
                              verbose_name=_('reason'))
    description = models.TextField(blank=True, verbose_name=_('description'),
                                   help_text=_('Describe what happened. If the issue is about ' \
                                               'an unregistered player, '
                                               'state their discord name here.'))
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.OPEN, verbose_name=_('status'))
    moderator_notes = models.TextField(blank=True, verbose_name=_('moderator notes'))
    resolved_by = models.ForeignKey('authentification.Player', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='resolved_reports',
                                    verbose_name=_('resolved by'))
    resolved_at = models.DateTimeField(null=True, blank=True,
                                       verbose_name=_('resolved at'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('modified'))

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['reported_player']),
            models.Index(fields=['match']),
        ]

    def __str__(self):
        return _('%(reason)s report by %(reporter)s') % {
            'reason': self.get_reason_display(), 'reporter': self.reporter}

    def clean(self):
        super().clean()
        if self.reported_player_id is None and not (self.description or '').strip():
            raise ValidationError({
                'description': _('State the details of the report in the description, '
                                 'or pick a reported player.')})
        if (self.reported_player_id is not None and self.reporter_id is not None
                and self.reported_player_id == self.reporter_id):
            raise ValidationError({'reported_player': _('You cannot report yourself.')})
        for field in ('reported_player', 'reference_player'):
            other = getattr(self, field)
            if (other is not None and self.reporter_id is not None
                    and other.pk == self.reporter_id and field == 'reference_player'):
                raise ValidationError({field: _('The reference player cannot be the reporter.')})
        if (self.reference_player is not None and self.reported_player is not None
                and self.reference_player.pk == self.reported_player.pk):
            raise ValidationError({'reference_player': _('The reference player cannot be the reported player.')})
        if self.status in (self.Status.RESOLVED, self.Status.DISMISSED):
            if self.resolved_by_id is None or self.resolved_at is None:
                raise ValidationError(_('Resolved reports require a moderator and a resolution date.'))


class ReportEvidence(models.Model):
    """Screenshot URL backing a report."""

    report = models.ForeignKey(Report, on_delete=models.CASCADE,
                               related_name='evidences', verbose_name=_('report'))
    url = models.URLField(max_length=1000, verbose_name=_('URL'))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_('caption'))

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['report', 'url'], name='unique_evidence_url_per_report'),
        ]

    def __str__(self):
        return self.caption or self.url
