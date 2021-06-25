from django.conf import settings
from django.urls import path, re_path, include

from unrest.views import index, favicon, intentional_500

urlpatterns = [
    path('intentional_500/', intentional_500),
    path('favicon.ico', favicon),
    re_path('^(?:login|logout|signup|reset-password|new)/', index),
    re_path('^$', index),
    re_path('', include('unrest.user.urls')),
    re_path('', include('unrest.schema.urls')),
]

if settings.DEBUG:  # pragma: no cover
    from django.views.static import serve
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
        }),
    ]