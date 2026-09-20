from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from more_admin_filters.filters import MultiSelectRelatedFilter

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Report, ReportEvidence


class ReportEvidenceInline(admin.TabularInline):
    model = ReportEvidence
    extra = 0


CHANGE_STATUS_BUTTONS = {
    '_mark-in-review': Report.Status.IN_REVIEW,
    '_mark-resolved': Report.Status.RESOLVED,
    '_mark-dismissed': Report.Status.DISMISSED,
}


class ReportPlayerInlineBase(admin.TabularInline):
    model = Report
    extra = 0
    readonly_fields = ['report_link', 'reason', 'match', 'status', 'created']
    fields = ['report_link', 'reason', 'match', 'status', 'created']
    can_delete = False

    def get_admin_url(self, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse('admin:reports_%s_change' % content_type.model, args=(obj.id,))

    def report_link(self, report):
        url = self.get_admin_url(report)
        return mark_safe("<a href='{}'>{}</a>".format(url, report))
    report_link.short_description = _('report')

    def has_add_permission(self, request, obj=None):
        return False


class ReportedPlayerInline(ReportPlayerInlineBase):
    fk_name = 'reported_player'
    verbose_name = _('report filed against this player')
    verbose_name_plural = _('reports filed against this player')


class FiledReportInline(ReportPlayerInlineBase):
    fk_name = 'reporter'
    verbose_name = _('report filed by this player')
    verbose_name_plural = _('reports filed by this player')


class MatchReportInline(ReportPlayerInlineBase):
    fk_name = 'match'
    verbose_name = _('report filed on this match')
    verbose_name_plural = _('reports filed on this match')

    readonly_fields = ['report_link', 'reason', 'reported_player', 'status', 'created']
    fields = ['report_link', 'reason', 'reported_player', 'status', 'created']


class ReferencedReportInline(ReportPlayerInlineBase):
    fk_name = 'reference_player'
    verbose_name = _('report referencing this player as witness')
    verbose_name_plural = _('reports referencing this player as witness')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = [ReportEvidenceInline]
    list_display = ['status', 'reason', 'reported_player', 'match',
                    'reference_player', 'reporter', 'created']
    list_filter = [('status', admin.ChoicesFieldListFilter),
                   ('reason', admin.ChoicesFieldListFilter),
                   ('match__tournament', MultiSelectRelatedFilter)]
    search_fields = ['reported_player__username', 'reported_player__in_game_name',
                     'reported_player__discord_name', 'reporter__username',
                     'match__title', 'description']
    autocomplete_fields = ['reporter', 'reported_player', 'match',
                           'reference_player', 'resolved_by']
    readonly_fields = ['created', 'modified']
    actions = ['mark_in_review', 'mark_resolved', 'mark_dismissed']
    change_form_template = 'admin/reports/report/change_form.html'

    def apply_status(self, request, report, status):
        report.status = status
        if status in (Report.Status.RESOLVED, Report.Status.DISMISSED):
            report.resolved_by = request.user
            report.resolved_at = timezone.now()
        report.save(update_fields=['status', 'resolved_by', 'resolved_at', 'modified'])
        messages.success(request, _('Report marked as %(status)s.') % {
            'status': Report.Status(status).label})

    def set_final_status(self, request, queryset, status):
        queryset.update(status=status, resolved_by=request.user, resolved_at=timezone.now())

    @admin.action(description=_('Mark as in review'))
    def mark_in_review(self, request, queryset):
        queryset.update(status=Report.Status.IN_REVIEW)

    @admin.action(description=_('Mark as resolved'))
    def mark_resolved(self, request, queryset):
        self.set_final_status(request, queryset, Report.Status.RESOLVED)

    @admin.action(description=_('Mark as dismissed'))
    def mark_dismissed(self, request, queryset):
        self.set_final_status(request, queryset, Report.Status.DISMISSED)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST' and object_id is not None:
            for button, status in CHANGE_STATUS_BUTTONS.items():
                if button in request.POST:
                    report = self.get_object(request, object_id)
                    if report is not None:
                        self.apply_status(request, report, status)
                    return HttpResponseRedirect(request.path)
        return super().changeform_view(request, object_id, form_url, extra_context)
