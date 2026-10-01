from django.contrib.auth.models import Permission
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from authentification.models import Player
from authentification.widgets import PlayerWidget
from matchmaking.models import Match, Participant

from .forms import ReportEvidenceFormSet, ReportGeneralForm, ReportMatchForm
from .models import Report, ReportEvidence
from .views import MAX_OPEN_REPORTS_PER_DAY


def make_match(reporter, accused=None, witness=None, **kwargs):
    match = Match.objects.create(**kwargs)
    Participant.objects.create(match=match, player=reporter, turn_order=1)
    if accused is not None:
        Participant.objects.create(match=match, player=accused, turn_order=2)
    if witness is not None:
        Participant.objects.create(match=match, player=witness, turn_order=3)
    return match


class ReportModelTestCase(TestCase):
    def setUp(self):
        self.reporter = Player.objects.create_user('Reporter', 'reporter@test.com', 'test')
        self.accused = Player.objects.create_user('Accused', 'accused@test.com', 'test')
        self.witness = Player.objects.create_user('Witness', 'witness@test.com', 'test')

    def test_self_report_rejected(self):
        report = Report(reporter=self.reporter, reported_player=self.reporter,
                        reason=Report.Reason.TIMED_OUT, description='Timeout.')
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_witness_cannot_be_reporter(self):
        report = Report(reporter=self.reporter, reported_player=self.accused,
                        reference_player=self.reporter,
                        reason=Report.Reason.SIDE_CHAT, description='Side chat.')
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_witness_cannot_be_accused(self):
        report = Report(reporter=self.reporter, reported_player=self.accused,
                        reference_player=self.accused,
                        reason=Report.Reason.SIDE_CHAT, description='Side chat.')
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_unregistered_player_report_needs_no_reported_player(self):
        match = make_match(self.reporter)
        report = Report(reporter=self.reporter, match=match,
                        reason=Report.Reason.GHOSTED,
                        description='GhostPlayerBob sat in seat 4 without registering.')
        report.full_clean()

    def test_resolved_status_requires_moderator(self):
        report = Report(reporter=self.reporter, reported_player=self.accused,
                        reason=Report.Reason.OTHER, description='Other.',
                        status=Report.Status.RESOLVED)
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_evidence_url_unique_per_report(self):
        match = make_match(self.reporter, self.accused)
        report = Report.objects.create(reporter=self.reporter, reported_player=self.accused,
                                       match=match, reason=Report.Reason.OTHER,
                                       description='Other.')
        ReportEvidence.objects.create(report=report, url='https://example.com/a.png')
        with self.assertRaises(ValidationError):
            ReportEvidence(report=report, url='https://example.com/a.png').full_clean()


    def test_both_player_and_description_may_be_filled(self):
        match = make_match(self.reporter, self.accused)
        Report(reporter=self.reporter, reported_player=self.accused, match=match,
               reason=Report.Reason.TIMED_OUT, description='Timeout.').full_clean()

    def test_neither_player_nor_description_rejected(self):
        match = make_match(self.reporter)
        report = Report(reporter=self.reporter, match=match,
                        reason=Report.Reason.TIMED_OUT, description='')
        with self.assertRaises(ValidationError) as raised:
            report.full_clean()
        self.assertIn('description', raised.exception.message_dict)

    def test_whitespace_description_rejected_without_player(self):
        match = make_match(self.reporter)
        report = Report(reporter=self.reporter, match=match,
                        reason=Report.Reason.TIMED_OUT, description='   ')
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_submission_error_still_needs_description_without_player(self):
        match = make_match(self.reporter)
        report = Report(reporter=self.reporter, match=match,
                        reason=Report.Reason.SUBMISSION_ERROR, description='')
        with self.assertRaises(ValidationError) as raised:
            report.full_clean()
        self.assertIn('description', raised.exception.message_dict)



