from django.shortcuts import render
from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _
from extra_views import SearchableListMixin, SortableListMixin

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

def getattr_or_dictvalue(obj, attr, default=None):
    if (isinstance(obj, dict)):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)