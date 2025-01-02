from django.urls import path

from . import views

app_name = "matchmaking"

urlpatterns = [
    path('', views.listing, name='listing'),
    path('league/', views.league_listing, name='default_league_listing'),
    path('league/<int:league_id>/', views.league_listing, name='league_listing'),
    path('tournament/', views.tournament_listing, name='default_tournament_listing'),
    path('tournament/<int:tournament_id>/', views.tournament_listing, name='tournament_listing'),
    path('<int:match_id>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('register/', views.CreateMatchView.as_view(), name='register'),
    path('update/<int:match_id>/', views.UpdateMatchView.as_view(), name='update'),
    path('submitted/', views.submissions, name='submissions'),
    path('submitted/league/', views.league_submissions, name='default_league_submissions'),
    path('submitted/league/<int:league_id>/', views.league_submissions, name='league_submissions'),
    path('submitted/tournament/', views.tournament_submissions, name='default_tournament_submissions'),
    path('submitted/tournament/<int:tournament_id>/', views.tournament_submissions, name='tournament_submissions'),
]