#!/usr/bin/env python3
"""
setup.py - Instalação automática de dependências da skill yt-research.
Executa automaticamente na primeira execução da skill.
"""

import importlib
import io
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DEPENDENCIES = {
    'yt_dlp': 'yt-dlp',
    'sentence_transformers': 'sentence-transformers',
}

MINIMUM_VERSIONS = {
    'yt-dlp': '2024.01.01',
    'sentence-transformers': '2.0.0',
}


def check_python_version():
    """Verifica se Python é 3.8+."""
    if sys.version_info < (3, 8):
        print(f"ERRO: Python 3.8+ necessário. Versão atual: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK")
    return True


def check_dependency(module_name: str) -> bool:
    """Verifica se um módulo está instalado."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def install_dependency(package_name: str):
    """Instala um pacote via pip."""
    print(f"Instalando {package_name}...")
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', package_name, '--quiet'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        print(f"  {package_name} instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERRO ao instalar {package_name}: {e}")
        return False


def download_model():
    """Baixa o modelo paraphrase-multilingual-MiniLM-L12-v2."""
    print("Verificando modelo paraphrase-multilingual-MiniLM-L12-v2...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("  Modelo paraphrase-multilingual-MiniLM-L12-v2 OK")
        return True
    except Exception as e:
        print(f"  ERRO ao baixar modelo: {e}")
        return False


def setup():
    """Executa setup completo."""
    print("=" * 50)
    print("YT Research - Instalação de Dependências")
    print("=" * 50)
    print()

    if not check_python_version():
        return False

    print()
    print("Verificando dependências...")

    missing = []
    for module_name, package_name in DEPENDENCIES.items():
        if check_dependency(module_name):
            print(f"  {package_name} OK")
        else:
            print(f"  {package_name} NÃO ENCONTRADO")
            missing.append(package_name)

    if missing:
        print()
        print("Instalando dependências faltantes...")
        for package_name in missing:
            if not install_dependency(package_name):
                return False
    else:
        print()
        print("Todas as dependências já estão instaladas")

    print()
    print("Verificando modelo semântico...")
    if not download_model():
        print("AVISO: Modelo semântico não disponível. Usando fallback para keyword matching.")

    print()
    print("=" * 50)
    print("Setup concluído com sucesso!")
    print("=" * 50)
    return True


def main():
    success = setup()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
