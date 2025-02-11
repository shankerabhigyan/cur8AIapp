# transcription/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('transcribe/', views.TranscriptionViewSet.as_view({'post': 'transcribe'})),
    path('<int:pk>/status/', views.TranscriptionViewSet.as_view({'get': 'status'})),
]