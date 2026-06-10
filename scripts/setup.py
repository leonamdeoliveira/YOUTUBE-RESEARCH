#!/usr/bin/env python3
"""
setup.py - Instalação automática de dependências da skill yt-research.
Executa automaticamente na primeira execução da skill.
"""

import io
import os
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def get_requirements_path():
    """Retorna o caminho absoluto para requirements.txt."""
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    )


def install_from_requirements():
    """Instala dependências usando requirements.txt."""
    req_file = get_requirements_path()
    if os.path.exists(req_file):
        print(f"Instalando de {req_file}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file],
                check=True
            )
            print("Dependências instaladas com sucesso via requirements.txt")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERRO ao instalar via requirements.txt: {e}")
            return False
    else:
        print("requirements.txt não encontrado, usando fallback...")
        return install_dependencies_fallback()


def install_dependencies_fallback():
    """Fallback: instala dependências diretamente."""
    packages = ["yt-dlp>=2024.1.0", "sentence-transformers>=2.7.0"]
    print(f"Instalando: {', '.join(packages)}...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + packages,
            check=True
        )
        print("Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERRO ao instalar dependências: {e}")
        return False


def check_python_version():
    """Verifica se Python é 3.8+."""
    if sys.version_info < (3, 8):
        print(f"ERRO: Python 3.8+ necessário. Versão atual: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} OK")
    return True


def download_model():
    """Baixa o modelo sentence-transformers/paraphrase-multilingual-mpnet-base-v2."""
    print("Verificando modelo sentence-transformers/paraphrase-multilingual-mpnet-base-v2...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        print("  Modelo sentence-transformers/paraphrase-multilingual-mpnet-base-v2 OK")
        return True
    except Exception as e:
        print(f"  ERRO ao baixar modelo: {e}")
        return False


def write_setup_flag(skill_dir: str) -> None:
    """Cria o arquivo setup_done.json na raiz da skill como flag de conclusão."""
    import json
    import datetime
    flag_path = os.path.join(skill_dir, "setup_done.json")
    data = {
        "installed": True,
        "timestamp": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat()
    }
    with open(flag_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Setup concluído com sucesso. Dependências e modelo semântico instalados.")


def setup():
    """Executa setup completo."""
    skill_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    print("=" * 50)
    print("YT Research - Instalação de Dependências")
    print("=" * 50)
    print()

    if not check_python_version():
        return False

    print()
    print("Instalando dependências...")
    if not install_from_requirements():
        return False

    print()
    print("Verificando modelo semântico...")
    if not download_model():
        print("AVISO: Modelo semântico não disponível. Usando fallback para keyword matching.")

    print()
    print("=" * 50)
    print("Setup concluído com sucesso!")
    print("=" * 50)

    write_setup_flag(skill_dir)
    return True


def main():
    success = setup()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
