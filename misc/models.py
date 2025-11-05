from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Announcement(models.Model):
    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(_("content"), blank=True)
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date created'))
    date_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('date modified'))
    slug = models.SlugField(default="", null=False, unique=True)