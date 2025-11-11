from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.contrib.flatpages.models import FlatPage

from league.models import League, Tournament

class ReverseItemSiteMapMixin(object):
    def location(self, item):
        return reverse(item)

class MatchSitemap(ReverseItemSiteMapMixin, Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return ["match:listing", "match:register"]

class AboutSitemap(Sitemap):
    priority = 0.9
    changefreq = "yearly"

    def items(self):
        return FlatPage.objects.filter(url__istartswith="/about/") \
                               .exclude(registration_required=True)

class CommunitySitemap(ReverseItemSiteMapMixin, Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["home", "misc:news"]
    
class LeagueSiteMap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return League.objects.all()
    
class LeagueLeaderboardSiteMap(LeagueSiteMap):
    def location(self, item):
        return reverse('league:league_leaderboard', args=(item.id,))
    
class LeagueFactionStatsSiteMap(LeagueSiteMap):
    def location(self, item):
        return reverse('league:league_faction_stats', args=(item.id,))
    
class LeagueTurnOrderStatsSiteMap(LeagueSiteMap):
    def location(self, item):
        return reverse('league:league_turn_order_stats', args=(item.id,))
    
class TournamentSiteMap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return Tournament.objects.all()
    
class TournamentLeaderboardSiteMap(TournamentSiteMap):
    def location(self, item):
        return reverse('league:tournament_leaderboard', args=(item.id,))
    
class TournamentFactionStatsSiteMap(TournamentSiteMap):
    def location(self, item):
        return reverse('league:tournament_faction_stats', args=(item.id,))
    
class TournamentTurnOrderStatsSiteMap(TournamentSiteMap):
    def location(self, item):
        return reverse('league:tournament_turn_order_stats', args=(item.id,))

sitemaps = {
    "about": AboutSitemap,
    "community": CommunitySitemap,
    "match" : MatchSitemap,
    "league_leaderboard": LeagueLeaderboardSiteMap,
    "tournament_leaderboard": TournamentLeaderboardSiteMap,
    "league_faction_stats": LeagueFactionStatsSiteMap,
    "tournament_faction_stats": TournamentFactionStatsSiteMap,
    "league_turn_order_stats": LeagueTurnOrderStatsSiteMap,
    "tournament_turn_order_stats": TournamentTurnOrderStatsSiteMap,
}