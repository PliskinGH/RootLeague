from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class LeagueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'league'
    verbose_name = _('league')
