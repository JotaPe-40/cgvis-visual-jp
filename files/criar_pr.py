"""
Script para criar o Pull Request no repositório cgvis-visual-jp
---------------------------------------------------------------
Uso:
  1. Instale: pip install requests
  2. Crie um token em: https://github.com/settings/tokens
     (precisa de permissão: repo → Contents + Pull requests)
  3. Execute: python criar_pr.py
  4. Cole seu token quando solicitado
"""

import requests
import base64
import json
import os
from pathlib import Path
from getpass import getpass

# ── Configuração ─────────────────────────────────────────────────────
OWNER      = "JotaPe-40"
REPO       = "cgvis-visual-jp"
BASE_BRANCH = "main"
NEW_BRANCH  = "lab3-visualizacao-pescadores"
PR_TITLE    = "Lab3: Visualização interativa de armadores de pesca no Brasil"
PR_BODY     = """## Descrição

Implementação completa do Laboratório 3 — INF01047 (UFRGS).

### Arquivos adicionados

| Arquivo | Descrição |
|---------|-----------|
| `visualizacao_pescadores.ipynb` | Notebook principal com todo o código da visualização |
| `mapa_pescadores_brasil.html` | Mapa interativo gerado (abrir no navegador) |
| `MANUAL.md` | Manual de uso completo com instruções passo a passo |

### O que a visualização faz

- **Mapa interativo** do Brasil com 4 camadas sobrepostas:
  - 🗺️ Polígonos dos estados coloridos por região (5 cores distintas)
  - 🔥 Heatmap de concentração de pescadores (azul→vermelho)
  - 📍 MarkerCluster com agrupamento numérico
  - ⚫ Pontos individuais por região

- **Painel lateral deslizante** com 3 abas:
  - **Resumo**: cards com métricas, barras de top municípios
  - **Ranking**: posição do estado/região no contexto nacional
  - **Insights**: análise textual específica por estado/região

- **Interações**: clique em estado → zoom + isolamento + relatório no painel
- **Download**: botão para exportar relatório `.txt` de qualquer estado ou região

### Campos pendentes no RELATORIO.md

- Nome e cartão UFRGS
- Legenda (*caption*) — escrever manualmente
- Conclusão — escrever manualmente

> ⚠️ Esses campos exigem escrita manual sem IA, conforme as regras do lab.

---
*Branch: `lab3-visualizacao-pescadores` → `main`*
"""

API = f"https://api.github.com/repos/{OWNER}/{REPO}"

# ── Arquivos a enviar ─────────────────────────────────────────────────
# Estrutura: (caminho_local, caminho_no_repo)
# Ajuste os caminhos locais conforme onde você salvou os arquivos
ARQUIVOS = [
    ("visualizacao_pescadores.ipynb", "visualizacao_pescadores.ipynb"),
    ("mapa_pescadores_brasil.html",   "mapa_pescadores_brasil.html"),
    ("MANUAL.md",                     "MANUAL.md"),
    ("RELATORIO_preenchido.md",       "RELATORIO.md"),   # substitui o original
    ("CHECKLIST_atualizado.md",       "CHECKLIST.md"),   # marca os checkboxes
]

def get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

def get_sha_branch(token, branch):
    """Retorna o SHA do commit mais recente da branch."""
    r = requests.get(f"{API}/git/ref/heads/{branch}", headers=get_headers(token))
    r.raise_for_status()
    return r.json()["object"]["sha"]

def branch_exists(token, branch):
    r = requests.get(f"{API}/git/ref/heads/{branch}", headers=get_headers(token))
    return r.status_code == 200

def create_branch(token, branch, from_sha):
    payload = {"ref": f"refs/heads/{branch}", "sha": from_sha}
    r = requests.post(f"{API}/git/refs", headers=get_headers(token), json=payload)
    r.raise_for_status()
    print(f"  Branch '{branch}' criada")

def get_file_sha(token, path, branch):
    """Retorna SHA do arquivo se já existir na branch (para update)."""
    r = requests.get(f"{API}/contents/{path}",
                     headers=get_headers(token),
                     params={"ref": branch})
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def upload_file(token, local_path, repo_path, branch):
    """Faz upload (create ou update) de um arquivo."""
    p = Path(local_path)
    if not p.exists():
        print(f"   Arquivo não encontrado: {local_path} — pulando")
        return

    content_bytes = p.read_bytes()
    content_b64   = base64.b64encode(content_bytes).decode()

    existing_sha = get_file_sha(token, repo_path, branch)
    payload = {
        "message": f"Lab3: adiciona {repo_path}",
        "content": content_b64,
        "branch":  branch,
    }
    if existing_sha:
        payload["sha"] = existing_sha
        verb = "Atualizando"
    else:
        verb = "Enviando   "

    r = requests.put(f"{API}/contents/{repo_path}",
                     headers=get_headers(token), json=payload)
    if r.status_code in (200, 201):
        size_kb = len(content_bytes) / 1024
        print(f"   {verb}: {repo_path}  ({size_kb:.0f} KB)")
    else:
        print(f"   Erro ao enviar {repo_path}: {r.status_code} — {r.text[:200]}")

def create_pr(token, branch):
    payload = {
        "title": PR_TITLE,
        "body":  PR_BODY,
        "head":  branch,
        "base":  BASE_BRANCH,
    }
    r = requests.post(f"{API}/pulls", headers=get_headers(token), json=payload)
    if r.status_code == 201:
        pr_url = r.json()["html_url"]
        print(f"\n  🎉 PR criado com sucesso!\n  🔗 {pr_url}")
        return pr_url
    elif r.status_code == 422:
        # PR já existe
        msg = r.json().get("errors", [{}])[0].get("message", "")
        if "already exists" in msg.lower() or "pull request already" in msg.lower():
            print("  ℹ️  PR já existe para essa branch.")
        else:
            print(f"  ❌ Erro 422: {r.text[:300]}")
    else:
        print(f"  ❌ Erro ao criar PR: {r.status_code} — {r.text[:300]}")

# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  Criador de PR — cgvis-visual-jp (Lab3)")
    print("=" * 55)
    print()
    print("Crie um token em: https://github.com/settings/tokens")
    print("Permissões necessárias: repo (Contents + Pull requests)")
    print()
    token = getpass("Cole seu GitHub Token: ").strip()
    if not token:
        print("Token vazio. Abortando.")
        return

    # Verificar autenticação
    me = requests.get("https://api.github.com/user", headers=get_headers(token))
    if me.status_code != 200:
        print(f"❌ Token inválido ou sem permissão: {me.status_code}")
        return
    print(f"  ✅ Autenticado como: {me.json()['login']}\n")

    print(f"[1/3] Preparando branch '{NEW_BRANCH}'...")
    main_sha = get_sha_branch(token, BASE_BRANCH)
    if branch_exists(token, NEW_BRANCH):
        print(f"  ℹ️  Branch já existe, reaproveitando.")
    else:
        create_branch(token, NEW_BRANCH, main_sha)

    print(f"\n[2/3] Enviando {len(ARQUIVOS)} arquivos...")
    for local, remote in ARQUIVOS:
        upload_file(token, local, remote, NEW_BRANCH)

    print("\n[3/3] Criando Pull Request...")
    create_pr(token, NEW_BRANCH)

    print()
    print("Pronto! Acesse o repositório para revisar e fazer merge.")
    print(f"https://github.com/{OWNER}/{REPO}/pulls")

if __name__ == "__main__":
    main()
