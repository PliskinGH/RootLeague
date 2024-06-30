from django.urls import path

from . import views

app_name = "matchmaking"

urlpatterns = [
    path('', views.listing, name='listing'),
    path('<int:match_id>/', views.match_details, name='match_details'),
    path('new_match', views.new_match, name='new_match'),
    path('search/', views.search, name='search'),
]