from django import forms
from crispy_forms.layout import Submit
from django.core.validators import EMPTY_VALUES

class NonPrimarySubmit(Submit):
    field_classes = "btn"

class IconSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.choices_urls = kwargs.pop('choices_urls', {})
        super().__init__(*args, **kwargs)
        self.attrs['is'] = "ms-dropdown"
        self.attrs['style'] = 'width : 100%'
        css_class = self.attrs.get('class', '')
        if (css_class not in EMPTY_VALUES):
            self.attrs['class'] += ' '
        else:
            self.attrs['class'] = ''
        self.attrs['class'] += 'select'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        url = self.choices_urls.get(option['value'], None)
        if (url not in EMPTY_VALUES):
            option['attrs']['data-image'] = url
        return option