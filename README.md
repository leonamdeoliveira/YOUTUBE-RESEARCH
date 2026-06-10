# YT Research

> Skill para agentes de IA que pesquisa vídeos do YouTube, transcreve os mais relevantes e gera sínteses acadêmicas integrativas — economizando tokens com pipeline otimizado.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/agents-OpenCode%20%7C%20Claude%20%7C%20Cursor%20%7C%20Windsurf-orange.svg" alt="Agents">
  <img src="https://img.shields.io/badge/tokens-80%25%20less-brightgreen.svg" alt="Token Savings">
</p>

---

## 📋 Sobre

**YT Research** transforma pesquisas no YouTube em sínteses acadêmicas de alta qualidade. Em vez de apenas resumir vídeos, a skill aplica metodologia de **síntese integrativa de literatura** — conectando múltiplas fontes para construir uma visão completa e responder perguntas complexas.

O diferencial? **Economia extrema de tokens**: 3 das 4 etapas do pipeline rodam localmente sem LLM (busca, transcrição e preparação), consumindo IA apenas na síntese final.

### Use quando:

- Usuário digita `YT <query>` ou `YT: <query>`
- Usuário pede "pesquise no youtube sobre..."
- Usuário quer respostas baseadas em vídeos do YouTube
- Usuário menciona "pesquisa YouTube", "vídeos YouTube", "transcrição YouTube"

---

## ✨ Features

- 🔍 **Busca inteligente** — Scoring composto com relevância semântica (modelo multilíngue), engajamento, views e duração
- 📝 **Transcrição automática** — Baixa legendas manuais ou automáticas com limpeza completa (remove timestamps, repetições, ruído)
- 🎓 **Síntese acadêmica** — Metodologia de 6 partes: resposta direta, contexto, seções temáticas, convergências, nuances e conclusão
- 🌍 **Multilíngue** — Detecta automaticamente o idioma da query e busca vídeos relevantes
- ⚡ **Pipeline otimizado** — 3 etapas sem LLM (zero tokens), apenas a síntese final usa IA
- 🔄 **Compatível com todos** — Funciona com OpenCode, Claude Code, Cursor, Windsurf e qualquer agente que suporte AgentSkills
- 🧹 **Limpeza automática** — Remove arquivos temporários após a síntese, mantendo apenas resumos finais

---

## 🚀 Instalação

### Instalação Rápida (Universal)

```bash
# Clone o repositório
git clone https://github.com/leonamdeoliveira/YOUTUBE-RESEARCH.git

# Copie para o diretório universal de skills
# Windows (PowerShell):
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.agents\skills\yt-research" -Recurse

# Linux/Mac:
cp -r YOUTUBE-RESEARCH ~/.agents/skills/yt-research
```

### Instalação por Agente

<details>
<summary><b>OpenCode</b></summary>

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.config\opencode\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.config/opencode/skills/yt-research
```
</details>

<details>
<summary><b>Claude Code / Claude Desktop</b></summary>

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.claude\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.claude/skills/yt-research
```
</details>

<details>
<summary><b>Cursor</b></summary>

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.cursor\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.cursor/skills/yt-research
```
</details>

<details>
<summary><b>Windsurf / Devin</b></summary>

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.codeium\windsurf\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.codeium/windsurf/skills/yt-research
```
</details>

