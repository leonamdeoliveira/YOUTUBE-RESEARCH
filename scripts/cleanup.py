#!/usr/bin/env python3
"""
cleanup.py - Limpa arquivos temporários após a síntese.
"""

import argparse
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def cleanup_temp_files(skill_dir: str, keep_final: bool = True):
    """Remove arquivos temporários, mantendo apenas resumos finais."""
    output_dir = os.path.join(skill_dir, 'output')

    if not os.path.exists(output_dir):
        print(f"Diretório output não encontrado: {output_dir}", file=sys.stderr)
        return

    temp_files = ['search_results.json', 'transcripts.json', 'synthesis_input.md']
    temp_dirs = ['transcripts']

    removed = []

    for filename in temp_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            removed.append(filename)

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
        final_files = [f for f in os.listdir(output_dir) if f.endswith('.md') and f not in temp_files]
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
