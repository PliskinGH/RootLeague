from django.urls import path

from . import views

app_name = "matchmaking"

urlpatterns = [
    path('', views.listing, name='listing'),
    path('<int:match_id>/', views.match_detail, name='match_detail'),
    path('register', views.CreateMatchView.as_view(), name='register'),
    path('search/', views.search, name='search'),
]