
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