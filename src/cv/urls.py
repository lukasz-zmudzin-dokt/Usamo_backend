from django.conf.urls import url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.GenerateView.as_view(), name='generate'),
    path('data/', views.DataView.as_view(), name='data'),
    path('picture/', views.PictureView.as_view(), name='picture'),
    url(r'^(?P<path>.*)$', serve, {'document_root': 'cv'})
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
