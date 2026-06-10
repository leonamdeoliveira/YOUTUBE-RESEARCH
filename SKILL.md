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

## Comportamento de Desambiguação e Qualidade de Query

Antes de seguir os passos de execução desta skill (Passo 0–5), siga estas regras
para garantir que a **query passada para os scripts seja clara e específica**.

Você, agente de IA, é responsável por:

- Interpretar a intenção do usuário.
- Decidir se a query está clara o suficiente.
- Perguntar por mais contexto quando houver ambiguidade.
- Só então acionar os scripts (`search.py`, `transcribe.py`, `synthesize.py`).

A skill em si **não** faz desambiguação nem conversa com o usuário; ela apenas
executa o pipeline local com a query que você fornecer.

### 1. Extração da query

Quando o usuário pedir para usar esta skill (por exemplo, com `YT <query>`,
`YT: <query>` ou frases como "pesquise no youtube sobre…"):

1. Remova apenas o prefixo de ativação:
   - `YT `
   - `YT: `
   - "pesquise no youtube sobre"
   - "pesquisa no youtube sobre"
2. Considere o restante como a `query_bruta` do usuário.
3. **Não resuma nem encurte** a frase; preserve a intenção original.

Exemplos:

- `YT energia solar` → `query_bruta = "energia solar"`
- `YT: o que é skill` → `query_bruta = "o que é skill"`
- `pesquise no youtube sobre modelos de linguagem grandes`
  → `query_bruta = "modelos de linguagem grandes"`

### 2. Detecção de queries curtas demais

Antes de chamar a skill:

1. Remova conectores comuns de perguntas, como:
   - `o que é`, `o que e`, `what is`, `qué es`, `que es`
2. Conte quantas **palavras de conteúdo** restam (ignorando "de, em, a, o, e" etc.).

Se, depois disso, restarem **1 ou 2 palavras apenas**, considere a query **possivelmente insuficiente**.

Exemplos:

- `o que é skill` → núcleo = `skill` → 1 palavra → **insuficiente**
- `o que é modelo generativo` → núcleo = `modelo generativo` → 2 palavras, mas ainda ambíguo
- `o que é skill em agentes de ia` → núcleo ≈ `skill em agentes de ia`
  → várias palavras → potencialmente clara

### 3. Detecção de ambiguidade sem lista fixa

Você não depende de uma lista fixa de termos ambíguos.  
Em vez disso, **pense explicitamente** sobre a pergunta:

> "Se eu responder isso sem pedir mais contexto, existem 2 ou mais interpretações
>  bem diferentes que poderiam ser a intenção do usuário?"

Se a resposta for **sim**, trate a query como AMBÍGUA.

Exemplos de queries AMBÍGUAS:

- `o que é skill`  
  (pode ser skill em IA, soft skills, skills em jogos, etc.)
- `o que é token`  
  (token de texto, token de autenticação, token de cripto)
- `modelo generativo`  
  (modelo em IA, modelo estatístico, outro contexto)
- `prompt`  
  (prompt de IA, prompt de comando, prompt em UX)

Exemplos de queries CLARAS:

- `o que é skill em agentes de IA e arquivos SKILL.md`
- `diferença entre hard skills e soft skills no mercado de trabalho`
- `como funcionam tokens de texto em modelos de linguagem`
- `modelos generativos em machine learning para imagens`

### 4. O que fazer quando a query for AMBÍGUA ou curta

Se a query for:

- curta demais (após remover "o que é / what is / qué es"), **ou**
- claramente ambígua (vários sentidos muito diferentes possíveis),

**NÃO chame os scripts da skill ainda.**

Em vez disso, faça uma pergunta de clarificação para o usuário, em linguagem natural.

Diretrizes:

- Nomeie o termo ambíguo explicitamente.
- Dê 2–3 exemplos de contextos possíveis.
- Peça que o usuário explique em **uma frase**.

Exemplos de perguntas:

- Para `o que é skill`:
  - `Quando você diz "skill", está falando de habilidades profissionais (hard/soft skills), de skills em agentes de IA / arquivos SKILL.md, de skills em jogos ou de outra coisa? Explique em uma frase.`
- Para `o que é token`:
  - `Você quer saber sobre tokens de texto em modelos de linguagem, tokens de API/autenticação ou tokens em criptomoedas? Explique em uma frase.`
- Para `modelo generativo`:
  - `Você quer entender modelo generativo em IA (como modelos de linguagem e diffusion) ou outro tipo de modelo? Explique em uma frase.`

Após a resposta do usuário:

1. **Reescreva internamente** uma query mais específica que reflita exatamente o contexto explicado.
   - Ex.: usuário: `skill em agentes de IA e SKILL.md`  
     → query_final: `o que é skill em agentes de IA e arquivos SKILL.md`
2. Use essa `query_final` como `"SUA_QUERY_AQUI"` nos comandos de:
   - `search.py`
   - `synthesize.py`

Somente então siga os passos normais da skill (Passo 0–5).

### 5. O que fazer quando a query estiver CLARA

Se, ao analisar a `query_bruta`, você concluir que:

- há apenas **uma interpretação razoável**, e  
- a frase já está suficientemente específica,

então **não peça clarificação**.  
Simplesmente use essa query (ou uma versão minimamente corrigida) como `"SUA_QUERY_AQUI"`.

Exemplos:

- Usuário: `YT o que é skill em agentes de IA e SKILL.md`
  - Intenção clara → use `o que é skill em agentes de IA e SKILL.md`
- Usuário: `pesquise no youtube sobre impactos da IA no mercado de trabalho brasileiro`
  - Intenção clara → use `impactos da IA no mercado de trabalho brasileiro`

### 6. Princípio geral

Prefira **fazer uma pergunta de clarificação** em vez de:

- Chamar a skill com uma query ambígua que possa trazer vídeos totalmente fora de contexto
  (por exemplo, vídeos de jogos quando o usuário queria IA ou carreira).
- Tentar "adivinhar" sozinho um único sentido quando você enxerga claramente
  múltiplas intenções plausíveis.

A skill `YT Research` assume que, quando você a aciona, a query já está
**desambiguada e bem especificada**.

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
- Modelo sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (baixado automaticamente na primeira execução)

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
- **Modelo semântico multilíngue:** sentence-transformers/paraphrase-multilingual-mpnet-base-v2 (~120MB) rodando localmente

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
