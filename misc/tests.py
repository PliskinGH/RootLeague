from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.flatpages.models import FlatPage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from authentification.models import Player

from .forms import IconSelect, NonPrimarySubmit
from .models import Announcement
from .templatetags.custom_tags import dict_value, index, sort_by
from .views import filter_announcements, getattr_or_dictvalue, home, news
from .views import ImprovedListMixin
from .widgets import DateTimeWidget, FullWidthSelect2MultipleWidget


class AnnouncementModelTestCase(TestCase):

	def test_absolute_url_uses_slug(self):
		announcement = Announcement.objects.create(title='News', slug='news', published=True)
		self.assertEqual(announcement.get_absolute_url(), reverse('misc:announcement', args=('news',)))

	def test_default_visibility_flags_are_private(self):
		announcement = Announcement.objects.create(title='Draft', slug='draft')
		self.assertFalse(announcement.published)
		self.assertFalse(announcement.registration_required)

	def test_slug_is_unique(self):
		Announcement.objects.create(title='First', slug='duplicate')
		with self.assertRaises(Exception):
			Announcement.objects.create(title='Second', slug='duplicate')


class AnnouncementVisibilityTestCase(TestCase):

	def setUp(self):
		self.public = Announcement.objects.create(
			title='Public', slug='public', published=True,
		)
		self.restricted = Announcement.objects.create(
			title='Restricted', slug='restricted', published=True,
			registration_required=True,
		)
		self.draft = Announcement.objects.create(
			title='Draft', slug='draft', published=False,
		)
		self.user = Player.objects.create_user('NewsUser', 'news@test.com', 'test')

	def test_anonymous_users_see_only_published_public_announcements(self):
		request = RequestFactory().get('/misc/news')
		request.user = AnonymousUser()
		visible = filter_announcements(request, Announcement.objects.all())
		self.assertEqual(list(visible), [self.public])

	def test_authenticated_users_see_published_restricted_announcements(self):
		request = RequestFactory().get('/misc/news')
		request.user = self.user
		visible = filter_announcements(request, Announcement.objects.all())
		self.assertCountEqual(visible, [self.public, self.restricted])

	def test_unpublished_announcements_are_never_visible(self):
		request = RequestFactory().get('/misc/news')
		request.user = self.user
		visible = filter_announcements(request, Announcement.objects.all())
		self.assertNotIn(self.draft, visible)


class NewsViewTestCase(TestCase):

	def setUp(self):
		self.older = Announcement.objects.create(title='Older', slug='older', published=True)
		self.newer = Announcement.objects.create(title='Newer', slug='newer', published=True)

	def test_news_orders_newest_first_and_configures_search(self):
		request = RequestFactory().get('/misc/news')
		request.user = AnonymousUser()
		with patch('misc.views.ImprovedListView.as_view', return_value=lambda request: None) as as_view:
			news(request)
		kwargs = as_view.call_args.kwargs
		self.assertEqual(list(kwargs['queryset']), [self.newer, self.older])
		self.assertTrue(kwargs['search_use_q'])
		self.assertEqual(kwargs['search_fields'], ['title', 'content'])

	def test_news_limits_results(self):
		request = RequestFactory().get('/misc/news')
		request.user = AnonymousUser()
		with patch('misc.views.ImprovedListView.as_view', return_value=lambda request: None) as as_view:
			news(request, total_number=1)
		self.assertEqual(list(as_view.call_args.kwargs['queryset']), [self.newer])

	def test_home_disables_search_and_uses_three_item_limit(self):
		request = RequestFactory().get('/')
		with patch('misc.views.news') as news_view:
			home(request)
		kwargs = news_view.call_args.kwargs
		self.assertEqual(kwargs['total_number'], 3)
		self.assertFalse(kwargs['use_search'])
		self.assertEqual(kwargs['template_name'], 'misc/home.html')

	def test_home_passes_first_home_flatpage(self):
		FlatPage.objects.create(url='/home/example/', title='Home page', content='Home content')
		request = RequestFactory().get('/')
		with patch('misc.views.news') as news_view:
			home(request)
		self.assertEqual(news_view.call_args.kwargs['extra_context']['flatpage'].title, 'Home page')

	def test_news_accepts_explicit_ordering(self):
		request = RequestFactory().get('/misc/news')
		request.user = AnonymousUser()
		with patch('misc.views.ImprovedListView.as_view', return_value=lambda request: None) as as_view:
			news(request, announcements=Announcement.objects.all(), ordering=['title'])
		self.assertEqual([item.title for item in as_view.call_args.kwargs['queryset']], ['Newer', 'Older'])


