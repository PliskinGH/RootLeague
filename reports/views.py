from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView

from authentification.models import Player
from matchmaking.models import Match

from .forms import ReportEvidenceFormSet, ReportGeneralForm, ReportMatchForm
from .models import Report

MAX_OPEN_REPORTS_PER_DAY = 5


class ReportCreateBaseView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Report
    template_name = 'reports/report_form.html'
    success_message = _('Your report was submitted. Admins will review it.')
    success_url = reverse_lazy('home')
    match = None

    def get_context_data(self, **kwargs):
        if 'evidence_formset' not in kwargs:
            kwargs['evidence_formset'] = ReportEvidenceFormSet(prefix='evidence')
        kwargs['upper_title'] = _('Report an issue')
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        evidence_formset = ReportEvidenceFormSet(request.POST, prefix='evidence')
        if form.is_valid() and evidence_formset.is_valid():
            return self.forms_valid(form, evidence_formset)
        return self.forms_invalid(form, evidence_formset)

    def forms_valid(self, form, evidence_formset):
        form.instance.reporter = self.request.user
        form.instance.match = self.match
        self.check_duplicate(form)
        if form.errors:
            return self.forms_invalid(form, evidence_formset)
        self.check_rate_limit(form)
        if form.errors:
            return self.forms_invalid(form, evidence_formset)
        self.object = form.save()
        evidence_formset.instance = self.object
        evidence_formset.save()
        self.notify_moderators()
        return super().form_valid(form)

    def forms_invalid(self, form, evidence_formset):
        return self.render_to_response(
            self.get_context_data(form=form, evidence_formset=evidence_formset))

    def check_duplicate(self, form):
        reported = form.cleaned_data.get('reported_player')
        exists = Report.objects.filter(
            reporter=self.request.user, match=self.match,
            reported_player=reported, status=Report.Status.OPEN).exists()
        if exists:
            if self.match is not None:
                message = _('You already have an open report for this player in this match.')
            else:
                message = _('You already have an open report for this player.')
            form.add_error(None, message)

    def check_rate_limit(self, form):
        since = timezone.now() - timedelta(days=1)
        count = Report.objects.filter(reporter=self.request.user, created__gte=since).count()
        if count >= MAX_OPEN_REPORTS_PER_DAY:
            form.add_error(None, _('You submitted too many reports recently. Please wait before filing another.'))

    def notify_moderators(self):
        site = get_current_site(self.request)
        context = {
            'report': self.object,
            'site_name': site.name,
            'domain': site.domain,
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
        recipients = [player.email for player in Player.objects.filter(is_staff=True)
                      .exclude(email__in=[None, ''])
                      if player.has_perm('reports.view_report')]
        if recipients:
            subject = ''.join(render_to_string(
                'reports/report_email_subject.txt', context).splitlines())
            message = render_to_string('reports/report_email.html', context)
            send_mail(subject, message, None, recipients, fail_silently=True)


class ReportMatchCreateView(ReportCreateBaseView):
    form_class = ReportMatchForm
    pk_url_kwarg = 'match_id'

    def dispatch(self, request, *args, **kwargs):
        self.match = get_object_or_404(Match, pk=kwargs.get(self.pk_url_kwarg))
        if (request.user.is_authenticated
                and not self.match.is_reportable_by(request.user)):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['match'] = self.match
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['match'] = self.match
        kwargs['lower_title'] = str(self.match)
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return self.match.get_absolute_url()


class ReportCreateView(ReportCreateBaseView):
    form_class = ReportGeneralForm

    def get_context_data(self, **kwargs):
        kwargs['lower_title'] = get_current_site(self.request).name
        return super().get_context_data(**kwargs)
