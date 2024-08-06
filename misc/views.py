from django.shortcuts import render
from django.views.generic import ListView

# Create your views here.
def about(request):
    return render(request, 'misc/about.html')

class ElidedListView(ListView):
    title = ""
    
    def get_context_data(self, *args, **kwargs):
      context = super(ElidedListView, self).get_context_data(*args, **kwargs)
      page = context['page_obj']
      context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
      context['title'] = self.title
      return context