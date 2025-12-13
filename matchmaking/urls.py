from django.urls import path

from . import views

app_name = "matchmaking"

urlpatterns = [
    path('', views.listing, name='listing'),
    path('league/', views.league_listing, name='default_league_listing'),
    path('league/<int:league_id>/', views.league_listing, name='league_listing'),
    path('tournament/', views.tournament_listing, name='default_tournament_listing'),
    path('tournament/<int:tournament_id>/', views.tournament_listing, name='tournament_listing'),
    path('<int:match_id>/', views.MatchDetailView.as_view(), name='detail'),
    path('register/', views.CreateMatchView.as_view(), name='register'),
    path('update/<int:match_id>/', views.UpdateMatchView.as_view(), name='update'),
    path('delete/<int:match_id>/', views.DeleteMatchView.as_view(), name='delete'),
    path('submitted/', views.submissions, name='submissions'),
    path('submitted/league/', views.league_submissions, name='default_league_submissions'),
    path('submitted/league/<int:league_id>/', views.league_submissions, name='league_submissions'),
    path('submitted/tournament/', views.tournament_submissions, name='default_tournament_submissions'),
    path('submitted/tournament/<int:tournament_id>/', views.tournament_submissions, name='tournament_submissions'),
    path('played/', views.played_games, name='played_games'),
    path('played/league/', views.league_played_games, name='default_league_played_games'),
    path('played/league/<int:league_id>/', views.league_played_games, name='league_played_games'),
    path('played/tournament/', views.tournament_played_games, name='default_tournament_played_games'),
    path('played/tournament/<int:tournament_id>/', views.tournament_played_games, name='tournament_played_games'),
    path('filters/', views.summary, name='filters'), # kept for legacy url compatibility... TODO Remove at some point
    path('summary/', views.summary, name='summary'),
    path('summary/league/', views.league_summary, name='default_league_summary'),
    path('summary/league/<int:league_id>/', views.league_summary, name='league_summary'),
    path('summary/tournament/', views.tournament_summary, name='default_tournament_summary'),
    path('summary/tournament/<int:tournament_id>/', views.tournament_summary, name='tournament_summary'),
]