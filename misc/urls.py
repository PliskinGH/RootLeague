from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "misc"

urlpatterns = [
    path('', TemplateView.as_view(template_name="misc/about.html"), name='about'),
    path('news', views.news, name='news'),
    path('announcement/<slug:slug>', views.announcement, name='announcement'),
]