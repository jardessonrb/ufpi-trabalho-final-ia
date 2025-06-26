import os
import json

# Caminho da pasta onde estão os JSONs (diretório atual)
VIDEO_ID = 'ZcMHnzuinUI'
pasta_jsons = '.'
saida_json = f'comentarios_com_replies_{VIDEO_ID}.json'
arquivo_entrada = 'comentarios_completos_ZcMHnzuinUI_1750638689.0803263.json'

# Lista para armazenar os dados combinados


# Iterar pelos arquivos no diretório atual
def agrupar_videos(lista_nomes: list):
    grupos_processados = []
    for nome_arquivo in lista_nomes:
        if nome_arquivo.endswith('.json') and nome_arquivo != saida_json:
            caminho = os.path.join(pasta_jsons, nome_arquivo)
            with open(caminho, 'r', encoding='utf-8') as f:
                try:
                    dados = json.load(f)
                except json.JSONDecodeError as e:
                    print(f'Erro ao ler {nome_arquivo}: {e}')
                    continue

            video_info = dados.get('video', {})
            comentarios = dados.get('comments', [])

            # Filtrar apenas comentários com replies
            comentarios_com_replies = [c for c in comentarios if c.get('replies') and len(c['replies']) > 0]

            for comentario in comentarios_com_replies:
                grupo = {
                    'video': video_info,
                    'comentario_principal': comentario
                }
                grupos_processados.append(grupo)

    print(f'Total de grupos com replies encontrados: {len(grupos_processados)}')
    return grupos_processados

# grupos_processados = agrupar_videos(os.listdir(pasta_jsons))
grupos_processados = agrupar_videos([arquivo_entrada])
# Salvar tudo em um único JSON
with open(saida_json, 'w', encoding='utf-8') as f_out:
    json.dump(grupos_processados, f_out, indent=2, ensure_ascii=False)

print(f'Arquivo de saída gerado: {saida_json}')
