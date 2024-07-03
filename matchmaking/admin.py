from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from .models import Match, Participant

# Mixn
class AdminURLMixin(object):
    def get_admin_url(self, obj, app = "matchmaking"):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:"+app+"_%s_change" % (
            content_type.model),
            args=(obj.id,))

# Register your models here.
admin.site.register(Participant)

class ParticipantInline(admin.TabularInline, AdminURLMixin):
    model = Participant
    extra = 0
    readonly_fields = ['player_link']
    fields = ['player', 'player_link', 'faction', 'turn_order',
              'winner', 'score','dominance', 'coalition']
    def player_link(self, participant):
        if (participant.player is None):
            url = self.get_admin_url(participant)
            title_link = participant.__str__()
        else:
            url = self.get_admin_url(participant.player, "authentification")
            title_link = participant.player.__str__()
        return mark_safe("<a href='{}'>{}</a>".format(url, title_link))

class ParticipationInline(ParticipantInline):
    readonly_fields = ['match_link']
    fields = ['match', 'match_link', 'faction', 'turn_order',
              'winner', 'score', 'dominance', 'coalition']
    verbose_name = "Participation"
    verbose_name_plural = "Participations"
    def match_link(self, participant):
        url = self.get_admin_url(participant.match)
        return mark_safe("<a href='{}'>{}</a>".format(url, participant.match.__str__()))

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline,] # list of participants in the match
    search_fields = ['title']
    list_filter = ['created_at', 'closed', 'closed_at', 'board_map']
    readonly_fields = ["created_at"]