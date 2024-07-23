from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Role(models.Model):
    """
    Model for roles to give players, such as "Champion", "Beginner", etc.
    """
    name = models.CharField(max_length=200, blank=False,
                            verbose_name=_('name'))
    icon = models.ImageField(blank=True, null=True,
                             verbose_name=_('icon'))
    

class Player(AbstractUser):
    """
    Model for players registered in the league database.
    """
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)
    discord_name = models.CharField(max_length=200, blank=True,
                                    verbose_name=_("discord username"))
    in_game_name = models.CharField(max_length=200, blank=True,
                                    verbose_name=_("in-game Username"))
    in_game_id = models.IntegerField(blank=True, null=True,
                                     verbose_name=_("in-game ID"))
    roles = models.ManyToManyField(Role, related_name='players',
                                   blank=True,
                                   verbose_name=_('roles'))

    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")
    
    def __str__(self):
        result = ""
        if (self.in_game_name not in [None, ""]):
            result = self.in_game_name
            if (self.in_game_id not in [None, ""]):
                result = result + "+" + str(self.in_game_id)
        if (result == ""):
            result = super().__str__()
        return result