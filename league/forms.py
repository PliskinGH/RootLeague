from django.forms import ModelForm
from django.core.validators import EMPTY_VALUES
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from .models import League, Tournament

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

class LeagueForm(ModelForm):
    class Meta:
        model = League
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (self.instance):
            self.fields['active_season'].queryset = self.instance.seasons.all()
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