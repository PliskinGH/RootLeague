from django.urls import path

from . import views

app_name = "league"

urlpatterns = [
    path('', views.global_leaderboard, name='global_leaderboard'),
    path('<int:league_id>/', views.league_leaderboard, name='league_leaderboard'),
]