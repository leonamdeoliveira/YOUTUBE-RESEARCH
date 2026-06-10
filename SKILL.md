---
name: yt-research
description: Pesquisa no YouTube com síntese acadêmica. Use quando o usuário pedir para pesquisar no YouTube, usar "YT", ou quiser respostas baseadas em vídeos do YouTube. Exemplo "YT energia solar" ou "pesquise no youtube sobre X".
---

# YT Research - Pesquisa YouTube com Síntese Acadêmica

## Quando Usar

- Usuário digita `YT <query>` ou `YT: <query>`
- Usuário pede "pesquise no youtube sobre..."
- Usuário quer respostas baseadas em vídeos do YouTube
- Usuário menciona "pesquisa YouTube", "vídeos YouTube", "transcrição YouTube"

## Configuração do Caminho

**IMPORTANTE:** Antes de executar qualquer script, determine o caminho absoluto desta skill:

- No Windows: `C:\Users\<usuario>\.agents\skills\yt-research\`
- No Linux/Mac: `~/.agents/skills/yt-research/`

Use este caminho como `<SKILL_DIR>` em todos os comandos abaixo.

## Passo 0: Verificação Automática de Dependências

**ANTES de qualquer outra coisa**, verifique se as dependências estão instaladas:

```bash
python "<SKILL_DIR>/scripts/setup.py"
```

Este script:
- Verifica Python 3.8+
- Verifica se `yt-dlp` está instalado
- Verifica se `sentence-transformers` está instalado
- Instala automaticamente o que estiver faltando
- Baixa o modelo `paraphrase-multilingual-MiniLM-L12-v2` (~120MB) na primeira execução

**Se o setup falhar:** Informe o usuário e sugira instalação manual:
```bash
pip install yt-dlp sentence-transformers
```

## Workflow Completo

### Passo 1: Busca e Seleção de Vídeos

Execute o script de busca para encontrar os 3 vídeos mais relevantes:

```bash
python "<SKILL_DIR>/scripts/search.py" "<query>" --top-n 3 -o "<SKILL_DIR>/output/search_results.json"
```

Este script:
- Detecta automaticamente o idioma da query
- Busca 20 candidatos via yt-dlp
- Filtra: duração 3-30min, tem transcrição, exclui shorts/notícias
- Aplica scoring composto (views 25% + engajamento 30% + semântica 35% + duração 10%)
- Retorna top 3 com transcrição confirmada

**Se falhar:** Informe o usuário que não foi possível encontrar vídeos suficientes com transcrição.

### Passo 2: Transcrição dos Vídeos

Execute o script de transcrição:

```bash
python "<SKILL_DIR>/scripts/transcribe.py" "<SKILL_DIR>/output/search_results.json" -o "<SKILL_DIR>/output/transcripts" --output-json "<SKILL_DIR>/output/transcripts.json"
```

Este script:
- Baixa transcrição dos 3 vídeos (legendas manuais ou automáticas)
- Faz limpeza leve (remove timestamps, linhas vazias, repetições)
- Salva arquivos .md em `output/transcripts/`
- Retorna JSON com caminhos dos arquivos

**Se falhar:** Informe quantas transcrições foram bem-sucedidas e prossega apenas com essas.

### Passo 3: Preparação da Síntese

Execute o script de preparação:

```bash
python "<SKILL_DIR>/scripts/synthesize.py" "<SKILL_DIR>/output/transcripts.json" -q "<query>" -o "<SKILL_DIR>/output/synthesis_input.md"
```

Este script:
- Lê as transcrições
- Prepara input estruturado com instruções para o agente
- Inclui matriz de síntese para uso interno

### Passo 4: Síntese Final (Pelo Agente)

**Leia o arquivo `output/synthesis_input.md`** e siga as instruções contidas nele para criar a síntese integrativa.

O arquivo contém:
- Query original do usuário
- Instruções detalhadas de síntese
- Transcrições dos 3 vídeos (em detalhes colapsáveis)
- Matriz de síntese para uso interno
- Estrutura obrigatória de 6 partes

**Sua tarefa:** Ler as transcrições e criar uma **síntese integrativa** (não resumo) seguindo a metodologia acadêmica descrita no arquivo.

### Passo 5: Output para o Usuário

Após criar a síntese:

1. **Mostre o resultado no chat** formatado em markdown
2. **Pergunte se quer salvar:** "Deseja salvar esta pesquisa em arquivo? (sim/não)"
3. **Se sim:** Salve em `<SKILL_DIR>/output/<query-slug>.md` com a estrutura:

```markdown
# <Query do usuário>

