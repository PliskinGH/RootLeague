from django.contrib.auth import get_user_model
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget

from misc.widgets import FullWidthWidgetMixin

class PlayerWidgetMixin(FullWidthWidgetMixin):
    model = get_user_model()
    search_fields = ['username__icontains',
                     'in_game_name__icontains',
                     'discord_name__icontains']

class PlayerWidget(PlayerWidgetMixin, ModelSelect2Widget):
    pass

class PlayerMultipleWidget(PlayerWidgetMixin, ModelSelect2MultipleWidget):
    pass