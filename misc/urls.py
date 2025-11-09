from django.urls import path

from . import views

app_name = "misc"

urlpatterns = [
    path('news', views.news, name='news'),
    path('announcement/<slug:slug>', views.announcement, name='announcement'),
]