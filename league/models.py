from django.db import models
from django.utils.translation import gettext_lazy as _

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
    
    class Meta:
        abstract = True

    def __str__(self):
        result = super(AbstractTournament, self).__str__()
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


class League(AbstractTournament):
    """
    Model for a league, which is a set of matches,
    that could be divided into seasons (= tournaments).
    """
    active_season = models.OneToOneField(Tournament, on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name="active_in_league",
                                         verbose_name=_('active season'))
