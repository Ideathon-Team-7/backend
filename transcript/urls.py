# transcript_downloader/urls.py
from django.urls import path
from .views import download_script_json

urlpatterns = [
    path('download-script/', download_script_json, name='download_script'),
]