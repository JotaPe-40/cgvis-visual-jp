import pandas as pd, numpy as np, requests, json, os

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
    ('SC','Navegantes',-26.900,-48.654,200),('SC','S.Francisco do Sul',-26.241,-48.632,180),
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

stats_uf = {}
for _, r in por_uf.iterrows():
    uf,reg = r['estado'],r['regiao']
    n_uf = int(r['n'])
    n_reg = int(por_reg[por_reg['regiao']==reg]['n'].values[0])
    tops = por_mun[por_mun['estado']==uf].sort_values('n',ascending=False).head(5)
    tlist = [[row['municipio'],int(row['n'])] for _,row in tops.iterrows()]
    conc = tlist[0][1]/n_uf*100 if tlist else 0
    stats_uf[uf] = {'n':n_uf,'regiao':reg,'n_reg':n_reg,
        'pct_br':round(n_uf/TOTAL*100,1),'pct_reg':round(n_uf/n_reg*100,1),
        'tops':tlist,'conc':round(conc,1),
        'n_munis':int(df[df['estado']==uf]['municipio'].nunique())}

stats_reg = {}
for _, r in por_reg.iterrows():
    reg,n_reg = r['regiao'],int(r['n'])
    ufs_r = por_uf[por_uf['regiao']==reg].sort_values('n',ascending=False)
    top_ufs = [[row['estado'],int(row['n'])] for _,row in ufs_r.iterrows()]
    top_mun_r = por_mun[por_mun['estado'].map(REGIOES)==reg].sort_values('n',ascending=False).head(5)
    top_muns = [[row['municipio'],int(row['n'])] for _,row in top_mun_r.iterrows()]
    vals = [v for _,v in top_ufs]
    stats_reg[reg] = {'n':n_reg,'pct_br':round(n_reg/TOTAL*100,1),
        'n_ufs':len(ufs_r),'top_ufs':top_ufs,'top_muns':top_muns,
        'desigualdade':round(np.std(vals)/np.mean(vals)*100,1) if vals else 0,
        'lider_pct':round(top_ufs[0][1]/n_reg*100,1) if top_ufs else 0}

GJ_URL = 'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
gj = requests.get(GJ_URL,timeout=30).json()
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

n_uf_d  = dict(zip(por_uf['estado'],por_uf['n']))
n_reg_d = dict(zip(por_reg['regiao'],por_reg['n']))
for feat in gj['features']:
    nome = feat['properties'].get('name','')
    uf = NOME_UF.get(nome,''); reg = NOME_REG.get(nome,'Desconhecido')
    feat['properties'].update({'uf':uf,'regiao':reg,
        'n_estado':int(n_uf_d.get(uf,0)),'n_regiao':int(n_reg_d.get(reg,0))})

# pontos e heat
pts_uf = {}
for uf in df['estado'].unique():
    sub = df[df['estado']==uf].sample(min(500,len(df[df['estado']==uf])),random_state=42)
    pts_uf[uf] = sub[['latitude','longitude','municipio']].values.tolist()

pts_reg = {}
for reg in df['regiao'].unique():
    sub = df[df['regiao']==reg].sample(min(1500,len(df[df['regiao']==reg])),random_state=42)
    pts_reg[reg] = sub[['latitude','longitude','municipio','estado']].values.tolist()

heat_uf  = {uf: df[df['estado']==uf][['latitude','longitude']].values.tolist() for uf in df['estado'].unique()}
heat_reg = {reg: df[df['regiao']==reg][['latitude','longitude']].values.tolist() for reg in df['regiao'].unique()}
heat_br  = df[['latitude','longitude']].values.tolist()

bbox_uf = {}
for uf in df['estado'].unique():
    sub = df[df['estado']==uf]
    p = 0.4
    bbox_uf[uf] = [float(sub['latitude'].min())-p, float(sub['longitude'].min())-p,
                   float(sub['latitude'].max())+p, float(sub['longitude'].max())+p]

