from django.forms import ModelForm

from .models import League, Tournament

class LeagueForm(ModelForm):
    class Meta:
        model = League
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(LeagueForm, self).__init__(*args, **kwargs)
        if (self.instance and (self.fields['active_season'].queryset.count() >= 1)):
            self.fields['active_season'].queryset = Tournament.objects.filter(league=self.instance)