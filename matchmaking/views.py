
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory, CreateWithInlinesView, SuccessMessageMixin
from django.utils.translation import gettext_lazy as _

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH, DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH
from .forms import MatchForm, ParticipantForm

# Create your views here.

def index(request):
    matchs = Match.objects.all().order_by('-date_registered')[:5]
    return listing(request, matchs=matchs,
                   title=_("Last matches"), number_per_page=5)

class ElidedListView(ListView):
    title = ""
    
    def get_context_data(self, *, object_list=None, **kwargs):
      context = super(ElidedListView, self).get_context_data(**kwargs)
      page = context['page_obj']
      context['paginator_range'] = page.paginator.get_elided_page_range(page.number)
      context['title'] = self.title
      return context

def listing(request, matchs = None, title = _("All games"),
            number_per_page = 10):
    if (matchs is None):
        matchs = Match.objects.all().order_by('-date_registered')
    return ElidedListView.as_view(model=Match,
                                  queryset=matchs,
                                  paginate_by=number_per_page,
                                  ordering = '-date_registered',
                                  title=title
                                  )(request)

class MatchDetailView(DetailView):
    model = Match
    queryset = Match.objects.all()
    pk_url_kwarg='match_id'
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

def match_detail(*args, **kwargs):
    return MatchDetailView.as_view()(*args, **kwargs)

class ParticipantInline(InlineFormSetFactory):
    model = Participant
    form_class = ParticipantForm
    fields = [
        'turn_order',
        'player',
        'faction',
        'game_score',
        'dominance',
        'league_score']
    factory_kwargs = {"extra" : DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH, 
                      "max_num" : MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                      "absolute_max" : MAX_NUMBER_OF_PLAYERS_IN_MATCH}
    initial = [{ 'turn_order': 1},
               { 'turn_order': 2},
               { 'turn_order': 3},
               { 'turn_order': 4},]

class CreateMatchView(LoginRequiredMixin, SuccessMessageMixin, CreateWithInlinesView):
    model = Match
    inlines = [ParticipantInline]
    form_class = MatchForm
    success_message = _("Match successfully registered!")
    
    def get_success_url(self):
        return reverse_lazy('matchmaking:match_detail', args=(self.object.id,))

    def forms_valid(self, form, inlines):
        response = super(CreateMatchView, self).forms_valid(form, inlines)
        if (form.cleaned_data.get('closed', False)):
            self.object.date_closed = self.object.date_registered
        if (len(inlines) == 1):
            participants_formset = inlines[0]
            index_participant = 0
            participants = []
            for participant in self.object.participants.all():
                participants.append(participant)
            for form in participants_formset.forms:
                index_participant += 1
                index_coalitioned = form.cleaned_data.get('coalitioned_player', '')
                if (not(index_coalitioned in [None, ''])):
                    index_coalitioned = int(index_coalitioned)
                    participant = participants[index_participant-1]
                    coalitioned_player = participants[index_coalitioned-1]
                    if (coalitioned_player is not None):
                        participant.coalition = coalitioned_player
                        participant.save()
        self.object.save()
        return response

def search(request):
    query = request.GET.get('query')
    if not query:
        matchs = Match.objects.all()
    else:
        matchs = Match.objects.filter(Q(title__icontains=query) |
                                      Q(participants__player__in_game_name__icontains=query) |
                                      Q(participants__player__username__icontains=query) |
                                      Q(participants__player__discord_name__icontains=query))
    if matchs.exists():
        matchs = matchs.order_by('-date_registered')
    title = _("Search results for the request %s")%query
    return listing(request, matchs=matchs, title=title)