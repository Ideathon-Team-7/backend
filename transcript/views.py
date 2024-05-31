# transcript/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import openai
import json
from django.http import HttpResponse


# Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
OPENAI_YOUR_KEY = "API_KEY"
openai.api_key = OPENAI_YOUR_KEY

def extract_video_id(url):
    query = urlparse(url)
    if query.hostname == 'www.youtube.com':
        if query.path == '/watch':
            video_id = parse_qs(query.query)['v'][0]
            return video_id
        else:
            return None
    elif query.hostname == 'youtu.be':
        return query.path[1:]
    else:
        return None

def translate_transcript(transcript_json, attitude):

    print("Attitude:", attitude)

    str = "You are a competent translator. You speak both Korean and English fluently at a native level and have a high level of vocabulary."
    if attitude == "2":
        str = "You are a competent translator. You speak both Korean and English fluently at a native level, have a high level of vocabulary, and talk to people like they're your best friends."
    if attitude == "3":
        str = "You are a competent translator. You speak both Korean and English fluently at a native level, have a high level of vocabulary, and you sound very professional and formal."

    print("str", str)
    prompt = "Please translate the following JSON-formatted English subtitle data into a natural and clean Korean language with the format intact :\n\n" + transcript_json
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": str},
            {"role": "user", "content": prompt}
        ]
    )
    translated_text = response.choices[0].message['content']
    return translated_text

@require_GET
def download_and_translate_script(request):
    url = request.GET.get('url')
    attitude = request.GET.get('attitude')
    video_id = extract_video_id(url)

    print("Attitude:", attitude)
    if not video_id:
        return JsonResponse({'error': 'No video_id provided'}, status=400)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    transcript_json = json.dumps(transcript, ensure_ascii=False, indent=4)
    translated_transcript = translate_transcript(transcript_json, attitude)


    return HttpResponse(translated_transcript, content_type='application/json')