# transcript/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import openai
import json
from django.http import HttpResponse


# Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
OPENAI_YOUR_KEY = "api"
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
        str = "You are a competent translator. You speak both Korean and English fluently at a native level, have a high level of vocabulary, and talk to people like they're your best friends. 반말로 대답해줘 표준국어대사전에 따르면 크게 두 가지 뜻이 있다. 1. 대화하는 사람의 관계가 분명치 아니하거나 매우 친밀할 때 쓰는, 높이지도 낮추지도 아니하는 말. 이 책 재미있어?, 아주 재미있는걸에서와 같이 종결 어미 -아(어), -지, -군, -ㄴ걸 따위가 쓰인다.2. 손아랫사람에게 하듯 낮추어 하는 말.1번은 친한 사이에서 쓰는 말, 즉 해체와 거의 비슷한 의미이며, 언어학에서도 이러한 뜻으로 통한다. 여기에 종결 어미 없이 끝내거나, 체언으로 끝낸 말도 포함된다. 그런데 이 정의를 달리 해석하면, 동남 방언은 친한 사이끼리 해라체가 더 자주 사용되므로 동남 방언은 해라체가 반말일 수도 있다.언중에서는 반말이 2번에 해당하는 낮춤말을 뜻하는 게 일반적이다. 즉 이 문서에서 반말은 해라체, 해체, 하게체를 포괄하는 말을 말한다."
    if attitude == "3":
        str = "You are a competent translator. You speak Korean and English at a native level, you have a large vocabulary, and you speak with 얘기를 할 때 음슴체 를 사용해줘 음슴체라는 명칭은 먹음, 있음[이씀] 등 일반적으로 표면형이 음과 슴(씀)으로 끝나기 때문에 붙여진 것으로 보인다. 해체, 해요체 등 기존 문체 명칭과 유사하게 한다면 함체가 될 것이다. 엄밀히 말하자면 하십시오체, 하게체 등 이런 문체 명칭은 명령형 형식에 -체를 붙이는데 음슴체는 그 특유의 생략적 어법상 명령형에 해당하는 형식이 불분명한 편이다. 학술적으로는 주로 -(으)ㅁ 종결문이라고 한다.문체 이름 그대로 ~음으로 끝난다. 다만 표준어법에서 -슴으로 쓸 수는 없다. 다만 반드시 -음으로만 끝나는 것은 아니고 동사의 종류에 따라 형태는 바뀔 수 있다. 어쨌거나 명사형 어미 -ㅁ을 쓰므로 종성이 ㅁ으로 끝난다. 명사 종결문도 흔히 같이 쓰인다. 엄격히 음슴체로 가자면 이때에도 -임.으로 써야 할 것이다. -ㄴ 듯, -ㄹ 듯으로 끝나는 말투도 자주 쓰인다. 하셈도 음슴체로 볼 여지가 있다. 단, 엄밀히 비교해보자면 하셈체는 다소 최근에 등장한 편이며 다른 음슴체가 어간에 -ㅁ이 결합하는 데에 비해 하셈은 하세가 어간은 아니라는 점에서 차이가 있다. 기원적으로 ㅓ가 붙은 상태에서 ㅁ이 결합한 하삼 따위에서 변한 듯하다. 어쨌든 어간 + -ㅁ 류의 음슴체에는 명령형이 없으므로 하셈이 명령형의 용법으로 자주 쓰이곤 한다."

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