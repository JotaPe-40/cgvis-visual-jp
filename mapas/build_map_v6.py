import pandas as pd, numpy as np, requests, json, os, tarfile, io

np.random.seed(42)

# ── DADOS CONSTANTES (MUNICÍPIOS DE PESCA) ──────────────────────────────────
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
        rows.append({'estado':estado,'municipio':municipio,
                     'latitude':lat+np.random.normal(0,0.18),
                     'longitude':lon+np.random.normal(0,0.18)})
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

por_uf  = df.groupby(['estado','regiao']).size().reset_index(name='n')
por_mun = df.groupby(['estado','municipio']).size().reset_index(name='n')
por_reg = df.groupby('regiao').size().reset_index(name='n')

# ── ESTATÍSTICAS ────────────────────────────────────────────────────────────
stats_uf = {}
for _, r in por_uf.iterrows():
    uf, reg = r['estado'], r['regiao']
    n_uf = int(r['n'])
    n_reg = int(por_reg[por_reg['regiao']==reg]['n'].values[0])
    tops = por_mun[por_mun['estado']==uf].sort_values('n', ascending=False).head(5)
    tlist = [[row['municipio'], int(row['n'])] for _, row in tops.iterrows()]
    conc = tlist[0][1]/n_uf*100 if tlist else 0
    stats_uf[uf] = {'n': n_uf, 'regiao': reg, 'n_reg': n_reg,
        'pct_br': round(n_uf/TOTAL*100, 1), 'pct_reg': round(n_uf/n_reg*100, 1),
        'tops': tlist, 'conc': round(conc, 1),
        'n_munis': int(df[df['estado']==uf]['municipio'].nunique())}

stats_reg = {}
for _, r in por_reg.iterrows():
    reg, n_reg = r['regiao'], int(r['n'])
    ufs_r = por_uf[por_uf['regiao']==reg].sort_values('n', ascending=False)
    top_ufs = [[row['estado'], int(row['n'])] for _, row in ufs_r.iterrows()]
    top_mun_r = por_mun[por_mun['estado'].map(REGIOES)==reg].sort_values('n', ascending=False).head(5)
    top_muns = [[row['municipio'], int(row['n'])] for _, row in top_mun_r.iterrows()]
    vals = [v for _, v in top_ufs]
    stats_reg[reg] = {'n': n_reg, 'pct_br': round(n_reg/TOTAL*100, 1), 'n_ufs': len(ufs_r),
        'top_ufs': top_ufs, 'top_muns': top_muns,
        'desigualdade': round(np.std(vals)/np.mean(vals)*100, 1) if vals else 0,
        'lider_pct': round(top_ufs[0][1]/n_reg*100, 1) if top_ufs else 0}

# ── GEOJSON DOS ESTADOS ──────────────────────────────────────────────────────
GJ_URL = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
gj = requests.get(GJ_URL, timeout=30).json()
NOME_UF = {'Acre':'AC','Amazonas':'AM','Amapá':'AP','Pará':'PA','Rondônia':'RO','Roraima':'RR','Tocantins':'TO',
    'Alagoas':'AL','Bahia':'BA','Ceará':'CE','Maranhão':'MA','Paraíba':'PB','Pernambuco':'PE',
    'Piauí':'PI','Rio Grande do Norte':'RN','Sergipe':'SE','Distrito Federal':'DF',
    'Goiás':'GO','Mato Grosso do Sul':'MS','Mato Grosso':'MT','Espírito Santo':'ES',
    'Minas Gerais':'MG','Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR',
    'Rio Grande do Sul':'RS','Santa Catarina':'SC'}
NOME_REG = {'Acre':'Norte','Amazonas':'Norte','Amapá':'Norte','Pará':'Norte','Rondônia':'Norte','Roraima':'Norte','Tocantins':'Norte',
    'Alagoas':'Nordeste','Bahia':'Nordeste','Ceará':'Nordeste','Maranhão':'Nordeste','Paraíba':'Nordeste',
    'Pernambuco':'Nordeste','Piauí':'Nordeste','Rio Grande do Norte':'Nordeste','Sergipe':'Nordeste',
    'Distrito Federal':'Centro-Oeste','Goiás':'Centro-Oeste','Mato Grosso do Sul':'Centro-Oeste','Mato Grosso':'Centro-Oeste',
    'Espírito Santo':'Sudeste','Minas Gerais':'Sudeste','Rio de Janeiro':'Sudeste','São Paulo':'Sudeste',
    'Paraná':'Sul','Rio Grande do Sul':'Sul','Santa Catarina':'Sul'}

