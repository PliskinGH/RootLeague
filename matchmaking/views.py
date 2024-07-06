from django.shortcuts import render, get_object_or_404
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from .models import Match, Participant
from .forms import MatchForm, ParticipantsFormSet

# Create your views here.

def index(request):
    matchs = Match.objects.all().order_by('-created_at')[:5]
    return listing(request, matchs=matchs,
                   title="Last matches", number_per_page=5)

def listing(request, matchs = None, title = "All games",
            number_per_page = 10):
    if (matchs is None):
        matchs = Match.objects.all().order_by('-created_at')
    return ListView.as_view(model=Match,
                            queryset=matchs,
                            paginate_by=number_per_page,
                            extra_context={'title' : title}
                     )(request)

def match_details(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    participants = [participant.player.__str__()
                    for participant in match.participants.all()]
    participants_names = ", ".join(participants)
    context = {
        'match_title': match.title,
        'participants_names': participants_names,
    }
    return render(request, 'matchmaking/match_details.html', context)

@login_required
def new_match(request):
    context = {}
    if request.method == 'POST':
        match_form = MatchForm(request.POST)
        if match_form.is_valid():
            title = match_form.cleaned_data['title']
            board_map = match_form.cleaned_data['board_map']
            closed = match_form.cleaned_data['closed']
            match = Match.objects.create(title = title,
                                         board_map = board_map,
                                         closed = closed)
            if (closed):
                match.closed_at = match.created_at
                match.save()
            participants_formset = ParticipantsFormSet(request.POST,
                                                       instance=match)
            if (participants_formset.is_valid()):
                participants=[]
                for form in participants_formset.forms:
                    player = form.cleaned_data['player']
                    faction = form.cleaned_data['faction']
                    winner = form.cleaned_data['winner']
                    score = form.cleaned_data['score']
                    dominance = form.cleaned_data['dominance']
                    turn_order = form.cleaned_data['turn_order']
                    participant = Participant.objects.create(match = match,
                                                             player = player,
                                                             faction = faction,
                                                             winner = winner,
                                                             score = score,
                                                             dominance = dominance,
                                                             turn_order = turn_order,
                                                             )
                    match.participants.add(participant)
                    participants.append(participant)
                index_participant = 0
                for form in participants_formset.forms:
                    index_participant += 1
                    index_coalitioned = form.cleaned_data['coalitioned_player']
                    if (not(index_coalitioned in [None, ''])):
                        index_coalitioned = int(index_coalitioned)
                        participant = participants[index_participant-1]
                        coalitioned_player = participants[index_coalitioned-1]
                        if (coalitioned_player is not None):
                            participant.coalition = coalitioned_player
                            participant.save()
                match.save()
            return match_details(request, match.id)
        else:
            context['match_errors'] = match_form.errors.items()
    else:
        match_form = MatchForm()
        participants_formset = ParticipantsFormSet()
        context['match_form'] = match_form
        context['participants_formset'] = participants_formset
    return render(request, 'matchmaking/new_match.html', context)

def search(request):
    query = request.GET.get('query')
    if not query:
        matchs = Match.objects.all()
    else:
        matchs = Match.objects.filter(Q(title__icontains=query) |
                                      Q(participants__player__in_game_name__icontains=query))
    if matchs.exists():
        matchs = matchs.order_by('-created_at')
    title = "Search results for the request %s"%query
    return listing(request, matchs=matchs, title=title)