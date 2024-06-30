from django.urls import path

from . import views

app_name = "misc"

urlpatterns = [
    path('', views.about, name='about'),
    path('about', views.about, name='about'),
]