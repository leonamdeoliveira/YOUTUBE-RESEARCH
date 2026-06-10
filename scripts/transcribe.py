#!/usr/bin/env python3
"""
transcribe.py - Baixa e limpa transcrições dos vídeos selecionados.
Sem uso de LLM - zero tokens consumidos nesta etapa.
"""

import argparse
import io
import json
import os
import re
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def validate_video_url(url: str) -> str:
    """Valida que a URL é um link válido do YouTube."""
    url = url.strip()
    if not url:
        raise ValueError("URL vazia")
    if len(url) > 500:
        raise ValueError("URL muito longa")
    if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.be)/', url):
        raise ValueError(f"URL não é um link válido do YouTube: {url}")
    if re.search(r'[;&|`$()]', url):
        raise ValueError(f"URL contém caracteres suspeitos: {url}")
    return url


MAX_DURATION_SECONDS = 60 * 60
MAX_TRANSCRIPT_CHARS = 80_000


def enforce_duration_limit(duration_seconds: int, video_id: str) -> None:
    """Rejeita vídeos acima de 1 hora antes de baixar a transcrição."""
    if duration_seconds > MAX_DURATION_SECONDS:
        raise ValueError(
            f"Vídeo {video_id} tem {duration_seconds//60}min — "
            f"excede limite de {MAX_DURATION_SECONDS//60}min."
        )


def truncate_transcript(text: str, video_title: str = "") -> str:
    """Trunca transcrição em ~20.000 tokens para não explodir contexto do LLM."""
    if len(text) <= MAX_TRANSCRIPT_CHARS:
        return text

    truncated = text[:MAX_TRANSCRIPT_CHARS]
    last_newline = truncated.rfind('\n')
    if last_newline > MAX_TRANSCRIPT_CHARS * 0.8:
        truncated = truncated[:last_newline]

    aviso = (
        f"\n\n---\n"
        f"TRANSCRIÇÃO TRUNCADA: '{video_title}' excedeu {MAX_TRANSCRIPT_CHARS:,} chars "
        f"(~20.000 tokens). Primeiros {len(truncated):,} chars incluídos.\n---"
    )
    return truncated + aviso


def clean_transcript(text: str) -> str:
    """Limpeza completa: remove timestamps, tags VTT, repetições sobrepostas."""
    text = re.sub(r'WEBVTT[^\n]*', '', text)
    text = re.sub(r'Kind:\s*\w+', '', text)
    text = re.sub(r'Language:\s*\w+', '', text)

    text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
    text = re.sub(r'<\d{2}:\d{2}:\d{2}>', '', text)
    text = re.sub(r'</?c>', '', text)
    text = re.sub(r'</?v[^>]*>', '', text)
    text = re.sub(r'<[^>]+>', '', text)

    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&amp;', '&')
    text = text.replace('&nbsp;', ' ')

    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d{2}:\d{2}\s*-->.*$', '', text, flags=re.MULTILINE)

    lines = text.split('\n')
    blocks = []
    current_block = []

    for line in lines:
        line = line.strip()
        if not line:
            if current_block:
                blocks.append(' '.join(current_block))
                current_block = []
            continue
        if re.match(r'^NOTE\b', line):
            continue
        current_block.append(line)

    if current_block:
        blocks.append(' '.join(current_block))

    cleaned_blocks = []
    for i, block in enumerate(blocks):
        if i == 0:
            cleaned_blocks.append(block)
        else:
            prev_block = cleaned_blocks[-1]
            words_prev = prev_block.split()
            words_curr = block.split()

            overlap = 0
            max_check = min(len(words_prev), len(words_curr), 20)

            for check_len in range(max_check, 0, -1):
                if words_prev[-check_len:] == words_curr[:check_len]:
                    overlap = check_len
                    break

            if overlap > 0:
                new_text = ' '.join(words_curr[overlap:])
                if new_text:
                    cleaned_blocks.append(new_text)
            else:
                cleaned_blocks.append(block)

    result = ' '.join(cleaned_blocks)
    result = re.sub(r'\s+', ' ', result)
    return result.strip()


