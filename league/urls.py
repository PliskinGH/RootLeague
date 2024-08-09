from django.urls import path

from . import views

app_name = "league"

urlpatterns = [
    path('', views.league_leaderboard, name='default_leaderboard'),
    path('<int:league_id>/', views.league_leaderboard, name='league_leaderboard'),
    path('tournament/', views.tournament_leaderboard, name='default_tournament_leaderboard'),
    path('tournament/<int:tournament_id>/', views.tournament_leaderboard, name='tournament_leaderboard'),
    path('global/', views.leaderboard, name='global_leaderboard'),
    path('factions/', views.league_faction_stats, name='default_faction_stats'),
    path('factions/<int:league_id>/', views.league_faction_stats, name='league_faction_stats'),
    path('factions/tournament/', views.tournament_faction_stats, name='default_tournament_faction_stats'),
    path('factions/tournament/<int:tournament_id>/', views.tournament_faction_stats, name='tournament_faction_stats'),
    path('factions/global/', views.faction_stats, name='global_faction_stats'),
]