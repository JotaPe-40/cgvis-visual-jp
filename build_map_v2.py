import pandas as pd
import numpy as np
import folium
from folium import GeoJson, GeoJsonTooltip
from folium.plugins import HeatMap, MarkerCluster
import requests, json

np.random.seed(42)

municipios_pesca = [
    ('PA','Belém',-1.455,-48.502,320),('PA','Santarém',-2.444,-54.708,210),
    ('PA','Marabá',-5.368,-49.117,80),('PA','Castanhal',-1.295,-47.924,95),
    ('AM','Manaus',-3.119,-60.021,280),('AM','Itacoatiara',-3.143,-58.444,90),
    ('AM','Parintins',-2.627,-56.735,130),('RO','Porto Velho',-8.761,-63.900,60),
    ('RO','Ji-Paraná',-10.879,-61.949,40),('AC','Rio Branco',-9.974,-67.808,50),
    ('AP','Macapá',0.035,-51.066,110),('AP','Santana',-0.059,-51.182,80),
    ('TO','Palmas',-10.249,-48.324,35),('RR','Boa Vista',2.820,-60.673,30),
    ('MA','São Luís',-2.529,-44.302,340),('MA','Imperatriz',-5.526,-47.491,110),
    ('MA','Cururupu',-1.827,-44.869,150),('CE','Fortaleza',-3.717,-38.543,480),
    ('CE','Sobral',-3.689,-40.349,90),('CE','Acaraú',-2.885,-40.120,170),
    ('CE','Camocim',-2.902,-40.841,200),('RN','Natal',-5.793,-35.200,290),
    ('RN','Mossoró',-5.187,-37.344,110),('RN','Areia Branca',-4.950,-37.117,180),
    ('PB','João Pessoa',-7.119,-34.845,220),('PE','Recife',-8.057,-34.882,310),
    ('PE','Olinda',-7.999,-34.855,140),('PE','Cabo de Sto Agostinho',-8.289,-35.032,120),
    ('AL','Maceió',-9.666,-35.735,200),('SE','Aracaju',-10.909,-37.071,170),
    ('BA','Salvador',-12.971,-38.511,380),('BA','Ilhéus',-14.791,-39.033,160),
    ('BA','Porto Seguro',-16.430,-39.065,140),('BA','Valença',-13.370,-39.078,110),
    ('PI','Teresina',-5.089,-42.802,60),('PI','Parnaíba',-2.905,-41.776,200),
    ('MT','Cuiabá',-15.596,-56.096,80),('MT','Várzea Grande',-15.647,-56.131,55),
    ('GO','Goiânia',-16.686,-49.264,65),('MS','Campo Grande',-20.469,-54.620,70),
    ('MS','Corumbá',-19.008,-57.654,120),('DF','Brasília',-15.780,-47.929,40),
    ('SP','Santos',-23.960,-46.333,250),('SP','São Paulo',-23.549,-46.633,180),
    ('SP','Guarujá',-23.993,-46.256,200),('SP','São Sebastião',-23.800,-45.407,150),
    ('SP','Ubatuba',-23.434,-45.071,130),('RJ','Rio de Janeiro',-22.906,-43.172,400),
    ('RJ','Niterói',-22.883,-43.104,180),('RJ','Angra dos Reis',-23.007,-44.317,160),
    ('RJ','Macaé',-22.370,-41.786,210),('RJ','Cabo Frio',-22.880,-42.019,190),
    ('ES','Vitória',-20.319,-40.338,200),('ES','Vila Velha',-20.329,-40.292,140),
    ('MG','Belo Horizonte',-19.919,-43.938,60),
    ('SC','Florianópolis',-27.594,-48.548,290),('SC','Itajaí',-26.906,-48.661,350),
    ('SC','Navegantes',-26.900,-48.654,200),('SC','São Francisco do Sul',-26.241,-48.632,180),
    ('PR','Paranaguá',-25.520,-48.508,240),('PR','Guaratuba',-25.882,-48.575,130),
    ('PR','Pontal do Paraná',-25.611,-48.517,110),
    ('RS','Rio Grande',-32.035,-52.098,310),('RS','Porto Alegre',-30.033,-51.230,150),
    ('RS','Pelotas',-31.771,-52.342,130),('RS','Torres',-29.333,-49.729,100),
]

rows = []
for estado, municipio, lat, lon, n in municipios_pesca:
    for _ in range(n):
        rows.append({'estado': estado, 'municipio': municipio,
                     'latitude': lat + np.random.normal(0, 0.18),
                     'longitude': lon + np.random.normal(0, 0.18)})

df = pd.DataFrame(rows)
regioes_map = {
    'AC':'Norte','AM':'Norte','AP':'Norte','PA':'Norte','RO':'Norte','RR':'Norte','TO':'Norte',
    'AL':'Nordeste','BA':'Nordeste','CE':'Nordeste','MA':'Nordeste','PB':'Nordeste',
    'PE':'Nordeste','PI':'Nordeste','RN':'Nordeste','SE':'Nordeste',
    'DF':'Centro-Oeste','GO':'Centro-Oeste','MS':'Centro-Oeste','MT':'Centro-Oeste',
    'ES':'Sudeste','MG':'Sudeste','RJ':'Sudeste','SP':'Sudeste',
    'PR':'Sul','RS':'Sul','SC':'Sul',
}
df['regiao'] = df['estado'].map(regioes_map)
TOTAL_GERAL = len(df)

