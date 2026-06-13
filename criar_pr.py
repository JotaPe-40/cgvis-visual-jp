"""
Cria o Pull Request no repositório cgvis-visual-jp via API do GitHub.
Uso: python criar_pr.py
"""
import requests, base64, json
from pathlib import Path
from getpass import getpass

OWNER       = "JotaPe-40"
REPO        = "cgvis-visual-jp"
BASE_BRANCH = "main"
NEW_BRANCH  = "lab3-visualizacao-pescadores"
API         = f"https://api.github.com/repos/{OWNER}/{REPO}"

PR_TITLE = "Lab3: Visualização interativa de armadores de pesca — v5"
PR_BODY = """## O que foi implementado

Visualização interativa completa para o Laboratório 3 — INF01047 (UFRGS).

### Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `visualizacao_pescadores.ipynb` | Notebook principal documentado |
| `build_map_v5.py` | Script que gera o HTML (baixa Leaflet automaticamente) |
| `mapa_pescadores_brasil.html` | Mapa interativo standalone (abrir no navegador) |
| `MANUAL.md` | Como rodar em 5 passos |

### Funcionalidades do mapa

- Brasil isolado com fundo escuro (sem tiles do mundo)
- Polígonos dos estados coloridos por região com **alto contraste** (5 cores vibrantes)
- Clique num estado → isola visualmente, zoom, filtra heatmap e pontos para aquela UF
- **Heatmap corrigido**: Leaflet e plugin em blocos `<script>` separados + `map.whenReady()` + `invalidateSize()`
- **Pontos com borda contrastante**: radius=5, border escuro sobre fill vívido
- Painel lateral: Resumo, Ranking, Insights, Melhorias
- Modal de relatório completo com download `.txt` e cópia para clipboard
- Todos os assets (Leaflet.js + Leaflet.heat) embutidos inline — funciona offline

### Pendente no RELATORIO.md (preencher manualmente)
- Nome e cartão UFRGS
- Legenda (*caption*)
- Conclusão da análise

---
*Branch: `lab3-visualizacao-pescadores` → `main`*
"""

ARQUIVOS = [
    ("mapa_pescadores_brasil.html",   "mapa_pescadores_brasil.html"),
    ("build_map_v5.py",               "build_map_v5.py"),
    ("visualizacao_pescadores.ipynb", "visualizacao_pescadores.ipynb"),
    ("MANUAL.md",                     "MANUAL.md"),
]

def hdrs(token):
    return {"Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"}

def sha_main(token):
    r = requests.get(f"{API}/git/ref/heads/{BASE_BRANCH}", headers=hdrs(token))
    r.raise_for_status()
    return r.json()["object"]["sha"]

def branch_existe(token):
    r = requests.get(f"{API}/git/ref/heads/{NEW_BRANCH}", headers=hdrs(token))
    return r.status_code == 200

def criar_branch(token, sha):
    r = requests.post(f"{API}/git/refs", headers=hdrs(token),
                      json={"ref": f"refs/heads/{NEW_BRANCH}", "sha": sha})
    r.raise_for_status()
    print(f"  ✅ Branch '{NEW_BRANCH}' criada")

def sha_arquivo(token, path):
    r = requests.get(f"{API}/contents/{path}", headers=hdrs(token),
                     params={"ref": NEW_BRANCH})
    return r.json().get("sha") if r.status_code == 200 else None

def upload(token, local, remote):
    p = Path(local)
    if not p.exists():
        print(f"  ⚠️  {local} não encontrado — pulando")
        return
    content_b64 = base64.b64encode(p.read_bytes()).decode()
    sha = sha_arquivo(token, remote)
    payload = {"message": f"Lab3: {remote}", "content": content_b64, "branch": NEW_BRANCH}
    if sha:
        payload["sha"] = sha
    r = requests.put(f"{API}/contents/{remote}", headers=hdrs(token), json=payload)
    if r.status_code in (200, 201):
        print(f"  ✅ {remote}  ({p.stat().st_size//1024} KB)")
    else:
        print(f"  ❌ {remote}: {r.status_code} — {r.text[:120]}")

def criar_pr(token):
    r = requests.post(f"{API}/pulls", headers=hdrs(token),
                      json={"title": PR_TITLE, "body": PR_BODY,
                            "head": NEW_BRANCH, "base": BASE_BRANCH})
    if r.status_code == 201:
        url = r.json()["html_url"]
        print(f"\n  🎉 PR criado: {url}")
        return url
    elif "already exists" in r.text.lower() or r.status_code == 422:
        print("  ℹ️  PR já existe para esta branch.")
    else:
        print(f"  ❌ Erro ao criar PR: {r.status_code} — {r.text[:200]}")

def main():
    print("=" * 52)
    print("  Criador de PR — cgvis-visual-jp (Lab3 v5)")
    print("=" * 52)
    print("Token em: github.com/settings/tokens → repo")
    print()
    token = getpass("GitHub Token: ").strip()
    if not token:
        print("Token vazio. Abortando."); return

    me = requests.get("https://api.github.com/user", headers=hdrs(token))
    if me.status_code != 200:
        print(f"❌ Token inválido ({me.status_code})"); return
    print(f"  ✅ Autenticado: {me.json()['login']}\n")

    print(f"[1/3] Branch '{NEW_BRANCH}'...")
    if branch_existe(token):
        print("  ℹ️  Branch já existe, reaproveitando")
    else:
        criar_branch(token, sha_main(token))

    print(f"\n[2/3] Enviando {len(ARQUIVOS)} arquivos...")
    for local, remote in ARQUIVOS:
        upload(token, local, remote)

    print("\n[3/3] Pull Request...")
    criar_pr(token)
    print(f"\nhttps://github.com/{OWNER}/{REPO}/pulls")

if __name__ == "__main__":
    main()
