from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MatchmakingConfig(AppConfig):
    name = 'matchmaking'
    verbose_name = _('matchmaking')