<conteúdo da síntese>

---
*Pesquisa realizada em <data>*
```

### Passo 6: Limpeza de Arquivos Temporários

Após salvar o resumo final (se o usuário quiser salvar), execute o script de limpeza:

```bash
python "<SKILL_DIR>/scripts/cleanup.py" "<SKILL_DIR>"
```

Este script:
- Remove `search_results.json`, `transcripts.json`, `synthesis_input.md`
- Remove pasta `transcripts/` com arquivos individuais
- Mantém apenas os resumos finais salvos em `output/`

## Estrutura da Síntese (6 Partes)

1. **Resposta Direta** (2-3 frases respondendo diretamente)
2. **Contexto e Definições** (conceitos essenciais)
3. **Seções Temáticas** (organizadas por tema, não por fonte)
4. **Pontos de Convergência** (onde as fontes concordam)
5. **Nuances e Limitações** (divergências e ressalvas)
6. **Conclusão** (síntese aplicada à pergunta)

## Regras de Síntese

- Organize por **temas**, não por "Vídeo 1 disse X, Vídeo 2 disse Y"
- Comece cada seção com uma **tese**, depois sustente com evidências
- Identifique onde as fontes **convergem ou divergem**
- Não cite as fontes sequencialmente — integre-as
- Se um ponto aparece em múltiplas fontes, reforce como evidência convergente

## Opções de Comando

- `YT <query>` - Pesquisa normal e salva
- `YT --no-save <query>` - Pesquisa sem salvar arquivo
- `YT: <query>` - Alternativa com dois-pontos

## Dependências

- Python 3.8+
- yt-dlp (instalado automaticamente pelo setup.py)
- sentence-transformers (instalado automaticamente pelo setup.py)
- Modelo paraphrase-multilingual-MiniLM-L12-v2 (baixado automaticamente na primeira execução)

## Estrutura de Arquivos

```
yt-research/
├── SKILL.md                    # Este arquivo
├── README.md                   # Guia do usuário
├── scripts/
│   ├── setup.py                # Instalação automática de dependências
│   ├── search.py               # Busca + seleção (zero tokens)
│   ├── transcribe.py           # Transcrição + limpeza (zero tokens)
│   ├── synthesize.py           # Preparação para síntese (zero tokens)
│   └── cleanup.py              # Limpeza de temporários
├── references/
│   └── methodology.md          # Metodologia acadêmica completa
└── output/                     # Pasta de saída (resumos finais)
    └── <query-slug>.md         # Resumos finais salvos
```

## Economia de Tokens

- **Etapas 1-3:** Zero tokens de LLM (scripts Python puros)
- **Etapa 4:** Agente lê transcrições e faz síntese diretamente
- **Limpeza de transcrição:** Remove timestamps e formatação inútil antes de enviar ao agente
- **Modelo semântico multilíngue:** paraphrase-multilingual-MiniLM-L12-v2 (~120MB) rodando localmente

## Troubleshooting

**"Nenhum vídeo encontrado com transcrição"**
- Alguns vídeos não têm transcrição disponível
- O script pula automaticamente para o próximo candidato
- Se menos de 3 vídeos tiverem transcrição, informa o usuário

**"Erro ao carregar modelo semântico"**
- O script usa fallback para keyword matching
- Resultado é menos preciso mas funcional

**"Transcrição vazia ou muito curta"**
- Algumas transcrições automáticas são ruins
- O script filtra por contagem mínima de palavras

**Dependências não instalam automaticamente**
- Execute manualmente: `pip install yt-dlp sentence-transformers`
- Ou execute: `python <SKILL_DIR>/scripts/setup.py`
