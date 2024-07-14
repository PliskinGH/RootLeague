from django.shortcuts import render
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory, CreateWithInlinesView, SuccessMessageMixin

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH, DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH
from .forms import MatchForm, ParticipantForm, ParticipantsFormSet, ParticipantsFormSetHelper

# Create your views here.

def index(request):
    matchs = Match.objects.all().order_by('-date_registered')[:5]
    return listing(request, matchs=matchs,
                   title="Last matches", number_per_page=5)

def listing(request, matchs = None, title = "All games",
            number_per_page = 10):
    if (matchs is None):
        matchs = Match.objects.all().order_by('-date_registered')
    return ListView.as_view(model=Match,
                            queryset=matchs,
                            paginate_by=number_per_page,
                            extra_context={'title' : title}
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
    success_message = "Match successfully registered!"
    
    def get_success_url(self):
        return reverse_lazy('matchmaking:match_detail', args=(self.object.id,))

@login_required
def register_match(request):
    context = {}
    if request.method == 'POST':
        match_form = MatchForm(request.POST)
        participants_formset = ParticipantsFormSet(request.POST)
        if (match_form.is_valid()):
            match = match_form.save(commit=False)
            if (match_form.cleaned_data['closed']):
                match.date_closed = match.date_registered
            match.save()
            if (participants_formset.is_valid()):
                participants=[]
                for form in participants_formset.forms:
                    participant = form.save(commit=False)
                    participant.match = match
                    participant.save()
                    match.participants.add(participant)
                    participants.append(participant)
                index_participant = 0
                for form in participants_formset.forms:
                    index_participant += 1
                    index_coalitioned = form.cleaned_data.get('coalitioned_player')
                    if (not(index_coalitioned in [None, ''])):
                        index_coalitioned = int(index_coalitioned)
                        participant = participants[index_participant-1]
                        coalitioned_player = participants[index_coalitioned-1]
                        if (coalitioned_player is not None):
                            participant.coalition = coalitioned_player
                for participant in participants:
                    participant.save()
            return match_detail(request, match_id=match.id)
    else:
        match_form = MatchForm()
        participants_formset = ParticipantsFormSet(initial=[
                                { 'turn_order': 1},
                                { 'turn_order': 2},
                                { 'turn_order': 3},
                                { 'turn_order': 4},])
    participants_helper = ParticipantsFormSetHelper()
    context['match_form'] = match_form
    context['participants_formset'] = participants_formset
    context['participants_helper'] = participants_helper
    return render(request, 'matchmaking/match_register.html', context)

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
    title = "Search results for the request %s"%query
    return listing(request, matchs=matchs, title=title)