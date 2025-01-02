from django.shortcuts import render
from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _
from extra_views import SearchableListMixin

# Create your views here.

class SearchableElidedListView(SearchableListMixin, ListView):
    title = ""
    search_use_q = False
    url_search = "index"
    search_placeholder = ""
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        page = context['page_obj']
        context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
        context['title'] = self.title
        context['display_search'] = self.search_use_q
        context['url_search'] = self.url_search
        context['search_placeholder'] = self.search_placeholder
        context['search_query'] = ""
        query = self.get_search_query()
        if (query):
            context['search_query'] = query
        return context