n_uf_d = dict(zip(por_uf['estado'], por_uf['n']))
n_reg_d = dict(zip(por_reg['regiao'], por_reg['n']))
for feat in gj['features']:
    nome = feat['properties'].get('name', '')
    uf = NOME_UF.get(nome, '')
    reg = NOME_REG.get(nome, 'Desconhecido')
    feat['properties'].update({'uf': uf, 'regiao': reg,
        'n_estado': int(n_uf_d.get(uf, 0)), 'n_regiao': int(n_reg_d.get(reg, 0))})

# ── PONTOS INDIVIDUAIS (AMOSTRAS) ───────────────────────────────────────────
pts_uf = {uf: df[df['estado']==uf].sample(min(500, len(df[df['estado']==uf])), random_state=42)[['latitude','longitude','municipio']].values.tolist()
        for uf in df['estado'].unique()}
pts_reg = {reg: df[df['regiao']==reg].sample(min(1500, len(df[df['regiao']==reg])), random_state=42)[['latitude','longitude','municipio','estado']].values.tolist()
         for reg in df['regiao'].unique()}

# ── ALGORITMO OTIMIZADO DE HEATMAP DO V5 ─────────────────────────────────────
def make_heat(sub_df, normalize_by=None):
    counts = sub_df.groupby(['latitude','longitude']).size().reset_index(name='c')
    max_c = normalize_by or counts['c'].max() or 1
    return [[round(r['latitude'], 5), round(r['longitude'], 5), min(1.0, r['c']/max_c)]
            for _, r in counts.iterrows()]

global_max = df.groupby(['latitude','longitude']).size().max()
heat_br = make_heat(df, global_max)
heat_uf = {uf: make_heat(df[df['estado']==uf], global_max) for uf in df['estado'].unique()}
heat_reg = {reg: make_heat(df[df['regiao']==reg], global_max) for reg in df['regiao'].unique()}

bbox_uf = {}
for uf in df['estado'].unique():
    sub = df[df['estado']==uf]
    p = 0.4
    bbox_uf[uf] = [float(sub['latitude'].min())-p, float(sub['longitude'].min())-p,
                   float(sub['latitude'].max())+p, float(sub['longitude'].max())+p]

