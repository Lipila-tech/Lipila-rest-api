from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('video/', views.video_upload, name='video_upload'),
    path('audio/', views.audio_upload, name='audio_upload'),
    path('youtube', views.you_tube_player, name='you_tube_player'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)