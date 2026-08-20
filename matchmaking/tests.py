from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from . import models
from authentification.models import Player
from league.models import Tournament

# Create your tests here.

class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

class MatchDetailslPageTestCase(TestCase):

    # ran before each test.
    def setUp(self):
        models.Match.objects.create(title="Test match")
        self.match = models.Match.objects.get(title='Test match')

    # test that detail page returns a 200 if the match exists
    def test_details_page_returns_200(self):
        match_id = self.match.id
        response = self.client.get(reverse('match:detail', args=(match_id,)))
        self.assertEqual(response.status_code, 200)

    # test that detail page returns a 404 if the item match does not exist
    def test_details_page_returns_404(self):
        match_id = self.match.id + 1
        response = self.client.get(reverse('match:detail', args=(match_id,)))
        self.assertEqual(response.status_code, 404)

class NewMatchPageTestCase(TestCase):
    
    def setUp(self):
        self.user = Player.objects.create_user('TestUser', 'test@test.com', 'test')
        self.tournament = Tournament.objects.create(name='Test Tournament')
        self.client.login(username='TestUser', password='test')

    # test that a new match is made
    def test_new_match_is_registered(self):
        old_match_count = models.Match.objects.count()
        self.client.post(reverse('match:register'), {
            'title': 'new game',
            'board_map': models.MAP_AUTUMN,
            'tournament': self.tournament.pk,
            "participants-TOTAL_FORMS": "1",
            "participants-INITIAL_FORMS": "0",}
        )
        new_match_count = models.Match.objects.count()
        self.assertEqual(new_match_count, old_match_count+1)

    # test that a new match is not made
    def test_new_match_is_not_registered(self):
        old_match_count = models.Match.objects.count()
        self.client.post(reverse('match:register'), {
            'title': 'new game',
            'board_map': 'test'
        })
        new_match_count = models.Match.objects.count()
        self.assertEqual(new_match_count, old_match_count)


class MatchApiTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Player.objects.create_user('ApiUser', 'api@test.com', 'test')
        self.other_user = Player.objects.create_user('OtherUser', 'other@test.com', 'test')
        self.tournament = Tournament.objects.create(name='API Tournament')
        permissions = Permission.objects.filter(
            content_type__app_label='matchmaking',
            codename__in=('drf_add_match', 'drf_change_match', 'drf_delete_match'),
        )
        self.user.user_permissions.add(*permissions)

    def test_create_requires_add_permission(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(reverse('match-list'), {
            'title': 'API match',
            'tournament': self.tournament.pk,
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_create_sets_submitter(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('match-list'), {
            'title': 'API match',
            'tournament': self.tournament.pk,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        match = models.Match.objects.get(title='API match')
        self.assertEqual(match.submitted_by, self.user)

    def test_update_requires_editable_match(self):
        match = models.Match.objects.create(
            title='API match',
            tournament=self.tournament,
            submitted_by=self.other_user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse('match-detail', args=(match.pk,)),
            {'title': 'Updated API match'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_update_allowed_for_submitter_with_change_permission(self):
        match = models.Match.objects.create(
            title='API match',
            tournament=self.tournament,
            submitted_by=self.user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse('match-detail', args=(match.pk,)),
            {'title': 'Updated API match'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        match.refresh_from_db()
        self.assertEqual(match.title, 'Updated API match')

    def test_delete_requires_delete_permission(self):
        match = models.Match.objects.create(
            title='API match',
            tournament=self.tournament,
            submitted_by=self.user,
        )
        self.client.force_authenticate(self.other_user)
        response = self.client.delete(reverse('match-detail', args=(match.pk,)))
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(self.user)
        response = self.client.delete(reverse('match-detail', args=(match.pk,)))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(models.Match.objects.filter(pk=match.pk).exists())

    def test_open_matches_are_visible_to_change_permission_users(self):
        models.Match.objects.create(title='Open API match', tournament=self.tournament)
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        self.client.force_authenticate(self.other_user)
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_open_matches_are_visible_to_delete_permission_users(self):
        delete_user = Player.objects.create_user('DeleteUser', 'delete@test.com', 'test')
        delete_permission = Permission.objects.get(
            content_type__app_label='matchmaking',
            codename='drf_delete_match',
        )
        delete_user.user_permissions.add(delete_permission)
        models.Match.objects.create(title='Open API match', tournament=self.tournament)

        self.client.force_authenticate(delete_user)
        response = self.client.get(reverse('match-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)