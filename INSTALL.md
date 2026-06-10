# Instalação da Skill YT Research

## Instalação Rápida (Universal)

### Windows  (PowerShell)

```powershell
# Clone o repositório
git clone https://github.com/leonamdeoliveira/YOUTUBE-RESEARCH.git

# Copie para o local universal de skills
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.agents\skills\yt-research" -Recurse
```

### Linux / macOS (Terminal)

```bash
# Clone o repositório
git clone https://github.com/leonamdeoliveira/YOUTUBE-RESEARCH.git

# Copie para o local universal de skills
cp -r YOUTUBE-RESEARCH ~/.agents/skills/yt-research
```

## Instalação por Agente

### OpenCode

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.config\opencode\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.config/opencode/skills/yt-research
```

### Claude Code / Claude Desktop

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.claude\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.claude/skills/yt-research
```

### Cursor

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.cursor\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.cursor/skills/yt-research
```

### Windsurf / Devin

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.codeium\windsurf\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.codeium/windsurf/skills/yt-research
```

### Codex

```bash
# Windows
Copy-Item -Path "YOUTUBE-RESEARCH" -Destination "$env:USERPROFILE\.codex\skills\yt-research" -Recurse

# Linux/Mac
cp -r YOUTUBE-RESEARCH ~/.codex/skills/yt-research
```

## Verificação da Instalação

Após instalar, verifique se a skill está no local correto:

```bash
# Windows
Test-Path "$env:USERPROFILE\.agents\skills\yt-research\SKILL.md"

# Linux/Mac
ls ~/.agents/skills/yt-research/SKILL.md
```

Deve retornar `True` ou mostrar o caminho do arquivo.

## Instalação de Dependências

A skill instala automaticamente as dependências na primeira execução. Se preferir instalar manualmente:

```bash
pip install -r requirements.txt
```

O modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (~50MB) é baixado automaticamente na primeira execução.

## Teste Rápido

Após instalar, teste a skill no seu agente:

```
YT energia solar
```

Ou:

```
pesquise no youtube sobre inteligência artificial
```

## Troubleshooting

### Skill não é encontrada

Verifique se a pasta `yt-research` está no local correto:

```bash
# Windows
Get-ChildItem "$env:USERPROFILE\.agents\skills\yt-research"

# Linux/Mac
ls ~/.agents/skills/yt-research/
```

### Erro ao executar scripts

Verifique se Python está instalado e no PATH:

```bash
python --version
```

Deve retornar Python 3.8 ou superior.

### Dependências não instalam

Instale manualmente:

```bash
pip install -r requirements.txt
```

### Erro de permissão

No Windows, execute o PowerShell como Administrador. No Linux/Mac:

```bash
chmod +x ~/.agents/skills/yt-research/scripts/*.py
```

## Desinstalação

Para remover a skill:

```bash
# Windows
Remove-Item "$env:USERPROFILE\.agents\skills\yt-research" -Recurse -Force

# Linux/Mac
rm -rf ~/.agents/skills/yt-research
```

## Comportamento de Inicialização

A skill realiza uma verificação automática de dependências na **primeira execução**:
- Instala pacotes via requirements.txt ou fallback direto
- Baixa o modelo semântico sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Cria o arquivo setup_done.json como confirmação

Nas execuções seguintes, o setup é pulado. Zero overhead adicional.

Para forçar reinstalação manualmente, delete `setup_done.json` e rode:
```bash
python "SKILL_DIR/scripts/setup.py"
```

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório:
https://github.com/leonamdeoliveira/YOUTUBE-RESEARCH/issues
