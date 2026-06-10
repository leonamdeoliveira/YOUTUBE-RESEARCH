#!/usr/bin/env python3
"""
search.py - Busca e seleciona os 3 vídeos mais relevantes do YouTube.
Sem uso de LLM - zero tokens consumidos nesta etapa.
"""

import argparse
import io
import json
import math
import re
import sys
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def sanitize_query(query: str) -> str:
    """Remove caracteres que podem ser interpretados como argumentos de shell."""
    query = query.strip()
    query = re.sub(r'[\x00-\x1f\x7f]', '', query)
    if len(query) > 200:
        query = query[:200]
    if not query:
        raise ValueError("Query inválida ou vazia após sanitização")
    return query

def detect_language(query: str) -> str:
    """Detecta idioma da query baseado em palavras comuns."""
    pt_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'para', 'com', 'sobre', 'como', 'qual', 'quais', 'e', 'é', 'que', 'em', 'no', 'na'}
    en_words = {'the', 'a', 'an', 'of', 'for', 'to', 'with', 'about', 'how', 'what', 'which', 'and', 'is', 'are', 'in', 'on', 'at'}
    es_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'para', 'con', 'sobre', 'como', 'cual', 'cuales', 'y', 'es', 'que', 'en', 'del'}

    words = set(query.lower().split())
    pt_score = len(words & pt_words)
    en_score = len(words & en_words)
    es_score = len(words & es_words)

    if pt_score >= en_score and pt_score >= es_score:
        return 'pt'
    elif en_score >= es_score:
        return 'en'
    else:
        return 'es'


def search_videos(query: str, max_results: int = 20, language: str = 'pt'):
    """Busca candidatos via yt-dlp sem baixar nada."""
    import yt_dlp

    lang_map = {'pt': 'pt', 'en': 'en', 'es': 'es'}
    search_query = f"ytsearch{max_results}:{query}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            return result.get('entries', [])
    except Exception as e:
        print(f"Erro na busca: {e}", file=sys.stderr)
        return []


def get_video_details(video_url: str):
    """Obtém metadados completos de um vídeo."""
    import yt_dlp

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info
    except Exception as e:
        print(f"Erro ao obter detalhes de {video_url}: {e}", file=sys.stderr)
        return None


def has_transcription(video_info: dict) -> bool:
    """Verifica se o vídeo tem transcrição disponível."""
    if not video_info:
        return False

    subtitles = video_info.get('subtitles', {})
    auto_captions = video_info.get('automatic_captions', {})

    return bool(subtitles) or bool(auto_captions)


def is_short_or_news(video_info: dict) -> bool:
    """Filtra shorts e canais de notícias."""
    if not video_info:
        return True

    title = (video_info.get('title') or '').lower()
    channel = (video_info.get('uploader') or video_info.get('channel') or '').lower()
    duration = video_info.get('duration') or 0

    news_keywords = ['news', 'notícias', 'noticia', 'breaking', 'urgente', 'ao vivo', 'live']
    if any(kw in title for kw in news_keywords):
        return True
    if any(kw in channel for kw in news_keywords):
        return True

    if '#short' in title or 'shorts' in channel:
        return True

    return False


def parse_duration_seconds(duration) -> float:
    """Converte duração para minutos."""
    if isinstance(duration, (int, float)):
        return duration / 60.0
    if isinstance(duration, str):
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            h, m, s = (int(x or 0) for x in match.groups())
            return (h * 60 + m + s / 60)
    return 0


def calculate_semantic_relevance(query: str, title: str, description: str, model=None) -> float:
    """Calcula relevância semântica usando sentence-transformers."""
    if model is None:
        return keyword_relevance(query, title, description)

    try:
        from sentence_transformers import util

        text = f"{title} {description[:300]}"
        emb_query = model.encode(query, convert_to_tensor=True)
        emb_video = model.encode(text, convert_to_tensor=True)
        return float(util.cos_sim(emb_query, emb_video))
    except Exception:
        return keyword_relevance(query, title, description)


def keyword_relevance(query: str, title: str, description: str) -> float:
    """Fallback: relevância por palavras-chave."""
    query_words = set(query.lower().split())
    title_words = set(title.lower().split())
    desc_words = set(description[:300].lower().split())

    if not query_words:
        return 0.0

    title_match = len(query_words & title_words) / len(query_words)
    desc_match = len(query_words & desc_words) / len(query_words)

    return min(title_match * 0.7 + desc_match * 0.3, 1.0)


