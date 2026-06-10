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

**IMPORTANTE:** Antes de executar qualquer script, determine o caminho absoluto desta skill.

Este caminho será referenciado como `SKILL_DIR` em todos os comandos abaixo.

**Exemplos de SKILL_DIR:**
- Windows: `C:\Users\SeuUsuario\.agents\skills\yt-research`
- Linux/Mac: `/home/seuusuario/.agents/skills/yt-research`

**Como determinar:** O caminho é o diretório onde este arquivo `SKILL.md` está localizado.

## Passo 0: Verificação Automática de Dependências

A skill verifica e instala dependências automaticamente na primeira execução.
Não é necessário rodar nenhum comando de instalação separadamente.

O setup é executado automaticamente pelo `search.py` na primeira vez que a skill é usada.
Um arquivo `setup_done.json` é criado na raiz da skill para indicar que a instalação foi concluída.
Nas execuções seguintes, o setup é pulado automaticamente (zero overhead).

Todos os comandos dos scripts incluem `--skill-dir` automaticamente via
detecção de caminho relativo. Se precisar especificar manualmente:

```bash
python "SKILL_DIR/scripts/search.py" --skill-dir "SKILL_DIR" "SUA_QUERY_AQUI"
python "SKILL_DIR/scripts/transcribe.py" --skill-dir "SKILL_DIR" "ARQUIVO_JSON"
```

## Passo 1: Busca e Seleção de Vídeos

Execute o script de busca para encontrar os 3 vídeos mais relevantes:

```bash
python "SKILL_DIR/scripts/search.py" "SUA_QUERY_AQUI" --top-n 3 --backup-n 7 -o "SKILL_DIR/output/search_results.json"
```

**Exemplo real:**
```bash
python "SKILL_DIR/scripts/search.py" "energia solar" --top-n 3 --backup-n 7 -o "SKILL_DIR/output/search_results.json"
```

Este script:
- Detecta automaticamente o idioma da query
- Busca 20 candidatos via yt-dlp
- Filtra: duração 3-60min, tem transcrição, exclui shorts/notícias
- Aplica scoring composto (relevância semântica 35% + engajamento 30% + views 25% + duração 10%)
- Retorna top 3 principais + 7 candidatos de backup (10 total)

**Se falhar:** Informe o usuário que não foi possível encontrar vídeos suficientes com transcrição.

## Passo 2: Transcrição dos Vídeos

Execute o script de transcrição:

```bash
python "SKILL_DIR/scripts/transcribe.py" "SKILL_DIR/output/search_results.json" -o "SKILL_DIR/output/transcripts" --output-json "SKILL_DIR/output/transcripts.json" --target-n 3
```

Este script:
- Tenta transcrever os 3 vídeos principais em ordem de relevância
- **Se algum falhar**, automaticamente tenta o próximo candidato de backup
- Continua até ter 3 transcrições bem-sucedidas ou acabar a lista de candidatos
- Baixa transcrição dos vídeos (legendas manuais ou automáticas)
- Suporta formatos VTT, SRT e JSON3 (parse automático)
- Faz limpeza completa (remove timestamps, tags, repetições sobrepostas)
- Trunca transcrições acima de ~20.000 tokens (80.000 chars)
- Rejeita vídeos acima de 1 hora (60 minutos)
- Salva arquivos .md em `SKILL_DIR/output/transcripts/`
- Retorna JSON com caminhos dos arquivos e metadados (incluindo duration_min)

**Se falhar:** Se nenhum candidato tiver transcrição, informa o usuário. Caso contrário, prossegue com as transcrições bem-sucedidas.

## Passo 3: Preparação da Síntese

Execute o script de preparação:

```bash
python "SKILL_DIR/scripts/synthesize.py" "SKILL_DIR/output/transcripts.json" -q "SUA_QUERY_AQUI" -o "SKILL_DIR/output/synthesis_input.md"
```

**Exemplo real:**
```bash
python "SKILL_DIR/scripts/synthesize.py" "SKILL_DIR/output/transcripts.json" -q "energia solar" -o "SKILL_DIR/output/synthesis_input.md"
```

Este script:
- Lê as transcrições do JSON
- Prepara input estruturado com instruções para o agente
- Inclui metadados dos vídeos (título, canal, duração, palavras)
- Inclui matriz de síntese para uso interno

