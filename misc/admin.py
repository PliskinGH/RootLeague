from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.urls import reverse
from tinymce.widgets import TinyMCE
from more_admin_filters.filters import MultiSelectMixin, flatten_used_parameters
from django.contrib.admin.utils import reverse_field_path
from django.utils.translation import gettext_lazy as _

from .models import Announcement

# Register your models here.

class TinyMCEAdminMixin:
    def formfield_for_dbfield(self, db_field, *args, **kwargs):
        if db_field.name == 'content':
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={'external_link_list_url': reverse('tinymce-linklist')},
            ))
        return super().formfield_for_dbfield(db_field, *args, **kwargs)

class TinyMCEFlatPageAdmin(TinyMCEAdminMixin, FlatPageAdmin):
    pass

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)

@admin.register(Announcement)
class AnnouncementAdmin(TinyMCEAdminMixin, admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ['date_created', 'date_modified']
    list_display = ['title', 'date_created', 'date_modified']
    readonly_fields = ['date_created', 'date_modified']
    prepopulated_fields = {"slug": ["title"]}

class MultiSelectChoicesFilter(MultiSelectMixin, admin.ChoicesFieldListFilter):
    """
    Multi select filter for all kind of fields.
    """
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__in' % field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        lookup_vals = request.GET.get(self.lookup_kwarg)
        self.lookup_vals = lookup_vals.split(',') if lookup_vals else list()
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        self.empty_value_display = model_admin.get_empty_value_display()
        parent_model, reverse_path = reverse_field_path(model, field_path)
        # Obey parent ModelAdmin queryset when deciding which options to show
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        self.lookup_choices = (queryset
                               .distinct()
                               .order_by(field.name)
                               .values_list(field.name, flat=True))
        super(admin.ChoicesFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)
        flatten_used_parameters(self.used_parameters)
        self.used_parameters = self.prepare_used_parameters(self.used_parameters)

    def prepare_querystring_value(self, value):
        # mask all commas or these values will be used
        # in a comma-seperated-list as get-parameter
        return str(value).replace(',', '%~')

    def prepare_used_parameters(self, used_parameters):
        # remove comma-mask from list-values for __in-lookups
        for key, value in used_parameters.items():
            if not key.endswith('__in'): continue
            used_parameters[key] = [v.replace('%~', ',') for v in value]
        return used_parameters

    def choices(self, changelist):
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        yield {
            'selected': not self.lookup_vals and self.lookup_val_isnull is None,
            'query_string': changelist.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        count = None
        none_title = ""
        for i, (lookup, title) in enumerate(self.field.flatchoices):
            if add_facets:
                count = facet_counts[f"{i}__c"]
                title = f"{title} ({count})"
            if lookup is None:
                none_title = title
                continue
            val = str(lookup)
            qval = self.prepare_querystring_value(val)
            yield {
                "selected": qval in self.lookup_vals,
                "query_string": self.querystring_for_choices(qval, changelist),
                "display": title,
            }
        if none_title:
            yield {
                "selected": bool(self.lookup_val_isnull),
                "query_string": self.querystring_for_isnull(changelist),
                "display": none_title,
            }