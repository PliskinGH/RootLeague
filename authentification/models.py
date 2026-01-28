from django.db import models

from django.db.models.functions import Lower
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
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

    discord_validator = UnicodeUsernameValidator(
        regex = r"^[a-z0-9._]+\Z",
        message = _(
        "Enter a valid Discord username. This value may contain only unaccented lowercase letters, "
        "numbers, and ./_ characters."
    ))

    ign_validator = UnicodeUsernameValidator(
        regex = r"^[\w.@-]+\Z",
        message = _(
        "Enter a valid username. This value may contain only unaccented lowercase a-z "
        "and uppercase A-Z letters, numbers, and @/./-/_ characters."
    ))

    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True,
                              blank=True, null=True, default=None)
    discord_name = models.CharField(max_length=200,
                                    blank=True, null=True, default=None,
                                    unique=True,
                                    verbose_name=_("Discord username"),
                                    validators=[discord_validator],)
    in_game_name = models.CharField(max_length=200,
                                    blank=False,
                                    verbose_name=_("in-game username"),
                                    validators=[ign_validator],)
    in_game_id = models.IntegerField(verbose_name=_("in-game ID"),
                                     blank=False, null=True)
    roles = models.ManyToManyField(Role, related_name='players',
                                   blank=True,
                                   verbose_name=_('roles'))

    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")
        constraints = [
            models.UniqueConstraint(
                Lower('in_game_name'),
                "in_game_id",
                name='unique_in_game_id',
                violation_error_message=_("A user with that ign+igid already exists."),
            ),
        ]
    
    def __str__(self):
        result = ""
        if (self.in_game_name not in [None, ""]):
            result = self.in_game_name
            if (self.in_game_id not in [None, ""]):
                result = result + "+" + str(self.in_game_id)
        if (result == ""):
            result = super().__str__()
        return result