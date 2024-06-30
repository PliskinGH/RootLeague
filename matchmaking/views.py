from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Match, Participant
from .forms import MatchForm, ParticipantsFormSet

# Create your views here.

def index(request):
    matchs = Match.objects.all().order_by('-created_at')[:12]
    return listing(request, matchs=matchs,
                   title="Last matches", paginate=False)

def listing(request, matchs = None, title = "All matches",
            number_per_page = 3, paginate = True):
    if (matchs is None):
        matchs = Match.objects.all().order_by('-created_at')
    if paginate:
        paginator = Paginator(matchs, number_per_page)
        page = request.GET.get('page')
        try:
            matchs = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            matchs = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            matchs = paginator.page(paginator.num_pages)
    context = {
        "list_title" : title,
        'matchs': matchs,
        'paginate': paginate,
    }
    return render(request, 'matchmaking/index.html', context)

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
        matchs = Match.objects.filter(title__icontains=query)
    if not matchs.exists():
        matchs = Match.objects.filter(participants__player__ig_name__icontains=query)
    if not matchs.exists():
        matchs = Match.objects.filter(participants__player__ig_id__icontains=query)
    if matchs.exists():
        matchs = matchs.order_by('-created_at')
    title = "Search results for the request %s"%query
    return listing(request, matchs=matchs, title=title, paginate=False)