# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from des import urls as des_urls


admin.autodiscover()

urlpatterns = [url(r'', include('monitoreo.apps.dashboard.urls',
                                namespace="dashboard")),
               url(r'', include('django_datajsonar.urls',
                                namespace="django_datajsonar")),
               url(r'^django-rq/', include('django_rq.urls')),
               url(r'^django-des/', include(des_urls)),
               url(r'^admin/password_reset/$',
                   auth_views.PasswordResetView.as_view(),
                   name='admin_password_reset',),
               url(r'^admin/password_reset/done/$',
                   auth_views.PasswordResetDoneView.as_view(),
                   name='password_reset_done',),
               url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                   auth_views.PasswordResetConfirmView.as_view(),
                   name='password_reset_confirm',),
               url(r'^reset/done/$',
                   auth_views.PasswordResetCompleteView.as_view(),
                   name='password_reset_complete',),
               url(r'^admin/', include(admin.site.urls)),
               ]\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