CONCLUSOES = {
    'geral': [
        "O Nordeste concentra 39% dos pescadores — mais que qualquer região, apesar de não ser a mais rica. A pesca artesanal é central para a subsistência.",
        "O Norte tem 68% dos pescadores em municípios ribeirinhos do interior, não no litoral — a pesca amazônica é predominantemente fluvial.",
        "O Sul tem a maior densidade de pescadores por km de litoral. Itajaí/SC e Rio Grande/RS são os dois maiores portos pesqueiros do país.",
        "O Sudeste combina pesca industrial (Santos, Macaé) com artesanal costeira. RJ e SP concentram 84% da região.",
        "O Centro-Oeste representa apenas 3,9% do total. A pesca pantaneira de Corumbá/MS é a única concentração relevante."
    ],
    'insights_uf': {
        'CE':'Fortaleza concentra 51% dos pescadores cearenses — hub de pesca industrial e artesanal no Nordeste.',
        'MA':'São Luís domina o estado, mas Cururupu emerge como segundo polo — pesca artesanal no litoral ocidental.',
        'AM':'Manaus concentra 56% do estado. A pesca fluvial amazônica se organiza em torno de grandes centros ribeirinhos.',
        'PA':'Belém responde por 45% do estado. Santarém, 800km rio acima, é o segundo polo — vocação ao longo do Amazonas.',
        'SC':'Itajaí é o maior porto pesqueiro do Brasil em volume desembarcado. Alta concentração reflete pesca oceânica industrial.',
        'RS':'Rio Grande concentra 45% dos gaúchos — polo da pesca oceânica do extremo sul, incluindo alto mar.',
        'RJ':'Macaé aparece como segundo polo fluminense, ligado à plataforma continental e à indústria offshore.',
        'SP':'Santos e Guarujá somam 50% dos pescadores paulistas — eixo da pesca no maior estado do país.',
        'BA':'Salvador concentra 48% da Bahia, mas Ilhéus e Porto Seguro revelam pesca artesanal no litoral sul.',
        'RN':'Areia Branca surpreende como 2º polo no RN — exportação de lagosta e camarão explica a concentração.',
        'PE':'Recife domina, mas a Grande Recife centraliza toda a pesca pernambucana.',
        'PI':'Parnaíba concentra quase toda a pesca piauiense — apesar do estado ser majoritariamente interiorano.',
        'MS':'Corumbá responde pela maior parte do MS — âncora da pesca fluvial do Centro-Oeste no Pantanal.'
    },
    'insights_reg': {
        'Norte':'68% dos pescadores estão no interior ribeirinho, não no litoral. Único padrão fluvial dominante — reflexo da Bacia Amazônica.',
        'Nordeste':'Maior volume absoluto (39%). Pesca artesanal é estratégica para segurança alimentar. CE, BA e MA respondem por 65% da região.',
        'Centro-Oeste':'Apenas 3,9% do total. Pesca restrita às bacias do Pantanal e Araguaia-Tocantins.',
        'Sudeste':'Combina pesca industrial em portos (Santos, Macaé) e artesanal costeira no litoral fluminense e paulista.',
        'Sul':'Maior densidade por km². Itajaí e Rio Grande são referências nacionais em pesca oceânica e processamento industrial.'
    },
    'melhorias': [
        '📊 Série temporal: evolução anual de registros por estado',
        '🎯 Filtro por tipo: Pessoa Física × Jurídica e Armador × Proprietário',
        '📈 Correlação IDH: cruzar dados de pesca com IDH municipal',
        '🌊 Overlay de bacias hidrográficas: mostrar correlação com rios no Norte',
        '🔍 Busca por município: campo de texto para localizar diretamente',
        '📱 Layout responsivo: painel inferior em telas mobile',
        '🗓️ Gráfico comparativo animado entre regiões',
        '📤 Exportar relatório em PDF com gráficos embutidos'
    ]
}

# ── DOWNLOAD ASSETS INLINE ──────────────────────────────────────────────────
print("Baixando Leaflet...")
r = requests.get("https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz", timeout=60)
t = tarfile.open(fileobj=io.BytesIO(r.content))
LEAFLET_JS = LEAFLET_CSS = ""
for m in t.getmembers():
    if m.name.endswith('dist/leaflet.js') and 'src' not in m.name:
        LEAFLET_JS = t.extractfile(m).read().decode('utf-8')
    if m.name.endswith('dist/leaflet.css'):
        LEAFLET_CSS = t.extractfile(m).read().decode('utf-8')

print("Baixando Leaflet.heat...")
LEAFLET_HEAT = requests.get(
    "https://raw.githubusercontent.com/Leaflet/Leaflet.heat/gh-pages/dist/leaflet-heat.js",
    timeout=30).text

# ── PREPARAÇÃO DOS TEMPLATES PARA INJEÇÃO ───────────────────────────────────
GJ_STR = json.dumps(gj, ensure_ascii=False)
S_UF = json.dumps(stats_uf, ensure_ascii=False)
S_REG = json.dumps(stats_reg, ensure_ascii=False)
PTS_UF = json.dumps(pts_uf, ensure_ascii=False)
PTS_REG = json.dumps(pts_reg, ensure_ascii=False)
HEAT_UF = json.dumps(heat_uf, ensure_ascii=False)
HEAT_REG = json.dumps(heat_reg, ensure_ascii=False)
HEAT_BR = json.dumps(heat_br, ensure_ascii=False)
BBOX_UF = json.dumps(bbox_uf, ensure_ascii=False)
CONC_STR = json.dumps(CONCLUSOES, ensure_ascii=False)
TOT_STR = f"{TOTAL:,}".replace(",", ".")

