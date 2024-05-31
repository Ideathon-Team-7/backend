from django.shortcuts import render

# Create your views here.
# transcript_downloader/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from youtube_transcript_api import YouTubeTranscriptApi
import json

@require_GET
def download_script_json(request):
    video_id = request.GET.get('video_id')
    if not video_id:
        return JsonResponse({'error': 'No video_id provided'}, status=400)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Convert transcript to JSON format
    transcript_json = json.dumps(transcript, ensure_ascii=False, indent=4)

    return JsonResponse({'transcript': transcript_json})