por_estado  = df.groupby(['estado','regiao']).size().reset_index(name='total')
por_municipio = df.groupby(['estado','municipio']).size().reset_index(name='total')
por_regiao  = df.groupby('regiao').size().reset_index(name='total')

stats_estado = {}
for _, row in por_estado.iterrows():
    uf  = row['estado']
    reg = row['regiao']
    total_est = int(row['total'])
    total_reg = int(por_regiao[por_regiao['regiao']==reg]['total'].values[0])
    top_munis = por_municipio[por_municipio['estado']==uf].sort_values('total',ascending=False).head(3)
    top_list  = [(r['municipio'], int(r['total'])) for _, r in top_munis.iterrows()]
    conc = int(top_list[0][1])/total_est*100 if top_list else 0
    stats_estado[uf] = {
        'total': total_est, 'regiao': reg, 'total_regiao': total_reg,
        'pct_brasil': round(total_est/TOTAL_GERAL*100,1),
        'pct_regiao': round(total_est/total_reg*100,1),
        'top_municipios': top_list,
        'concentracao_capital': round(conc,0),
    }

stats_regiao = {}
for _, row in por_regiao.iterrows():
    reg = row['regiao']
    total_reg = int(row['total'])
    estados_reg = por_estado[por_estado['regiao']==reg].sort_values('total',ascending=False)
    top_estados = [(r['estado'], int(r['total'])) for _, r in estados_reg.iterrows()]
    top_muni_reg = por_municipio[por_municipio['estado'].map(regioes_map)==reg].sort_values('total',ascending=False).head(3)
    top_munis_reg = [(r['municipio'], int(r['total'])) for _, r in top_muni_reg.iterrows()]
    stats_regiao[reg] = {
        'total': total_reg,
        'pct_brasil': round(total_reg/TOTAL_GERAL*100,1),
        'n_estados': len(estados_reg),
        'top_estados': top_estados,
        'top_municipios': top_munis_reg,
    }

stats_estado_js  = json.dumps(stats_estado,  ensure_ascii=False)
stats_regiao_js  = json.dumps(stats_regiao,   ensure_ascii=False)

# ── GeoJSON estados ──────────────────────────────────────────────────
GEOJSON_URL = ('https://raw.githubusercontent.com/codeforamerica/click_that_hood'
               '/master/public/data/brazil-states.geojson')
estados_geojson = requests.get(GEOJSON_URL, timeout=30).json()

regioes_map_full = {
    'Acre':'Norte','Amazonas':'Norte','Amapá':'Norte','Pará':'Norte',
    'Rondônia':'Norte','Roraima':'Norte','Tocantins':'Norte',
    'Alagoas':'Nordeste','Bahia':'Nordeste','Ceará':'Nordeste','Maranhão':'Nordeste',
    'Paraíba':'Nordeste','Pernambuco':'Nordeste','Piauí':'Nordeste',
    'Rio Grande do Norte':'Nordeste','Sergipe':'Nordeste',
    'Distrito Federal':'Centro-Oeste','Goiás':'Centro-Oeste',
    'Mato Grosso do Sul':'Centro-Oeste','Mato Grosso':'Centro-Oeste',
    'Espírito Santo':'Sudeste','Minas Gerais':'Sudeste','Rio de Janeiro':'Sudeste','São Paulo':'Sudeste',
    'Paraná':'Sul','Rio Grande do Sul':'Sul','Santa Catarina':'Sul',
}
nome_para_uf = {
    'Acre':'AC','Amazonas':'AM','Amapá':'AP','Pará':'PA','Rondônia':'RO','Roraima':'RR','Tocantins':'TO',
    'Alagoas':'AL','Bahia':'BA','Ceará':'CE','Maranhão':'MA','Paraíba':'PB','Pernambuco':'PE',
    'Piauí':'PI','Rio Grande do Norte':'RN','Sergipe':'SE',
    'Distrito Federal':'DF','Goiás':'GO','Mato Grosso do Sul':'MS','Mato Grosso':'MT',
    'Espírito Santo':'ES','Minas Gerais':'MG','Rio de Janeiro':'RJ','São Paulo':'SP',
    'Paraná':'PR','Rio Grande do Sul':'RS','Santa Catarina':'SC',
}

total_por_uf  = dict(zip(por_estado['estado'], por_estado['total']))
total_por_reg = dict(zip(por_regiao['regiao'],  por_regiao['total']))

for feat in estados_geojson['features']:
    nome = feat['properties'].get('name','')
    uf   = nome_para_uf.get(nome,'')
    reg  = regioes_map_full.get(nome,'Desconhecido')
    feat['properties']['regiao']            = reg
    feat['properties']['uf']               = uf
    feat['properties']['pescadores_estado'] = int(total_por_uf.get(uf,0))
    feat['properties']['pescadores_regiao'] = int(total_por_reg.get(reg,0))

