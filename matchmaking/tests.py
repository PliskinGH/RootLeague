from django.test import TestCase
from django.urls import reverse

from . import models
from authentification.models import Player
from league.models import Tournament

# Create your tests here.

class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class MatchDetailslPageTestCase(TestCase):

    # ran before each test.
    def setUp(self):
        models.Match.objects.create(title="Test match")
        self.match = models.Match.objects.get(title='Test match')

    # test that detail page returns a 200 if the match exists
    def test_details_page_returns_200(self):
        match_id = self.match.id
        response = self.client.get(reverse('match:match_detail', args=(match_id,)))
        self.assertEqual(response.status_code, 200)

    # test that detail page returns a 404 if the item match does not exist
    def test_details_page_returns_404(self):
        match_id = self.match.id + 1
        response = self.client.get(reverse('match:match_detail', args=(match_id,)))
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