class ReportFormTestCase(TestCase):
    def setUp(self):
        self.reporter = Player.objects.create_user('Reporter', 'reporter@test.com', 'test')
        self.accused = Player.objects.create_user('Accused', 'accused@test.com', 'test')
        self.outsider = Player.objects.create_user('Outsider', 'outsider@test.com', 'test')
        self.match = make_match(self.reporter, self.accused)

    def check_scoped(self, field):
        players = list(ReportMatchForm(match=self.match).fields[field].queryset)
        self.assertIn(self.reporter, players)
        self.assertIn(self.accused, players)
        self.assertNotIn(self.outsider, players)

    def test_player_fields_scoped_to_match(self):
        self.check_scoped('reported_player')
        self.check_scoped('reference_player')

    def test_outsider_rejected_as_reported_player(self):
        form = ReportMatchForm(match=self.match, data={
            'reported_player': self.outsider.pk, 'reason': Report.Reason.OTHER,
            'description': 'Other.'})
        self.assertFalse(form.is_valid())
        self.assertIn('reported_player', form.errors)

    def test_evidence_formset_caps_at_three(self):
        data = {'evidence-TOTAL_FORMS': '4', 'evidence-INITIAL_FORMS': '0',
                'evidence-MIN_NUM_FORMS': '0', 'evidence-MAX_NUM_FORMS': '3'}
        for i in range(4):
            data[f'evidence-{i}-url'] = f'https://example.com/{i}.png'
            data[f'evidence-{i}-caption'] = ''
        self.assertFalse(ReportEvidenceFormSet(data, prefix='evidence').is_valid())

    def test_general_form_player_fields_use_autocomplete(self):
        form = ReportGeneralForm()
        self.assertIsInstance(form.fields['reported_player'].widget, PlayerWidget)
        self.assertIsInstance(form.fields['reference_player'].widget, PlayerWidget)

    def test_general_form_players_not_scoped(self):
        form = ReportGeneralForm()
        self.assertIn(self.accused, form.fields['reported_player'].queryset)
        self.assertIn(self.outsider, form.fields['reported_player'].queryset)


