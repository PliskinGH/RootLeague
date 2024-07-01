from django.test import TestCase
from django.urls import reverse

from .models import Match

# Create your tests here.

class IndexPageTestCase(TestCase):
    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

class MatchDetailslPageTestCase(TestCase):

    # ran before each test.
    def setUp(self):
        Match.objects.create(title="Test match")
        self.match = Match.objects.get(title='Test match')

    # test that detail page returns a 200 if the match exists
    def test_details_page_returns_200(self):
        match_id = self.match.id
        response = self.client.get(reverse('matchmaking:match_details', args=(match_id,)))
        self.assertEqual(response.status_code, 200)

    # test that detail page returns a 404 if the item match does not exist
    def test_details_page_returns_404(self):
        match_id = self.match.id + 1
        response = self.client.get(reverse('matchmaking:match_details', args=(match_id,)))
        self.assertEqual(response.status_code, 404)

class NewMatchPageTestCase(TestCase):

    # test that a new match is made
    def test_new_match_is_registered(self):
        old_match_count = Match.objects.count()
        self.client.post(reverse('matchmaking:new_match'), {
            'title': 'new game',
            'board_map': 'autumn'
        })
        new_match_count = Match.objects.count()
        self.assertEqual(new_match_count, old_match_count+1)

    # test that a new match is not made
    # def test_new_match_is_not_registered(self):
    #     old_match_count = Match.objects.count()
    #     self.client.post(reverse('matchmaking:new_match'), {
    #         'title': 'new game',
    #         'board_map': 'invalid'
    #     })
    #     new_match_count = Match.objects.count()
    #     self.assertEqual(new_match_count, old_match_count)