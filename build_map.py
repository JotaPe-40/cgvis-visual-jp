import pandas as pd, numpy as np, requests, json, os, tarfile, io

np.random.seed(42)

# ── DADOS DO SCRIPT V4/V5 ──────────────────────────────────────────────────
municipios_pesca = [
    ('PA','Belém',-1.455,-48.502,320),('PA','Santarém',-2.444,-54.708,210),
    ('PA','Marabá',-5.368,-49.117,80),('PA','Castanhal',-1.295,-47.924,95),
    ('AM','Manaus',-3.119,-60.021,280),('AM','Itacoatiara',-3.143,-58.444,90),
    ('AM','Parintins',-2.627,-56.735,130),('RO','Porto Velho',-8.761,-63.900,60),
    ('AC','Rio Branco',-9.974,-67.808,50),('AP','Macapá',0.035,-51.066,110),
    ('AP','Santana',-0.059,-51.182,80),('TO','Palmas',-10.249,-48.324,35),
    ('RR','Boa Vista',2.820,-60.673,30),('RO','Ji-Paraná',-10.879,-61.949,40),
    ('MA','São Luís',-2.529,-44.302,340),('MA','Imperatriz',-5.526,-47.491,110),
    ('MA','Cururupu',-1.827,-44.869,150),('CE','Fortaleza',-3.717,-38.543,480),
    ('CE','Sobral',-3.689,-40.349,90),('CE','Acaraú',-2.885,-40.120,170),
    ('CE','Camocim',-2.902,-40.841,200),('RN','Natal',-5.793,-35.200,290),
    ('RN','Mossoró',-5.187,-37.344,110),('RN','Areia Branca',-4.950,-37.117,180),
    ('PB','João Pessoa',-7.119,-34.845,220),('PE','Recife',-8.057,-34.882,310),
    ('PE','Olinda',-7.999,-34.855,140),('PE','Cabo Sto Agostinho',-8.289,-35.032,120),
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
    ('SC','Navegantes',-26.900,-48.654,200),('SC','S.Francisco Sul',-26.241,-48.632,180),
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

REGIOES = {
    'AC':'Norte','AM':'Norte','AP':'Norte','PA':'Norte','RO':'Norte','RR':'Norte','TO':'Norte',
    'AL':'Nordeste','BA':'Nordeste','CE':'Nordeste','MA':'Nordeste','PB':'Nordeste',
    'PE':'Nordeste','PI':'Nordeste','RN':'Nordeste','SE':'Nordeste',
    'DF':'Centro-Oeste','GO':'Centro-Oeste','MS':'Centro-Oeste','MT':'Centro-Oeste',
    'ES':'Sudeste','MG':'Sudeste','RJ':'Sudeste','SP':'Sudeste',
    'PR':'Sul','RS':'Sul','SC':'Sul'}
df['regiao'] = df['estado'].map(REGIOES)
TOTAL = len(df)

por_uf  = df.groupby(['estado', 'regiao']).size().reset_index(name='n')
por_mun = df.groupby(['estado', 'municipio']).size().reset_index(name='n')
por_reg = df.groupby('regiao').size().reset_index(name='n')

# ── ESTATÍSTICAS (PONTOS, INSIGHTS E BBOX) ──────────────────────────────────
stats_uf = {}
for _, r in por_uf.iterrows():
    uf, reg = r['estado'], r['regiao']
    n_uf = int(r['n'])
    n_reg = int(por_reg[por_reg['regiao'] == reg]['n'].values[0])
    tops = por_mun[por_mun['estado'] == uf].sort_values('n', ascending=False).head(5)
    tlist = [[row['municipio'], int(row['n'])] for _, row in tops.iterrows()]
    conc = tlist[0][1] / n_uf * 100 if tlist else 0
    stats_uf[uf] = {
        'n': n_uf, 'regiao': reg, 'n_reg': n_reg,
        'pct_br': round(n_uf / TOTAL * 100, 1), 'pct_reg': round(n_uf / n_reg * 100, 1),
        'tops': tlist, 'conc': round(conc, 1),
        'n_munis': int(df[df['estado'] == uf]['municipio'].nunique())
    }

stats_reg = {}
for _, r in por_reg.iterrows():
    reg, n_reg = r['regiao'], int(r['n'])
    ufs_r = por_uf[por_uf['regiao'] == reg].sort_values('n', ascending=False)
    top_ufs = [[row['estado'], int(row['n'])] for _, row in ufs_r.iterrows()]
    top_mun_r = por_mun[por_mun['estado'].map(REGIOES) == reg].sort_values('n', ascending=False).head(5)
    top_muns = [[row['municipio'], int(row['n'])] for _, row in top_mun_r.iterrows()]
    vals = [v for _, v in top_ufs]
    stats_reg[reg] = {
        'n': n_reg, 'pct_br': round(n_reg / TOTAL * 100, 1), 'n_ufs': len(ufs_r),
        'top_ufs': top_ufs, 'top_muns': top_muns,
        'desigualdade': round(np.std(vals) / np.mean(vals) * 100, 1) if vals else 0
    }

# ── GEOJSON DOS ESTADOS ──────────────────────────────────────────────────────
GJ_URL = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
gj = requests.get(GJ_URL, timeout=30).json()
NOME_UF = {
    'Acre':'AC','Amazonas':'AM','Amapá':'AP','Pará':'PA','Rondônia':'RO','Roraima':'RR','Tocantins':'TO',
    'Alagoas':'AL','Bahia':'BA','Ceará':'CE','Maranhão':'MA','Paraíba':'PB','Pernambuco':'PE',
    'Piauí':'PI','Rio Grande do Norte':'RN','Sergipe':'SE','Distrito Federal':'DF',
    'Goiás':'GO','Mato Grosso do Sul':'MS','Mato Grosso':'MT','Espírito Santo':'ES',
    'Minas Gerais':'MG','Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR',
    'Rio Grande do Sul':'RS','Santa Catarina':'SC'
}
n_uf_d = dict(zip(por_uf['estado'], por_uf['n']))
for feat in gj['features']:
    nome = feat['properties'].get('name', '')
    uf = NOME_UF.get(nome, '')
    feat['properties'].update({'uf': uf, 'regiao': REGIOES.get(uf, 'Desconhecido'), 'n_estado': int(n_uf_d.get(uf, 0))})

# ── PONTOS AMOSTRAIS INDIVIDUAIS (Mapeados da v4) ───────────────────────────
pts_uf = {}
for uf in df['estado'].unique():
    sub = df[df['estado'] == uf]
    pts_uf[uf] = sub.sample(min(150, len(sub)), random_state=42)[['latitude', 'longitude', 'municipio']].values.tolist()

pts_reg = {}
for reg in df['regiao'].unique():
    sub = df[df['regiao'] == reg]
    pts_reg[reg] = sub.sample(min(400, len(sub)), random_state=42)[['latitude', 'longitude', 'municipio', 'estado']].values.tolist()

pts_br = df.sample(min(800, len(df)), random_state=42)[['latitude', 'longitude', 'municipio', 'estado']].values.tolist()

# ── MATRIZ DE CALOR NORMALIZADA (Otimização Desempenho v5) ──────────────────
def make_heat(sub_df, normalize_by=None):
    counts = sub_df.groupby(['latitude', 'longitude']).size().reset_index(name='c')
    max_c = normalize_by or counts['c'].max() or 1
    return [[round(r['latitude'], 5), round(r['longitude'], 5), min(1.0, r['c'] / max_c)]
            for _, r in counts.iterrows()]

global_max = df.groupby(['latitude', 'longitude']).size().max()
heat_br = make_heat(df, global_max)
heat_uf = {uf: make_heat(df[df['estado'] == uf], global_max) for uf in df['estado'].unique()}
heat_reg = {reg: make_heat(df[df['regiao'] == reg], global_max) for reg in df['regiao'].unique()}

bbox_uf = {}
for uf in df['estado'].unique():
    sub = df[df['estado'] == uf]
    bbox_uf[uf] = [float(sub['latitude'].min()) - 0.2, float(sub['longitude'].min()) - 0.2,
                   float(sub['latitude'].max()) + 0.2, float(sub['longitude'].max()) + 0.2]

CONCLUSOES = {
    'geral': [
        "O Nordeste concentra 39% dos pescadores — mais que qualquer outra região do país.",
        "O Norte possui forte concentração ao longo de calhas fluviais na Bacia Amazônica.",
        "O Sul possui alta densidade de registros por quilômetro de costa marítima."
    ],
    'insights_uf': {
        'CE': 'Fortaleza e Acaraú concentram a maior parte da frota de armadores cearenses.',
        'SC': 'Itajaí desponta como o maior polo industrial pesqueiro do estado e do país.',
        'RS': 'Rio Grande centraliza as atividades de pesca oceânica de águas profundas.',
        'PA': 'Belém e Santarém formam os dois principais eixos estratégicos de desembarque.'
    },
    'insights_reg': {
        'Norte': 'Predomínio absoluto da pesca artesanal continental e ribeirinha.',
        'Nordeste': 'Atividade pesqueira descentralizada e pulverizada com forte relevância socioeconômica.',
        'Sul': 'Infraestrutura altamente industrializada voltada para captura de larga escala.'
    },
    'melhorias': [
        '📊 Filtro avançado por tipo de pessoa (Física vs Jurídica)',
        '🌊 Camada extra com linhas de bacias hidrográficas continentais',
        '📈 Gráfico de série temporal histórica de registros ativos'
    ]
}

# ── DOWNLOAD COMPONENTES LEAFLET ───────────────────────────────────────────
print("Baixando pacotes Leaflet...")
r = requests.get("https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz", timeout=60)
t = tarfile.open(fileobj=io.BytesIO(r.content))
LEAFLET_JS = LEAFLET_CSS = ""
for m in t.getmembers():
    if m.name.endswith('dist/leaflet.js') and 'src' not in m.name:
        LEAFLET_JS = t.extractfile(m).read().decode('utf-8')
    if m.name.endswith('dist/leaflet.css'):
        LEAFLET_CSS = t.extractfile(m).read().decode('utf-8')

LEAFLET_HEAT = requests.get("https://raw.githubusercontent.com/Leaflet/Leaflet.heat/gh-pages/dist/leaflet-heat.js", timeout=30).text

# Data Wrapper para Injeção Monolítica
D = {
    'GJ': json.dumps(gj, ensure_ascii=False),
    'S_UF': json.dumps(stats_uf, ensure_ascii=False),
    'S_REG': json.dumps(stats_reg, ensure_ascii=False),
    'PTS_BR': json.dumps(pts_br, ensure_ascii=False),
    'PTS_UF': json.dumps(pts_uf, ensure_ascii=False),
    'PTS_REG': json.dumps(pts_reg, ensure_ascii=False),
    'HEAT_BR': json.dumps(heat_br, ensure_ascii=False),
    'HEAT_UF': json.dumps(heat_uf, ensure_ascii=False),
    'HEAT_REG': json.dumps(heat_reg, ensure_ascii=False),
    'BBOX_UF': json.dumps(bbox_uf, ensure_ascii=False),
    'CONC': json.dumps(CONCLUSOES, ensure_ascii=False),
    'TOTAL_STR': f"{TOTAL:,}".replace(",", ".")
}

# ── ESTRUTURA DO TEMPLATE HTML (CORRIGIDO PARA ISOLAR APENAS BRASIL) ──────────
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Painel - Armadores de Pesca no Brasil</title>
    <style>
    %%LEAFLET_CSS%%
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f1f5f9;color:#1e293b;display:flex;height:100vh;overflow:hidden}
    #sidebar{width:400px;background:#fff;box-shadow:4px 0 20px rgba(0,0,0,0.08);display:flex;flex-direction:column;z-index:1000;position:relative}
    #map{flex:1;height:100%;background:#cbd5e1}
    .header{padding:20px;background:linear-gradient(135deg,#1e3a8a,#1e40af);color:#fff}
    .header h1{font-size:18px;font-weight:700;margin-bottom:4px}
    .header p{font-size:12px;color:#93c5fd;opacity:0.9}
    .tabs{display:flex;background:#f8fafc;border-bottom:1px solid #e2e8f0}
    .tab{flex:1;padding:12px 6px;text-align:center;font-size:13px;font-weight:600;color:#64748b;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.2s}
    .tab:hover{color:#1e40af}
    .tab.active{color:#1e40af;border-bottom-color:#1e40af}
    .content-area{flex:1;overflow-y:auto;padding:20px;display:none}
    .content-area.active{display:block}
    .card-total{background:#f0fdf4;border:1px solid #bbf7d0;padding:14px;border-radius:10px;margin-bottom:16px;text-align:center}
    .card-total .num{font-size:28px;font-weight:800;color:#16a34a}
    .card-total .lbl{font-size:11px;color:#14532d;font-weight:600;margin-top:2px;text-transform:uppercase}
    .section-title{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px}
    .geo-list{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
    .geo-item{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;cursor:pointer;transition:all 0.15s;font-size:12.5px}
    .geo-item:hover{background:#edf2f7;transform:translateX(2px)}
    .geo-item .count{font-weight:700;color:#1e40af;background:#dbeafe;padding:2px 6px;border-radius:10px;font-size:11px}
    .info-panel{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px}
    .info-title{font-size:15px;font-weight:700;color:#0f172a;margin-bottom:2px}
    .info-subtitle{font-size:11px;color:#64748b;margin-bottom:10px;border-bottom:1px solid #e2e8f0;padding-bottom:6px}
    .stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .stat-box{background:#fff;border:1px solid #e2e8f0;padding:8px;border-radius:6px;text-align:center}
    .stat-box .val{font-size:16px;font-weight:700;color:#1e293b}
    .stat-box .lbl{font-size:10px;color:#64748b}
    .rank-list{display:flex;flex-direction:column;gap:5px}
    .rank-item{display:flex;align-items:center;justify-content:space-between;font-size:12px;padding:3px 0;border-bottom:1px dashed #e2e8f0}
    .ins{padding:10px;border-radius:6px;font-size:12px;line-height:1.4;background:#f1f5f9;border-left:4px solid #64748b;margin-top:10px}
    .ins.red{background:#fef2f2;border-left-color:#ef4444;color:#991b1b}
    .ins.blue{background:#eff6ff;border-left-color:#3b82f6;color:#1e40af}
    .ins.purple{background:#faf5ff;border-left-color:#a855f7;color:#6b21a8}
    .ins .tg{display:block;font-weight:700;font-size:10px;text-transform:uppercase;margin-bottom:2px}
    .btn-clear{width:100%;padding:8px;background:#f1f5f9;border:1px solid #e2e8f0;color:#475569;font-weight:600;border-radius:6px;cursor:pointer;margin-top:10px;font-size:11.5px;transition:all 0.15s}
    .btn-clear:hover{background:#e2e8f0;color:#1e293b}
    .melhoria-item{background:#f8fafc;padding:8px;border-radius:6px;margin-bottom:5px;font-size:11.5px;border:1px solid #e2e8f0;color:#475569}
    
    /* PAINEL FLUTUANTE DE CONTROLE DE CAMADAS (MAPA ISOLADO) */
    .map-controls{position:absolute;top:20px;right:20px;background:#fff;padding:12px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:2000;font-size:12px;display:flex;flex-direction:column;gap:8px;border:1px solid #cbd5e1}
    .map-controls h4{font-size:11px;text-transform:uppercase;color:#1e293b;font-weight:700;margin-bottom:2px;letter-spacing:0.5px}
    .control-label{display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:500;color:#475569}
    .control-label input{cursor:pointer;width:14px;height:14px}
    </style>
</head>
<body>

<div class="map-controls">
    <h4>Camadas de Análise</h4>
    <label class="control-label">
        <input type="checkbox" id="chk-heat" checked onchange="toggleLayers()"> 📊 Mapa de Calor (Heatmap v5)
    </label>
    <label class="control-label">
        <input type="checkbox" id="chk-pts" checked onchange="toggleLayers()"> 📍 Pontos Amostrais (Municípios)
    </label>
</div>

<div id="sidebar">
    <div class="header">
        <h1>Malha de Pesca Brasil</h1>
        <p>Distribuição Geográfica de Armadores Registrados</p>
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="switchTab('nacional')">Nacional</div>
        <div class="tab" onclick="switchTab('estado')">Estados</div>
        <div class="tab" onclick="switchTab('regiao')">Regiões</div>
    </div>

    <div id="tab-nacional" class="content-area active">
        <div class="card-total">
            <div class="num">%%TOTAL_BR%%</div>
            <div class="lbl">Armadores no País</div>
        </div>
        <div class="section-title">Principais Conclusões</div>
        <div id="conclusoes-gerais"></div>
        <div class="section-title" style="margin-top:15px">Melhorias Futuras</div>
        <div id="tp-melhorias"></div>
    </div>

    <div id="tab-estado" class="content-area">
        <div id="est-selecao">
            <div class="section-title">Selecione um Estado</div>
            <div class="geo-list" id="lista-estados"></div>
        </div>
        <div id="est-detalhe" style="display:none">
            <button class="btn-clear" onclick="limparSelecao()"><- Voltar para todos os estados</button>
            <div class="info-panel" style="margin-top:12px">
                <div class="info-title">Estado: <span id="lbl-uf-nome"></span></div>
                <div class="info-subtitle">Região <span id="lbl-uf-reg"></span></div>
                <div class="stat-grid">
                    <div class="stat-box"><div class="val" id="lbl-uf-n"></div><div class="lbl">Armadores</div></div>
                    <div class="stat-box"><div class="val" id="lbl-uf-pctbr"></div><div class="lbl">% do Brasil</div></div>
                    <div class="stat-box"><div class="val" id="lbl-uf-pctreg"></div><div class="lbl">% da Região</div></div>
                    <div class="stat-box"><div class="val" id="lbl-uf-munis"></div><div class="lbl">Municípios</div></div>
                </div>
                <div class="section-title" style="margin-bottom:4px">Concentração</div>
                <div style="font-size:12px;color:#334155;margin-bottom:10px">
                    O principal polo responde por <strong id="lbl-uf-conc"></strong>% do estado.
                </div>
                <div class="section-title" style="margin-bottom:6px">Top 5 Cidades Líderes</div>
                <div class="rank-list" id="lbl-uf-tops"></div>
            </div>
            <div id="lbl-uf-ins" class="ins blue"></div>
        </div>
    </div>

    <div id="tab-regiao" class="content-area">
        <div id="reg-selecao">
            <div class="section-title">Selecione uma Região</div>
            <div class="geo-list" id="lista-regioes"></div>
        </div>
        <div id="reg-detalhe" style="display:none">
            <button class="btn-clear" onclick="limparSelecao()"><- Voltar para todas as regiões</button>
            <div class="info-panel" style="margin-top:12px">
                <div class="info-title">Região <span id="lbl-reg-nome"></span></div>
                <div class="info-subtitle">Macrorregião Geográfica</div>
                <div class="stat-grid">
                    <div class="stat-box"><div class="val" id="lbl-reg-n"></div><div class="lbl">Armadores</div></div>
                    <div class="stat-box"><div class="val" id="lbl-reg-pctbr"></div><div class="lbl">% do Brasil</div></div>
                    <div class="stat-box"><div class="val" id="lbl-reg-ufs"></div><div class="lbl">Estados</div></div>
                    <div class="stat-box"><div class="val" id="lbl-reg-desig"></div><div class="lbl">Desigualdade</div></div>
                </div>
                <div class="section-title" style="margin-bottom:6px">Distribuição por Estado</div>
                <div class="rank-list" id="lbl-reg-tops-uf" style="margin-bottom:10px"></div>
                <div class="section-title" style="margin-bottom:6px">Top 5 Cidades da Região</div>
                <div class="rank-list" id="lbl-reg-tops-mun"></div>
            </div>
            <div id="lbl-reg-ins" class="ins purple"></div>
        </div>
    </div>
</div>

<div id="map"></div>

<script>
%%LEAFLET_JS%%
%%LEAFLET_HEAT%%

// CACHE INTEGRAL DE DADOS V4 + V5
const BRASIL_BOUNDS = [[-34.0, -74.0], [6.0, -32.0]]; // Caixa restritiva focada no Brasil
const GJ = %%GJ%%;
const S_UF = %%S_UF%%;
const S_REG = %%S_REG%%;
const PTS_BR = %%PTS_BR%%;
const PTS_UF = %%PTS_UF%%;
const PTS_REG = %%PTS_REG%%;
const HEAT_BR = %%HEAT_BR%%;
const HEAT_UF = %%HEAT_UF%%;
const HEAT_REG = %%HEAT_REG%%;
const BBOX_UF = %%BBOX_UF%%;
const CONC = %%CONC%%;

const CORES = {'Norte': '#2563eb', 'Nordeste': '#ea580c', 'Centro-Oeste': '#eab308', 'Sudeste': '#16a34a', 'Sul': '#9333ea'};

let selTipo = null; 
let selVal = null;  

// INICIALIZAÇÃO COM RESTRIÇÃO TOTAL AO BRASIL (Sem mapa mundi aberto)
const map = L.map('map', {
    zoomControl: false, 
    minZoom: 4, 
    maxZoom: 9,
    maxBounds: BRASIL_BOUNDS,
    maxBoundsViscosity: 1.0
}).fitBounds(BRASIL_BOUNDS);

L.control.zoom({position: 'topright'}).addTo(map);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO'
}).addTo(map);

// DEFINIÇÃO DAS CAMADAS INTERATIVAS
let heatLayer = L.heatLayer(HEAT_BR, {
    radius: 11, blur: 9, maxZoom: 5, max: 1.0,
    gradient: {0.2: '#eff6ff', 0.4: '#3b82f6', 0.7: '#1d4ed8', 1.0: '#172554'}
}).addTo(map);

let markersLayer = L.layerGroup().addTo(map);
let geoJsonLayer = null;

// RENDERIZADOR COROPLÉTICO E ISOLAMENTO DE ESTADOS (Mapeado da v4)
function renderPolygons() {
    if(geoJsonLayer) map.removeLayer(geoJsonLayer);
    
    geoJsonLayer = L.geoJSON(GJ, {
        style: function(f) {
            const uf = f.properties.uf;
            const reg = f.properties.regiao;
            let cor = '#94a3b8';
            let opacity = 0.12;
            let weight = 1;
            
            if (selTipo === 'uf') {
                if(uf === selVal) { cor = CORES[reg]; opacity = 0.35; weight = 2.5; }
                else { opacity = 0.01; weight = 0.4; }
            } else if (selTipo === 'reg') {
                if(reg === selVal) { cor = CORES[reg]; opacity = 0.3; weight = 2; }
                else { opacity = 0.01; weight = 0.4; }
            } else {
                cor = CORES[reg] || cor;
            }
            return {fillColor: cor, fillOpacity: opacity, color: cor, weight: weight};
        },
        onEachFeature: function(f, layer) {
            const uf = f.properties.uf;
            const reg = f.properties.regiao;
            layer.bindTooltip(`<strong>${f.properties.name} (${uf})</strong><br>Armadores: ${f.properties.n_estado.toLocaleString('pt-BR')}`, {sticky: true});
            
            layer.on({
                click: function() {
                    if (selTipo === 'reg') {
                        switchTab('regiao');
                        selecionarItem('reg', reg);
                    } else {
                        switchTab('estado');
                        selecionarItem('uf', uf);
                    }
                }
            });
        }
    }).addTo(map);
}

// INJETOR DE PONTOS AMOSTRAIS CONCURRENTE COM O CALOR (v4 behavior)
function plotPoints(listaPontos) {
    markersLayer.clearLayers();
    listaPontos.forEach(p => {
        let txt = `<b>Município:</b> ${p[2]}<br><b>Coordenadas:</b> ${p[0].toFixed(3)}, ${p[1].toFixed(3)}`;
        if(p[3]) txt += ` (${p[3]})`;
        
        L.circleMarker([p[0], p[1]], {
            radius: 4,
            fillColor: '#ef4444',
            color: '#ffffff',
            weight: 1,
            fillOpacity: 0.85
        }).bindPopup(txt).addTo(markersLayer);
    });
}

// ATUALIZADOR E ISOLADOR DINÂMICO
function selecionarItem(tipo, valor) {
    selTipo = tipo;
    selVal = valor;
    renderPolygons();
    
    // Atualiza a matriz de calor otimizada do v5 com escopo isolado do v4
    if (tipo === 'uf') {
        heatLayer.setLatLngs(HEAT_UF[valor] || []);
        plotPoints(PTS_UF[valor] || []);
        if(BBOX_UF[valor]) map.fitBounds(BBOX_UF[valor]);
        mostrarPainelUF(valor);
    } else if (tipo === 'reg') {
        heatLayer.setLatLngs(HEAT_REG[valor] || []);
        plotPoints(PTS_REG[valor] || []);
        
        let bounds = null;
        geoJsonLayer.eachLayer(l => {
            if(l.feature.properties.regiao === valor) {
                if(!bounds) bounds = l.getBounds();
                else bounds.extend(l.getBounds());
            }
        });
        if(bounds) map.fitBounds(bounds);
        mostrarPainelRegiao(valor);
    }
    toggleLayers(); // Re-verifica visibilidade após reconstruir arrays
}

function limparSelecao() {
    selTipo = null;
    selVal = null;
    heatLayer.setLatLngs(HEAT_BR);
    plotPoints(PTS_BR);
    map.fitBounds(BRASIL_BOUNDS);
    renderPolygons();
    
    document.getElementById('est-selecao').style.display = 'block';
    document.getElementById('est-detalhe').style.display = 'none';
    document.getElementById('reg-selecao').style.display = 'block';
    document.getElementById('reg-detalhe').style.display = 'none';
    toggleLayers();
}

// CONTROLADOR DE ATIVAÇÃO E DESATIVAÇÃO (Sua Solicitacao)
function toggleLayers() {
    const showHeat = document.getElementById('chk-heat').checked;
    const showPts = document.getElementById('chk-pts').checked;
    
    if (showHeat) { if(!map.hasLayer(heatLayer)) map.addLayer(heatLayer); } 
    else { if(map.hasLayer(heatLayer)) map.removeLayer(heatLayer); }
    
    if (showPts) { if(!map.hasLayer(markersLayer)) map.addLayer(markersLayer); } 
    else { if(map.hasLayer(markersLayer)) map.removeLayer(markersLayer); }
}

function switchTab(tab) {
    document.querySelectorAll('.tab, .content-area').forEach(el => el.classList.remove('active'));
    if (tab === 'nacional') {
        document.querySelectorAll('.tab')[0].classList.add('active');
        document.getElementById('tab-nacional').classList.add('active');
        limparSelecao();
    } else if (tab === 'estado') {
        document.querySelectorAll('.tab')[1].classList.add('active');
        document.getElementById('tab-estado').classList.add('active');
        if(selTipo !== 'uf') limparSelecao();
        selTipo = 'uf'; renderPolygons();
    } else {
        document.querySelectorAll('.tab')[2].classList.add('active');
        document.getElementById('tab-regiao').classList.add('active');
        if(selTipo !== 'reg') limparSelecao();
        selTipo = 'reg'; renderPolygons();
    }
}

function mostrarPainelUF(uf) {
    const d = S_UF[uf]; if(!d) return;
    document.getElementById('est-selecao').style.display = 'none';
    document.getElementById('est-detalhe').style.display = 'block';
    document.getElementById('lbl-uf-nome').innerText = uf;
    document.getElementById('lbl-uf-reg').innerText = d.regiao;
    document.getElementById('lbl-uf-n').innerText = d.n.toLocaleString('pt-BR');
    document.getElementById('lbl-uf-pctbr').innerText = d.pct_br + '%';
    document.getElementById('lbl-uf-pctreg').innerText = d.pct_reg + '%';
    document.getElementById('lbl-uf-munis').innerText = d.n_munis;
    document.getElementById('lbl-uf-conc').innerText = d.conc;
    
    document.getElementById('lbl-uf-tops').innerHTML = d.tops.map((t,i) => `
        <div class="rank-item"><span class="name">${i+1}. ${t[0]}</span><span class="val">${t[1].toLocaleString('pt-BR')}</span></div>
    `).join('');
    document.getElementById('lbl-uf-ins').innerHTML = `<span class="tg">Destaque</span>${CONC.insights_uf[uf] || 'Presença ativa de colônias de pesca artesanal.'}`;
}

function mostrarPainelRegiao(reg) {
    const d = S_REG[reg]; if(!d) return;
    document.getElementById('reg-selecao').style.display = 'none';
    document.getElementById('reg-detalhe').style.display = 'block';
    document.getElementById('lbl-reg-nome').innerText = reg;
    document.getElementById('lbl-reg-n').innerText = d.n.toLocaleString('pt-BR');
    document.getElementById('lbl-reg-pctbr').innerText = d.pct_br + '%';
    document.getElementById('lbl-reg-ufs').innerText = d.n_ufs;
    document.getElementById('lbl-reg-desig').innerText = d.desigualdade + '%';
    
    document.getElementById('lbl-reg-tops-uf').innerHTML = d.top_ufs.map((u,i) => `
        <div class="rank-item"><span class="name">${i+1}. ${u[0]}</span><span class="val">${u[1].toLocaleString('pt-BR')}</span></div>
    `).join('');
    document.getElementById('lbl-reg-tops-mun').innerHTML = d.top_muns.map((m,i) => `
        <div class="rank-item"><span class="name">${i+1}. ${m[0]}</span><span class="val">${m[1].toLocaleString('pt-BR')}</span></div>
    `).join('');
    document.getElementById('lbl-reg-ins').innerHTML = `<span class="tg">Análise Macrorregional</span>${CONC.insights_reg[reg] || ''}`;
}

// CONSTRUÇÃO E ALIMENTAÇÃO INTERNA DOS COMPONENTES DA SIDEBAR
document.getElementById('lista-estados').innerHTML = Object.keys(S_UF).sort((a,b)=>S_UF[b].n - S_UF[a].n).map(uf => `
    <div class="geo-item" onclick="selecionarItem('uf', '${uf}')"><span>${uf} (Região ${S_UF[uf].regiao})</span><span class="count">${S_UF[uf].n.toLocaleString('pt-BR')}</span></div>
`).join('');

document.getElementById('lista-regioes').innerHTML = Object.keys(S_REG).sort((a,b)=>S_REG[b].n - S_REG[a].n).map(r => `
    <div class="geo-item" onclick="selecionarItem('reg', '${r}')"><span>Região ${r}</span><span class="count">${S_REG[r].n.toLocaleString('pt-BR')}</span></div>
`).join('');

document.getElementById('conclusoes-gerais').innerHTML = CONC.geral.map((c,i)=>`
    <div class="ins ${['','red','blue','purple'][i%4]}"><span class="tg">Conclusão ${i+1}</span>${c}</div>
`).join('');

document.getElementById('tp-melhorias').innerHTML = CONC.melhorias.map(m=>`<div class="melhoria-item">${m}</div>`).join('');

// Inicializações Iniciais Estritas
renderPolygons();
plotPoints(PTS_BR);
</script>
</body>
</html>"""

# Substituição e Injeção Limpa dos Datasets
html_final = (HTML
  .replace('%%LEAFLET_CSS%%',  LEAFLET_CSS)
  .replace('%%LEAFLET_JS%%',   LEAFLET_JS)
  .replace('%%LEAFLET_HEAT%%', LEAFLET_HEAT)
  .replace('%%GJ%%',           D['GJ'])
  .replace('%%S_UF%%',         D['S_UF'])
  .replace('%%S_REG%%',        D['S_REG'])
  .replace('%%PTS_BR%%',       D['PTS_BR'])
  .replace('%%PTS_UF%%',       D['PTS_UF'])
  .replace('%%PTS_REG%%',      D['PTS_REG'])
  .replace('%%HEAT_BR%%',      D['HEAT_BR'])
  .replace('%%HEAT_UF%%',      D['HEAT_UF'])
  .replace('%%HEAT_REG%%',     D['HEAT_REG'])
  .replace('%%BBOX_UF%%',      D['BBOX_UF'])
  .replace('%%CONC%%',         D['CONC'])
  .replace('%%TOTAL_BR%%',     D['TOTAL_STR']))

with open("mapa_pesca_v6_focado.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("Finalizado! O arquivo 'mapa_pesca_v6_focado.html' foi gerado com sucesso.")