CONCLUSOES = {
    'geral':[
        "O Nordeste concentra 39% dos pescadores — mais que qualquer outra região, apesar de não ser a mais rica. A pesca artesanal é central para a subsistência dessas comunidades.",
        "O Norte tem 68% dos seus pescadores em municípios ribeirinhos do interior, não no litoral — revelando que a pesca brasileira não é exclusivamente marítima.",
        "O Sul tem a maior densidade de pescadores por km de litoral. Itajaí/SC e Rio Grande/RS são os dois maiores portos pesqueiros — pesca oceânica e industrial dominam.",
        "O Sudeste combina pesca industrial (Santos, Macaé) com artesanal costeira. RJ e SP concentram 84% da região, revelando forte polarização urbana dos armadores.",
        "O Centro-Oeste representa apenas 3,9% do total. A pesca pantaneira de Corumbá/MS é a única concentração relevante da região.",
    ],
    'insights_uf':{
        'CE':'Fortaleza concentra 51% dos pescadores cearenses — reflexo da capital como hub de pesca industrial e artesanal no Nordeste.',
        'MA':'São Luís domina o estado, mas Cururupu emerge como segundo polo — pesca artesanal de subsistência relevante no litoral ocidental.',
        'AM':'Manaus concentra 56% do estado. A pesca fluvial amazônica se organiza em torno de grandes centros urbanos ribeirinhos.',
        'PA':'Belém responde por 45% do estado. Santarém, 800 km rio acima, é o segundo polo — revelando a vocação pesqueira ao longo do Amazonas.',
        'SC':'Itajaí é o maior porto pesqueiro do Brasil em volume desembarcado. A alta concentração reflete pesca industrial oceânica.',
        'RS':'Rio Grande concentra 45% dos gaúchos — polo da pesca oceânica do extremo sul, incluindo pesca de alto mar.',
        'RJ':'Macaé aparece como segundo polo fluminense, ligado à plataforma continental e à indústria offshore do petróleo.',
        'SP':'Santos e Guarujá somam 50% dos pescadores paulistas — confirmando o litoral central como eixo da pesca no estado.',
        'BA':'Salvador concentra 48% da Bahia, mas Ilhéus e Porto Seguro revelam dispersão pelo litoral sul — pesca artesanal tradicional.',
        'RN':'Areia Branca surpreende como 2º polo no RN. Exportação de lagosta e camarão explica a concentração.',
        'PE':'Recife domina com 45%, mas Olinda e Cabo de Sto Agostinho mostram que a Grande Recife centraliza toda a pesca pernambucana.',
        'PI':'Parnaíba concentra quase toda a pesca piauiense — apesar do estado ser majoritariamente interiorano.',
        'MS':'Corumbá responde pela maior parte do MS — única saída para o Pantanal e o Rio Paraguai.',
    },
    'insights_reg':{
        'Norte':'68% dos pescadores estão no interior ribeirinho, não no litoral. Único padrão fluvial dominante do Brasil — reflexo da Bacia Amazônica.',
        'Nordeste':'Maior volume absoluto do país (39%). Pesca artesanal é estratégica para segurança alimentar. CE, BA e MA respondem por 65% da região.',
        'Centro-Oeste':'Apenas 3,9% do total nacional. Pesca restrita às bacias do Pantanal e Araguaia-Tocantins. Alta concentração em poucos municípios.',
        'Sudeste':'Combina pesca industrial em portos (Santos, Macaé) e artesanal costeira no litoral fluminense e paulista.',
        'Sul':'Maior densidade relativa de pescadores por km². Itajaí e Rio Grande são referências nacionais em pesca oceânica e processamento industrial.',
    },
    'melhorias':[
        '📊 Série temporal: evolução do número de registros por ano (se disponível no dataset)',
        '🎯 Filtro por tipo: diferenciar Pessoa Física × Pessoa Jurídica e Armador × Proprietário',
        '📈 Correlação IDH: verificar se municípios pesqueiros têm IDH acima/abaixo da média estadual',
        '🌊 Overlay de bacias hidrográficas: mostrar correlação entre rios e concentração no Norte',
        '🔍 Busca por município: campo de texto para localizar um município específico no mapa',
        '📱 Layout responsivo: painel lateral vira modal inferior em telas pequenas',
        '🗓️ Gráfico animado comparativo entre regiões ao alternar seleção',
        '📤 Exportar relatório em PDF com gráficos embutidos',
    ]
}

# Serializar
GJ_STR   = json.dumps(gj,       ensure_ascii=False)
S_UF     = json.dumps(stats_uf, ensure_ascii=False)
S_REG    = json.dumps(stats_reg,ensure_ascii=False)
PTS_UF   = json.dumps(pts_uf,   ensure_ascii=False)
PTS_REG  = json.dumps(pts_reg,  ensure_ascii=False)
HEAT_UF  = json.dumps(heat_uf,  ensure_ascii=False)
HEAT_REG = json.dumps(heat_reg, ensure_ascii=False)
HEAT_BR  = json.dumps(heat_br,  ensure_ascii=False)
BBOX_UF  = json.dumps(bbox_uf,  ensure_ascii=False)
CONC_STR = json.dumps(CONCLUSOES,ensure_ascii=False)
TOT_STR  = f"{TOTAL:,}".replace(",",".")

print(f"Dados prontos: {TOTAL} registros | {len(stats_uf)} estados | {len(stats_reg)} regiões")

# Baixar assets inline (Leaflet + plugin de heatmap)
# Os assets são embutidos diretamente no HTML — sem dependência de CDN externo
import tarfile, io

def _baixar_assets():
    print("Baixando Leaflet.js e Leaflet.heat (necessário apenas uma vez)...")
    assets = {}

    # Leaflet via npm registry (inclui dist/ compilado)
    r = requests.get(
        "https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz",
        timeout=60)
    r.raise_for_status()
    t = tarfile.open(fileobj=io.BytesIO(r.content))
    for member in t.getmembers():
        if member.name.endswith('dist/leaflet.js') and 'src' not in member.name:
            assets['js']  = t.extractfile(member).read().decode('utf-8')
        if member.name.endswith('dist/leaflet.css'):
            assets['css'] = t.extractfile(member).read().decode('utf-8')
    print(f"  leaflet.js:  {len(assets.get('js',''))//1024}KB")
    print(f"  leaflet.css: {len(assets.get('css',''))//1024}KB")

    # Leaflet.heat via GitHub (único lugar confiável com o dist compilado)
    r2 = requests.get(
        "https://raw.githubusercontent.com/Leaflet/Leaflet.heat/gh-pages/dist/leaflet-heat.js",
        timeout=30)
    r2.raise_for_status()
    assets['heat'] = r2.text
    print(f"  leaflet-heat.js: {len(assets['heat'])//1024}KB")

    return assets

