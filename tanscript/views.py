from django.shortcuts import render

import os
from openai import OpenAI

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
import re
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키를 가져옵니다.
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
API_KEY = os.getenv('YOUTUBE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def get_english_transcript(video_id):
    """
    주어진 비디오 ID에 대한 영어 자막을 가져옵니다.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript_text = ' '.join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        print(f'자막을 가져오는데 실패했습니다: {e}')
        return None

def translate_to_korean(text, tone):
    """
    주어진 텍스트를 한국어로 번역합니다.
    말투는 '전문적인', '친구같은', 또는 '문서같은' 중 하나를 선택할 수 있습니다.
    """
    # 말투에 따른 추가 설명
    tone_description = {
        "기본적인": "",
        "전문적인": "The translation should be professional, suitable for formal presentations and discussions.",
        "친구같은": "Make the translation sound more friendly and casual. It's not suitable for official presentations or discussions, like chatting with a friend. Just translate it to feel comfortable and natural.",
    }
    
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a highly skilled translator fluent in English and Korean."},
        {"role": "user", "content": f"Please translate the following English text into Korean. {tone_description[tone]} The translation should be grammatically correct. The translation should be fluent and natural.: {text}"}
    ])
    return response.choices[0].message.content.strip()

def main():
    youtube_url = input("유튜브 비디오 URL을 입력해주세요: ")
    video_id_match = re.search(r"(?<=v=)[^&#]+", youtube_url) or re.search(r"(?<=be/)[^&#]+", youtube_url)
    video_id = video_id_match.group(0) if video_id_match else None
    
    if video_id:
        english_transcript = get_english_transcript(video_id)
        
        if english_transcript:
            # 사용자로부터 말투 선택 받기
            print("번역할 말투를 선택해주세요: 기본적인, 전문적인, 친구같은")
            selected_tone = input()
            
            if selected_tone not in ["기본적인", "전문적인", "친구같은"]:
                print("잘못된 말투 선택입니다. '기본적인', '전문적인', '친구같은' 중 하나를 선택해주세요.")
                return
            
            korean_translation = translate_to_korean(english_transcript, selected_tone)
            print("번역된 한국어 자막:")
            print(korean_translation)
        else:
            print("유효한 자막을 가져올 수 없습니다.")
    else:
        print("유효한 YouTube 비디오 ID를 찾을 수 없습니다.")


if __name__ == "__main__":
    main()