class AnnouncementTemplateViewTestCase(TestCase):

	def setUp(self):
		self.public = Announcement.objects.create(
			title='Public', slug='public', published=True,
		)
		self.restricted = Announcement.objects.create(
			title='Restricted', slug='restricted', published=True,
			registration_required=True,
		)

	def test_public_announcement_detail_is_available(self):
		response = self.client.get(reverse('misc:announcement', args=('public',)))
		self.assertEqual(response.status_code, 200)

	def test_restricted_announcement_detail_is_hidden_anonymously(self):
		response = self.client.get(reverse('misc:announcement', args=('restricted',)))
		self.assertEqual(response.status_code, 404)

	def test_restricted_announcement_detail_is_available_to_logged_in_user(self):
		user = Player.objects.create_user('DetailUser', 'detail@test.com', 'test')
		self.client.force_login(user)
		response = self.client.get(reverse('misc:announcement', args=('restricted',)))
		self.assertEqual(response.status_code, 200)

	def test_unknown_announcement_is_not_found(self):
		response = self.client.get(reverse('misc:announcement', args=('unknown',)))
		self.assertEqual(response.status_code, 404)


class MiscHelperTestCase(TestCase):

	def test_getattr_or_dictvalue_supports_objects_and_dictionaries(self):
		class Item:
			value = 'object value'

		self.assertEqual(getattr_or_dictvalue(Item(), 'value'), 'object value')
		self.assertEqual(getattr_or_dictvalue({'value': 'dict value'}, 'value'), 'dict value')
		self.assertEqual(getattr_or_dictvalue({}, 'missing', 'fallback'), 'fallback')
		self.assertIsNone(getattr_or_dictvalue({'value': None}, 'value', 'fallback'))

	def test_template_filters(self):
		self.assertEqual(index(['zero', 'one'], 1), 'one')
		self.assertEqual(dict_value({'key': 'value'}, 'key'), 'value')

	def test_sort_by_delegates_to_queryset_ordering(self):
		class Ordered:
			def order_by(self, order):
				return order

		self.assertEqual(sort_by(Ordered(), '-date_created'), '-date_created')


class MiscFormsAndWidgetsTestCase(TestCase):

	def test_non_primary_submit_uses_button_class(self):
		self.assertEqual(NonPrimarySubmit.field_classes, 'btn')

	def test_icon_select_sets_expected_attributes_and_image(self):
		widget = IconSelect(choices=[('cats', 'Cats')], choices_urls={'cats': '/cats.png'})
		option = widget.create_option('faction', 'cats', 'Cats', False, 0)
		self.assertEqual(widget.attrs['is'], 'ms-dropdown')
		self.assertIn('select', widget.attrs['class'])
		self.assertEqual(option['attrs']['data-image'], '/cats.png')

	def test_date_time_widget_uses_datetime_local(self):
		self.assertEqual(DateTimeWidget.input_type, 'datetime-local')

	def test_full_width_select_widget_sets_width(self):
		widget = FullWidthSelect2MultipleWidget()
		self.assertEqual(widget.attrs['style'], 'width : 100%')
from django.test import TestCase

# Create your tests here.
