from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _
from extra_views import SearchableListMixin, SortableListMixin

from .models import Announcement

# Create your views here.

class ImprovedListView(SortableListMixin, SearchableListMixin, ListView):
    title = ""
    search_use_q = False
    current_url = "index"
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

# TODO Move somewhere else
def getattr_or_dictvalue(obj, attr, default=None):
    if (isinstance(obj, dict)):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)

def news(request,
         announcements = None,
         title = _("All announcements"),
         ordering = ['-date_created'],
         total_number = None,
         number_per_page = 5,
         use_search = True,
         current_url = 'misc:news',
         current_url_arg = "",
         search_placeholder = _("Find announcement"),
         ):
    announcements = filter_announcements(request, announcements)

    return ImprovedListView.as_view(model=Announcement,
                                    queryset=announcements,
                                    paginate_by=number_per_page,
                                    ordering=ordering,
                                    search_use_q=use_search,
                                    current_url=current_url,
                                    current_url_arg=current_url_arg,
                                    search_placeholder=search_placeholder,
                                    search_fields = ['title', 'content'],
                                    title=title,
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