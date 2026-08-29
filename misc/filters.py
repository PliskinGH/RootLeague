
from datetime import datetime

from django.http import QueryDict
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext_lazy as _
from django.core.validators import EMPTY_VALUES
from crispy_forms.layout import Layout, Div, Button, Submit, Hidden
from crispy_forms.bootstrap import Modal

class ModalFormFilterMixin(object):
    html_title = _("Filters")
    html_id = "filtersModal"
    hidden_fields = None

    def append_hidden_fields(self, linked_filter):
        if (not(isinstance(self.hidden_fields, list))):
            self.hidden_fields = []
        if (linked_filter is not None):
            self.hidden_fields += list(linked_filter.base_form.fields.keys())
    
    @property
    def base_form(self):
        Form = self.get_form_class()
        return Form()

    @property
    def form(self):
        form = super().form

        layout_components = list(form.fields.keys())
        hidden_components = []
        if (self.hidden_fields not in EMPTY_VALUES):
            for field in self.hidden_fields:
                values = self.data.getlist(field, [])
                for value in values:
                    hidden_components.append(Hidden(name=field, value=value))
        form.helper.layout = Layout(
            Modal(*layout_components,
                  *hidden_components,
                  Div(Button("close", _("Close"), css_class="btn btn-secondary", data_bs_dismiss="modal"),
                      Submit("", _("Confirm"), css_class="btn-default"),
                      css_class="modal-footer"),
                  css_id=self.html_id, title=self.html_title, title_id=self.html_id, )
        )

        return form

    @property
    def active_filters(self):
        """Read-only, human-readable summary of the currently active filters."""
        if (not self.is_bound):
            return []
        self.form.is_valid()
        active_filters = []
        for name, value in self.form.cleaned_data.items():
            if (self._is_empty_filter_value(value)):
                continue
            query = self._mutable_query()
            query.pop(name, None)
            query.pop('page', None)
            active_filters.append({
                'name': name,
                'label': self.filters[name].label,
                'display': self._format_filter_value(name, value),
                'remove_query': query.urlencode(),
            })
        return active_filters

    @property
    def clear_query(self):
        """Query string with every filter of this filterset removed."""
        if (not self.active_filters):
            return ""
        query = self._mutable_query()
        for name in self.filters:
            query.pop(name, None)
        query.pop('page', None)
        return query.urlencode()

    def _mutable_query(self):
        """Return a mutable QueryDict built from the bound data.

        Handles both QueryDict (e.g. request.GET) and plain dict inputs.
        """
        query = QueryDict(mutable=True)
        if (isinstance(self.data, QueryDict)):
            query.update(self.data)
        else:
            for key, value in self.data.items():
                query.setlist(key, value if isinstance(value, (list, tuple)) else [value])
        return query

    def _is_empty_filter_value(self, value):
        if (hasattr(value, 'exists')):
            return not value.exists()
        return value in EMPTY_VALUES

    def _format_filter_value(self, name, value):
        filter_ = self.filters[name]
        if (isinstance(value, bool)):
            return _("Yes") if value else _("No")
        if (hasattr(value, 'exists')):
            return ", ".join(str(item) for item in value.all())
        if (isinstance(value, (list, tuple))):
            choices = dict(getattr(filter_.field, 'choices', None) or [])
            return ", ".join(str(choices.get(item, item)) for item in value)
        if (isinstance(value, datetime)):
            return date_format(timezone.localtime(value), "DATETIME_FORMAT")
        return str(value)