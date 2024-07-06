from django.urls import path, reverse_lazy

from django.contrib.auth import views as auth_views
from . import views

app_name = "authentification"

urlpatterns = [
    path('', auth_views.LoginView.as_view(
            template_name='authentification/login.html',
            redirect_authenticated_user=True),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(
                    next_page='index'),
        name='logout'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
         template_name='authentification/password_change.html',
         success_url = reverse_lazy('authentification:password_change_done') ),
         name='password_change'
         ),
    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='authentification/password_change_done.html'),
         name='password_change_done'
         ),
    path('register', views.PlayerSignUpView.as_view(), name='register'),
]