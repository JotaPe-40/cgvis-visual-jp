# Manual de Uso — Visualização de Armadores de Pesca no Brasil
**Laboratório 3 — INF01047 Computação Gráfica e Visualização I — UFRGS**

---

## Índice

1. [Visão geral da visualização](#1-visão-geral-da-visualização)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Opção A — Rodar no Google Colab (recomendado)](#3-opção-a--rodar-no-google-colab-recomendado)
4. [Opção B — Rodar localmente (VS Code / Jupyter)](#4-opção-b--rodar-localmente-vs-code--jupyter)
5. [Como obter e conectar os dados reais](#5-como-obter-e-conectar-os-dados-reais)
6. [Guia de uso do mapa interativo](#6-guia-de-uso-do-mapa-interativo)
7. [Descrição das camadas](#7-descrição-das-camadas)
8. [Ideias de análise e conclusões](#8-ideias-de-análise-e-conclusões)
9. [Estrutura de arquivos do repositório](#9-estrutura-de-arquivos-do-repositório)
10. [Preenchendo o RELATORIO.md](#10-preenchendo-o-relatóriomd)
11. [Problemas frequentes](#11-problemas-frequentes)

---

## 1. Visão geral da visualização

O notebook gera um **mapa interativo HTML** do Brasil com quatro camadas sobrepostas:

| Camada | Descrição |
|--------|-----------|
| 🗺️ Regiões / Estados | Polígonos dos 26 estados + DF coloridos por região. Clique num estado para **zoom e isolamento** |
| 🔥 Heatmap | Gradiente de calor azul→vermelho mostrando onde pescadores se concentram |
| 📍 MarkerCluster | Marcadores agrupados numericamente; expande com o zoom |
| ⚫ Pontos individuais | Círculos coloridos por região para análise fina em zoom alto |

O arquivo final é um **`.html` standalone** — abre em qualquer navegador sem servidor, sem internet, sem instalar nada.

---

## 2. Pré-requisitos

### Bibliotecas Python necessárias

```
folium
pandas
openpyxl
geopandas
requests
matplotlib
numpy
```

A **célula 1** do notebook instala tudo automaticamente com `pip`.

### Versões mínimas recomendadas

| Pacote | Versão mínima |
|--------|--------------|
| Python | 3.8 |
| folium | 0.14 |
| pandas | 1.3 |
| matplotlib | 3.4 |

---

## 3. Opção A — Rodar no Google Colab (recomendado)

É a forma mais simples: sem instalação local, funciona em qualquer computador com navegador.

### Passo a passo

**1.** Acesse [colab.research.google.com](https://colab.research.google.com)

**2.** Clique em **Arquivo → Abrir notebook → GitHub**

**3.** Cole a URL do repositório:
```
https://github.com/JotaPe-40/cgvis-visual-jp
```
e selecione `visualizacao_pescadores.ipynb`

> **Alternativa:** Baixe o arquivo `.ipynb` deste repositório e faça upload via **Arquivo → Fazer upload de notebook**

**4.** No menu superior, clique em **Runtime → Run all** (ou `Ctrl+F9`)

**5.** Aguarde todas as células executarem (~2 minutos na primeira vez por causa das instalações)

**6.** O mapa aparece inline na **célula 7**. O arquivo `mapa_pescadores_brasil.html` é baixado automaticamente pelo seu navegador (célula 8)

**7.** Abra o `.html` baixado em qualquer navegador para ver a versão completa e interativa

---

## 4. Opção B — Rodar localmente (VS Code / Jupyter)

### 4.1 Clonar o repositório

```bash
git clone https://github.com/JotaPe-40/cgvis-visual-jp.git
cd cgvis-visual-jp
```

### 4.2 Criar ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / macOS:
source venv/bin/activate
```

### 4.3 Instalar dependências

```bash
pip install folium pandas openpyxl geopandas requests matplotlib numpy
```

### 4.4 Abrir o notebook

**Via Jupyter:**
```bash
pip install jupyter
jupyter notebook visualizacao_pescadores.ipynb
```

**Via VS Code:**
- Instale a extensão **Jupyter** no VS Code
- Abra o arquivo `.ipynb` diretamente
- Selecione o kernel Python do seu ambiente virtual

### 4.5 Executar

Execute as células em ordem (de cima para baixo). O mapa será salvo como `mapa_pescadores_brasil.html` na pasta do projeto. Abra-o no navegador.

---

## 5. Como obter e conectar os dados reais

### 5.1 Baixar o dataset do MPA

O dataset de armadores de pesca está disponível no SharePoint do MPA. O link está no `TAREFAS.md` do repositório. Baixe o arquivo `.xlsx`.

### 5.2 Fazer upload no Colab

No Colab, clique no ícone de **pasta** no painel esquerdo → **Upload** → selecione o arquivo `.xlsx`.
Renomeie para `armadores_pesca.xlsx` ou ajuste o caminho no código.

### 5.3 Verificar colunas disponíveis

Na **célula 3**, há um `print(df_raw.columns.tolist())` que lista todas as colunas do arquivo real. Execute-o primeiro para saber os nomes exatos.

### 5.4 Adaptar o mapeamento de colunas

Na **célula 4** há um bloco comentado. Descomente e ajuste os nomes das colunas conforme o dataset real:

```python
df = df_raw.rename(columns={
    'UF':        'estado',      # ← ajuste para o nome real da coluna
    'MUNICIPIO': 'municipio',   # ← ajuste
    'LATITUDE':  'latitude',    # ← ajuste (se existir)
    'LONGITUDE': 'longitude',   # ← ajuste (se existir)
}).dropna(subset=['latitude', 'longitude'])
```

### 5.5 E se o dataset não tiver latitude/longitude?

Muitos datasets do governo têm apenas nome do município e UF. Nesse caso, use geocodificação:

```python
from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent='cgvis_pescadores')

coords_cache = {}

def geocodificar(municipio, estado):
    chave = f"{municipio},{estado}"
    if chave in coords_cache:
        return coords_cache[chave]
    try:
        loc = geolocator.geocode(f"{municipio}, {estado}, Brasil", timeout=10)
        time.sleep(1)  # respeitar limite da API
        if loc:
            coords_cache[chave] = (loc.latitude, loc.longitude)
            return (loc.latitude, loc.longitude)
    except:
        pass
    return (None, None)

# Aplicar (pode demorar alguns minutos para datasets grandes)
df[['latitude','longitude']] = df.apply(
    lambda r: geocodificar(r['municipio'], r['estado']),
    axis=1, result_type='expand'
)
```

> ⚠️ **Dica de performance:** Geocodifique apenas os municípios únicos (não cada linha) e depois faça um `merge` com o dataframe completo. Isso reduz de milhares de chamadas para ~500.

---

## 6. Guia de uso do mapa interativo

Ao abrir o arquivo `mapa_pescadores_brasil.html` no navegador:

### Navegação básica

| Ação | Como fazer |
|------|-----------|
| Mover o mapa | Clicar e arrastar |
| Zoom in/out | Scroll do mouse ou botões `+` / `−` no canto superior esquerdo |
| Voltar ao Brasil todo | Recarregar a página (`F5`) |

### Interações especiais

| Ação | Como fazer |
|------|-----------|
| **Ver o nome e dados de um estado** | Passar o mouse sobre o polígono (tooltip aparece) |
| **Zoom e isolamento de um estado** | Clicar sobre o polígono do estado |
| **Ver detalhes em popup** | Clicar no estado (abre popup com nome, região e contagens) |
| **Ligar/desligar camadas** | Clicar nas checkboxes no controle de camadas (canto superior direito) |
| **Expandir cluster** | Clicar num marcador agrupado (círculo com número) |
| **Ver dado individual** | Passar o mouse sobre um ponto na camada de pontos individuais |

### Fluxo de uso sugerido para análise por região

1. **Vista geral:** Deixe apenas o Heatmap e os Polígonos ativos. Observe onde estão as manchas vermelhas (alta concentração).
2. **Identificar região:** A cor do polígono indica a região (ver legenda).
3. **Isolar região:** Clique num estado para fazer zoom naquela área. O mapa centraliza e amplia.
4. **Detalhar estado:** Com zoom alto, ative a camada de Pontos Individuais para ver a distribuição intramunicipal.
5. **Comparar regiões:** Volte ao zoom nacional (`F5`) e compare visualmente as densidades.

---

## 7. Descrição das camadas

### 🗺️ Regiões / Estados

- Cada estado é um polígono preenchido com a cor da sua região geográfica.
- **Tooltip** (hover): mostra nome do estado, região, nº de pescadores no estado e na região.
- **Clique:** faz zoom automático no bounding box do estado (`fitBounds`), dando a sensação de isolamento.
- Para voltar ao Brasil inteiro, pressione `F5` ou use o scroll para dar zoom out.

### 🔥 Heatmap de concentração

- Gradiente contínuo: **azul** (poucos pescadores) → **verde** → **amarelo** → **vermelho** (muitos pescadores).
- Cada ponto contribui com uma "bolha de calor"; regiões com muitos pontos próximos ficam mais quentes.
- Muda dinamicamente com o zoom: em zoom baixo mostra tendências regionais; em zoom alto mostra concentração local.
- Parâmetros usados: `radius=18`, `blur=22` — ajuste na célula 7 se quiser mais ou menos suavização.

### 📍 MarkerCluster

- Agrupa automaticamente pontos próximos em círculos com o número de pescadores.
- Cores dos círculos de cluster: azul claro (poucos) → amarelo → vermelho (muitos).
- Ao dar zoom, os clusters se expandem progressivamente até mostrar pontos individuais.
- **Bom para:** contar pescadores em áreas específicas; ver exatamente onde estão.

### ⚫ Pontos individuais por região

- Cada ponto é um pescador registrado, colorido pela cor da região.
- Ligeiramente transparentes para que sobreposições fiquem mais escuras naturalmente.
- **Bom para:** análise visual de dispersão dentro de um estado em zoom alto.

---

## 8. Ideias de análise e conclusões

Estas são **sugestões de insights** para você explorar no mapa e escrever sua própria conclusão no relatório (sem IA).

### Ideia 1 — Pesca marítima vs. fluvial
Observe que os estados do **Norte** (PA, AM, AP) têm concentrações em cidades ribeirinhas do interior, enquanto os estados do **Nordeste e Sul** concentram pescadores no litoral. Isso revela os dois padrões de pesca do Brasil.

### Ideia 2 — Nordeste lidera em volume absoluto
O Nordeste, apesar de ser a região mais pobre, aparece como a de maior volume de pescadores. Isso pode indicar a importância da pesca artesanal como fonte de renda. Compare com o Sudeste, onde há mais armadores (donos de embarcações) mas proporcionalmente menos pescadores individuais.

### Ideia 3 — Concentração em capitais vs. interior
Note que em muitos estados os pontos se concentram na capital, mas em estados como o Pará (PA) há forte dispersão pelo interior. Isso reflete a malha hidrográfica.

### Ideia 4 — Desproporção Sul vs. Centro-Oeste
A Região Sul tem densidade de pescadores muito maior que o Centro-Oeste apesar de área menor. O cerrado e o pantanal têm pesca, mas a escala é incomparavelmente menor.

### Ideia 5 — Itajaí/SC como polo pesqueiro industrial
Na região de Itajaí (SC), o heatmap mostra uma das maiores concentrações do Sul. Itajaí é o maior porto pesqueiro do Brasil — o mapa torna isso visualmente evidente.

---

## 9. Estrutura de arquivos do repositório

Após concluir o trabalho, seu repositório deve ter esta estrutura:

```
cgvis-visual-jp/
├── visualizacao_pescadores.ipynb   ← notebook principal (código)
├── mapa_pescadores_brasil.html     ← saída interativa (commitar após gerar)
├── grafico_resumo_pescadores.png   ← imagem estática para o relatório
├── RELATORIO.md                    ← relatório preenchido por você
├── TAREFAS.md                      ← descrição das tarefas (não editar)
├── CHECKLIST.md                    ← lista de verificação
├── MANUAL.md                       ← este manual
└── exemplo/                        ← exemplo de referência
```

### O que commitar

```bash
git add visualizacao_pescadores.ipynb
git add mapa_pescadores_brasil.html
git add grafico_resumo_pescadores.png
git add RELATORIO.md
git add MANUAL.md
git commit -m "Adiciona visualização interativa de armadores de pesca"
git push
```

---

## 10. Preenchendo o RELATORIO.md

Abra o `RELATORIO.md` e preencha cada campo **com suas próprias palavras** (sem IA).

### Dados utilizados

```markdown
1. **Dataset 1**: [link para o arquivo MPA/SERMOP]
   - **Descrição curta**: Registros de armadores de pesca (donos de embarcações)
     cadastrados no Ministério da Pesca e Aquicultura, contendo município,
     estado e dados da embarcação.
```

### Código-fonte

```markdown
- **Arquivo principal**: `visualizacao_pescadores.ipynb`
- **Arquivos complementares**: `mapa_pescadores_brasil.html` (saída interativa)
```

### Imagem da visualização

Substitua `imagem-da-visualizacao.png` por `grafico_resumo_pescadores.png` no campo de imagem, e descreva como acessar o HTML:

```markdown
A visualização interativa principal é o arquivo `mapa_pescadores_brasil.html`.
Para acessá-la, baixe o arquivo e abra-o em qualquer navegador web moderno
(Chrome, Firefox, Edge). Não é necessário servidor ou conexão com a internet.
```

### Legenda (*caption*) — escreva você mesmo

Descreva os elementos visuais: o que cada cor representa, o que o heatmap mostra, como interagir.

### Conclusão — escreva você mesmo

Escolha **uma** das ideias da seção 8 deste manual, explore visualmente no mapa, e escreva 3–4 frases sobre o padrão observado e por que ele é não-óbvio.

---

## 11. Problemas frequentes

### "ModuleNotFoundError: No module named 'folium'"
Execute a célula 1 novamente ou instale manualmente:
```bash
pip install folium
```

### O mapa aparece vazio / sem estados
O GeoJSON é baixado automaticamente da internet na célula 5. Verifique se há conexão. Se estiver sem internet, salve o GeoJSON localmente:
```python
# Baixar uma vez e salvar:
import json, requests
r = requests.get(URL)
with open('estados.geojson', 'w') as f:
    json.dump(r.json(), f)

# Depois carregar localmente:
with open('estados.geojson') as f:
    estados_geojson = json.load(f)
```

### O heatmap não aparece
Verifique se o dataframe `df` tem colunas `latitude` e `longitude` com valores numéricos válidos (não NaN). Use:
```python
print(df[['latitude','longitude']].isna().sum())
print(df[['latitude','longitude']].describe())
```

### O notebook trava na geocodificação
A geocodificação com Nominatim pode ser lenta. Use a estratégia de geocodificar apenas municípios únicos (seção 5.5). Para datasets grandes (>5.000 municípios únicos), considere o serviço pago do Google Maps API ou um arquivo de coordenadas pré-processado do IBGE.

### O arquivo HTML está muito grande (>50 MB)
Reduza o número de pontos na camada de pontos individuais. Na célula 7, diminua o valor do `sample`:
```python
amostra_reg = grupo.sample(min(200, len(grupo)), random_state=42)
```

### O zoom no clique não funciona
Alguns navegadores bloqueiam JavaScript em arquivos locais. Tente:
- Abrir com **Chrome** em vez de Firefox
- Usar um servidor local: `python -m http.server 8080` e acessar `http://localhost:8080/mapa_pescadores_brasil.html`

---

*Manual criado para o Laboratório 3 — INF01047 — UFRGS — Junho/2026*
