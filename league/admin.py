from django.contrib import admin

from .models import League, Tournament
from .forms import LeagueForm

# Register your models here.

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    form = LeagueForm
    
admin.site.register(Tournament)