# transcript/urls.py
from django.urls import path
from .views import download_and_translate_script

urlpatterns = [
    path('translate-scipt/', download_and_translate_script, name='download_and_translate_script'),
]
