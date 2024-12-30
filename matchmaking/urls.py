from django.urls import path

from . import views

app_name = "matchmaking"

urlpatterns = [
    path('', views.listing, name='listing'),
    path('<int:match_id>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('register', views.CreateMatchView.as_view(), name='register'),
    path('update/<int:match_id>/', views.UpdateMatchView.as_view(), name='update'),
    path('search/', views.search, name='search'),
    path('submitted/', views.submissions, name='submissions'),
]