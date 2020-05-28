from django.urls import path
from . import views


urlpatterns = [
    path('tile/', views.TileCreateView.as_view()),
    path('tile/<int:tile_id>/', views.TileView.as_view()),
    path('', views.TileListView.as_view()),
    path('tile/<int:tile_id>/photo/', views.TilePhotoView.as_view())

]