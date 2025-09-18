from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.contrib.flatpages.models import FlatPage

from league.models import League, Tournament

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "never"

    def items(self):
        return ["match:listing", "match:register"]

    def location(self, item):
        return reverse(item)

class FlatPageSitemap(Sitemap):
    priority = 0.9
    changefreq = "yearly"

    def items(self):
        return FlatPage.objects.all()
    
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
    "static" : StaticViewSitemap,
    "flatpage": FlatPageSitemap,
    "league_leaderboard": LeagueLeaderboardSiteMap,
    "tournament_leaderboard": TournamentLeaderboardSiteMap,
    "league_faction_stats": LeagueFactionStatsSiteMap,
    "tournament_faction_stats": TournamentFactionStatsSiteMap,
    "league_turn_order_stats": LeagueTurnOrderStatsSiteMap,
    "tournament_turn_order_stats": TournamentTurnOrderStatsSiteMap,
}