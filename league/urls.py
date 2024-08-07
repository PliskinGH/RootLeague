from django.urls import path

from . import views

app_name = "league"

urlpatterns = [
    path('', views.league_leaderboard, name='default_leaderboard'),
    path('<int:league_id>/', views.league_leaderboard, name='league_leaderboard'),
    path('tournament/', views.tournament_leaderboard, name='default_tournament_leaderboard'),
    path('tournament/<int:tournament_id>/', views.tournament_leaderboard, name='tournament_leaderboard'),
    path('global', views.global_leaderboard, name='global_leaderboard'),
]