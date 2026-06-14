"""
Cria o Pull Request — cgvis-visual-jp (Lab3 v7)
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

PR_TITLE = "Lab3: Visualização interativa v7 — heatmap, isolamento e modo claro/escuro"

PR_BODY = """## Resumo

Implementação completa do Laboratório 3 — INF01047 UFRGS.

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `visualizacao_pescadores.ipynb` | Notebook documentado |
| `build_map_v7.py` | Script Python que gera o HTML |
| `template_v7.html` | Template HTML (usado pelo script) |
| `mapa_pescadores_brasil.html` | Mapa interativo standalone |
| `MANUAL.md` | Como rodar em 5 passos |

## O que foi implementado

### Correções desta versão
- **Heatmap funcionando**: Leaflet e Leaflet.heat em `<script>` separados + `map.whenReady()` + `invalidateSize()`
- **Isolamento de estados corrigido**: polígonos em SVG (sem `preferCanvas`), estados não selecionados com `fillOpacity:0.97` — heatmap canvas não interfere
- **Dados de heat com intensidade** `[lat, lon, 0..1]` normalizada

### Funcionalidades
- 🗺️ Brasil isolado com fundo escuro, `maxBounds` impedindo scroll fora
- 🔥 Heatmap de concentração (azul → vermelho)
- ⚫ Pontos individuais com alto contraste (radius=5, border escuro)
- 🌊 Overlay de bacias hidrográficas (Natural Earth)
- 🔍 Busca por município (5.571 municípios com geocoords)
- 📅 Série temporal por estado e por região (Chart.js, gráfico animado)
- 🎯 Filtro por tipo: Pessoa Física × Jurídica | Armador × Proprietário
- 📈 Correlação IDH × pescadores (scatter plot SVG + Pearson)
- 📄 Relatório por estado: download `.txt` e exportar PDF
- 🌙/☀️ **Modo claro/escuro** com variáveis CSS
- UI clean com design system em CSS vars, backdrop-blur, hover animations

### Pendente no RELATORIO.md (preencher manualmente)
- Nome e cartão UFRGS  
- Legenda (*caption*)  
- Conclusão da análise

---
*Branch: `lab3-visualizacao-pescadores` → `main`*
"""

ARQUIVOS = [
    ("mapa_pescadores_brasil.html",   "mapa_pescadores_brasil.html"),
    ("build_map_v7.py",               "build_map_v7.py"),
    ("template_v7.html",              "template_v7.html"),
    ("visualizacao_pescadores.ipynb", "visualizacao_pescadores.ipynb"),
    ("MANUAL.md",                     "MANUAL.md"),
]

def h(token):
    return {"Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"}

def sha_main(token):
    r = requests.get(f"{API}/git/ref/heads/{BASE_BRANCH}", headers=h(token))
    r.raise_for_status(); return r.json()["object"]["sha"]

def branch_existe(token):
    return requests.get(f"{API}/git/ref/heads/{NEW_BRANCH}", headers=h(token)).status_code == 200

def criar_branch(token, sha):
    r = requests.post(f"{API}/git/refs", headers=h(token),
                      json={"ref": f"refs/heads/{NEW_BRANCH}", "sha": sha})
    r.raise_for_status(); print(f"  ✅ Branch '{NEW_BRANCH}' criada")

def sha_arquivo(token, path):
    r = requests.get(f"{API}/contents/{path}", headers=h(token), params={"ref": NEW_BRANCH})
    return r.json().get("sha") if r.status_code == 200 else None

def upload(token, local, remote):
    p = Path(local)
    if not p.exists(): print(f"  ⚠️  {local} não encontrado — pulando"); return
    b64 = base64.b64encode(p.read_bytes()).decode()
    sha = sha_arquivo(token, remote)
    payload = {"message": f"Lab3 v7: {remote}", "content": b64, "branch": NEW_BRANCH}
    if sha: payload["sha"] = sha
    r = requests.put(f"{API}/contents/{remote}", headers=h(token), json=payload)
    if r.status_code in (200, 201):
        print(f"  ✅ {remote}  ({p.stat().st_size//1024} KB)")
    else:
        print(f"  ❌ {remote}: {r.status_code} — {r.text[:120]}")

def criar_pr(token):
    r = requests.post(f"{API}/pulls", headers=h(token),
                      json={"title": PR_TITLE, "body": PR_BODY,
                            "head": NEW_BRANCH, "base": BASE_BRANCH})
    if r.status_code == 201:
        print(f"\n  🎉 PR criado: {r.json()['html_url']}")
    elif r.status_code == 422:
        print("  ℹ️  PR já existe para esta branch.")
    else:
        print(f"  ❌ Erro: {r.status_code} — {r.text[:200]}")

def main():
    print("=" * 54)
    print("  PR — cgvis-visual-jp Lab3 v7")
    print("=" * 54)
    print("Token em: github.com/settings/tokens → marque 'repo'")
    print()
    token = getpass("GitHub Token: ").strip()
    if not token: print("Token vazio."); return

    me = requests.get("https://api.github.com/user", headers=h(token))
    if me.status_code != 200: print(f"❌ Token inválido ({me.status_code})"); return
    print(f"  ✅ Autenticado: {me.json()['login']}\n")

    print(f"[1/3] Branch '{NEW_BRANCH}'...")
    if branch_existe(token): print("  ℹ️  Branch já existe")
    else: criar_branch(token, sha_main(token))

    print(f"\n[2/3] Enviando {len(ARQUIVOS)} arquivos...")
    for local, remote in ARQUIVOS:
        upload(token, local, remote)

    print("\n[3/3] Pull Request...")
    criar_pr(token)
    print(f"\nhttps://github.com/{OWNER}/{REPO}/pulls")

if __name__ == "__main__":
    main()
