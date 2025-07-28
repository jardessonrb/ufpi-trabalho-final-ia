import json
import csv
from datetime import datetime
from dateutil import parser

VIDEO_ID = 'ZcMHnzuinUI'
# Arquivo de entrada (JSON consolidado)
arquivo_json = f'./comentarios_com_replies/comentarios_com_replies_json_completo.json'
arquivo_saida = f'./comentarios_padrao_csv/comentarios_estruturados_v2.csv'

def dias_criacao_canal(channel_info):
    if 'publishedAt' in channel_info:
        created_at = parser.parse(channel_info['publishedAt'])
        days_since_channel_created = (comment_time - created_at).days
        return days_since_channel_created
    else:
        days_since_channel_created = ''
        return days_since_channel_created


# Carregar os dados do JSON
with open(arquivo_json, "r", encoding="utf-8") as f:
    dados = json.load(f)

linhas = []

for grupo in dados:
    video = grupo['video']
    comentario = grupo['comentario_principal']
    
    video_id = video['video_id']
    video_time = parser.parse(video['publishedAt'])
    
    # Comentário principal
    comment_id = f"{video['video_id']}_{comentario['channel_id']}_{len(linhas)}"
    comment_time = parser.parse(comentario['publishedAt'])
    seconds_after_video: int = int((comment_time - video_time).total_seconds())
    is_bot = comentario.get('bot', 0)
    channel_info = comentario['channel_info']

    linhas.append({
        'video_id': video_id,
        'comment_id': comment_id,
        'is_reply': 0,
        'reply_to': comment_id,
        'comment_lenght': len(comentario['comment']),
        # 'comment_body': comentario['comment'],
        'author': comentario['author'],
        'channel_id': comentario['channel_id'],
        'root_channel_id': comentario['channel_id'],
        'comment_publishedAt': comentario['publishedAt'],
        'seconds_after_video': seconds_after_video if seconds_after_video >= 0 else 0,
        'seconds_after_comment': 0,
        'subscriber_count': comentario['channel_info'].get('subscriberCount', 0),
        'video_count': comentario['channel_info'].get('videoCount', 0),
        'view_count': comentario['channel_info'].get('viewCount', 0),
        'bot': is_bot,
        'created_channel': dias_criacao_canal(channel_info),
        'comment_is_number': 1 if comentario['comment'].replace(" ", "").isdigit() else 0
    })

    # Replies
    for i, reply in enumerate(comentario.get('replies', [])):
        reply_id = f"{video['video_id']}_{reply['channel_id']}_{len(linhas)}"
        reply_time = parser.parse(reply['publishedAt'])
        seconds_after_video = int((reply_time - video_time).total_seconds())
        seconds_after_comment = int((reply_time - comment_time).total_seconds())
        channel_info = reply['channel_info']

        linhas.append({
            'video_id': video_id,
            'comment_id': reply_id,
            'is_reply': 1,
            'reply_to': comment_id,
            # 'comment_body': reply['comment'],
            'comment_lenght': len(reply['comment']),
            'author': reply['author'],
            'channel_id': reply['channel_id'],
            'root_channel_id': comentario['channel_id'],
            'comment_publishedAt': reply['publishedAt'],
            'seconds_after_video': seconds_after_video if seconds_after_video >= 0 else 0,
            'seconds_after_comment': seconds_after_comment,
            'subscriber_count': reply['channel_info'].get('subscriberCount', 0),
            'video_count': reply['channel_info'].get('videoCount', 0),
            'view_count': reply['channel_info'].get('viewCount', 0),
            'bot': is_bot,
            'created_channel': dias_criacao_canal(channel_info),
            'comment_is_number': 1 if reply['comment'].replace(" ", "").isdigit() else 0

        })

# Escrever o CSV
with open(arquivo_saida, "w", newline='', encoding="utf-8") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=linhas[0].keys())
    writer.writeheader()
    writer.writerows(linhas)

print(f"✅ CSV gerado com sucesso: {arquivo_saida}")
print(f"Total de comentários no dataset: {len(linhas)}")