class ReportViewTestCase(TestCase):
    def setUp(self):
        self.reporter = Player.objects.create_user('Reporter', 'reporter@test.com', 'test',
                                                   in_game_name='Reporter', in_game_id=1)
        self.accused = Player.objects.create_user('Accused', 'accused@test.com', 'test',
                                                  in_game_name='Accused', in_game_id=2)
        self.outsider = Player.objects.create_user('Outsider', 'outsider@test.com', 'test',
                                                   in_game_name='Outsider', in_game_id=3)
        self.match = make_match(self.reporter, self.accused)
        self.url = reverse('reports:report_match', kwargs={'match_id': self.match.pk})

    def post_report(self, user, **overrides):
        self.client.force_login(user)
        data = {'reported_player': self.accused.pk, 'reason': Report.Reason.TIMED_OUT,
                'description': 'Timed out on purpose.',
                'evidence-TOTAL_FORMS': '0', 'evidence-INITIAL_FORMS': '0',
                'evidence-MIN_NUM_FORMS': '0', 'evidence-MAX_NUM_FORMS': '3'}
        data.update(overrides)
        return self.client.post(self.url, data, follow=True)

    def test_anonymous_redirected_to_login(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/', response.url)

    def test_non_participant_forbidden(self):
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_participant_can_file_report(self):
        response = self.post_report(self.reporter)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get()
        self.assertEqual(report.reporter, self.reporter)
        self.assertEqual(report.match, self.match)

    def test_closed_match_stays_reportable(self):
        self.match.date_closed = timezone.now()
        self.match.save()
        self.assertEqual(self.post_report(self.reporter).status_code, 200)
        self.assertEqual(Report.objects.count(), 1)

    def test_duplicate_open_report_blocked(self):
        self.post_report(self.reporter)
        response = self.post_report(self.reporter)
        self.assertEqual(Report.objects.count(), 1)
        self.assertContains(response, 'already have an open report')

    def test_match_page_shows_button_to_participant(self):
        self.client.force_login(self.reporter)
        response = self.client.get(self.match.get_absolute_url())
        self.assertContains(response, 'Report an issue')

    def test_match_page_hides_button_from_outsider(self):
        self.client.force_login(self.outsider)
        response = self.client.get(self.match.get_absolute_url())
        self.assertNotContains(response, reverse('reports:report_match',
                                                 kwargs={'match_id': self.match.pk}))

    def test_report_without_player_nor_description_blocked(self):
        response = self.post_report(self.reporter, reported_player='', description='')
        self.assertEqual(Report.objects.count(), 0)


class ReportAdminTestCase(TestCase):
    def setUp(self):
        self.staff = Player.objects.create_user('Staff', 'staff@test.com', 'test',
                                                in_game_name='Staff', in_game_id=9,
                                                is_staff=True, is_superuser=True)
        self.reporter = Player.objects.create_user('Reporter', 'reporter@test.com', 'test')
        self.accused = Player.objects.create_user('Accused', 'accused@test.com', 'test')
        self.match = make_match(self.reporter, self.accused)
        self.report = Report.objects.create(
            reporter=self.reporter, reported_player=self.accused, match=self.match,
            reason=Report.Reason.TIMED_OUT, description='Timeout.')
        self.url = reverse('admin:reports_report_change', args=(self.report.pk,))

    def post_change_button(self, button):
        self.client.force_login(self.staff)
        return self.client.post(self.url, {button: '1'})

    def test_change_form_shows_status_buttons(self):
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        self.assertContains(response, '_mark-resolved')
        self.assertContains(response, '_mark-dismissed')
        self.assertContains(response, '_mark-in-review')

    def test_change_form_resolve_stamps_moderator(self):
        self.post_change_button('_mark-resolved')
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.RESOLVED)
        self.assertEqual(self.report.resolved_by, self.staff)
        self.assertIsNotNone(self.report.resolved_at)

    def test_change_form_dismiss_stamps_moderator(self):
        self.post_change_button('_mark-dismissed')
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.DISMISSED)
        self.assertEqual(self.report.resolved_by, self.staff)

    def test_change_form_in_review_keeps_moderator_empty(self):
        self.post_change_button('_mark-in-review')
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.IN_REVIEW)
        self.assertIsNone(self.report.resolved_by)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReportEmailTestCase(TestCase):
    def setUp(self):
        self.reporter = Player.objects.create_user('Reporter', 'reporter@test.com', 'test',
                                                   in_game_name='Reporter', in_game_id=1)
        self.accused = Player.objects.create_user('Accused', 'accused@test.com', 'test',
                                                  in_game_name='Accused', in_game_id=2)
        self.moderator = Player.objects.create_user('Moderator', 'moderator@test.com', 'test',
                                                    in_game_name='Moderator', in_game_id=4,
                                                    is_staff=True)
        self.plain_staff = Player.objects.create_user('Plain', 'plain@test.com', 'test',
                                                      in_game_name='Plain', in_game_id=5,
                                                      is_staff=True)
        self.match = make_match(self.reporter, self.accused)
        self.url = reverse('reports:report_match', kwargs={'match_id': self.match.pk})

    def grant_view_permission(self, player):
        player.user_permissions.add(Permission.objects.get(
            codename='view_report', content_type__app_label='reports'))

    def post_report(self, **overrides):
        self.client.force_login(self.reporter)
        data = {'reported_player': self.accused.pk, 'reason': Report.Reason.TIMED_OUT,
                'description': 'Timed out on purpose.',
                'evidence-TOTAL_FORMS': '0', 'evidence-INITIAL_FORMS': '0',
                'evidence-MIN_NUM_FORMS': '0', 'evidence-MAX_NUM_FORMS': '3'}
        data.update(overrides)
        self.client.post(self.url, data, follow=True)
        return Report.objects.get()

    def test_email_sent_to_staff_with_view_permission(self):
        self.grant_view_permission(self.moderator)
        report = self.post_report()
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['moderator@test.com'])
        self.assertEqual(email.subject, 'New player report on example.com')
        self.assertIn('Reason: Timed out on purpose', email.body)
        self.assertIn('Reporter: Reporter', email.body)
        self.assertIn('Reported player: Accused', email.body)
        self.assertIn(f'/admin/reports/report/{report.pk}/change/', email.body)
        self.assertIn('http://example.com', email.body)
        self.assertIn('The example.com team', email.body)

    def test_email_lines_omitted_when_empty(self):
        self.grant_view_permission(self.moderator)
        self.post_report(reported_player='', reason=Report.Reason.SUBMISSION_ERROR,
                         description='Submission error.')
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertNotIn('Reported player:', body)
        self.assertNotIn('Witness:', body)
        self.assertIn('Submission error.', body)

    def test_email_includes_witness_and_evidence(self):
        witness = Player.objects.create_user('Witness', 'witness@test.com', 'test',
                                             in_game_name='Witness', in_game_id=3)
        Participant.objects.create(match=self.match, player=witness, turn_order=3)
        self.grant_view_permission(self.moderator)
        self.client.force_login(self.reporter)
        self.client.post(self.url, {
            'reported_player': self.accused.pk, 'reference_player': witness.pk,
            'reason': Report.Reason.TIMED_OUT, 'description': 'Timed out on purpose.',
            'evidence-TOTAL_FORMS': '1', 'evidence-INITIAL_FORMS': '0',
            'evidence-MIN_NUM_FORMS': '0', 'evidence-MAX_NUM_FORMS': '3',
            'evidence-0-url': 'https://example.com/shot.png', 'evidence-0-caption': '',
        }, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn('Witness: Witness+3', body)
        self.assertIn('Evidence:', body)
        self.assertIn('https://example.com/shot.png', body)

    def test_staff_without_permission_gets_no_email(self):
        self.post_report()
        self.assertEqual(len(mail.outbox), 0)

    def test_non_staff_with_permission_gets_no_email(self):
        civilian = Player.objects.create_user('Civilian', 'civilian@test.com', 'test',
                                              in_game_name='Civilian', in_game_id=6)
        self.grant_view_permission(civilian)
        self.post_report()
        self.assertEqual(len(mail.outbox), 0)

    def test_staff_without_email_gets_no_email(self):
        no_email = Player.objects.create_user('NoEmail', '', 'test',
                                              in_game_name='NoEmail', in_game_id=7,
                                              is_staff=True)
        self.grant_view_permission(no_email)
        self.post_report()
        self.assertEqual(len(mail.outbox), 0)


class ReportGeneralViewTestCase(TestCase):
    def setUp(self):
        self.reporter = Player.objects.create_user('Reporter', 'reporter@test.com', 'test',
                                                   in_game_name='Reporter', in_game_id=1)
        self.accused = Player.objects.create_user('Accused', 'accused@test.com', 'test',
                                                  in_game_name='Accused', in_game_id=2)
        self.witness = Player.objects.create_user('Witness', 'witness@test.com', 'test',
                                                  in_game_name='Witness', in_game_id=3)
        self.url = reverse('reports:report')

    def post_report(self, user, **overrides):
        self.client.force_login(user)
        data = {'reported_player': self.accused.pk, 'reference_player': self.witness.pk,
                'reason': Report.Reason.OTHER, 'description': 'Something went wrong.',
                'evidence-TOTAL_FORMS': '0', 'evidence-INITIAL_FORMS': '0',
                'evidence-MIN_NUM_FORMS': '0', 'evidence-MAX_NUM_FORMS': '3'}
        data.update(overrides)
        return self.client.post(self.url, data, follow=True)

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/', response.url)

    def test_form_renders_with_autocomplete_widgets(self):
        self.client.force_login(self.reporter)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'django_select2')

    def test_report_is_filed_without_match(self):
        response = self.post_report(self.reporter)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get()
        self.assertIsNone(report.match)
        self.assertEqual(report.reporter, self.reporter)
        self.assertEqual(report.reported_player, self.accused)
        self.assertEqual(report.reference_player, self.witness)

    def test_description_only_report_allowed(self):
        self.post_report(self.reporter, reported_player='', reference_player='',
                         description='The homepage layout is broken.')
        report = Report.objects.get()
        self.assertIsNone(report.match)
        self.assertIsNone(report.reported_player)

    def test_report_without_player_nor_description_blocked(self):
        self.post_report(self.reporter, reported_player='', description='')
        self.assertEqual(Report.objects.count(), 0)

    def test_duplicate_open_report_blocked(self):
        self.post_report(self.reporter)
        response = self.post_report(self.reporter)
        self.assertEqual(Report.objects.count(), 1)
        self.assertContains(response, 'already have an open report')

    def test_rate_limit_applies(self):
        for i in range(MAX_OPEN_REPORTS_PER_DAY):
            Report.objects.create(reporter=self.reporter, reason=Report.Reason.OTHER,
                                  description=f'Existing report {i}.')
        response = self.post_report(self.reporter)
        self.assertEqual(Report.objects.count(), MAX_OPEN_REPORTS_PER_DAY)
        self.assertContains(response, 'too many reports')

    def test_success_redirects_home(self):
        self.client.force_login(self.reporter)
        response = self.client.post(self.url, {
            'reported_player': '', 'reference_player': '',
            'reason': Report.Reason.OTHER, 'description': 'Something went wrong.',
            'evidence-TOTAL_FORMS': '0', 'evidence-INITIAL_FORMS': '0',
            'evidence-MIN_NUM_FORMS': '0', 'evidence-MAX_NUM_FORMS': '3'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


