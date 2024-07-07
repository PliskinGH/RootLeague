"""RootLeagueProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path

from matchmaking import views # import views so we can use them in urls.

urlpatterns = [
    path('', views.index, name='index'),
    path('matchmaking/', include('matchmaking.urls', namespace='matchmaking')),
    path('misc/', include('misc.urls', namespace='misc')),
    path('auth/', include('authentification.urls', namespace='auth')),
    path('leaderboards/', include('leaderboards.urls', namespace='leaderboards')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