## Passo 4: Síntese Final (Pelo Agente)

**Leia o arquivo `SKILL_DIR/output/synthesis_input.md`** e siga as instruções contidas nele para criar a síntese integrativa.

O arquivo contém:
- Query original do usuário
- Instruções detalhadas de síntese
- Transcrições dos 3 vídeos (em detalhes colapsáveis)
- Matriz de síntese para uso interno
- Estrutura obrigatória de 6 partes

**Sua tarefa:** Ler as transcrições e criar uma **síntese integrativa** (não resumo) seguindo a metodologia acadêmica descrita no arquivo.

## Passo 5: Output para o Usuário

Após criar a síntese:

1. **Mostre o resultado no chat** formatado em markdown
2. **Pergunte se quer salvar:** "Deseja salvar esta pesquisa em arquivo? (sim/não)"
3. **Se sim:** Salve em `SKILL_DIR/output/NOME_DA_PESQUISA.md` com a estrutura:

```markdown
# Título da Pesquisa

<conteúdo da síntese>

---
*Pesquisa realizada em DD/MM/AAAA*
```

O nome do arquivo deve ser um slug da query (ex: "energia-solar.md").

## Passo 6: Limpeza de Arquivos Temporários

Após salvar o resumo final (se o usuário quiser salvar), execute o script de limpeza:

```bash
python "SKILL_DIR/scripts/cleanup.py" "SKILL_DIR"
```

Este script:
- Valida se o SKILL_DIR existe e é válido
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
- yt-dlp (instalado automaticamente na primeira execução)
- sentence-transformers (instalado automaticamente na primeira execução)
- torch (instalado automaticamente na primeira execução)
- transformers (instalado automaticamente na primeira execução)
- numpy (instalado automaticamente na primeira execução)
- Modelo paraphrase-multilingual-MiniLM-L12-v2 (baixado automaticamente na primeira execução)

## Estrutura de Arquivos

```
yt-research/
├── SKILL.md                    # Este arquivo
├── README.md                   # Guia do usuário
├── INSTALL.md                  # Guia detalhado de instalação
├── LICENSE                     # MIT License
├── .gitignore                  # Ignora output/ e setup_done.json
├── requirements.txt            # Dependências Python
├── setup_done.json             # Flag de setup concluído (gitignored)
├── scripts/
│   ├── setup.py                # Instalação automática de dependências
│   ├── search.py               # Busca + seleção (zero tokens)
│   ├── transcribe.py           # Transcrição + limpeza (zero tokens)
│   ├── synthesize.py           # Preparação para síntese (zero tokens)
│   └── cleanup.py              # Limpeza de temporários
├── references/
│   └── methodology.md          # Metodologia acadêmica completa
└── output/                     # Pasta de saída (resumos finais, gitignored)
    └── <query-slug>.md         # Resumos finais salvos
```

## Economia de Tokens

- **Setup:** Executado apenas na primeira execução (flag `setup_done.json`). Nas execuções seguintes, zero overhead.
- **Etapas 1-3:** Zero tokens de LLM (scripts Python puros)
- **Etapa 4:** Agente lê transcrições e faz síntese diretamente
- **Limpeza de transcrição:** Remove timestamps e formatação inútil antes de enviar ao agente
- **Modelo semântico multilíngue:** paraphrase-multilingual-MiniLM-L12-v2 (~120MB) rodando localmente

## Troubleshooting

**"Nenhum vídeo encontrado com transcrição"**
- Alguns vídeos não têm transcrição disponível
- O script busca 10 candidatos (3 principais + 7 backups)
- Se uma transcrição falhar, automaticamente tenta o próximo candidato
- Só falha se nenhum dos candidatos tiver transcrição utilizável

**"Erro ao carregar modelo semântico"**
- O script usa fallback para keyword matching
- Resultado é menos preciso mas funcional

**"Transcrição vazia ou muito curta"**
- Algumas transcrições automáticas são ruins
- O script filtra por contagem mínima de palavras

**Dependências não instalam automaticamente**
- Execute manualmente: `pip install -r SKILL_DIR/requirements.txt`
- Ou execute: `python SKILL_DIR/scripts/setup.py`
