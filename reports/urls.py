from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportCreateView.as_view(), name='report'),
    path('match/<int:match_id>/', views.ReportMatchCreateView.as_view(), name='report_match'),
]
