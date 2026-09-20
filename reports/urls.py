from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('match/<int:match_id>/', views.ReportMatchCreateView.as_view(), name='report_match'),
]
