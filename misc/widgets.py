from django.forms import DateTimeInput
from django_select2.forms import Select2MultipleWidget

class DateTimeWidget(DateTimeInput):
    input_type = "datetime-local"

class FullWidthWidgetMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['style'] = 'width : 100%'

class FullWidthSelect2MultipleWidget(FullWidthWidgetMixin, Select2MultipleWidget):
    pass