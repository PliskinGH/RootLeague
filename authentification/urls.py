from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

app_name = "authentification"

urlpatterns = [
    path('', views.PlayerLoginView.as_view(),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(
                    next_page='index'),
        name='logout'),
    path('change-password/', views.PlayerPasswordChangeView.as_view(),
         name='password_change'
         ),
    path('register/', views.PlayerSignUpView.as_view(), name='register'),
]