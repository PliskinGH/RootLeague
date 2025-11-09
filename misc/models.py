from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

# Create your models here.

class Announcement(models.Model):
    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(_("content"), blank=True)
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name=_('date created'))
    date_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('date modified'))
    slug = models.SlugField(default="", null=False, unique=True)
    published = models.BooleanField(
        _("published"),
        help_text=_(
            "If this is checked, the announcement will be published."
        ),
        default=False,
        )
    registration_required = models.BooleanField(
        _("registration required"),
        help_text=_(
            "If this is checked, only logged-in users will be able to view the announcement."
        ),
        default=False,
    )
    
    def get_absolute_url(self):
        return reverse_lazy('misc:announcement', args=(self.slug,))