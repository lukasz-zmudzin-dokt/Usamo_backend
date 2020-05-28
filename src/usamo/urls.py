from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
   openapi.Info(
      title="Usamodzielnieni API",
      default_version='v1',
      description="Dokumentacja API projektu Usamodzielnieni",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('account/', include('account.urls')),
    path('cv/', include('cv.urls')),
    path('job/', include('job.urls')),
    path('blog/', include('blog.urls')),
    path('helpline/', include('helpline.urls')),
    path('videos/', include('videos.urls')),
    path('notification/', include('notification.urls')),
    path('chat/', include('chat.urls')),
    path('steps/', include('steps.urls')),
    path('tiles/', include('tiles.urls')),    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]