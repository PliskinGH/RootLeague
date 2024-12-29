
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from extra_views import InlineFormSetFactory, CreateWithInlinesView, UpdateWithInlinesView, SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.forms.formsets import all_valid
from django.core.validators import EMPTY_VALUES

from .models import Match, Participant, MAX_NUMBER_OF_PLAYERS_IN_MATCH, DEFAULT_NUMBER_OF_PLAYERS_IN_MATCH
from league.models import Tournament
from .forms import MatchForm, UpdateMatchForm, ParticipantForm, ParticipantFormSet
from misc.views import ElidedListView

# Create your views here.

def index(request):
    matchs = Match.objects.exclude(date_closed=None).order_by('-date_closed', '-date_modified', '-date_registered')[:5]
    return listing(request, matchs=matchs,
                   title=_("Latest matches"), number_per_page=5)

def listing(request, matchs = None, title = _("All games"),
            number_per_page = 10):
    if (matchs is None):
        matchs = Match.objects.exclude(date_closed=None).order_by('-date_closed', '-date_modified', '-date_registered')
    return ElidedListView.as_view(model=Match,
                                  queryset=matchs,
                                  paginate_by=number_per_page,
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
                      "absolute_max" : MAX_NUMBER_OF_PLAYERS_IN_MATCH}
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

class MatchViewMixin(object):
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

class CreateMatchView(LoginRequiredMixin, MatchViewMixin, SuccessMessageMixin, CreateWithInlinesView):
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

class UpdateMatchView(LoginRequiredMixin, MatchViewMixin, SuccessMessageMixin, UpdateWithInlinesView):
    form_class = UpdateMatchForm
    success_message = _("Match successfully updated!")
    extra_context = {'upper_title' : _("Update match"),
                     'lower_title' : _("Form")}
    
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

def search(request):
    query = request.GET.get('query')
    if not query:
        matchs = Match.objects.all()
    else:
        matchs = Match.objects.filter(Q(title__icontains=query) |
                                      Q(participants__player__in_game_name__icontains=query) |
                                      Q(participants__player__username__icontains=query) |
                                      Q(participants__player__discord_name__icontains=query))
        matchs = matchs.distinct()
    if matchs.exists():
        matchs = matchs.order_by('-date_closed', '-date_modified', '-date_registered')
    title = _("Search results for the request %s")%query
    return listing(request, matchs=matchs, title=title)