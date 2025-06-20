import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
VIDEO_ID = 'rPXasD5We5k'
BASE_URL = 'https://www.googleapis.com/youtube/v3/'

def get_comments(video_id, api_key):
    comments = []
    next_page_token = None

    while True:
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'key': api_key,
            'maxResults': 100,
            'textFormat': 'plainText',
            'pageToken': next_page_token
        }

        response = requests.get(BASE_URL + 'commentThreads', params=params)
        if response.status_code != 200:
            print('Erro:', response.text)
            break

        data = response.json()
        for item in data.get('items', []):
            top_comment = item['snippet']['topLevelComment']['snippet']
            comment_data = {
                'comment': top_comment['textDisplay'],
                'author': top_comment['authorDisplayName'],
                'channel_id': top_comment['authorChannelId'].get('value', 'N/A'),
                'replies': []
            }

            total_replies = item['snippet'].get('totalReplyCount', 0)
            if total_replies > 0:
                comment_id = item['snippet']['topLevelComment']['id']
                comment_data['replies'] = get_replies(comment_id, api_key)

            comments.append(comment_data)

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

        time.sleep(1)  # evitar rate limit

    return comments

def get_replies(parent_id, api_key):
    replies = []
    next_page_token = None

    while True:
        params = {
            'part': 'snippet',
            'parentId': parent_id,
            'key': api_key,
            'maxResults': 100,
            'pageToken': next_page_token
        }

        response = requests.get(BASE_URL + 'comments', params=params)
        if response.status_code != 200:
            print('Erro nas replies:', response.text)
            break

        data = response.json()
        for item in data.get('items', []):
            reply = item['snippet']
            replies.append({
                'comment': reply['textDisplay'],
                'author': reply['authorDisplayName'],
                'channel_id': reply['authorChannelId'].get('value', 'N/A')
            })

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

        time.sleep(1)  # evitar rate limit

    return replies

if __name__ == '__main__':
    resultado = get_comments(VIDEO_ID, API_KEY)

    with open('comentarios_youtube.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f'Total de comentários principais coletados: {len(resultado)}')