def download_transcript(video_url: str, output_dir: str, video_id: str = None) -> dict:
    """Baixa transcrição de um vídeo via yt-dlp."""
    import yt_dlp

    video_url = validate_video_url(video_url)

    if not video_id:
        video_id = video_url.split('v=')[-1].split('&')[0]

    temp_dir = tempfile.mkdtemp(prefix='yt_transcript_')

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['pt', 'pt-BR', 'en', 'es', '-live_chat'],
        'subtitlesformat': 'vtt',
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            duration_seconds = info.get('duration') or 0
            enforce_duration_limit(duration_seconds, video_id)

            subtitles = info.get('subtitles', {})
            auto_captions = info.get('automatic_captions', {})

            transcript_text = None
            transcript_lang = None
            transcript_type = None

            for lang in ['pt', 'pt-BR', 'en', 'es']:
                if lang in subtitles:
                    subs = subtitles[lang]
                    for fmt in ['vtt', 'srt', 'json3']:
                        for sub in subs:
                            if sub.get('ext') == fmt:
                                transcript_text = download_subtitle_file(sub.get('url'), temp_dir, video_id, fmt)
                                transcript_lang = lang
                                transcript_type = 'manual'
                                break
                        if transcript_text:
                            break
                if transcript_text:
                    break

            if not transcript_text:
                for lang in ['pt', 'pt-BR', 'en', 'es']:
                    if lang in auto_captions:
                        subs = auto_captions[lang]
                        for fmt in ['vtt', 'srt', 'json3']:
                            for sub in subs:
                                if sub.get('ext') == fmt:
                                    transcript_text = download_subtitle_file(sub.get('url'), temp_dir, video_id, fmt)
                                    transcript_lang = lang
                                    transcript_type = 'auto'
                                    break
                            if transcript_text:
                                break
                    if transcript_text:
                        break

            if not transcript_text:
                return {
                    'video_id': video_id,
                    'url': video_url,
                    'title': info.get('title'),
                    'success': False,
                    'error': 'Nenhuma transcrição disponível',
                }

            cleaned = clean_transcript(transcript_text)

            original_len = len(cleaned)
            cleaned = truncate_transcript(cleaned, info.get('title', 'Sem título'))
            if len(cleaned) < original_len:
                print(f"  Transcrição truncada: {original_len:,} -> {MAX_TRANSCRIPT_CHARS:,} chars", file=sys.stderr)
            else:
                print(f"  Transcrição OK: {len(cleaned):,} chars (dentro do limite)", file=sys.stderr)

            output_path = os.path.join(output_dir, f'{video_id}.md')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {info.get('title', 'Sem título')}\n\n")
                f.write(f"**Canal:** {info.get('uploader', 'Desconhecido')}\n")
                f.write(f"**Duração:** {round((info.get('duration') or 0) / 60, 1)} min\n")
                f.write(f"**Idioma da transcrição:** {transcript_lang} ({transcript_type})\n\n")
                f.write(f"---\n\n")
                f.write(cleaned)

            word_count = len(cleaned.split())

            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

            return {
                'video_id': video_id,
                'url': video_url,
                'title': info.get('title'),
                'channel': info.get('uploader'),
                'language': transcript_lang,
                'type': transcript_type,
                'word_count': word_count,
                'file_path': output_path,
                'success': True,
            }

    except Exception as e:
        return {
            'video_id': video_id,
            'url': video_url,
            'success': False,
            'error': str(e),
        }


def download_subtitle_file(url: str, temp_dir: str, video_id: str, ext: str) -> str:
    """Baixa arquivo de legenda e retorna o texto."""
    import urllib.request

    output_path = os.path.join(temp_dir, f'{video_id}.{ext}')

    try:
        urllib.request.urlretrieve(url, output_path)
        with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao baixar legenda: {e}", file=sys.stderr)
        return None


def transcribe_videos(videos_json: str, output_dir: str, target_n: int = 3) -> list:
    """Transcreve lista de vídeos, tentando backups até atingir target_n sucessos."""
    videos = json.loads(videos_json) if isinstance(videos_json, str) else videos_json

    os.makedirs(output_dir, exist_ok=True)

    results = []
    success_count = 0
    for i, video in enumerate(videos, 1):
        if success_count >= target_n:
            remaining = len(videos) - i + 1
            if remaining > 0:
                print(f"Meta atingida: {success_count} transcrições. {remaining} candidatos não processados.", file=sys.stderr)
            break

        url = video.get('url')
        video_id = video.get('video_id')
        is_primary = video.get('is_primary', i <= target_n)
        role = "principal" if is_primary else "backup"
        print(f"[{i}/{len(videos)}] ({role}) Transcrevendo: {video.get('title', url)}", file=sys.stderr)

        result = download_transcript(url, output_dir, video_id)
        results.append(result)

        if result['success']:
            success_count += 1
            print(f"  ✓ {result['word_count']} palavras ({result['type']}, {result['language']}) [{success_count}/{target_n}]", file=sys.stderr)
        else:
            print(f"  ✗ {result.get('error', 'Erro desconhecido')}", file=sys.stderr)
            if not is_primary or success_count < target_n:
                print(f"  → Tentando próximo candidato...", file=sys.stderr)

    return results


def main():
    parser = argparse.ArgumentParser(description='Baixa transcrições de vídeos do YouTube')
    parser.add_argument('input', help='JSON com lista de vídeos ou arquivo JSON')
    parser.add_argument('--output-dir', '-o', default=None, help='Diretório de saída (default: temp)')
    parser.add_argument('--output-json', help='Arquivo JSON de saída (default: stdout)')
    parser.add_argument('--target-n', type=int, default=3, help='Número alvo de transcrições bem-sucedidas (default: 3)')

    args = parser.parse_args()

    if os.path.isfile(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            videos = json.load(f)
    else:
        videos = json.loads(args.input)

    output_dir = args.output_dir or os.path.join(tempfile.gettempdir(), 'yt_transcripts')

    results = transcribe_videos(videos, output_dir, target_n=args.target_n)

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output_json:
        os.makedirs(os.path.dirname(args.output_json) or '.', exist_ok=True)
        with open(args.output_json, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Resultados salvos em: {args.output_json}", file=sys.stderr)
    else:
        print(output)

    success_count = sum(1 for r in results if r['success'])
    target = args.target_n
    if success_count >= target:
        print(f"\nTranscrições: {success_count}/{target} com sucesso (meta atingida)", file=sys.stderr)
    else:
        print(f"\nTranscrições: {success_count}/{target} com sucesso (meta não atingida, {len(results)} candidatos tentados)", file=sys.stderr)

    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