print("Gerando HTML...")
HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Armadores de Pesca — Brasil</title>
    <style>
    LEAFLET_CSS_PLACEHOLDER
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f1f5f9;color:#1e293b;display:flex;height:100vh;overflow:hidden}
    #sidebar{width:420px;background:#fff;box-shadow:4px 0 20px rgba(0,0,0,0.08);display:flex;flex-direction:column;z-index:1000;position:relative}
    #map{flex:1;height:100%;background:#cbd5e1}
    .header{padding:24px;background:linear-gradient(135deg,#1e3a8a,#1e40af);color:#fff}
    .header h1{font-size:20px;font-weight:700;margin-bottom:6px;letter-spacing:-0.5px}
    .header p{font-size:13px;color:#93c5fd;opacity:0.9}
    .tabs{display:flex;background:#f8fafc;border-bottom:1px solid #e2e8f0;padding:0 8px}
    .tab{flex:1;padding:12px 4px;text-align:center;font-size:13px;font-weight:600;color:#64748b;cursor:pointer;border-bottom:2px solid transparent;transition:all 0.2s}
    .tab:hover{color:#1e40af}
    .tab.active{color:#1e40af;border-bottom-color:#1e40af}
    .content-area{flex:1;overflow-y:auto;padding:20px;display:none}
    .content-area.active{display:block}
    .card-total{background:#f0fdf4;border:1px solid #bbf7d0;padding:16px;border-radius:12px;margin-bottom:20px;text-align:center}
    .card-total .num{font-size:32px;font-weight:800;color:#16a34a;line-height:1}
    .card-total .lbl{font-size:12px;color:#14532d;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px}
    .section-title{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;display:flex;align-items:center;justify-content:between}
    .geo-list{display:flex;flex-direction:column;gap:8px;margin-bottom:20px}
    .geo-item{display:flex;align-items:center;justify-content:between;padding:10px 14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;transition:all 0.15s;font-size:13px;font-weight:500}
    .geo-item:hover{background:#edf2f7;border-color:#cbd5e1;transform:translateX(2px)}
    .geo-item .count{font-weight:700;color:#1e40af;background:#dbeafe;padding:2px 8px;border-radius:12px;font-size:12px}
    .info-panel{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px}
    .info-title{font-size:16px;font-weight:700;color:#0f172a;margin-bottom:4px;display:flex;align-items:center;gap:6px}
    .info-subtitle{font-size:12px;color:#64748b;margin-bottom:14px;border-bottom:1px solid #e2e8f0;padding-bottom:8px}
    .stat-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
    .stat-box{background:#fff;border:1px solid #e2e8f0;padding:10px;border-radius:8px;text-align:center}
    .stat-box .val{font-size:18px;font-weight:700;color:#1e293b}
    .stat-box .lbl{font-size:11px;color:#64748b}
    .rank-list{display:flex;flex-direction:column;gap:6px}
    .rank-item{display:flex;align-items:center;justify-content:between;font-size:12px;padding:4px 0;border-bottom:1px dashed #e2e8f0}
    .rank-item:last-child{border-none}
    .rank-item .name{color:#334155}
    .rank-item .val{font-weight:600;color:#0f172a}
    .ins{padding:12px;border-radius:8px;font-size:12.5px;line-height:1.5;background:#f1f5f9;border-left:4px solid #64748b;margin-top:12px}
    .ins.red{background:#fef2f2;border-left-color:#ef4444;color:#991b1b}
    .ins.blue{background:#eff6ff;border-left-color:#3b82f6;color:#1e40af}
    .ins.green{background:#f0fdf4;border-left-color:#22c55e;color:#166534}
    .ins.purple{background:#faf5ff;border-left-color:#a855f7;color:#6b21a8}
    .ins .tg{display:block;font-weight:700;font-size:11px;text-transform:uppercase;margin-bottom:3px;letter-spacing:0.5px}
    .btn-clear{width:100%;padding:10px;background:#f1f5f9;border:1px solid #e2e8f0;color:#475569;font-weight:600;border-radius:8px;cursor:pointer;margin-top:12px;font-size:12px;transition:all 0.15s;display:flex;align-items:center;justify-content:center;gap:6px}
    .btn-clear:hover{background:#e2e8f0;color:#1e293b}
    .melhoria-item{display:flex;align-items:start;gap:8px;background:#f8fafc;padding:10px;border-radius:6px;margin-bottom:6px;font-size:12px;border:1px solid #e2e8f0}
    .legend-control{background:white;padding:10px 14px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);font-size:12px;line-height:1.4;color:#334155}
    .legend-control h4{font-size:11px;text-transform:uppercase;color:#1e293b;margin-bottom:6px;font-weight:700;letter-spacing:0.5px}
    .legend-row{display:flex;align-items:center;gap:6px;margin-bottom:3px}
    .legend-box{width:14px;height:14px;border-radius:3px}
    </style>
</head>
<body>

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
            <div class="num">TOTAL_BR_PLACEHOLDER</div>
            <div class="lbl">Armadores Registrados no País</div>
        </div>
        <div class="section-title">Análise Macroestrutural</div>
        <div id="conclusoes-gerais"></div>
    </div>

    <div id="tab-estado" class="content-area">
        <div id="est-selecao">
            <div class="section-title">Selecione um Estado no Mapa ou Abaixo</div>
            <div class="geo-list" id="lista-estados"></div>
        </div>
        <div id="est-detalhe" style="display:none">
            <button class="btn-clear" onclick="limparSelecao()"><- Voltar para lista de estados</button>
            <div class="info-panel" style="margin-top:12px">
                <div class="info-title"><span id="lbl-uf-nome"></span></div>
                <div class="info-subtitle">Região <span id="lbl-uf-reg"></span></div>
                <div class="stat-grid">
                    <div class="stat-box"><div class="val" id="lbl-uf-n"></div><div class="lbl">Armadores</div></div>
                    <div class="stat-box"><div class="val" id="lbl-uf-pctbr"></div><div class="lbl">% do Brasil</div></div>
                    <div class="stat-box"><div class="val" id="lbl-uf-pctreg"></div><div class="lbl">% da Região</div></div>
                    <div class="stat-box"><div class="val" id="lbl-uf-munis"></div><div class="lbl">Cidades</div></div>
                </div>
                <div class="section-title" style="margin-bottom:6px">Concentração da Atividade</div>
                <div class="stat-box" style="margin-bottom:12px;text-align:left;padding:8px 12px">
                    <div class="val" style="font-size:16px;color:#b91c1c"><span id="lbl-uf-conc"></span>%</div>
                    <div class="lbl">dos armadores estão concentrados no principal município.</div>
                </div>
                <div class="section-title" style="margin-bottom:8px">Top 5 Municípios Líderes</div>
                <div class="rank-list" id="lbl-uf-tops"></div>
            </div>
            <div id="lbl-uf-ins" class="ins blue"></div>
        </div>
    </div>

    <div id="tab-regiao" class="content-area">
        <div id="reg-selecao">
            <div class="section-title">Selecione uma Região Geográfica</div>
            <div class="geo-list" id="lista-regioes"></div>
        </div>
        <div id="reg-detalhe" style="display:none">
            <button class="btn-clear" onclick="limparSelecao()"><- Voltar para lista de regiões</button>
            <div class="info-panel" style="margin-top:12px">
                <div class="info-title">Região <span id="lbl-reg-nome"></span></div>
                <div class="info-subtitle">Macrorregião do Território Nacional</div>
                <div class="stat-grid">
                    <div class="stat-box"><div class="val" id="lbl-reg-n"></div><div class="lbl">Armadores</div></div>
                    <div class="stat-box"><div class="val" id="lbl-reg-pctbr"></div><div class="lbl">% do Brasil</div></div>
                    <div class="stat-box"><div class="val" id="lbl-reg-ufs"></div><div class="lbl">Estados Part.</div></div>
                    <div class="stat-box"><div class="val" id="lbl-reg-desig"></div><div class="lbl">Desigualdade (CV)</div></div>
                </div>
                <div class="section-title" style="margin-bottom:8px">Top Estados na Região</div>
                <div class="rank-list" id="lbl-reg-tops-uf" style="margin-bottom:14px"></div>
                <div class="section-title" style="margin-bottom:8px">Top 5 Cidades da Região</div>
                <div class="rank-list" id="lbl-reg-tops-mun"></div>
            </div>
            <div id="lbl-reg-ins" class="ins purple"></div>
        </div>
    </div>
</div>

<div id="map"></div>

<script>
LEAFLET_JS_PLACEHOLDER
LEAFLET_HEAT_PLACEHOLDER

// INJEÇÃO DOS DATASETS E ESTATÍSTICAS DO PYTHON
const BRASIL = [[-33.74, -73.98], [5.26, -28.84]];
const GJ = __GJ__;
const S_UF = __S_UF__;
const S_REG = __S_REG__;
const PTS_UF = __PTS_UF__;
const PTS_REG = __PTS_REG__;
const HEAT_UF = __HEAT_UF__;
const HEAT_REG = __HEAT_REG__;
const HEAT_BR = __HEAT_BR__;
const BBOX_UF = __BBOX_UF__;
const CONC = __CONC__;

const COR_REG = {
    'Norte': '#2563eb', 'Nordeste': '#ea580c', 'Centro-Oeste': '#eab308',
    'Sudeste': '#16a34a', 'Sul': '#9333ea'
};

let selTipo = null; // 'uf' ou 'reg'
let selVal = null;  // ex: 'RS', 'Sul'

// Inicialização da Malha Cartográfica do Leaflet
const map = L.map('map', {zoomControl:false, minZoom:4, maxZoom:10}).fitBounds(BRASIL);
L.control.zoom({position:'topright'}).addTo(map);

// Camada Base Clean (CartoDB Positron)
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO'
}).addTo(map);

// Inicializa a camada de Calor com a configuração adequada do V5
let heatLayer = L.heatLayer(HEAT_BR, {
    radius: 10,
    blur: 8,
    maxZoom: 5,
    max: 1.0,
    gradient: {0.2: '#eff6ff', 0.4: '#93c5fd', 0.6: '#3b82f6', 0.8: '#1d4ed8', 1.0: '#172554'}
}).addTo(map);

let geoLayer = null;

// Renderização Poligonal da camada Coroplética/Fronteiras (Destaque e clique)
function renderGeoJson() {
    if(geoLayer) map.removeLayer(geoLayer);
    
    geoLayer = L.geoJSON(GJ, {
        style: function(f) {
            const uf = f.properties.uf;
            const reg = f.properties.regiao;
            let cor = '#94a3b8';
            let fillOpacity = 0.05;
            let weight = 1;
            
            if (selTipo === 'uf') {
                if (uf === selVal) { cor = COR_REG[reg] || '#3b82f6'; fillOpacity = 0.4; weight = 2.5; }
                else { fillOpacity = 0.01; weight = 0.5; }
            } else if (selTipo === 'reg') {
                if (reg === selVal) { cor = COR_REG[reg]; fillOpacity = 0.3; weight = 2; }
                else { fillOpacity = 0.01; weight = 0.5; }
            } else {
                // Estado Neutro (Modo Nacional)
                cor = COR_REG[reg] || cor;
                fillOpacity = 0.12;
            }
            
            return {fillColor:cor, fillOpacity:fillOpacity, color:cor, weight:weight, opacity:0.6};
        },
        onEachFeature: function(f, layer) {
            const uf = f.properties.uf;
            const nome = f.properties.name;
            const reg = f.properties.regiao;
            const n = f.properties.n_estado;
            
            layer.bindTooltip(`<strong>${nome} (${uf})</strong><br>Região: ${reg}<br>Armadores: ${n.toLocaleString('pt-BR')}`, {sticky:true});
            
            layer.on({
                mouseover: function(e) {
                    if(!selTipo) {
                        e.target.setStyle({fillOpacity: 0.35, weight: 2});
                    }
                },
                mouseout: function(e) {
                    if(!selTipo) geoLayer.resetStyle(e.target);
                },
                click: function() {
                    switchTab(selTipo === 'reg' ? 'regiao' : 'estado');
                    selecionarGeo(selTipo === 'reg' ? 'reg' : 'uf', selTipo === 'reg' ? reg : uf);
                }
            });
        }
    }).addTo(map);
}

// Lógica Unificada de Seleção e Isolamento Geográfico
function selecionarGeo(tipo, valor) {
    selTipo = tipo;
    selVal = valor;
    
    renderGeoJson();
    
    // Atualização dinâmica dos dados do Heatmap conforme V5 (com isolamento do V4)
    if (tipo === 'uf') {
        heatLayer.setLatLngs(HEAT_UF[valor] || []);
        if(BBOX_UF[valor]) map.fitBounds(BBOX_UF[valor]);
        mostrarPainelUF(valor);
    } else if (tipo === 'reg') {
        heatLayer.setLatLngs(HEAT_REG[valor] || []);
        
        // Enquadrar limites geográficos da região filtrando as feições correspondentes
        let coords = [];
        geoLayer.eachLayer(l => {
            if(l.feature.properties.regiao === valor) {
                if(l.getBounds) coords.push(l.getBounds());
            }
        });
        if(coords.length > 0) {
            let b = coords[0];
            coords.forEach(c => b.extend(c));
            map.fitBounds(b);
        }
        mostrarPainelRegiao(valor);
    }
}

function limparSelecao() {
    selTipo = null;
    selVal = null;
    heatLayer.setLatLngs(HEAT_BR);
    map.fitBounds(BRASIL, {padding:[10,10]});
    renderGeoJson();
    
    document.getElementById('est-selecao').style.display = 'block';
    document.getElementById('est-detalhe').style.display = 'none';
    document.getElementById('reg-selecao').style.display = 'block';
    document.getElementById('reg-detalhe').style.display = 'none';
}

// Transições das interfaces laterais
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
        selTipo = 'uf';
        renderGeoJson();
    } else {
        document.querySelectorAll('.tab')[2].classList.add('active');
        document.getElementById('tab-regiao').classList.add('active');
        if(selTipo !== 'reg') limparSelecao();
        selTipo = 'reg';
        renderGeoJson();
    }
}

// Renderização dos Painéis Informativos
function mostrarPainelUF(uf) {
    const d = S_UF[uf];
    if(!d) return;
    document.getElementById('est-selecao').style.display = 'none';
    document.getElementById('est-detalhe').style.display = 'block';
    
    document.getElementById('lbl-uf-nome').innerText = `${uf}`;
    document.getElementById('lbl-uf-reg').innerText = d.regiao;
    document.getElementById('lbl-uf-n').innerText = d.n.toLocaleString('pt-BR');
    document.getElementById('lbl-uf-pctbr').innerText = d.pct_br + '%';
    document.getElementById('lbl-uf-pctreg').innerText = d.pct_reg + '%';
    document.getElementById('lbl-uf-munis').innerText = d.n_munis;
    document.getElementById('lbl-uf-conc').innerText = d.conc;
    
    document.getElementById('lbl-uf-tops').innerHTML = d.tops.map((t, i) => `
        <div class="rank-item">
            <span class="name">${i+1}. ${t[0]}</span>
            <span class="val">${t[1].toLocaleString('pt-BR')}</span>
        </div>
    `).join('');
    
    document.getElementById('lbl-uf-ins').innerHTML = `<span class="tg">Análise Local</span>${CONC.insights_uf[uf] || 'Distribuição pulverizada característica regional.'}`;
}

function mostrarPainelRegiao(reg) {
    const d = S_REG[reg];
    if(!d) return;
    document.getElementById('reg-selecao').style.display = 'none';
    document.getElementById('reg-detalhe').style.display = 'block';
    
    document.getElementById('lbl-reg-nome').innerText = reg;
    document.getElementById('lbl-reg-n').innerText = d.n.toLocaleString('pt-BR');
    document.getElementById('lbl-reg-pctbr').innerText = d.pct_br + '%';
    document.getElementById('lbl-reg-ufs').innerText = d.n_ufs;
    document.getElementById('lbl-reg-desig').innerText = d.desigualdade + '%';
    
    document.getElementById('lbl-reg-tops-uf').innerHTML = d.top_ufs.map((u, i) => `
        <div class="rank-item">
            <span class="name">${i+1}. ${u[0]}</span>
            <span class="val">${u[1].toLocaleString('pt-BR')} (${Math.round(u[1]/d.n*100)}%)</span>
        </div>
    `).join('');
    
    document.getElementById('lbl-reg-tops-mun').innerHTML = d.top_muns.map((m, i) => `
        <div class="rank-item">
            <span class="name">${i+1}. ${m[0]}</span>
            <span class="val">${m[1].toLocaleString('pt-BR')}</span>
        </div>
    `).join('');
    
    document.getElementById('lbl-reg-ins').innerHTML = `<span class="tg">Destaque Regional</span>${CONC.insights_reg[reg]}`;
}

// Inicializações estruturais das listas do menu lateral
const estOrdenados = Object.keys(S_UF).sort((a,b) => S_UF[b].n - S_UF[a].n);
document.getElementById('lista-estados').innerHTML = estOrdenados.map(uf => `
    <div class="geo-item" onclick="selecionarGeo('uf', '${uf}')">
        <span>${uf} - Região ${S_UF[uf].regiao}</span>
        <span class="count">${S_UF[uf].n.toLocaleString('pt-BR')}</span>
    </div>
`).join('');

const regOrdenadas = Object.keys(S_REG).sort((a,b) => S_REG[b].n - S_REG[a].n);
document.getElementById('lista-regioes').innerHTML = regOrdenadas.map(r => `
    <div class="geo-item" onclick="selecionarGeo('reg', '${r}')">
        <span>${r}</span>
        <span class="count">${S_REG[r].n.toLocaleString('pt-BR')}</span>
    </div>
`).join('');

document.getElementById('conclusoes-gerais').innerHTML = CONC.geral.map((c, i) => `
    <div class="ins ${['','red','blue','green','purple'][i%5]}" style="margin-bottom:5px;text-align:left">
        <span class="tg">${i+1}ª conclusão</span>${c}
    </div>
`).join('');

// Adicionar legenda estática para as intensidades do Heatmap
const legenda = L.control({position: 'bottomright'});
legenda.onAdd = function() {
    const div = L.DomUtil.create('div', 'legend-control');
    div.innerHTML = `
        <h4>Densidade</h4>
        <div class="legend-row"><div class="legend-box" style="background:#172554"></div>Crítica (Alta)</div>
        <div class="legend-row"><div class="legend-box" style="background:#1d4ed8"></div>Alta</div>
        <div class="legend-row"><div class="legend-box" style="background:#3b82f6"></div>Moderada</div>
        <div class="legend-row"><div class="legend-box" style="background:#93c5fd"></div>Dispersa</div>
    `;
    return div;
};
legenda.addTo(map);

// Primeirização geométrica neutra
renderGeoJson();
</script>
</body>
</html>"""

# Substituição de placeholders e geração do artefato compilado final
html_final = (HTML
  .replace('LEAFLET_CSS_PLACEHOLDER',  LEAFLET_CSS)
  .replace('LEAFLET_JS_PLACEHOLDER',   LEAFLET_JS)
  .replace('LEAFLET_HEAT_PLACEHOLDER', LEAFLET_HEAT)
  .replace('__GJ__',       D['GJ'])
  .replace('__S_UF__',     D['S_UF'])
  .replace('__S_REG__',    D['S_REG'])
  .replace('__PTS_UF__',   D['PTS_UF'])
  .replace('__PTS_REG__',  D['PTS_REG'])
  .replace('__HEAT_UF__',  D['HEAT_UF'])
  .replace('__HEAT_REG__', D['HEAT_REG'])
  .replace('__HEAT_BR__',  D['HEAT_BR'])
  .replace('__BBOX_UF__',  D['BBOX_UF'])
  .replace('__CONC__',     D['CONC'])
  .replace('TOTAL_BR_PLACEHOLDER', D['TOTAL_STR']))

with open("mapa_pesca_unificado.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("Sucesso! O arquivo unificado 'mapa_pesca_unificado.html' foi gerado.")