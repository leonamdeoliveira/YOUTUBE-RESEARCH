#!/usr/bin/env python3
"""
synthesize.py - Prepara transcrições para síntese pelo agente.
Sem uso de LLM - apenas organiza o material para o agente processar.
"""

import argparse
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def prepare_synthesis_input(transcripts_json: str, query: str) -> str:
    """Prepara input estruturado para o agente fazer a síntese."""
    transcripts = json.loads(transcripts_json) if isinstance(transcripts_json, str) else transcripts_json

    output = []
    output.append(f"# Pesquisa: {query}\n")
    output.append("---\n")
    output.append("## Instruções para o Agente\n")
    output.append("Você recebeu transcrições de 3 vídeos relevantes do YouTube sobre o tema acima.")
    output.append("Sua tarefa é criar uma **síntese integrativa** (não apenas resumo) seguindo a metodologia acadêmica.\n")
    output.append("### Estrutura Obrigatória do Output:\n")
    output.append("1. **Resposta Direta** (2-3 frases respondendo diretamente à query)")
    output.append("2. **Contexto e Definições** (conceitos essenciais)")
    output.append("3. **Seções Temáticas** (organizadas por tema, não por fonte)")
    output.append("   - Cada seção começa com uma tese/afirmação central")
    output.append("   - Evidências das 3 fontes entrelaçadas")
    output.append("4. **Pontos de Convergência** (onde as fontes concordam)")
    output.append("5. **Nuances e Limitações** (divergências e ressalvas)")
    output.append("6. **Conclusão** (síntese aplicada à pergunta original)\n")
    output.append("### Regras de Síntese:\n")
    output.append("- Organize por **temas**, não por \"Vídeo 1 disse X, Vídeo 2 disse Y\"")
    output.append("- Comece cada seção com uma **tese**, depois sustente com evidências")
    output.append("- Identifique onde as fontes **convergem ou divergem**")
    output.append("- Não cite as fontes sequencialmente — integre-as")
    output.append("- Se um ponto aparece em múltiplas fontes, reforce como evidência convergente\n")
    output.append("---\n")
    output.append("## Transcrições dos Vídeos\n")

    for i, transcript in enumerate(transcripts, 1):
        if not transcript.get('success'):
            output.append(f"### Vídeo {i}: [FALHOU - {transcript.get('error', 'Erro desconhecido')}]\n")
            continue

        file_path = transcript.get('file_path')
        if not file_path or not os.path.exists(file_path):
            output.append(f"### Vídeo {i}: [Arquivo não encontrado: {file_path}]\n")
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        output.append(f"### Vídeo {i}: {transcript.get('title', 'Sem título')}\n")
        output.append(f"**Canal:** {transcript.get('channel', 'Desconhecido')}")
        output.append(f"**Duração:** {transcript.get('duration_min', 'N/A')} min")
        output.append(f"**Palavras:** {transcript.get('word_count', 'N/A')}")
        output.append(f"**Tipo de transcrição:** {transcript.get('type', 'N/A')} ({transcript.get('language', 'N/A')})\n")
        output.append("<details>")
        output.append("<summary>Clique para ver a transcrição completa</summary>\n")
        output.append(content)
        output.append("\n</details>\n")
        output.append("---\n")

    output.append("## Matriz de Síntese (para uso interno do agente)\n")
    output.append("Antes de escrever, preencha mentalmente esta matriz:\n")
    output.append("| Dimensão | Vídeo 1 | Vídeo 2 | Vídeo 3 |")
    output.append("|----------|---------|---------|---------|")
    output.append("| Argumento principal | ... | ... | ... |")
    output.append("| Evidências-chave | ... | ... | ... |")
    output.append("| Convergências | ... | ... | ... |")
    output.append("| Divergências | ... | ... | ... |")
    output.append("| Limitações | ... | ... | ... |\n")
    output.append("---\n")
    output.append("## Output Esperado\n")
    output.append("Agora escreva a síntese integrativa seguindo a estrutura de 6 partes acima.")
    output.append("Lembre-se: **síntese** conecta as fontes sob temas relevantes à query,")
    output.append("não reporta sequencialmente o que cada fonte disse.\n")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Prepara transcrições para síntese pelo agente')
    parser.add_argument('input', help='JSON com lista de transcrições ou arquivo JSON')
    parser.add_argument('--query', '-q', required=True, help='Query original do usuário')
    parser.add_argument('--output', '-o', help='Arquivo de saída (default: stdout)')

    args = parser.parse_args()

    if os.path.isfile(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            transcripts = json.load(f)
    else:
        transcripts = json.loads(args.input)

    synthesis_input = prepare_synthesis_input(transcripts, args.query)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(synthesis_input)
        print(f"Input de síntese salvo em: {args.output}", file=sys.stderr)
    else:
        print(synthesis_input)

    success_count = sum(1 for t in transcripts if t.get('success'))
    print(f"\nPreparado: {success_count}/{len(transcripts)} transcrições para síntese", file=sys.stderr)

    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
