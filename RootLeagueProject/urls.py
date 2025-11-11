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
from django.contrib.sitemaps import views as sitemap_views
from rest_framework import routers

from matchmaking import views as match_views
from misc import views as misc_views
from .sitemaps import sitemaps

# DRF rooter
router = routers.SimpleRouter()
router.register('match', match_views.MatchViewset, basename='match')

urlpatterns = [
    path("select2/", include("django_select2.urls")),
    path('', misc_views.home, name='home'),
    path('match/', include('matchmaking.urls', namespace='match')),
    path('misc/', include('misc.urls', namespace='misc')),
    path('auth/', include('authentification.urls', namespace='auth')),
    path('league/', include('league.urls', namespace='league')),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path("pages/", include("django.contrib.flatpages.urls")),
    path(
        "sitemap.xml",
        sitemap_views.index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path('api-auth/', include('rest_framework.urls', namespace="rest_framework")),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
