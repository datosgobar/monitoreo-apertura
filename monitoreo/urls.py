# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = [url(r'^admin/', include(admin.site.urls)),
               url(r'', include('monitoreo.apps.dashboard.urls', namespace="dashboard"))] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
