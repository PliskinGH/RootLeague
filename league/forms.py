from django.forms import ModelForm, Form, ModelChoiceField
from django.core.validators import EMPTY_VALUES
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from .models import League, Tournament
from authentification.models import Player
from authentification.forms import PlayerWidget
from misc.forms import NonPrimarySubmit

class TournamentFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    template_name = "league/related_widget_wrapper.html"

    def __init__(self, *args, **kwargs):
        self.league_id = kwargs.pop('extra_param', None)
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context["extra_params"] = ''
        if (self.league_id not in EMPTY_VALUES):
            context["extra_params"] = '&league='+str(self.league_id)
        return context

class LeagueAdminForm(ModelForm):
    class Meta:
        model = League
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.instance):
            if (self.instance.pk is not None):
                self.fields['active_season'].queryset = self.instance.seasons.all()
            else:
                self.fields['active_season'].queryset = Tournament.objects.none()
            widget = self.fields['active_season'].widget
            self.fields['active_season'].widget = (
            TournamentFieldWidgetWrapper( 
                widget.widget,
                widget.rel,            
                widget.admin_site,
                can_add_related=widget.can_add_related,
                can_change_related=widget.can_change_related,
                can_delete_related=widget.can_delete_related,
                can_view_related=widget.can_view_related,
                extra_param=self.instance.id,
            )
       )

class PlayerInStatsForm(Form):
    player = ModelChoiceField(queryset=Player.objects.all().order_by('username'),
                              label=_("Subset of players"),
                              empty_label=_("All players"),
                              widget=PlayerWidget,
                              required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Row(Column("player", css_class='col-10'),
                Column(NonPrimarySubmit("", _("Filter"), css_class="btn-outline-secondary"), css_class='col-2')
            )
        )