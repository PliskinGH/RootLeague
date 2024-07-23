from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MiscConfig(AppConfig):
    name = 'misc'
    verbose_name = _('miscellaneous')