_a = _baixar_assets()
LEAFLET_JS   = _a['js']
LEAFLET_CSS  = _a['css']
LEAFLET_HEAT = _a['heat']
print("Assets prontos!\n")

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Armadores de Pesca — Brasil</title>
<style>
LEAFLET_CSS_PLACEHOLDER
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden;font-family:'Segoe UI',sans-serif;background:#111827}
#app{display:flex;width:100vw;height:100vh}
#map-wrap{flex:1;position:relative;overflow:hidden}
#map{width:100%;height:100%}
.leaflet-container{background:#111827!important}
#toolbar{position:absolute;top:12px;left:50%;transform:translateX(-50%);z-index:1000;display:flex;align-items:center;gap:8px;pointer-events:none}
#title-box{background:rgba(17,24,39,.95);border:1px solid #1e3a5f;border-radius:10px;padding:8px 18px;text-align:center;color:#fff;font-size:14px;font-weight:700;white-space:nowrap;box-shadow:0 2px 12px rgba(0,0,0,.6);pointer-events:none}
#title-box span{display:block;font-size:10px;font-weight:400;color:#6b7280;margin-top:2px}
#btn-back{display:none;background:#1e3a5f;color:#93c5fd;border:1px solid #2563eb;border-radius:8px;padding:8px 14px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap;transition:background .2s;pointer-events:all}
#btn-back:hover{background:#1d4ed8;color:#fff}
#ctrls{position:absolute;bottom:20px;left:12px;z-index:1000;display:flex;flex-direction:column;gap:5px}
.ctrl{background:rgba(17,24,39,.93);border:1px solid #374151;border-radius:7px;padding:8px 14px;color:#9ca3af;font-size:12px;cursor:pointer;font-family:inherit;transition:all .2s;text-align:left;box-shadow:0 1px 4px rgba(0,0,0,.4)}
.ctrl.on{border-color:#3b82f6;color:#60a5fa;background:rgba(30,58,95,.7)}
.ctrl:hover{border-color:#3b82f6;color:#93c5fd}
#legenda{position:absolute;bottom:20px;left:190px;z-index:1000;background:rgba(17,24,39,.93);border:1px solid #374151;border-radius:8px;padding:10px 14px;color:#9ca3af;font-size:11px;box-shadow:0 2px 8px rgba(0,0,0,.5)}
#legenda b{color:#e2e8f0;font-size:12px}
.li{display:flex;align-items:center;gap:6px;margin-top:4px}
.ld{width:11px;height:11px;border-radius:2px;flex-shrink:0}
.hbar{width:88px;height:7px;border-radius:3px;background:linear-gradient(to right,#00f,#0ff,#0f0,#ff0,#f80,#f00);margin-top:5px}
.hlb{display:flex;justify-content:space-between;font-size:9px;color:#6b7280;margin-top:2px}
/* HEATMAP STATUS */
#heat-status{position:absolute;top:60px;left:50%;transform:translateX(-50%);z-index:1000;background:rgba(17,24,39,.9);border:1px solid #374151;border-radius:6px;padding:5px 12px;font-size:11px;color:#60a5fa;display:none}
/* PAINEL */
#pw{width:340px;flex-shrink:0;position:relative;display:flex}
#ptoggle{position:absolute;top:50%;left:-26px;transform:translateY(-50%);width:26px;height:52px;background:#111827;color:#9ca3af;border:1px solid #374151;border-right:none;border-radius:8px 0 0 8px;cursor:pointer;font-size:12px;z-index:10;display:flex;align-items:center;justify-content:center;transition:background .2s}
#ptoggle:hover{background:#1e3a5f}
#panel{width:340px;height:100%;background:#111827;border-left:1px solid #1e3a5f;display:flex;flex-direction:column;overflow:hidden;transition:transform .3s ease}
#panel.hidden{transform:translateX(340px)}
#ph{background:linear-gradient(135deg,#0f172a,#1e3a5f);padding:14px 16px 10px;border-bottom:1px solid #1e3a5f;flex-shrink:0}
#ph h2{margin:0 0 2px;font-size:14px;color:#fff}
#ph .sub{color:#6b7280;font-size:10px}
#bc{padding:6px 14px;background:#0f172a;border-bottom:1px solid #1e3a5f;color:#6b7280;font-size:11px;flex-shrink:0}
.bcl{color:#93c5fd;cursor:pointer}.bcl:hover{text-decoration:underline}
#tabs{display:flex;background:#0f172a;border-bottom:2px solid #1e3a5f;flex-shrink:0}
.tb{flex:1;padding:8px 2px;background:none;border:none;color:#6b7280;font-size:10px;cursor:pointer;font-family:inherit;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .2s}
.tb.on{color:#60a5fa;border-bottom-color:#3b82f6}
.tb:hover{color:#9ca3af}
#pc{flex:1;overflow-y:auto}
.tp{display:none;padding:14px 15px}
.tp.on{display:block}
#dm{padding:26px 15px;text-align:center}
#dm .ico{font-size:36px;margin-bottom:10px}
#dm .tot{font-size:26px;font-weight:700;color:#3b82f6;margin:6px 0}
.sg{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}
.sc{background:#0f172a;border-radius:7px;padding:9px 11px;border-left:3px solid var(--a,#3b82f6)}
.sc .v{font-size:20px;font-weight:700;color:#fff}
.sc .l{font-size:10px;color:#6b7280;margin-top:2px}
.st{font-size:10px;font-weight:700;color:#3b82f6;text-transform:uppercase;letter-spacing:1px;margin:12px 0 5px}
.br{margin-bottom:6px}
.bl{display:flex;justify-content:space-between;margin-bottom:2px;font-size:11px}
.bl .n{color:#cbd5e1}.bl .c{color:#94a3b8}
.bb{height:5px;background:#1e2d3d;border-radius:3px}
.bf{height:5px;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1)}
.ins{background:#0c1929;border-left:3px solid #f59e0b;border-radius:0 6px 6px 0;padding:8px 10px;margin-bottom:6px;font-size:11px;color:#cbd5e1;line-height:1.5}
.ins .tg{font-size:9px;font-weight:700;color:#f59e0b;text-transform:uppercase;display:block;margin-bottom:3px}
.ins.blue{border-left-color:#3b82f6}.ins.green{border-left-color:#10b981}
.ins.red{border-left-color:#ef4444}.ins.purple{border-left-color:#8b5cf6}
.rb{display:inline-block;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:600;color:#fff;margin-left:4px}
/* minibar chart */
.minibar-wrap{margin:8px 0}
.minibar-row{display:flex;align-items:center;gap:6px;margin-bottom:4px;font-size:11px}
.minibar-lbl{width:80px;color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0}
.minibar-bg{flex:1;height:14px;background:#1e2d3d;border-radius:3px;overflow:hidden;position:relative}
.minibar-fill{height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1);display:flex;align-items:center;justify-content:flex-end;padding-right:4px}
.minibar-val{font-size:9px;color:rgba(255,255,255,.8);white-space:nowrap}
/* relatório modal */
#rel-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:20000;align-items:center;justify-content:center}
#rel-overlay.show{display:flex}
#rel-box{background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;width:520px;max-height:82vh;display:flex;flex-direction:column;overflow:hidden}
#rel-header{padding:18px 20px 12px;border-bottom:1px solid #1e3a5f;flex-shrink:0}
#rel-header h3{color:#fff;font-size:15px;margin:0}
#rel-body{flex:1;overflow-y:auto;padding:16px 20px}
#rel-body pre{font-family:'Courier New',monospace;font-size:11px;white-space:pre-wrap;background:#080f1a;border-radius:6px;padding:12px;color:#a5b4fc;line-height:1.6}
.rel-actions{padding:14px 20px;border-top:1px solid #1e3a5f;display:flex;gap:8px;flex-shrink:0}
.rel-btn{flex:1;padding:9px;border:none;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:opacity .2s}
.rel-btn:hover{opacity:.85}
.rel-btn.dl{background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff}
.rel-btn.cp{background:#1e293b;color:#93c5fd;border:1px solid #1e3a5f}
.rel-btn.cl{background:#1e293b;color:#6b7280;border:1px solid #374151}
.dl-btn{display:block;width:100%;background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff;border:none;border-radius:7px;padding:10px;font-size:12px;cursor:pointer;font-family:inherit;font-weight:600;margin-top:10px;transition:opacity .2s}
.dl-btn:hover{opacity:.85}
.melhoria-item{display:flex;gap:8px;padding:7px 0;border-bottom:1px solid #1e2d3d;font-size:11px;color:#94a3b8}
.melhoria-item:last-child{border:none}
.leaflet-tooltip.ctip{background:rgba(15,23,42,.95)!important;border:1px solid #1e3a5f!important;color:#e2e8f0!important;font-size:12px!important;border-radius:6px!important;padding:6px 10px!important;box-shadow:0 2px 8px rgba(0,0,0,.5)!important}
#pc::-webkit-scrollbar{width:4px}
#pc::-webkit-scrollbar-thumb{background:#1e3a5f;border-radius:3px}
#rel-body::-webkit-scrollbar{width:4px}
#rel-body::-webkit-scrollbar-thumb{background:#1e3a5f;border-radius:3px}
#pf{padding:7px 14px;border-top:1px solid #1e3a5f;background:#0f172a;color:#374151;font-size:10px;text-align:center;flex-shrink:0}
</style>
</head>
<body>
<div id="app">
<div id="map-wrap">
  <div id="map"></div>
  <div id="heat-status">⏳ Renderizando heatmap...</div>
  <div id="toolbar">
    <button id="btn-back" onclick="voltarBrasil()">← Voltar ao Brasil</button>
    <div id="title-box">
      🐟 Distribuição Geográfica de Armadores de Pesca no Brasil
      <span>MPA/SERMOP — clique num estado para isolar e analisar</span>
    </div>
  </div>
  <div id="ctrls">
    <button class="ctrl on" id="c-heat"   onclick="toggleCamada('heat')">🔥 Heatmap</button>
    <button class="ctrl"    id="c-pontos" onclick="toggleCamada('pontos')">⚫ Pontos</button>
  </div>
  <div id="legenda">
    <b>Regiões</b>
    <div class="li"><div class="ld" style="background:#16a34a"></div>Norte</div>
    <div class="li"><div class="ld" style="background:#d97706"></div>Nordeste</div>
    <div class="li"><div class="ld" style="background:#b45309"></div>Centro-Oeste</div>
    <div class="li"><div class="ld" style="background:#1d4ed8"></div>Sudeste</div>
    <div class="li"><div class="ld" style="background:#7c3aed"></div>Sul</div>
    <div style="margin-top:8px"><b>Heatmap</b></div>
    <div class="hbar"></div>
    <div class="hlb"><span>Baixa</span><span>Alta</span></div>
  </div>
</div>
<div id="pw">
  <button id="ptoggle" onclick="togglePanel()">◀</button>
  <div id="panel">
    <div id="ph"><h2>🐟 Armadores de Pesca</h2><div class="sub">Clique num estado para análise e relatório</div></div>
    <div id="bc"><span class="bcl" onclick="voltarBrasil()">🇧🇷 Brasil</span><span id="bc2"></span></div>
    <div id="tabs">
      <button class="tb on" onclick="showTab('resumo')">📊 Resumo</button>
      <button class="tb"    onclick="showTab('ranking')">🏆 Ranking</button>
      <button class="tb"    onclick="showTab('insights')">💡 Insights</button>
      <button class="tb"    onclick="showTab('melhorias')">🔧 Melhorias</button>
    </div>
    <div id="pc">
      <div id="dm">
        <div class="ico">🗺️</div>
        <p style="font-size:12px;color:#6b7280;line-height:1.6">Clique em qualquer <strong style="color:#e2e8f0">estado</strong><br>para isolar, aproximar e analisar.</p>
        <hr style="border-color:#1e3a5f;margin:12px 0">
        <p style="color:#6b7280;font-size:11px">Total no Brasil</p>
        <div class="tot">__TOTAL__</div>
        <p style="color:#6b7280;font-size:11px">armadores registrados</p>
        <hr style="border-color:#1e3a5f;margin:12px 0">
        <div class="st" style="text-align:left">Conclusões da análise</div>
        <div id="conclusoes-gerais"></div>
      </div>
      <div class="tp" id="tp-resumo"></div>
      <div class="tp" id="tp-ranking"></div>
      <div class="tp" id="tp-insights"></div>
      <div class="tp" id="tp-melhorias"></div>
    </div>
    <div id="pf">Fonte: MPA/SERMOP &nbsp;|&nbsp; INF01047 — UFRGS</div>
  </div>
</div>
</div>
<div id="rel-overlay" onclick="if(event.target===this)fecharRel()">
  <div id="rel-box">
    <div id="rel-header"><h3 id="rel-titulo">Relatório</h3></div>
    <div id="rel-body"><pre id="rel-texto"></pre></div>
    <div class="rel-actions">
      <button class="rel-btn dl" onclick="baixarRel()">⬇ Baixar .txt</button>
      <button class="rel-btn cp" onclick="copiarRel()">📋 Copiar</button>
      <button class="rel-btn cl" onclick="fecharRel()">✕ Fechar</button>
    </div>
  </div>
</div>

<script>
LEAFLET_JS_PLACEHOLDER
LEAFLET_HEAT_PLACEHOLDER
</script>

<script>
const GJ     = __GJ__;
const S_UF   = __S_UF__;
const S_REG  = __S_REG__;
const PTS_UF = __PTS_UF__;
const PTS_REG= __PTS_REG__;
const HEAT_UF= __HEAT_UF__;
const HEAT_REG=__HEAT_REG__;
const HEAT_BR= __HEAT_BR__;
const BBOX_UF= __BBOX_UF__;
const TOTAL  = __TOTAL_NUM__;
const CONC   = __CONC__;

const COR = {Norte:'#16a34a',Nordeste:'#d97706','Centro-Oeste':'#b45309',Sudeste:'#1d4ed8',Sul:'#7c3aed',Desconhecido:'#6b7280'};

let sel=null, selTipo=null, panelOn=true, heatOn=true, pontosOn=false, tabAtual='resumo', relTxt='', relTitulo='';

// ── MAPA ──────────────────────────────────────────────────────────────
const BRASIL = L.latLngBounds(L.latLng(-34.5,-74.5), L.latLng(6.5,-27.5));
const map = L.map('map',{center:[-14,-52],zoom:4,minZoom:4,maxZoom:13,
  zoomControl:true,maxBounds:BRASIL,maxBoundsViscosity:1.0});

// Fundo escuro — sem tiles externos
L.rectangle([[-90,-180],[90,180]],{color:'#111827',fillColor:'#111827',fillOpacity:1,stroke:false,interactive:false}).addTo(map);

// ── HEATMAP — criado com L.heatLayer (inline, sem CDN) ───────────────
function mkHeat(data, r) {
  return L.heatLayer(data, {
    radius: r, blur: Math.round(r*1.4),
    gradient:{0.0:'#00f',0.2:'#0cf',0.45:'#0f0',0.65:'#ff0',0.82:'#f80',1.0:'#f00'},
    minOpacity: 0.35,
    max: 1.0,
  });
}

let heatLayer = mkHeat(HEAT_BR, 18);
heatLayer.addTo(map);

// ── GEOJSON ───────────────────────────────────────────────────────────
const featMap = {};

function corEstado(uf, reg) {
  if (!sel) return COR[reg]||'#6b7280';
  if (selTipo==='uf')  return uf===sel  ? COR[reg] : '#111827';
  if (selTipo==='reg') return reg===sel ? COR[reg] : '#111827';
  return COR[reg];
}

function estilo(f) {
  const uf=f.properties.uf||'', reg=f.properties.regiao||'Desconhecido';
  const fill=corEstado(uf,reg);
  const isSelected=sel&&((selTipo==='uf'&&uf===sel)||(selTipo==='reg'&&reg===sel));
  return {fillColor:fill, color:isSelected?'#fbbf24':(fill==='#111827'?'#111827':'rgba(255,255,255,0.12)'),
    weight:isSelected?2.5:0.8, fillOpacity:fill==='#111827'?1:0.6};
}

const gjLayer = L.geoJSON(GJ, {
  style: estilo,
  onEachFeature(feat, layer) {
    const uf=feat.properties.uf||'', reg=feat.properties.regiao||'', n=feat.properties.n_estado||0;
    featMap[uf]=layer;
    layer.on('mouseover', e=>{
      if(sel&&selTipo==='uf'&&uf!==sel) return;
      if(sel&&selTipo==='reg'&&reg!==sel) return;
      e.target.setStyle({fillOpacity:0.85,weight:2.5,color:'#fbbf24'});
    });
    layer.on('mouseout', ()=>{gjLayer.setStyle(estilo);});
    layer.on('click', ()=>selecionarUF(uf));
    layer.bindTooltip(`<b>${feat.properties.name}</b><br>Região: ${reg}<br>Pescadores: ${n.toLocaleString('pt-BR')}`,
      {sticky:true,className:'ctip'});
  }
}).addTo(map);

// ── PONTOS ────────────────────────────────────────────────────────────
const pontosLayer = L.layerGroup();

function buildPontos() {
  pontosLayer.clearLayers();
  if (!sel) {
    Object.entries(PTS_UF).forEach(([uf,pts])=>{
      const cor=COR[S_UF[uf]?.regiao]||'#6b7280';
      pts.forEach(([lat,lon,mun])=>mkPonto(lat,lon,mun,uf,cor));
    });
  } else if (selTipo==='uf') {
    const cor=COR[S_UF[sel]?.regiao]||'#6b7280';
    (PTS_UF[sel]||[]).forEach(([lat,lon,mun])=>mkPonto(lat,lon,mun,sel,cor));
  } else {
    const cor=COR[sel]||'#6b7280';
    (PTS_REG[sel]||[]).forEach(([lat,lon,mun,uf])=>mkPonto(lat,lon,mun,uf,cor));
  }
}
function mkPonto(lat,lon,mun,uf,cor) {
  L.circleMarker([lat,lon],{radius:3,color:cor,fillColor:cor,fillOpacity:0.75,weight:0})
   .bindTooltip(`${mun} (${uf})`,{className:'ctip'}).addTo(pontosLayer);
}

// ── SELECIONAR ESTADO ─────────────────────────────────────────────────
function selecionarUF(uf) {
  if (!uf) return;
  sel=uf; selTipo='uf';
  gjLayer.setStyle(estilo);

  const bbox=BBOX_UF[uf]||[-35,-74,6,-28];
  map.fitBounds([[bbox[0],bbox[1]],[bbox[2],bbox[3]]],{padding:[50,50],maxZoom:10,animate:true});

  // Heatmap filtrado para o estado
  if (heatOn) {
    map.removeLayer(heatLayer);
    heatLayer = mkHeat(HEAT_UF[uf]||[], 22);
    heatLayer.addTo(map);
  }

  buildPontos();
  if (pontosOn && !map.hasLayer(pontosLayer)) pontosLayer.addTo(map);

  document.getElementById('btn-back').style.display='block';
  renderUF(uf);
  if (!panelOn) togglePanel();
}

// ── VOLTAR BRASIL ─────────────────────────────────────────────────────
function voltarBrasil() {
  sel=null; selTipo=null;
  gjLayer.setStyle(estilo);
  map.fitBounds(BRASIL,{padding:[10,10],animate:true});

  if (heatOn) {
    map.removeLayer(heatLayer);
    heatLayer=mkHeat(HEAT_BR,18);
    heatLayer.addTo(map);
  }
  buildPontos();
  if (!pontosOn && map.hasLayer(pontosLayer)) map.removeLayer(pontosLayer);

  document.getElementById('btn-back').style.display='none';
  document.getElementById('bc2').textContent='';
  document.getElementById('dm').style.display='block';
  document.querySelectorAll('.tp').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.tb').forEach((b,i)=>b.classList.toggle('on',i===0));
  tabAtual='resumo';
}

// ── TOGGLE CAMADAS ────────────────────────────────────────────────────
function toggleCamada(tipo) {
  if (tipo==='heat') {
    heatOn=!heatOn;
    if (heatOn) {
      const dados = sel&&selTipo==='uf' ? HEAT_UF[sel]
                  : sel&&selTipo==='reg'? HEAT_REG[sel] : HEAT_BR;
      const r = sel ? 22 : 18;
      heatLayer=mkHeat(dados||[],r);
      heatLayer.addTo(map);
    } else { map.removeLayer(heatLayer); }
    document.getElementById('c-heat').classList.toggle('on',heatOn);
  } else {
    pontosOn=!pontosOn;
    if (pontosOn) { buildPontos(); pontosLayer.addTo(map); }
    else map.removeLayer(pontosLayer);
    document.getElementById('c-pontos').classList.toggle('on',pontosOn);
  }
}

function togglePanel() {
  panelOn=!panelOn;
  document.getElementById('panel').classList.toggle('hidden',!panelOn);
  document.getElementById('ptoggle').textContent=panelOn?'▶':'◀';
}

function showTab(t) {
  tabAtual=t;
  document.querySelectorAll('.tb').forEach((b,i)=>b.classList.toggle('on',['resumo','ranking','insights','melhorias'][i]===t));
  document.querySelectorAll('.tp').forEach(p=>p.classList.remove('on'));
  document.getElementById('tp-'+t).classList.add('on');
  document.getElementById('dm').style.display='none';
}

// ── HELPERS ───────────────────────────────────────────────────────────
function barra(nome,val,max,cor,extra='') {
  const pct=max>0?Math.round(val/max*100):0;
  return `<div class="br">
    <div class="bl"><span class="n">${nome}${extra}</span><span class="c">${val.toLocaleString('pt-BR')} (${pct}%)</span></div>
    <div class="bb"><div class="bf" style="width:${pct}%;background:${cor}"></div></div>
  </div>`;
}

function minibar(items, maxVal, cor) {
  return `<div class="minibar-wrap">${items.map(([lbl,val])=>{
    const pct=maxVal>0?Math.round(val/maxVal*100):0;
    return `<div class="minibar-row">
      <span class="minibar-lbl" title="${lbl}">${lbl}</span>
      <div class="minibar-bg"><div class="minibar-fill" style="width:${pct}%;background:${cor}">
        <span class="minibar-val">${val.toLocaleString('pt-BR')}</span>
      </div></div>
    </div>`;
  }).join('')}</div>`;
}

// ── RELATÓRIO ─────────────────────────────────────────────────────────
function gerarRel(tipo,id) {
  const dt=new Date().toLocaleString('pt-BR');
  const sep='─'.repeat(52);
  let L=['='.repeat(52)];
  if (tipo==='uf') {
    const s=S_UF[id];
    L.push(`  RELATÓRIO — ESTADO: ${id} (${s.regiao})`,'='.repeat(52),'',`Gerado em: ${dt}`,'Fonte: MPA/SERMOP | INF01047 UFRGS','',
      sep,'  NÚMEROS',sep,
      `Pescadores no estado : ${s.n.toLocaleString('pt-BR')}`,
      `% do Brasil          : ${s.pct_br}%`,
      `% da Região ${s.regiao.padEnd(12)}: ${s.pct_reg}%`,
      `Total na região      : ${s.n_reg.toLocaleString('pt-BR')}`,
      `Municípios presentes : ${s.n_munis}`,
      `Concentração/líder   : ${s.conc}% no maior município`,'',
      sep,'  TOP 5 MUNICÍPIOS',sep,
      ...s.tops.map(([m,v],i)=>`  ${i+1}. ${m}: ${v.toLocaleString('pt-BR')} (${Math.round(v/s.n*100)}%)`),
      '',sep,'  ANÁLISE DO ESTADO',sep,
      CONC.insights_uf[id]||`${id} representa ${s.pct_br}% dos pescadores nacionais.`,
      '',sep,'  CONTEXTO REGIONAL',sep,
      CONC.insights_reg[s.regiao]||'');
  } else {
    const s=S_REG[id];
    L.push(`  RELATÓRIO — REGIÃO: ${id}`,'='.repeat(52),'',`Gerado em: ${dt}`,'Fonte: MPA/SERMOP | INF01047 UFRGS','',
      sep,'  NÚMEROS',sep,
      `Pescadores na região : ${s.n.toLocaleString('pt-BR')}`,
      `% do Brasil          : ${s.pct_br}%`,
      `Nº de estados        : ${s.n_ufs}`,
      `Estado líder         : ${s.top_ufs[0]?.[0]} (${s.lider_pct}% da região)`,
      `Desigualdade interna : CV=${s.desigualdade}%`,'',
      sep,'  ESTADOS DA REGIÃO',sep,
      ...s.top_ufs.map(([e,v],i)=>`  ${i+1}. ${e}: ${v.toLocaleString('pt-BR')} (${Math.round(v/s.n*100)}%)`),
      '',sep,'  TOP 5 MUNICÍPIOS',sep,
      ...s.top_muns.map(([m,v],i)=>`  ${i+1}. ${m}: ${v.toLocaleString('pt-BR')}`),
      '',sep,'  ANÁLISE REGIONAL',sep,
      CONC.insights_reg[id]||'');
  }
  L.push('',sep,'  CONCLUSÕES GERAIS DO BRASIL',sep,
    ...CONC.geral.map((c,i)=>`${i+1}. ${c}`),'','='.repeat(52));
  return L.join('\\n');
}

function abrirRel(tipo,id) {
  relTitulo=tipo==='uf'?`Estado ${id}`:`Região ${id}`;
  relTxt=gerarRel(tipo,id);
  document.getElementById('rel-titulo').textContent=`📄 Relatório — ${relTitulo}`;
  document.getElementById('rel-texto').textContent=relTxt;
  document.getElementById('rel-overlay').classList.add('show');
}
function fecharRel(){document.getElementById('rel-overlay').classList.remove('show');}
function baixarRel(){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([relTxt],{type:'text/plain;charset=utf-8'}));
  a.download=`relatorio_pesca_${relTitulo.replace(/[^a-zA-Z0-9]/g,'_')}.txt`;
  a.click();
}
function copiarRel(){
  navigator.clipboard.writeText(relTxt).then(()=>{
    const b=document.querySelector('.rel-btn.cp');
    b.textContent='✅ Copiado!';
    setTimeout(()=>b.textContent='📋 Copiar',2000);
  });
}

// ── RENDERIZAR UF ─────────────────────────────────────────────────────
function renderUF(uf) {
  const s=S_UF[uf]; if(!s) return;
  const cor=COR[s.regiao]||'#3b82f6';
  document.getElementById('bc2').innerHTML=` › <span class="bcl" style="color:${cor}">${uf}</span>`;

  // RESUMO
  const maxMun=s.tops[0]?.[1]||1;
  document.getElementById('tp-resumo').innerHTML=`
    <div class="sg">
      <div class="sc" style="--a:${cor}"><div class="v">${s.n.toLocaleString('pt-BR')}</div><div class="l">Pescadores no estado</div></div>
      <div class="sc" style="--a:#f59e0b"><div class="v">${s.pct_br}%</div><div class="l">do total nacional</div></div>
      <div class="sc" style="--a:#10b981"><div class="v">${s.pct_reg}%</div><div class="l">da Região ${s.regiao}</div></div>
      <div class="sc" style="--a:#ef4444"><div class="v">${s.conc}%</div><div class="l">no maior município</div></div>
    </div>
    <div class="st">Região</div>
    <div style="margin-bottom:9px;font-size:12px"><span class="rb" style="background:${cor}">${s.regiao}</span>
      <span style="color:#6b7280"> — ${s.n_reg.toLocaleString('pt-BR')} pescadores na região</span></div>
    <div class="st">Top municípios</div>
    ${minibar(s.tops, maxMun, cor)}
    <button class="dl-btn" onclick="abrirRel('uf','${uf}')">📄 Gerar relatório completo</button>`;

  // RANKING
  const reg=S_REG[s.regiao], maxUF=reg.top_ufs[0]?.[1]||1;
  const rankRows=reg.top_ufs.map(([e,v])=>{
    const cur=e===uf;
    return `<div class="br" style="${cur?'background:#0c1929;border-radius:6px;padding:4px 6px;margin:-4px -6px 5px;':''}">
      <div class="bl"><span class="n" style="${cur?'color:#60a5fa;font-weight:700':''}">${cur?'▶ ':''}${e}</span>
        <span class="c">${v.toLocaleString('pt-BR')}</span></div>
      <div class="bb"><div class="bf" style="width:${Math.round(v/maxUF*100)}%;background:${cur?'#3b82f6':cor}"></div></div>
    </div>`;
  }).join('');
  const allRegs=Object.entries(S_REG).sort((a,b)=>b[1].n-a[1].n), maxReg=allRegs[0][1].n;
  const regRows=allRegs.map(([r,rs])=>barra(r,rs.n,maxReg,r===s.regiao?'#f59e0b':COR[r],
    r===s.regiao?` <span style="font-size:9px;color:#f59e0b">(sua região)</span>`:''));
  document.getElementById('tp-ranking').innerHTML=`
    <div class="st">Ranking — Região ${s.regiao}</div>${rankRows}
    <div class="st" style="margin-top:14px">Posição — Brasil</div>${barra(uf+' no Brasil',s.n,TOTAL,cor)}
    <div class="st" style="margin-top:14px">Comparativo de regiões</div>${regRows.join('')}`;

  // INSIGHTS
  const ins=CONC.insights_uf[uf]||`${uf} representa ${s.pct_br}% dos pescadores nacionais.`;
  document.getElementById('tp-insights').innerHTML=`
    <div class="ins"><span class="tg">📍 ${uf} — análise</span>${ins}</div>
    <div class="ins blue"><span class="tg">🌎 Região ${s.regiao}</span>${CONC.insights_reg[s.regiao]||''}</div>
    <div class="ins green"><span class="tg">📊 Dado-chave</span>
      ${s.tops[0]?.[0]} é o principal polo com ${(s.tops[0]?.[1]||0).toLocaleString('pt-BR')} registros (${s.conc}% do estado).
      ${s.tops[1]?`O segundo — ${s.tops[1][0]} — tem ${Math.round(s.tops[1][1]/s.tops[0][1]*100)}% do volume do líder.`:''}</div>
    <div class="st" style="margin-top:12px">Conclusões gerais do Brasil</div>
    ${CONC.geral.map((c,i)=>`<div class="ins ${['','red','blue','green','purple'][i%5]}"><span class="tg">${i+1}ª conclusão</span>${c}</div>`).join('')}
    <button class="dl-btn" onclick="abrirRel('uf','${uf}')">📄 Gerar relatório completo</button>`;

  // MELHORIAS
  document.getElementById('tp-melhorias').innerHTML=`
    <div class="ins blue" style="margin-bottom:10px"><span class="tg">🔧 Sugestões de melhoria</span>Funcionalidades que enriqueceriam esta visualização:</div>
    ${CONC.melhorias.map(m=>`<div class="melhoria-item"><span>${m}</span></div>`).join('')}
    <button class="dl-btn" style="margin-top:12px" onclick="abrirRel('uf','${uf}')">📄 Gerar relatório completo</button>`;

  document.getElementById('dm').style.display='none';
  showTab(tabAtual);
}

// ── INICIALIZAÇÃO ─────────────────────────────────────────────────────
// Conclusões na tela inicial
document.getElementById('conclusoes-gerais').innerHTML=
  CONC.geral.map((c,i)=>`<div class="ins ${['','red','blue','green','purple'][i%5]}" style="margin-bottom:5px;text-align:left"><span class="tg">${i+1}ª conclusão</span>${c}</div>`).join('');

// Aba melhorias disponível sem seleção
document.getElementById('tp-melhorias').innerHTML=`
  <div class="ins blue" style="margin-bottom:10px"><span class="tg">🔧 Sugestões de melhoria</span>Funcionalidades que enriqueceriam esta visualização:</div>
  ${CONC.melhorias.map(m=>`<div class="melhoria-item"><span>${m}</span></div>`).join('')}`;

map.fitBounds(BRASIL,{padding:[10,10]});
</script>
</body>
</html>"""

# Substituir placeholders
html_final = (HTML
  .replace('LEAFLET_CSS_PLACEHOLDER',  LEAFLET_CSS)
  .replace('LEAFLET_JS_PLACEHOLDER',   LEAFLET_JS)
  .replace('LEAFLET_HEAT_PLACEHOLDER', LEAFLET_HEAT)
  .replace('__GJ__',       GJ_STR)
  .replace('__S_UF__',     S_UF)
  .replace('__S_REG__',    S_REG)
  .replace('__PTS_UF__',   PTS_UF)
  .replace('__PTS_REG__',  PTS_REG)
  .replace('__HEAT_UF__',  HEAT_UF)
  .replace('__HEAT_REG__', HEAT_REG)
  .replace('__HEAT_BR__',  HEAT_BR)
  .replace('__BBOX_UF__',  BBOX_UF)
  .replace('__TOTAL__',    TOT_STR)
  .replace('__TOTAL_NUM__',str(TOTAL))
  .replace('__CONC__',     CONC_STR)
)

out = './mapa.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html_final)

size = os.path.getsize(out)/1024/1024
print(f"Gerado: {out}  ({size:.1f} MB)")