def calculate_score(video_info: dict, query: str, model=None) -> float:
    """Calcula score composto de relevância."""
    views = video_info.get('view_count') or 0
    likes = video_info.get('like_count') or 0
    comments = video_info.get('comment_count') or 0
    duration_sec = video_info.get('duration') or 0
    duration_min = duration_sec / 60.0

    score_views = math.log10(views + 1) / 8.0
    score_views = min(score_views, 1.0)

    engagement = (likes + comments) / (views + 1) if views > 0 else 0
    score_engagement = min(engagement * 100, 1.0)

    title = video_info.get('title') or ''
    description = video_info.get('description') or ''
    score_semantic = calculate_semantic_relevance(query, title, description, model)

    if 3 <= duration_min <= 60:
        score_duration = 1.0
    elif duration_min < 3:
        score_duration = 0.2
    else:
        score_duration = 0.2

    return (0.25 * score_views +
            0.30 * score_engagement +
            0.35 * score_semantic +
            0.10 * score_duration)


def select_top_videos(query: str, max_results: int = 20, top_n: int = 3, backup_n: int = 7, use_semantic: bool = True):
    """Pipeline completo: busca, filtra, pontua e seleciona top N."""
    query = sanitize_query(query)
    language = detect_language(query)
    print(f"Idioma detectado: {language}", file=sys.stderr)

    candidates = search_videos(query, max_results, language)
    print(f"Candidatos encontrados: {len(candidates)}", file=sys.stderr)

    model = None
    if use_semantic:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("Modelo semântico carregado: paraphrase-multilingual-MiniLM-L12-v2", file=sys.stderr)
        except Exception as e:
            print(f"Aviso: modelo semântico indisponível, usando keyword matching: {e}", file=sys.stderr)

    scored_videos = []
    for entry in candidates:
        video_id = entry.get('id') or entry.get('url', '')
        if not video_id:
            continue

        url = f"https://www.youtube.com/watch?v={video_id}"
        details = get_video_details(url)
        if not details:
            continue

        duration_min = (details.get('duration') or 0) / 60.0
        if duration_min < 3 or duration_min > 60:
            continue

        if is_short_or_news(details):
            continue

        if not has_transcription(details):
            continue

        score = calculate_score(details, query, model)
        scored_videos.append({
            'url': url,
            'video_id': video_id,
            'title': details.get('title'),
            'channel': details.get('uploader') or details.get('channel'),
            'duration_min': round(duration_min, 1),
            'views': details.get('view_count'),
            'likes': details.get('like_count'),
            'score': round(score, 4),
            'language': language,
        })

    scored_videos.sort(key=lambda x: x['score'], reverse=True)
    total_needed = top_n + backup_n
    selected = scored_videos[:total_needed]

    for idx, v in enumerate(selected):
        v['is_primary'] = idx < top_n

    print(f"Vídeos selecionados: {len(selected)} ({top_n} principais + {len(selected) - top_n} backup)", file=sys.stderr)
    for i, v in enumerate(selected, 1):
        marker = "★" if i <= top_n else " "
        print(f"  {marker} {i}. [{v['score']}] {v['title']} ({v['duration_min']}min)", file=sys.stderr)

    return selected


def main():
    parser = argparse.ArgumentParser(description='Busca e seleciona vídeos relevantes do YouTube')
    parser.add_argument('query', help='Query de pesquisa')
    parser.add_argument('--max-results', type=int, default=20, help='Máximo de candidatos (default: 20)')
    parser.add_argument('--top-n', type=int, default=3, help='Número de vídeos para selecionar (default: 3)')
    parser.add_argument('--backup-n', type=int, default=7, help='Número de candidatos extras de backup (default: 7)')
    parser.add_argument('--no-semantic', action='store_true', help='Desativa relevância semântica (mais rápido)')
    parser.add_argument('--output', '-o', help='Arquivo de saída JSON (default: stdout)')

    args = parser.parse_args()

    results = select_top_videos(
        query=args.query,
        max_results=args.max_results,
        top_n=args.top_n,
        backup_n=args.backup_n,
        use_semantic=not args.no_semantic,
    )

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Resultados salvos em: {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0 if results else 1


if __name__ == '__main__':
    sys.exit(main())