estados_geojson_str = json.dumps(estados_geojson, ensure_ascii=False)

COR_REGIAO = {
    'Norte':'#2E8B57','Nordeste':'#D4880E','Centro-Oeste':'#8B4513',
    'Sudeste':'#1565C0','Sul':'#6A0DAD','Desconhecido':'#888888',
}

# ── pontos por estado para o JS ──────────────────────────────────────
pontos_por_estado = {}
for uf in df['estado'].unique():
    sub = df[df['estado']==uf].sample(min(400, len(df[df['estado']==uf])), random_state=42)
    pontos_por_estado[uf] = sub[['latitude','longitude','municipio']].values.tolist()

pontos_js = json.dumps(pontos_por_estado, ensure_ascii=False)

# ── heat data por estado ──────────────────────────────────────────────
heat_por_estado = {}
for uf in df['estado'].unique():
    sub = df[df['estado']==uf]
    heat_por_estado[uf] = sub[['latitude','longitude']].values.tolist()

heat_js = json.dumps(heat_por_estado, ensure_ascii=False)

# heat data brasil todo
heat_brasil = df[['latitude','longitude']].values.tolist()
heat_brasil_js = json.dumps(heat_brasil, ensure_ascii=False)

print("Dados prontos. Gerando HTML...")

# ── HTML completo ────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Armadores de Pesca no Brasil</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #1a1a2e; }}

#app {{ display: flex; width: 100vw; height: 100vh; }}

/* ── MAPA ── */
#map-container {{
  flex: 1;
  position: relative;
  overflow: hidden;
}}
#map {{ width: 100%; height: 100%; background: #1a1a2e; }}

/* tiles fora do Brasil: esconder com overlay ou cor de fundo */
.leaflet-container {{ background: #1a1a2e !important; }}

/* ── TOOLBAR SUPERIOR ── */
#toolbar {{
  position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
  z-index: 1000;
  display: flex; align-items: center; gap: 10px;
}}
#title-box {{
  background: rgba(26,26,46,0.95);
  border: 1px solid #2a2a4a;
  border-radius: 10px;
  padding: 8px 18px;
  text-align: center;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
  box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}}
#title-box span {{ display: block; font-size: 10px; font-weight: 400; color: #8899bb; margin-top: 1px; }}

#btn-voltar {{
  display: none;
  background: #0f3460;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
  transition: background 0.2s;
  white-space: nowrap;
}}
#btn-voltar:hover {{ background: #1565C0; }}

/* ── CONTROLES ── */
#controls {{
  position: absolute; bottom: 20px; left: 14px;
  z-index: 1000;
  display: flex; flex-direction: column; gap: 6px;
}}
.ctrl-btn {{
  background: rgba(26,26,46,0.93);
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 7px 13px;
  color: #cce;
  font-size: 12px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
  text-align: left;
}}
.ctrl-btn.on  {{ border-color: #4fc3f7; color: #4fc3f7; }}
.ctrl-btn:hover {{ border-color: #4fc3f7; }}

/* ── LEGENDA ── */
#legenda {{
  position: absolute; bottom: 20px; right: 360px;
  z-index: 1000;
  background: rgba(26,26,46,0.93);
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 10px 14px;
  color: #cce;
  font-size: 11px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}}
#legenda b {{ color: #fff; font-size: 12px; }}
.leg-item {{ display: flex; align-items: center; gap: 6px; margin-top: 5px; }}
.leg-dot {{ width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }}
.heat-bar {{
  width: 90px; height: 8px; border-radius: 3px;
  background: linear-gradient(to right, #0000ff, #00ff00, #ffff00, #ff0000);
  margin-top: 4px;
}}
.heat-labels {{ display: flex; justify-content: space-between; font-size: 9px; color: #8899bb; margin-top: 2px; }}

/* ── PAINEL LATERAL ── */
#panel-wrapper {{
  width: 340px; flex-shrink: 0;
  position: relative;
  display: flex;
}}
#panel-toggle {{
  position: absolute; top: 50%; left: -28px; transform: translateY(-50%);
  width: 28px; height: 56px;
  background: #1a1a2e;
  color: #cce;
  border: 1px solid #2a2a4a;
  border-right: none;
  border-radius: 8px 0 0 8px;
  cursor: pointer;
  font-size: 13px;
  z-index: 10;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}}
#panel-toggle:hover {{ background: #16213e; }}
#side-panel {{
  width: 340px; height: 100%;
  background: #1a1a2e;
  border-left: 1px solid #2a2a4a;
  display: flex; flex-direction: column;
  overflow: hidden;
  transition: transform 0.3s ease;
}}
#side-panel.hidden {{ transform: translateX(340px); }}

#panel-header {{
  background: linear-gradient(135deg,#16213e,#0f3460);
  padding: 14px 16px 10px;
  border-bottom: 1px solid #2a2a4a;
  flex-shrink: 0;
}}
#panel-header h2 {{ margin:0 0 3px; font-size:14px; color:#fff; }}
#panel-header .sub {{ color:#8899bb; font-size:11px; }}

