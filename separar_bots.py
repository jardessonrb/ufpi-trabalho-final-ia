import csv

entrada = 'comentarios_estruturados.csv'
saida = 'bots_unicos.csv'

with open(entrada, 'r', encoding='utf-8') as f_in:
    reader = csv.DictReader(f_in)
    
    bots_vistos = set()
    bots_filtrados = []

    for row in reader:
        if row['bot'] == '1':
            chave = (row['channel_id'], row['author'])
            if chave not in bots_vistos:
                bots_vistos.add(chave)
                bots_filtrados.append({
                    'channel_id': row['channel_id'],
                    'author': row['author'],
                    'bot': row['bot'],
                    # 'comment': row['comment_body']
                })

with open(saida, 'w', newline='', encoding='utf-8') as f_out:
    writer = csv.DictWriter(f_out, fieldnames=['channel_id', 'author', 'bot'])
    writer.writeheader()
    writer.writerows(bots_filtrados)

print(f"✅ Arquivo gerado com {len(bots_filtrados)} bots únicos: {saida}")
