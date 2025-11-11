from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

app_name = "authentification"

urlpatterns = [
    path('', views.PlayerLoginView.as_view(),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(
                    next_page='home'),
        name='logout'),
    path('password/', views.PlayerPasswordChangeView.as_view(),
         name='password_change'
         ),
    path('reset-password/', views.PlayerPasswordResetView.as_view(),
         name='password_reset'
         ),
    path('reset-password-confirm/<uidb64>/<token>/', views.PlayerPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'
         ),
    path('register/', views.PlayerSignUpView.as_view(), name='register'),
    path('profile/', views.profileEditView, name='profile'),
]