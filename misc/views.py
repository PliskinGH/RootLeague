from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from extra_views import SearchableListMixin, SortableListMixin
from django_filters.views import FilterView
from django.core.validators import EMPTY_VALUES
from django.contrib.flatpages.models import FlatPage

from .models import Announcement

# Create your views here.

class ImprovedListMixin(SortableListMixin, SearchableListMixin):
    title = ""
    search_use_q = False
    current_url = "home"
    current_url_arg = ""
    search_placeholder = ""
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        page = context['page_obj']
        if (page is not None):
            context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
        context['title'] = self.title
        context['display_search'] = self.search_use_q
        context['url_search'] = self.current_url
        context['url_search_arg'] = self.current_url_arg
        context['search_placeholder'] = self.search_placeholder
        context['search_query'] = ""
        query = self.get_search_query()
        if (query):
            context['search_query'] = query
        context['url_sort'] = self.current_url
        context['url_sort_arg'] = self.current_url_arg
        return context

    def _sort_queryset(self, queryset):
        self.sort_helper = self.get_sort_helper()
        sort = self.sort_helper.get_sort()
        sortToDo = bool(sort)
        if sortToDo:
            try:
                queryset = queryset.order_by(sort)
                sortToDo = False
            except AttributeError:
                # Queryset is actually a list...
                pass
            except:
                # Unknown error
                sortToDo = False
        if sortToDo:
            sortToDo = False
            try:
                attr = sort
                reverse = (sort[0] == "-")
                if (reverse):
                    attr = sort[1:]
                queryset = sorted(queryset,
                                  reverse=reverse,
                                  key=lambda obj : getattr_or_dictvalue(obj, attr, None))
            except:
                pass
        return queryset

class ImprovedListView(ImprovedListMixin, ListView):
    pass

class ImprovedFilterView(ImprovedListMixin, FilterView):
    pass

# TODO Move somewhere else
def getattr_or_dictvalue(obj, attr, default=None):
    if (isinstance(obj, dict)):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)

def news(request,
         announcements = None,
         title = _("All announcements"),
         ordering = None,
         total_number = None,
         number_per_page = 5,
         use_search = True,
         current_url = 'misc:news',
         current_url_arg = "",
         search_placeholder = _("Find announcement"),
         template_name = None,
         extra_context = None,
         ):
    if (announcements is None):
        announcements = Announcement.objects.all()
    announcements = filter_announcements(request, announcements)

    if (ordering in EMPTY_VALUES):
        ordering = ['-date_created', '-date_modified']
    announcements = announcements.order_by(*ordering)

    if (total_number is not None):
        announcements = announcements[:total_number]

    return ImprovedListView.as_view(model=Announcement,
                                    queryset=announcements,
                                    template_name=template_name,
                                    paginate_by=number_per_page,
                                    search_use_q=use_search,
                                    current_url=current_url,
                                    current_url_arg=current_url_arg,
                                    search_placeholder=search_placeholder,
                                    search_fields = ['title', 'content'],
                                    title=title,
                                    extra_context=extra_context,
                                    )(request)

def announcement(request,
                 slug = None,
                 announcements = None,):
    announcements = filter_announcements(request, announcements)

    return DetailView.as_view(model=Announcement,
                              queryset=announcements,
                             )(request, slug=slug)

def filter_announcements(request, announcements):
    if (announcements is None):
        announcements = Announcement.objects.all()
    announcements = announcements.filter(published=True)
    user = request.user
    if (not(user is not None and user.is_authenticated and user.pk is not None)):
        announcements = announcements.exclude(registration_required=True)
    return announcements

def home(request):
    extra_context = {}
    home_pages = FlatPage.objects.filter(url__istartswith="/home/")
    if (home_pages.count()):
        extra_context['flatpage'] = home_pages.first()

    return news(request,
                title=_("Home"),
                total_number=3, number_per_page=3,
                use_search=False,
                current_url='home',
                template_name='misc/home.html',
                extra_context=extra_context)