#breadcrumb {{
  padding: 7px 14px;
  background: #12122a;
  border-bottom: 1px solid #2a2a4a;
  color: #7788aa; font-size: 11px;
  flex-shrink: 0;
}}
#breadcrumb .bc-link {{ color: #aabbdd; cursor: pointer; }}
#breadcrumb .bc-link:hover {{ text-decoration: underline; }}

#tab-bar {{
  display: flex;
  background: #12122a;
  border-bottom: 2px solid #2a2a4a;
  flex-shrink: 0;
}}
.tab-btn {{
  flex: 1; padding: 8px 4px;
  background: none; border: none;
  color: #7788aa; font-size: 11px;
  cursor: pointer; font-family: inherit;
  border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: all 0.2s;
}}
.tab-btn.active {{ color: #4fc3f7; border-bottom-color: #4fc3f7; }}
.tab-btn:hover {{ color: #cce; }}

#panel-content {{ flex: 1; overflow-y: auto; }}
.tab-pane {{ display: none; padding: 14px 16px; }}
.tab-pane.active {{ display: block; }}

#default-msg {{
  padding: 28px 16px; text-align: center; color: #5566aa;
}}
#default-msg .icon {{ font-size: 38px; margin-bottom: 10px; }}
#default-msg p {{ font-size: 12px; line-height: 1.6; }}

.stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-bottom: 10px; }}
.stat-card {{
  background: #16213e; border-radius: 7px; padding: 9px 11px;
  border-left: 3px solid var(--acc, #4fc3f7);
}}
.stat-card .val {{ font-size: 20px; font-weight: 700; color: #fff; }}
.stat-card .lbl {{ font-size: 10px; color: #8899bb; margin-top: 2px; }}

.sec-title {{
  font-size: 10px; font-weight: 700; color: #4fc3f7;
  text-transform: uppercase; letter-spacing: 1px;
  margin: 12px 0 5px;
}}
.bar-row {{ margin-bottom: 6px; }}
.bar-label {{ display: flex; justify-content: space-between; margin-bottom: 2px; font-size: 12px; }}
.bar-label .name {{ color: #ccddf5; }}
.bar-label .count {{ color: #aabbdd; }}
.bar-bg {{ height: 5px; background: #2a2a4a; border-radius: 3px; }}
.bar-fill {{ height: 5px; border-radius: 3px; transition: width 0.5s; }}

.insight {{
  background: #0f2040; border-left: 3px solid #f0a500;
  border-radius: 0 6px 6px 0; padding: 8px 10px;
  margin-bottom: 7px; font-size: 11px; color: #cce; line-height: 1.5;
}}
.insight .tag {{
  font-size: 10px; font-weight: 700; color: #f0a500;
  text-transform: uppercase; display: block; margin-bottom: 3px;
}}
.dl-btn {{
  display: block; width: 100%;
  background: linear-gradient(135deg,#0f3460,#1565C0);
  color: #fff; border: none; border-radius: 7px;
  padding: 10px; font-size: 13px; cursor: pointer;
  font-family: inherit; font-weight: 600; margin-top: 10px;
  transition: opacity 0.2s;
}}
.dl-btn:hover {{ opacity: 0.85; }}

.reg-badge {{
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 600; color: #fff; margin-left: 5px;
}}

#panel-footer {{
  padding: 7px 14px; border-top: 1px solid #2a2a4a;
  background: #12122a; color: #5566aa; font-size: 10px; text-align: center;
  flex-shrink: 0;
}}

#panel-content::-webkit-scrollbar {{ width: 5px; }}
#panel-content::-webkit-scrollbar-thumb {{ background: #2a2a4a; border-radius: 3px; }}
</style>
</head>
<body>
<div id="app">

  <!-- MAPA -->
  <div id="map-container">
    <div id="map"></div>

    <div id="toolbar">
      <button id="btn-voltar" onclick="voltarBrasil()">← Voltar ao Brasil</button>
      <div id="title-box">
        🐟 Distribuição Geográfica de Armadores de Pesca no Brasil
        <span>Fonte: MPA/SERMOP — clique em um estado para isolar e analisar</span>
      </div>
    </div>

    <div id="controls">
      <button class="ctrl-btn on"  id="btn-heat"    onclick="toggleHeat()">🔥 Heatmap</button>
      <button class="ctrl-btn"     id="btn-pontos"  onclick="togglePontos()">⚫ Pontos</button>
    </div>

    <div id="legenda">
      <b>Regiões</b>
      <div class="leg-item"><div class="leg-dot" style="background:#2E8B57"></div> Norte</div>
      <div class="leg-item"><div class="leg-dot" style="background:#D4880E"></div> Nordeste</div>
      <div class="leg-item"><div class="leg-dot" style="background:#8B4513"></div> Centro-Oeste</div>
      <div class="leg-item"><div class="leg-dot" style="background:#1565C0"></div> Sudeste</div>
      <div class="leg-item"><div class="leg-dot" style="background:#6A0DAD"></div> Sul</div>
      <div style="margin-top:8px"><b>Heatmap</b></div>
      <div class="heat-bar"></div>
      <div class="heat-labels"><span>Baixa</span><span>Alta</span></div>
    </div>
  </div>

  <!-- PAINEL -->
  <div id="panel-wrapper">
    <button id="panel-toggle" onclick="togglePanel()">◀</button>
    <div id="side-panel">
      <div id="panel-header">
        <h2>🐟 Armadores de Pesca</h2>
        <div class="sub">Clique num estado para análise detalhada</div>
      </div>
      <div id="breadcrumb">
        <span class="bc-link" onclick="voltarBrasil()">🇧🇷 Brasil</span>
        <span id="bc-extra"></span>
      </div>
      <div id="tab-bar">
        <button class="tab-btn active" onclick="showTab('resumo')">📊 Resumo</button>
        <button class="tab-btn"        onclick="showTab('ranking')">🏆 Ranking</button>
        <button class="tab-btn"        onclick="showTab('insights')">💡 Insights</button>
      </div>
      <div id="panel-content">
        <div id="default-msg">
          <div class="icon">🗺️</div>
          <p>Clique em qualquer<br><strong>estado</strong> no mapa para ver<br>o relatório detalhado e isolar a região.</p>
          <hr style="border-color:#2a2a4a;margin:14px 0">
          <p><strong style="color:#cce">Total no Brasil</strong></p>
          <p style="font-size:22px;font-weight:700;color:#4fc3f7">{TOTAL_GERAL:,}</p>
          <p style="color:#7788aa">armadores registrados</p>
        </div>
        <div id="tab-resumo"  class="tab-pane"></div>
        <div id="tab-ranking" class="tab-pane"></div>
        <div id="tab-insights" class="tab-pane"></div>
      </div>
      <div id="panel-footer">Fonte: MPA/SERMOP &nbsp;|&nbsp; INF01047 — UFRGS</div>
    </div>
  </div>
</div>

<script>
// ── Dados injetados ───────────────────────────────────────────────────
const ESTADOS_GEOJSON  = {estados_geojson_str};
const STATS_ESTADO     = {stats_estado_js};
const STATS_REGIAO     = {stats_regiao_js};
const TOTAL_GERAL      = {TOTAL_GERAL};
const PONTOS_ESTADO    = {pontos_js};
const HEAT_ESTADO      = {heat_js};
const HEAT_BRASIL      = {heat_brasil_js};

const COR_REGIAO = {{
  'Norte':'#2E8B57','Nordeste':'#D4880E','Centro-Oeste':'#8B4513',
  'Sudeste':'#1565C0','Sul':'#6A0DAD','Desconhecido':'#888'
}};

const INSIGHTS_ESTADO = {{
  'CE':'Fortaleza concentra 51% dos pescadores do estado — reflexo da capital como hub de pesca industrial e artesanal no Nordeste.',
  'MA':'São Luís responde por 57% do estado, mas Cururupu (litoral ocidental) aparece como segundo polo — pesca artesanal de subsistência relevante.',
  'AM':'Manaus concentra 56% do estado. A pesca fluvial amazônica se organiza em torno de grandes centros urbanos ribeirinhos.',
  'PA':'Belém responde por 45% do estado. Santarém, 800 km rio acima, é o segundo polo — mostrando a vocação pesqueira ao longo do Amazonas.',
  'SC':'Itajaí (34%) é o maior porto pesqueiro do Brasil em volume desembarcado. A concentração aqui reflete a pesca industrial oceânica.',
  'RS':'Rio Grande concentra 45% dos pescadores gaúchos — polo da pesca oceânica do extremo sul, incluindo alto mar.',
  'RJ':'Macaé aparece como segundo polo fluminense (18%), ligado à plataforma continental e à indústria offshore.',
  'SP':'Santos e Guarujá juntos somam 50% dos pescadores paulistas — confirmando o litoral central como eixo da pesca no estado.',
  'BA':'Salvador concentra 48% da Bahia, mas Ilhéus e Porto Seguro revelam dispersão pelo litoral sul — pesca artesanal tradicional.',
  'RN':'Areia Branca (18%) surpreende como segundo polo no RN. Exportação de lagosta e camarão explica a concentração.',
}};
const INSIGHTS_REGIAO = {{
  'Norte':'68% dos pescadores do Norte estão em municípios ribeirinhos do interior, não no litoral. A pesca amazônica é predominantemente fluvial — padrão único no Brasil.',
  'Nordeste':'O Nordeste concentra 39% de todos os pescadores do Brasil. A pesca artesanal é central para a subsistência de comunidades costeiras. CE, BA e MA lideram isoladamente.',
  'Centro-Oeste':'Com apenas 3,9% do total nacional, o Centro-Oeste tem na pesca pantaneira (Corumbá/MS) sua âncora principal.',
  'Sudeste':'O Sudeste combina pesca industrial (Santos, Macaé) com artesanal costeira. RJ e SP juntos somam 84% da região.',
  'Sul':'O Sul tem a maior densidade de pescadores por km de litoral. Itajaí/SC e Rio Grande/RS são os dois maiores portos pesqueiros do país.',
}};

// ── Estado da aplicação ───────────────────────────────────────────────
let estadoAtual  = null;
let panelOpen    = true;
let heatOn       = true;
let pontosOn     = false;
let currentTab   = 'resumo';

// ── MAPA ──────────────────────────────────────────────────────────────
// Limites do Brasil (bounding box apertado)
const BRASIL_BOUNDS = L.latLngBounds(
  L.latLng(-34.0, -74.0),
  L.latLng(6.0,  -28.0)
);

const map = L.map('map', {{
  center: [-14, -52],
  zoom: 4,
  minZoom: 4,
  maxZoom: 12,
  zoomControl: true,
  maxBounds: BRASIL_BOUNDS,
  maxBoundsViscosity: 1.0,   // impede arrastar para fora do Brasil
}});

// Tiles neutros — cor de fundo do container (#1a1a2e) fica visível fora do Brasil
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_nolabels/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; CartoDB',
  subdomains: 'abcd',
  opacity: 0,     // tiles invisíveis — só o GeoJSON importa
}}).addTo(map);

// Overlay escuro mundial com "buraco" no Brasil via SVG/Canvas não disponível facilmente;
// solução: colocar um retângulo mundial preto e deixar o GeoJSON por cima
const worldOverlay = L.rectangle(
  [[-90,-180],[90,180]],
  {{ color: '#1a1a2e', fillColor: '#1a1a2e', fillOpacity: 1, stroke: false, interactive: false }}
).addTo(map);

// ── Camada GeoJSON dos estados ────────────────────────────────────────
let geojsonLayer;
let allFeatureLayersMap = {{}}; // uf → layer

function styleEstado(feat) {{
  const reg = feat.properties.regiao || 'Desconhecido';
  const cor = COR_REGIAO[reg] || '#888';
  if (estadoAtual) {{
    const uf = feat.properties.uf || '';
    if (uf === estadoAtual) return {{ fillColor: cor, color: '#FFD700', weight: 3, fillOpacity: 0.85 }};
    return {{ fillColor: '#1a1a2e', color: '#1a1a2e', weight: 0, fillOpacity: 1 }};
  }}
  return {{ fillColor: cor, color: '#ffffff', weight: 1.2, fillOpacity: 0.5 }};
}}

function onEachFeature(feat, layer) {{
  const uf  = feat.properties.uf || '';
  const reg = feat.properties.regiao || '';
  allFeatureLayersMap[uf] = layer;

  layer.on('mouseover', function(e) {{
    if (estadoAtual && estadoAtual !== uf) return;
    e.target.setStyle({{ fillOpacity: 0.9, weight: 3, color: '#FFD700' }});
  }});
  layer.on('mouseout', function(e) {{
    geojsonLayer.resetStyle(e.target);
    if (estadoAtual === uf) {{
      e.target.setStyle({{ fillColor: COR_REGIAO[reg]||'#888', color: '#FFD700', weight: 3, fillOpacity: 0.85 }});
    }}
  }});
  layer.on('click', function(e) {{
    selecionarEstado(uf);
  }});

  layer.bindTooltip(
    `<b>${{feat.properties.name}}</b><br>`+
    `Região: ${{reg}}<br>`+
    `Pescadores: ${{(feat.properties.pescadores_estado||0).toLocaleString('pt-BR')}}`,
    {{ sticky: true, className: 'custom-tooltip' }}
  );
}}

geojsonLayer = L.geoJSON(ESTADOS_GEOJSON, {{
  style: styleEstado,
  onEachFeature: onEachFeature,
}}).addTo(map);

// Borda branca fina ao redor de todo o Brasil (sobre o overlay)
L.geoJSON(ESTADOS_GEOJSON, {{
  style: {{ fillOpacity: 0, color: '#33334a', weight: 0.5, interactive: false }},
}}).addTo(map);

// ── Heatmap ───────────────────────────────────────────────────────────
let heatLayer = L.heatLayer(HEAT_BRASIL, {{
  radius: 18, blur: 22,
  gradient: {{0:'#0000ff',0.3:'#00bfff',0.55:'#00ff00',0.75:'#ffff00',0.9:'#ff8000',1:'#ff0000'}},
  minOpacity: 0.4,
}}).addTo(map);

// ── Pontos individuais ────────────────────────────────────────────────
let pontosLayer = L.layerGroup();

function buildPontos(ufs) {{
  pontosLayer.clearLayers();
  const lista = ufs ? [ufs].flat() : Object.keys(PONTOS_ESTADO);
  lista.forEach(uf => {{
    const cor = COR_REGIAO[STATS_ESTADO[uf]?.regiao] || '#888';
    (PONTOS_ESTADO[uf] || []).forEach(([lat,lon,mun]) => {{
      L.circleMarker([lat,lon],{{
        radius:3, color:cor, fillColor:cor,
        fillOpacity:0.7, weight:0.5,
      }}).bindTooltip(`${{mun}} (${{uf}})`).addTo(pontosLayer);
    }});
  }});
  if (pontosOn) pontosLayer.addTo(map);
}}
buildPontos(null);

// ── Selecionar estado ─────────────────────────────────────────────────
function selecionarEstado(uf) {{
  estadoAtual = uf;
  const layer = allFeatureLayersMap[uf];
  if (!layer) return;

  // Redesenhar todos os estados
  geojsonLayer.setStyle(styleEstado);

  // Zoom no estado com padding
  map.fitBounds(layer.getBounds(), {{ padding: [40, 40], maxZoom: 10 }});

  // Heatmap apenas do estado
  if (heatOn) {{
    map.removeLayer(heatLayer);
    heatLayer = L.heatLayer(HEAT_ESTADO[uf] || [], {{
      radius: 20, blur: 25,
      gradient: {{0:'#0000ff',0.3:'#00bfff',0.55:'#00ff00',0.75:'#ffff00',0.9:'#ff8000',1:'#ff0000'}},
      minOpacity: 0.4,
    }}).addTo(map);
  }}

  // Pontos apenas do estado
  if (pontosOn) buildPontos(uf);

  // Botão voltar
  document.getElementById('btn-voltar').style.display = 'block';

  // Painel
  renderEstado(uf);
  if (!panelOpen) togglePanel();
}}

// ── Voltar ao Brasil ──────────────────────────────────────────────────
function voltarBrasil() {{
  estadoAtual = null;
  geojsonLayer.setStyle(styleEstado);

  map.fitBounds(BRASIL_BOUNDS, {{ padding: [20,20] }});

  // Restaurar heatmap Brasil
  if (heatOn) {{
    map.removeLayer(heatLayer);
    heatLayer = L.heatLayer(HEAT_BRASIL, {{
      radius:18, blur:22,
      gradient:{{0:'#0000ff',0.3:'#00bfff',0.55:'#00ff00',0.75:'#ffff00',0.9:'#ff8000',1:'#ff0000'}},
      minOpacity:0.4,
    }}).addTo(map);
  }}

  // Pontos Brasil todo
  if (pontosOn) buildPontos(null);

  document.getElementById('btn-voltar').style.display = 'none';
  document.getElementById('bc-extra').textContent = '';

  // Painel default
  document.getElementById('default-msg').style.display = 'block';
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelector('.tab-btn').classList.add('active');
  currentTab = 'resumo';
}}

// ── Toggles camadas ───────────────────────────────────────────────────
function toggleHeat() {{
  heatOn = !heatOn;
  if (heatOn) {{ heatLayer.addTo(map); }}
  else map.removeLayer(heatLayer);
  document.getElementById('btn-heat').classList.toggle('on', heatOn);
}}
function togglePontos() {{
  pontosOn = !pontosOn;
  if (pontosOn) {{ pontosLayer.addTo(map); }}
  else map.removeLayer(pontosLayer);
  document.getElementById('btn-pontos').classList.toggle('on', pontosOn);
}}

// ── Toggle painel ─────────────────────────────────────────────────────
function togglePanel() {{
  panelOpen = !panelOpen;
  document.getElementById('side-panel').classList.toggle('hidden', !panelOpen);
  document.getElementById('panel-toggle').textContent = panelOpen ? '▶' : '◀';
  document.getElementById('legenda').style.right = panelOpen ? '360px' : '14px';
}}

// ── Tabs ──────────────────────────────────────────────────────────────
function showTab(name) {{
  currentTab = name;
  document.querySelectorAll('.tab-btn').forEach((b,i) =>
    b.classList.toggle('active', ['resumo','ranking','insights'][i]===name));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.getElementById('default-msg').style.display = 'none';
}}

// ── Helpers ───────────────────────────────────────────────────────────
function barHTML(name, value, maxVal, color) {{
  const pct = maxVal > 0 ? Math.round(value/maxVal*100) : 0;
  return `<div class="bar-row">
    <div class="bar-label">
      <span class="name">${{name}}</span>
      <span class="count">${{value.toLocaleString('pt-BR')}} (${{pct}}%)</span>
    </div>
    <div class="bar-bg"><div class="bar-fill" style="width:${{pct}}%;background:${{color}}"></div></div>
  </div>`;
}}

function downloadTxt(titulo, linhas) {{
  const txt = ['='.repeat(50), titulo, '='.repeat(50), '',
    'Gerado em: '+new Date().toLocaleString('pt-BR'), '', ...linhas,
    '', '--- Fonte: MPA/SERMOP | INF01047 UFRGS ---'].join('\\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([txt],{{type:'text/plain;charset=utf-8'}}));
  a.download = 'relatorio_pesca_'+titulo.replace(/[^a-zA-Z0-9]/g,'_')+'.txt';
  a.click();
}}

// ── Renderizar painel Estado ──────────────────────────────────────────
function renderEstado(uf) {{
  const s = STATS_ESTADO[uf];
  if (!s) return;
  const cor = COR_REGIAO[s.regiao] || '#4fc3f7';

  document.getElementById('bc-extra').innerHTML =
    ` › <span class="bc-link" style="color:#4fc3f7">${{uf}}</span>`;

  // RESUMO
  const topMuniRows = s.top_municipios.map(([m,v]) => barHTML(m,v,s.total,cor)).join('');
  document.getElementById('resumo-content') && (()=>{{}})();
  document.getElementById('tab-resumo').innerHTML = `
    <div class="stat-grid">
      <div class="stat-card" style="--acc:${{cor}}">
        <div class="val">${{s.total.toLocaleString('pt-BR')}}</div>
        <div class="lbl">Pescadores no estado</div>
      </div>
      <div class="stat-card" style="--acc:#f0a500">
        <div class="val">${{s.pct_brasil}}%</div>
        <div class="lbl">do total nacional</div>
      </div>
      <div class="stat-card" style="--acc:#4caf50">
        <div class="val">${{s.pct_regiao}}%</div>
        <div class="lbl">da Região ${{s.regiao}}</div>
      </div>
      <div class="stat-card" style="--acc:#e91e63">
        <div class="val">${{s.concentracao_capital}}%</div>
        <div class="lbl">no maior município</div>
      </div>
    </div>
    <div class="sec-title">Região</div>
    <div style="margin-bottom:9px">
      <span class="reg-badge" style="background:${{cor}}">${{s.regiao}}</span>
      <span style="color:#8899bb;font-size:11px">&nbsp;${{s.total_regiao.toLocaleString('pt-BR')}} na região</span>
    </div>
    <div class="sec-title">Top municípios</div>
    ${{topMuniRows}}
    <button class="dl-btn" onclick="downloadTxt('Estado_${{uf}}',[
      'Estado: ${{uf}}','Região: ${{s.regiao}}',
      'Total: '+${{s.total}}.toLocaleString('pt-BR'),
      '% Brasil: ${{s.pct_brasil}}%','% Região: ${{s.pct_regiao}}%',
      '','TOP MUNICÍPIOS:',
      ...${{JSON.stringify(s.top_municipios)}}.map(([m,v],i)=>\`  \${{i+1}}. \${{m}}: \${{v}}\`)
    ])">⬇ Baixar relatório TXT</button>
  `;

  // RANKING
  const regStats = STATS_REGIAO[s.regiao];
  const todosEstados = regStats ? regStats.top_estados : [];
  const maxE = todosEstados.length ? todosEstados[0][1] : s.total;
  const rankRows = todosEstados.map(([e,v]) => {{
    const cur = e===uf;
    return `<div class="bar-row" style="${{cur?'background:#1e2e4a;border-radius:6px;padding:4px 6px;margin:-4px -6px 6px;':''}}">
      <div class="bar-label">
        <span class="name" style="${{cur?'color:#4fc3f7;font-weight:700':''}}">${{cur?'▶ ':''}}${{e}}</span>
        <span class="count">${{v.toLocaleString('pt-BR')}}</span>
      </div>
      <div class="bar-bg"><div class="bar-fill" style="width:${{Math.round(v/maxE*100)}}%;background:${{cur?'#4fc3f7':cor}}"></div></div>
    </div>`;
  }}).join('');
  document.getElementById('tab-ranking').innerHTML = `
    <div class="sec-title">Estados da Região ${{s.regiao}}</div>${{rankRows}}
    <div class="sec-title" style="margin-top:14px">Posição no Brasil</div>
    ${{barHTML(uf+' no Brasil', s.total, TOTAL_GERAL, cor)}}
    ${{barHTML(s.regiao+' no Brasil', s.total_regiao, TOTAL_GERAL, COR_REGIAO[s.regiao])}}
  `;

  // INSIGHTS
  const ins = INSIGHTS_ESTADO[uf] ||
    `${{uf}} representa ${{s.pct_brasil}}% dos pescadores nacionais. ` +
    `O maior município concentra ${{s.concentracao_capital}}% dos registros estaduais.`;
  document.getElementById('tab-insights').innerHTML = `
    <div class="insight"><span class="tag">📍 ${{uf}} — análise</span>${{ins}}</div>
    <div class="insight" style="border-left-color:#4fc3f7">
      <span class="tag">🌎 Contexto regional</span>${{INSIGHTS_REGIAO[s.regiao]||''}}
    </div>
    <div class="insight" style="border-left-color:#4caf50">
      <span class="tag">📊 Dado-chave</span>
      ${{s.top_municipios[0]?.[0]}} é o principal polo com ${{s.top_municipios[0]?.[1]?.toLocaleString('pt-BR')}} registros
      (${{s.concentracao_capital}}% do estado).
    </div>
  `;

  document.getElementById('default-msg').style.display = 'none';
  showTab(currentTab);
}}

// Ajuste inicial
map.fitBounds(BRASIL_BOUNDS, {{padding:[10,10]}});
</script>
</body>
</html>"""

with open('/home/claude/mapa_v2.html', 'w', encoding='utf-8') as f:
    f.write(html)

import os
size = os.path.getsize('/home/claude/mapa_v2.html') / 1024 / 1024
print(f"Gerado: /home/claude/mapa_v2.html — {size:.1f} MB")
