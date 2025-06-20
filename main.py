import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
VIDEO_ID = 'rPXasD5We5k'
BASE_URL = 'https://www.googleapis.com/youtube/v3/'

canal_cache = {}

def get_video_info(video_id, api_key):
    params = {
        'part': 'snippet',
        'id': video_id,
        'key': api_key
    }

    response = requests.get(BASE_URL + 'videos', params=params)
    if response.status_code != 200:
        print('Erro ao buscar vídeo:', response.text)
        return {}

    data = response.json()
    if not data['items']:
        return {}

    snippet = data['items'][0]['snippet']
    return {
        'video_id': video_id,
        'title': snippet['title'],
        'description': snippet.get('description', ''),
        'publishedAt': snippet['publishedAt'],
        'channelTitle': snippet['channelTitle'],
        'channelId': snippet['channelId']
    }

def get_channel_info(channel_id, api_key):
    if channel_id in canal_cache:
        return canal_cache[channel_id]

    params = {
        'part': 'snippet,statistics',
        'id': channel_id,
        'key': api_key
    }

    response = requests.get(BASE_URL + 'channels', params=params)
    if response.status_code != 200:
        print('Erro canal:', response.text)
        canal_cache[channel_id] = {}
        return {}

    data = response.json()
    if not data['items']:
        canal_cache[channel_id] = {}
        return {}

    item = data['items'][0]
    info = {
        'title': item['snippet']['title'],
        'description': item['snippet'].get('description', ''),
        'publishedAt': item['snippet']['publishedAt'],
        'subscriberCount': item['statistics'].get('subscriberCount', 'N/A'),
        'videoCount': item['statistics'].get('videoCount', 'N/A'),
        'viewCount': item['statistics'].get('viewCount', 'N/A')
    }

    canal_cache[channel_id] = info
    return info

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
            print('Erro replies:', response.text)
            break

        data = response.json()
        for item in data.get('items', []):
            snippet = item['snippet']
            channel_id = snippet['authorChannelId'].get('value', 'N/A')
            replies.append({
                'comment': snippet['textDisplay'],
                'author': snippet['authorDisplayName'],
                'channel_id': channel_id,
                'publishedAt': snippet['publishedAt'],
                'channel_info': get_channel_info(channel_id, api_key)
            })

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(1)

    return replies

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
            print('Erro comentários:', response.text)
            break

        data = response.json()
        for item in data.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            channel_id = snippet['authorChannelId'].get('value', 'N/A')

            comment_data = {
                'comment': snippet['textDisplay'],
                'author': snippet['authorDisplayName'],
                'channel_id': channel_id,
                'publishedAt': snippet['publishedAt'],
                'channel_info': get_channel_info(channel_id, api_key),
                'replies': []
            }

            if item['snippet'].get('totalReplyCount', 0) > 0:
                comment_id = item['snippet']['topLevelComment']['id']
                comment_data['replies'] = get_replies(comment_id, api_key)

            comments.append(comment_data)

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(1)

    return comments

if __name__ == '__main__':
    video_info = get_video_info(VIDEO_ID, API_KEY)
    print("Dados do vídeo:", json.dumps(video_info, indent=2, ensure_ascii=False))

    comentarios = get_comments(VIDEO_ID, API_KEY)
    print(f'Total de comentários principais coletados: {len(comentarios)}')

    resultado = {
        'video': video_info,
        'comments': comentarios
    }

    with open('comentarios_completos.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print('Arquivo salvo: comentarios_completos.json')