<details>
<summary><b>Codex</b></summary>

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.codex\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.codex/skills/yt-research
```
</details>

### Dependências

A skill instala automaticamente na primeira execução. Se precisar instalar manualmente:

```bash
pip install yt-dlp sentence-transformers
```

O modelo `paraphrase-multilingual-MiniLM-L12-v2` (~120MB) é baixado automaticamente.

---

## 📖 Uso

### Comando Básico

Digite no chat do seu agente:

```
YT energia solar
```

Ou:

```
pesquise no youtube sobre como funciona inteligência artificial
```

### Opções

- `YT <tema>` — Pesquisa e salva resumo
- `YT --no-save <tema>` — Pesquisa sem salvar arquivo

### Exemplos

```
YT mudanças climáticas
YT como investir em ações
YT: receita de bolo de chocolate
pesquise no youtube sobre machine learning
```

---

## ⚙️ Como Funciona

### Pipeline de 4 Etapas

```
┌─────────────────────────────────────────────────────────────┐
│  1. BUSCA (search.py) — Zero tokens                         │
│     • Detecta idioma da query                               │
│     • Busca 20 candidatos via yt-dlp                        │
│     • Filtra: duração 3-30min, tem transcrição              │
│     • Exclui shorts e notícias                              │
│     • Aplica scoring composto                               │
│     • Retorna top 3 com transcrição confirmada              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. TRANSCRIÇÃO (transcribe.py) — Zero tokens               │
│     • Baixa legendas manuais ou automáticas                 │
│     • Limpeza completa: timestamps, repetições, ruído       │
│     • Salva arquivos .md temporários                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. PREPARAÇÃO (synthesize.py) — Zero tokens                │
│     • Organiza transcrições em input estruturado            │
│     • Inclui instruções de síntese acadêmica                │
│     • Adiciona matriz de síntese para uso interno           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. SÍNTESE (Agente) — Usa LLM                              │
│     • Lê transcrições preparadas                            │
│     • Aplica metodologia de síntese integrativa             │
│     • Gera output estruturado em 6 partes                   │
│     • Mostra no chat e salva em .md (opcional)              │
└─────────────────────────────────────────────────────────────┘
```

### Scoring Composto

Cada vídeo recebe um score baseado em 4 critérios:

| Critério | Peso | Descrição |
|----------|------|-----------|
| **Relevância semântica** | 35% | Similaridade cosseno entre query e título+descrição (modelo multilíngue) |
| **Engajamento** | 30% | (Likes + comentários) / views |
| **Views** | 25% | Escala logarítmica para não favorecer apenas virais |
| **Duração** | 10% | Ideal: 3-30 minutos |

### Estrutura da Síntese (6 Partes)

1. **Resposta Direta** — 2-3 frases respondendo diretamente à query
2. **Contexto e Definições** — Conceitos essenciais para entender o tema
3. **Seções Temáticas** — Organizadas por tema, não por fonte
4. **Pontos de Convergência** — Onde as fontes concordam (evidência forte)
5. **Nuances e Limitações** — Divergências e ressalvas
6. **Conclusão** — Síntese aplicada à pergunta original

---

## 🏗️ Estrutura do Projeto

```
yt-research/
├── SKILL.md              # Instruções da skill (AgentSkills padrão)
├── README.md             # Você está aqui
├── INSTALL.md            # Guia detalhado de instalação
├── LICENSE               # MIT License
├── .gitignore
├── scripts/
│   ├── setup.py          # Instalação automática de dependências
│   ├── search.py         # Busca e seleção de vídeos
│   ├── transcribe.py     # Transcrição e limpeza
│   ├── synthesize.py     # Preparação da síntese
│   └── cleanup.py        # Limpeza de temporários
├── references/
│   └── methodology.md    # Metodologia acadêmica completa
└── output/               # Resumos finais salvos (gitignored)
    └── <tema>.md         # Arquivos de resumo
```

---

## 🤖 Compatibilidade

| Agente | Status | Caminho de Instalação |
|--------|--------|----------------------|
| **OpenCode** | ✅ Compatível | `~/.config/opencode/skills/yt-research/` |
| **Claude Code** | ✅ Compatível | `~/.claude/skills/yt-research/` |
| **Claude Desktop** | ✅ Compatível | `~/.claude/skills/yt-research/` |
| **Cursor** | ✅ Compatível | `~/.cursor/skills/yt-research/` |
| **Windsurf** | ✅ Compatível | `~/.codeium/windsurf/skills/yt-research/` |
| **Devin** | ✅ Compatível | `~/.codeium/windsurf/skills/yt-research/` |
| **Codex** | ✅ Compatível | `~/.codex/skills/yt-research/` |
| **GitHub Copilot** | ✅ Compatível | Via AgentSkills standard |
| **Outros** | ✅ Compatível | Qualquer agente que suporte SKILL.md |

A skill segue o padrão **AgentSkills** aberto, compatível com 30+ ferramentas de IA.

---

## 🔧 Troubleshooting

<details>
<summary><b>"Nenhum vídeo encontrado com transcrição"</b></summary>

Alguns vídeos não têm transcrição disponível. O script pula automaticamente para o próximo candidato. Se menos de 3 vídeos tiverem transcrição, o agente informa.
</details>

<details>
<summary><b>"Erro ao carregar modelo semântico"</b></summary>

O script usa fallback para keyword matching. O resultado é menos preciso mas funcional.
</details>

<details>
<summary><b>Dependências não instalam automaticamente</b></summary>

Execute manualmente:

```bash
python ~/.agents/skills/yt-research/scripts/setup.py
```

Ou instale diretamente:

```bash
pip install yt-dlp sentence-transformers
```
</details>

<details>
<summary><b>Skill não é encontrada pelo agente</b></summary>

Verifique se a pasta `yt-research` está no local correto para seu agente. Consulte [INSTALL.md](INSTALL.md) para caminhos específicos.
</details>

---

## 📊 Requisitos

- **Python** 3.8 ou superior
- **Conexão com internet** (para buscar vídeos e baixar modelo)
- **Espaço em disco** ~150MB (para modelo semântico e dependências)

---

## 🔒 Privacidade

- As queries são enviadas ao YouTube para busca
- As transcrições são processadas localmente
- O modelo semântico roda 100% local (sem envio de dados)
- Nenhum dado é enviado para terceiros além do YouTube

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir novas features
- Melhorar a documentação
- Submeter pull requests

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Download de vídeos e transcrições
- [sentence-transformers](https://www.sbert.net/) — Modelos de embeddings multilíngues
- [AgentSkills](https://agentskills.io/) — Padrão aberto para skills de agentes de IA

---

<p align="center">
  Feito com ❤️ para a comunidade de agentes de IA
</p>
