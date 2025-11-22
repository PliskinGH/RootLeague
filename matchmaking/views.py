
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory, CreateWithInlinesView, UpdateWithInlinesView, SuccessMessageMixin as SuccessMessageMixinWithInlines
from django.utils.translation import gettext_lazy as _
from django.forms.formsets import all_valid
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import PermissionDenied
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH, DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH
from .forms import MatchForm, UpdateMatchForm, DeleteMatchForm, ParticipantForm, ParticipantFormSet
from .filters import MatchFilter, ParticipantFilter
from .serializers import MatchSerializer
from league.common import get_league, get_tournament, get_dropdown_menu, get_title
from misc.views import ImprovedListView

# Create your views here.

def index(request):
    matchs = Match.objects.exclude(date_closed=None)
    return listing(request, matchs=matchs,
                   title=_("Latest matches"),
                   total_number=5, number_per_page=5,
                   use_search=False,
                   use_league_menu=False)

def listing(request,
            matchs = None,
            title = None,
            player = None,
            submitted_by = None,
            league = None,
            tournament = None,
            ordering = None,
            total_number = None,
            number_per_page = 10,
            extra_context = None,
            use_search = True,
            use_league_menu = True,
            display_edit = False,
            current_url = 'match:listing',
            current_url_arg = "",
            search_placeholder = _("Find a match"),
            global_url = 'match:listing',
            league_url = 'match:league_listing',
            tournament_url = 'match:tournament_listing',
            template_name=None):
    if (league in EMPTY_VALUES and
        tournament not in EMPTY_VALUES):
        league = tournament.league
    
    if (matchs is None):
        matchs = Match.objects.all()
    
    if (player not in EMPTY_VALUES):
        matchs = matchs.filter(participants__player=player)
    
    if (submitted_by not in EMPTY_VALUES):
        matchs = matchs.filter(submitted_by=submitted_by)
    
    if (tournament not in EMPTY_VALUES):
        matchs = matchs.filter(tournament=tournament)
    elif (league not in EMPTY_VALUES):
        matchs = matchs.filter(tournament__league=league)

    if (ordering is None):
        ordering = ['-date_closed', '-date_modified', '-date_registered']
    ordering += ['title', 'pk']
    
    matchs = matchs.order_by(*ordering)

    if (total_number is not None):
        matchs = matchs[:total_number]

    if (title in EMPTY_VALUES):
        title = get_title(tournament=tournament,
                          league=league)
        
    if (display_edit):
        display_edit = {}
        for match in matchs:
            display_edit[match.id] = match.is_editable_by(request.user)
        if (not(True in display_edit.values())):
            display_edit = False
    
    if (extra_context in EMPTY_VALUES):
        extra_context = {}
    if (use_league_menu):
        extra_context.update(get_dropdown_menu(tournament=tournament,
                                               league=league))
        extra_context['global_url'] = global_url
        extra_context['league_url'] = league_url
        extra_context['tournament_url'] = tournament_url
    extra_context['display_league_menu'] = use_league_menu
    extra_context['display_edit'] = display_edit
    
    return ImprovedListView.as_view(model=Match,
                                    queryset=matchs,
                                    paginate_by=number_per_page,
                                    search_use_q=use_search,
                                    current_url=current_url,
                                    current_url_arg=current_url_arg,
                                    search_placeholder=search_placeholder,
                                    search_fields = ['title',
                                                     'participants__player__in_game_name',
                                                     'participants__player__username',
                                                     'participants__player__discord_name'],
                                    title=title,
                                    extra_context=extra_context,
                                    template_name=template_name,
                                    )(request)

def league_listing(request,
                   league_id = None,
                   number_per_page = 10):
    league = get_league(league_id)
    current_url_arg = ""
    if (league):
        current_url_arg = league.id
    return listing(request,
                   league=league,
                   current_url = 'match:league_listing',
                   current_url_arg = current_url_arg,
                   number_per_page=number_per_page)

def tournament_listing(request,
                       tournament_id = None,
                       number_per_page = 10):
    tournament = get_tournament(tournament_id)
    current_url_arg = ""
    if (tournament):
        current_url_arg = tournament.id
    return listing(request,
                   tournament=tournament,
                   current_url = 'match:tournament_listing',
                   current_url_arg = current_url_arg,
                   number_per_page=number_per_page)

