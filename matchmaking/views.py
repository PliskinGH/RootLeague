
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory, CreateWithInlinesView, UpdateWithInlinesView, SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.forms.formsets import all_valid
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import PermissionDenied

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH, DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH
from league.models import Tournament
from league.views import get_league, get_tournament, get_dropdown_menu, get_title
from .forms import MatchForm, UpdateMatchForm, ParticipantForm, ParticipantFormSet
from misc.views import SearchableElidedListView

# Create your views here.

def index(request):
    matchs = Match.objects.exclude(date_closed=None).order_by('-date_closed', '-date_modified', '-date_registered')[:5]
    return listing(request, matchs=matchs,
                   title=_("Latest matches"), number_per_page=5,
                   use_search=False)

def listing(request,
            matchs = None,
            title = None,
            league = None,
            tournament = None,
            ordering = ['-date_closed', '-date_modified', '-date_registered'],
            number_per_page = 10,
            use_search = True,
            url_search = 'match:listing',
            url_search_arg = "",
            search_placeholder = _("Find a match")):
    if (league in EMPTY_VALUES and
        tournament not in EMPTY_VALUES):
        league = tournament.league
    
    if (matchs is None and tournament not in EMPTY_VALUES):
        matchs = tournament.matches.order_by(*ordering)
    
    if (matchs is None and league not in EMPTY_VALUES):
        matchs = Match.objects.filter(tournament__league=league).order_by(*ordering)
    
    if (matchs is None):
        matchs = Match.objects.order_by(*ordering)

    if (title in EMPTY_VALUES):
        title = get_title(tournament=tournament,
                          league=league)
    
    extra_context = get_dropdown_menu(tournament=tournament,
                                      league=league)
    
    return SearchableElidedListView.as_view(model=Match,
                                            queryset=matchs,
                                            paginate_by=number_per_page,
                                            search_use_q=use_search,
                                            url_search=url_search,
                                            url_search_arg=url_search_arg,
                                            search_placeholder=search_placeholder,
                                            search_fields = ['title',
                                                             'participants__player__in_game_name',
                                                             'participants__player__username',
                                                             'participants__player__discord_name'],
                                            title=title,
                                            extra_context=extra_context,
                                           )(request)

def league_listing(request,
                   league_id = None,
                   number_per_page = 10):
    league = get_league(league_id)
    url_search_arg = ""
    if (league):
        url_search_arg = league.id
    return listing(request,
                   league=league,
                   url_search = 'match:league_listing',
                   url_search_arg = url_search_arg,
                   number_per_page=number_per_page)

def tournament_listing(request,
                       tournament_id = None,
                       number_per_page = 10):
    tournament = get_tournament(tournament_id)
    url_search_arg = ""
    if (tournament):
        url_search_arg = tournament.id
    return listing(request,
                   tournament=tournament,
                   url_search = 'match:tournament_listing',
                   url_search_arg = url_search_arg,
                   number_per_page=number_per_page)

@login_required
def submissions(request, number_per_page = 10):
    player = request.user
    if (player):
        matchs = player.submissions.order_by('-date_closed', '-date_modified', '-date_registered')
    else:
        matchs = Match.objects.none()
    title = _("Submitted games")
    return listing(request, matchs=matchs, title=title,
                   number_per_page=number_per_page,
                   url_search='match:submissions')


class MatchDetailView(DetailView):
    model = Match
    pk_url_kwarg='match_id'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        match = self.object
        context['display_edit'] = match.is_editable_by(self.request.user)
        return context
    
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

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
    
    def get_success_url(self):
        return reverse_lazy('match:match_detail', args=(self.object.id,))
    
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
            index_participant = 0
            participants = [participant
                            for participant in self.object.participants.all()]
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

class CreateMatchView(LoginRequiredMixin, EditMatchViewMixin, SuccessMessageMixin, CreateWithInlinesView):
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

class UpdateMatchView(LoginRequiredMixin, EditMatchViewMixin, SuccessMessageMixin, UpdateWithInlinesView):
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
        elif (not(is_closed) and self.object.date_closed is not None):
            self.object.date_closed = None
        self.object.save()
        return response