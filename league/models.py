from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, UniqueConstraint, Deferrable
from django.core.validators import EMPTY_VALUES

from .constants import SETUP_TYPES, DECKS, MAPS

# Create your models here.

class AbstractTournament(models.Model):
    """
    Model for a set of matches, for a given period of time.
    """
    name = models.CharField(max_length=200, blank=False, unique=True,
                            verbose_name=_('name'))
    
    start_date = models.DateTimeField(blank=True, null=True,
                                      verbose_name=_('start date'))
    end_date = models.DateTimeField(blank=True, null=True,
                                    verbose_name=_('end date'))
    
    max_players_per_game = models.IntegerField(blank=True, null=True,
                                               verbose_name=_("maximum number of players per game")
                                               )
    min_players_per_game = models.IntegerField(blank=True, null=True,
                                               verbose_name=_("minimum number of players per game")
                                               )
    coalition_allowed = models.BooleanField(blank=True, null=True,
                                            verbose_name=_('coalition allowed'))
    three_coalition_allowed = models.BooleanField(blank=True, null=True,
                                                  verbose_name=_('three way coalition allowed'))
    
    min_games = models.IntegerField(blank=True, null=True,
                                    verbose_name=_("minimum number of games"),
                                    help_text=_('Threshold for leaderboards.'))
    
    win_score =  models.DecimalField(max_digits=3, decimal_places=2,
                                     blank=True, null=True,
                                     verbose_name=_('win score'))
    coalition_score_multiplier = models.DecimalField(max_digits=2, decimal_places=1,
                                                     blank=True, null=True,
                                                     verbose_name=_('coalition score multiplier'))
    total_score_per_game = models.DecimalField(max_digits=3, decimal_places=2,
                                               blank=True, null=True,
                                               verbose_name=_('total score per game'))
    
    game_setup = models.CharField(max_length=20,
                                  blank=True,
                                  choices=SETUP_TYPES,
                                  verbose_name=_('setup'))
    deck = models.CharField(max_length=200, choices=DECKS,
                            blank=True,
                            verbose_name=_('deck'))
    board_map = models.CharField(max_length=20, choices=MAPS,
                                 blank=True,
                                 verbose_name=_('map'))
    random_suits = models.BooleanField(blank=True, null=True,
                                       verbose_name=_('random suits'))
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if (self.three_coalition_allowed is None and
            self.coalition_allowed is not None):
            self.three_coalition_allowed = self.coalition_allowed
        super(AbstractTournament, self).save()

    def __str__(self):
        result = super().__str__()
        if (self.name not in ['', None]):
            result = self.name
        return result

class Tournament(AbstractTournament):
    """
    Model for a tournament, which is a set of matches.
    """
    league = models.ForeignKey('League', on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name="seasons",
                               verbose_name=_('league'))

    class Meta:
        verbose_name = _("tournament")

    @classmethod
    def get_default(cls):
        default_league, created_league = League.get_default()
        created = False
        if (not(created_league) and default_league is not None
            and default_league.active_season is not None):
            default_tournament = default_league.active_season
        else:
            tournament_name = "Test Tournament"
            if (default_league is not None and default_league.name not in EMPTY_VALUES):
                tournament_name = default_league.name + " Season 1"
            default_tournament, created = cls.objects.get_or_create(name=tournament_name, 
                                                            defaults=dict(league=default_league))
            if (default_league is not None and default_tournament is not None):
                default_league.active_season = default_tournament
                default_league.save()
        return (default_tournament, created)

    @classmethod
    def get_default_pk(cls):
        result = None
        tournament, _ = Tournament.get_default()
        if (tournament is not None):
            result = tournament.pk
        return result


class League(AbstractTournament):
    """
    Model for a league, which is a set of matches,
    that could be divided into seasons (= tournaments).
    """
    active_season = models.OneToOneField(Tournament, on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name="active_in_league",
                                         verbose_name=_('active season'))
    is_default = models.BooleanField(null=False, blank=False, default=False,
                                     verbose_name='is default')

    class Meta:
        verbose_name = _("league")

    def save(self, *args, **kwargs):
        if self.is_default:
            previous_defaults = League.objects.filter(is_default=True)
            for previous_default in previous_defaults:
                if (self != previous_default):
                    previous_default.is_default = False
                    previous_default.save()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default(cls):
        created = False
        default_league = None
        default_leagues = cls.objects.filter(is_default=True)
        if (default_leagues not in EMPTY_VALUES and len(default_leagues) == 1):
            default_league = default_leagues.first()
        if (default_league in EMPTY_VALUES):
            default_league, created = cls.objects.get_or_create(name='Test League')
            default_league.is_default = True
            default_league.save()
        return (default_league, created)