@login_required
def submissions(request,
                league = None,
                tournament = None,
                current_url = 'match:submissions',
                current_url_arg = "",
                number_per_page = 10):
    player = request.user
    title = _("Submitted games")
    return listing(request,
                   submitted_by=player,
                   league=league, tournament=tournament,
                   title=title,
                   number_per_page=number_per_page,
                   display_edit=True,
                   current_url=current_url,
                   current_url_arg=current_url_arg,
                   global_url='match:submissions',
                   league_url='match:league_submissions',
                   tournament_url='match:tournament_submissions',
                  )

@login_required
def league_submissions(request,
                       league_id = None,
                       number_per_page = 10):
    league = get_league(league_id)
    current_url_arg = ""
    if (league):
        current_url_arg = league.id
    return submissions(request,
                       league=league,
                       current_url = 'match:league_submissions',
                       current_url_arg = current_url_arg,
                       number_per_page=number_per_page)

@login_required
def tournament_submissions(request,
                           tournament_id = None,
                           number_per_page = 10):
    tournament = get_tournament(tournament_id)
    current_url_arg = ""
    if (tournament):
        current_url_arg = tournament.id
    return submissions(request,
                       tournament=tournament,
                       current_url = 'match:tournament_submissions',
                       current_url_arg = current_url_arg,
                       number_per_page=number_per_page)

@login_required
def played_games(request,
                 league = None,
                 tournament = None,
                 current_url = 'match:played_games',
                 current_url_arg = "",
                 number_per_page = 10):
    player = request.user
    title = _("Played games")
    return listing(request,
                   player=player,
                   league=league, tournament=tournament,
                   title=title,
                   number_per_page=number_per_page,
                   display_edit=True,
                   current_url=current_url,
                   current_url_arg=current_url_arg,
                   global_url='match:played_games',
                   league_url='match:league_played_games',
                   tournament_url='match:tournament_played_games',
                  )

@login_required
def league_played_games(request,
                        league_id = None,
                        number_per_page = 10):
    league = get_league(league_id)
    current_url_arg = ""
    if (league):
        current_url_arg = league.id
    return played_games(request,
                        league=league,
                        current_url = 'match:league_played_games',
                        current_url_arg = current_url_arg,
                        number_per_page=number_per_page)

@login_required
def tournament_played_games(request,
                            tournament_id = None,
                            number_per_page = 10):
    tournament = get_tournament(tournament_id)
    current_url_arg = ""
    if (tournament):
        current_url_arg = tournament.id
    return played_games(request,
                        tournament=tournament,
                        current_url = 'match:tournament_played_games',
                        current_url_arg = current_url_arg,
                        number_per_page=number_per_page)


class MatchDetailView(DetailView):
    model = Match
    pk_url_kwarg='match_id'

    def get_context_data(self, *args, **kwargs):
        match = self.object
        if (match is not None):
            kwargs['display_edit'] = match.is_editable_by(self.request.user)
        return super().get_context_data(*args, **kwargs)

class ParticipantInline(InlineFormSetFactory):
    model = Participant
    form_class = ParticipantForm
    formset_class = ParticipantFormSet
    fields = [
        'turn_order',
        'player',
        'faction',
        'game_score',
        'dominance',
        'tournament_score']
    factory_kwargs = {"extra" : DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH, 
                      "max_num" : MAX_NUMBER_OF_PLAYERS_IN_MATCH,
                      "validate_max" : True}
    initial = [{ 'turn_order': 1},
               { 'turn_order': 2},
               { 'turn_order': 3},
               { 'turn_order': 4},
               { 'turn_order': 5},
               { 'turn_order': 6},]

    def get_initial(self):
        if (self.object):
            return []
        return super().get_initial()

    def get_factory_kwargs(self):
        kwargs = super().get_factory_kwargs()
        if (self.object):
            kwargs["extra"] = 0
        return kwargs

class EditMatchViewMixin(object):
    model = Match
    inlines = [ParticipantInline]
    pk_url_kwarg='match_id'
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form and formset instances with the
        passed POST variables and then checked for validity.
        Rewrite of ProcessFormWithInlinesView.post due to formsets being validated
        despite parent form being invalid.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        initial_object = self.object
        if form.is_valid():
            self.object = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False

        inlines = self.construct_inlines()

        if form_validated and all_valid(inlines): # change order of conditions
            return self.forms_valid(form, inlines)
        self.object = initial_object
        return self.forms_invalid(form, inlines)

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        if (len(inlines) == 1):
            participants_formset = inlines[0]
            index_participant = -1
            participants = [participant
                            for participant in self.object.participants.exclude(turn_order=None).order_by('turn_order')]
            turn_order = lambda f : f.cleaned_data.get('turn_order', None)
            forms = [f for f in participants_formset.forms
                       if  f.cleaned_data
                       and not f.cleaned_data.get('DELETE', False)
                       and f.cleaned_data.get('turn_order', None) is not None]
            forms.sort(key=turn_order)
            for form in forms:
                index_participant += 1
                if (index_participant >= len(participants)):
                    break
                participant = participants[index_participant]
                turn_coalitioned = form.cleaned_data.get('coalitioned_player', '')
                in_coalition = False
                if (not(turn_coalitioned in EMPTY_VALUES)):
                    turn_coalitioned = int(turn_coalitioned)
                    for candidate in participants:
                        if (candidate is not None and candidate.turn_order == turn_coalitioned):
                            in_coalition = True
                            original_vagabond = getattr(candidate, 'coalitioned_vagabond', None)
                            if (original_vagabond is not None and
                                original_vagabond != participant):
                                original_vagabond.coalition = None
                                original_vagabond.save()
                            participant.coalition = candidate
                            participant.save()
                            break
                if (not(in_coalition) and participant.coalition is not None):
                    participant.coalition = None
                    participant.save()
        self.object.save()
        return response

