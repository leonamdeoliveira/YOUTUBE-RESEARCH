#!/usr/bin/env python3
"""
cleanup.py - Limpa arquivos temporários após a síntese.
"""

import argparse
import glob
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def cleanup_temp_files(skill_dir: str, keep_final: bool = True):
    """Remove arquivos temporários, mantendo apenas resumos finais."""
    skill_dir = os.path.abspath(skill_dir)
    if not os.path.isdir(skill_dir):
        print(f"Diretório da skill inválido: {skill_dir}", file=sys.stderr)
        return

    output_dir = os.path.abspath(os.path.join(skill_dir, 'output'))
    if not output_dir.startswith(skill_dir):
        print(f"Output dir fora da skill: {output_dir}", file=sys.stderr)
        return

    if not os.path.exists(output_dir):
        print(f"Diretório output não encontrado: {output_dir}", file=sys.stderr)
        return

    temp_patterns = ['search_results*.json', 'transcripts.json', 'synthesis_input.md']
    temp_dirs = ['transcripts']

    removed = []

    for pattern in temp_patterns:
        matches = glob.glob(os.path.join(output_dir, pattern))
        for filepath in matches:
            if os.path.isfile(filepath):
                os.remove(filepath)
                removed.append(os.path.basename(filepath))

    for dirname in temp_dirs:
        dirpath = os.path.join(output_dir, dirname)
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
            removed.append(dirname + '/')

    if removed:
        print(f"Arquivos temporários removidos: {', '.join(removed)}", file=sys.stderr)
    else:
        print("Nenhum arquivo temporário encontrado para remover", file=sys.stderr)

    if keep_final:
        temp_basenames = set(removed)
        final_files = [f for f in os.listdir(output_dir) if f.endswith('.md') and f not in temp_basenames]
        if final_files:
            print(f"Resumos finais mantidos: {', '.join(final_files)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description='Limpa arquivos temporários da skill')
    parser.add_argument('skill_dir', help='Caminho do diretório da skill')
    parser.add_argument('--keep-final', action='store_true', default=True, help='Manter resumos finais (default: True)')

    args = parser.parse_args()

    cleanup_temp_files(args.skill_dir, args.keep_final)
    return 0


if __name__ == '__main__':
    sys.exit(main())