class EditMatchPermissionsMixin(object):
    def get_object(self, *args, **kwargs):
        match = super().get_object(*args, **kwargs)
        if not(match.is_editable_by(self.request.user)):
            raise PermissionDenied()
        return match

class CreateMatchView(LoginRequiredMixin, EditMatchViewMixin, SuccessMessageMixinWithInlines, CreateWithInlinesView):
    form_class = MatchForm
    success_message = _("Match successfully registered!")
    extra_context = {'upper_title' : _("Register match"),
                     'lower_title' : _("Form")}
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        initial_tournament_name = ""
        if (self.request.method == 'GET'):
            initial_tournament_name = self.request.GET.get("tournament", "")
        initial_tournaments = []
        if (initial_tournament_name not in EMPTY_VALUES):
            initial_tournaments = form.fields['tournament'].queryset.filter(name=initial_tournament_name)
        initial_tournament = None
        if (len(initial_tournaments) == 1):
            initial_tournament = initial_tournaments[0]
        if (initial_tournament is not None):
            form.fields['tournament'].initial = initial_tournament
            form.fields['tournament'].disabled = True
        return form
    
    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        if (form.cleaned_data.get('closed', False)):
            self.object.date_closed = self.object.date_registered
        if (self.request.user):
            self.object.submitted_by = self.request.user
        self.object.save()
        return response

class UpdateMatchView(LoginRequiredMixin, EditMatchPermissionsMixin, EditMatchViewMixin, SuccessMessageMixinWithInlines, UpdateWithInlinesView):
    form_class = UpdateMatchForm
    success_message = _("Match successfully updated!")
    extra_context = {'upper_title' : _("Update match"),
                     'lower_title' : _("Form")}

    def get_object(self, *args, **kwargs):
        match = super().get_object(*args, **kwargs)
        if not(match.is_editable_by(self.request.user)):
            raise PermissionDenied()
        return match
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def forms_valid(self, form, inlines):
        response = super().forms_valid(form, inlines)
        is_closed = form.cleaned_data.get('closed', False)
        if (is_closed and self.object.date_closed is None):
            self.object.date_closed = self.object.date_modified
            if (self.request.user):
                self.object.submitted_by = self.request.user
        elif (not(is_closed) and self.object.date_closed is not None):
            self.object.date_closed = None
        self.object.save()
        return response

class DeleteMatchView(LoginRequiredMixin, EditMatchPermissionsMixin, SuccessMessageMixin, DeleteView):
    model = Match
    form_class = DeleteMatchForm
    pk_url_kwarg='match_id'
    success_message = _("Match successfully deleted!")
    success_url = reverse_lazy('match:submissions')

    def get_context_data(self, *args, **kwargs):
        kwargs['upper_title'] = _("Delete match")
        match = self.object
        if (match is not None):
            kwargs['lower_title'] = match.title
        else:
            kwargs['lower_title'] = _("Unknown match")
        return super().get_context_data(*args, **kwargs)

class MatchViewset(ReadOnlyModelViewSet):
    serializer_class = MatchSerializer
    filterset_class = MatchFilter
 
    def get_queryset(self):
        return Match.objects.exclude(date_closed=None)

def filtered_listing(request):
    filter = ParticipantFilter(request.GET, queryset=Participant.objects.all())
    participants = filter.qs
    matchs = Match.objects.filter(participants__in=participants).distinct()
    return listing(request,
                   title=_("Custom Filters"),
                   matchs=matchs,
                   extra_context={'filter': filter},
                   use_league_menu=False,
                   use_search=False,
                   number_per_page=5,
                   template_name='matchmaking/match_filter.html')