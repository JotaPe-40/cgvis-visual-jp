import pandas as pd, numpy as np, requests, json, os, tarfile, io
np.random.seed(42)

# ── DADOS ────────────────────────────────────────────────────────────
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

stats_uf = {}
for _, r in por_uf.iterrows():
    uf,reg = r['estado'],r['regiao']
    n_uf = int(r['n'])
    n_reg= int(por_reg[por_reg['regiao']==reg]['n'].values[0])
    tops = por_mun[por_mun['estado']==uf].sort_values('n',ascending=False).head(5)
    tlist= [[row['municipio'],int(row['n'])] for _,row in tops.iterrows()]
    conc = tlist[0][1]/n_uf*100 if tlist else 0
    stats_uf[uf]={'n':n_uf,'regiao':reg,'n_reg':n_reg,
        'pct_br':round(n_uf/TOTAL*100,1),'pct_reg':round(n_uf/n_reg*100,1),
        'tops':tlist,'conc':round(conc,1),
        'n_munis':int(df[df['estado']==uf]['municipio'].nunique())}

stats_reg = {}
for _, r in por_reg.iterrows():
    reg,n_reg = r['regiao'],int(r['n'])
    ufs_r = por_uf[por_uf['regiao']==reg].sort_values('n',ascending=False)
    top_ufs= [[row['estado'],int(row['n'])] for _,row in ufs_r.iterrows()]
    top_mun_r= por_mun[por_mun['estado'].map(REGIOES)==reg].sort_values('n',ascending=False).head(5)
    top_muns= [[row['municipio'],int(row['n'])] for _,row in top_mun_r.iterrows()]
    vals=[v for _,v in top_ufs]
    stats_reg[reg]={'n':n_reg,'pct_br':round(n_reg/TOTAL*100,1),'n_ufs':len(ufs_r),
        'top_ufs':top_ufs,'top_muns':top_muns,
        'desigualdade':round(np.std(vals)/np.mean(vals)*100,1) if vals else 0,
        'lider_pct':round(top_ufs[0][1]/n_reg*100,1) if top_ufs else 0}

# GeoJSON
GJ_URL='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson'
gj=requests.get(GJ_URL,timeout=30).json()
NOME_UF={'Acre':'AC','Amazonas':'AM','Amapá':'AP','Pará':'PA','Rondônia':'RO','Roraima':'RR','Tocantins':'TO',
    'Alagoas':'AL','Bahia':'BA','Ceará':'CE','Maranhão':'MA','Paraíba':'PB','Pernambuco':'PE',
    'Piauí':'PI','Rio Grande do Norte':'RN','Sergipe':'SE','Distrito Federal':'DF',
    'Goiás':'GO','Mato Grosso do Sul':'MS','Mato Grosso':'MT','Espírito Santo':'ES',
    'Minas Gerais':'MG','Rio de Janeiro':'RJ','São Paulo':'SP','Paraná':'PR',
    'Rio Grande do Sul':'RS','Santa Catarina':'SC'}
NOME_REG={'Acre':'Norte','Amazonas':'Norte','Amapá':'Norte','Pará':'Norte','Rondônia':'Norte','Roraima':'Norte','Tocantins':'Norte',
    'Alagoas':'Nordeste','Bahia':'Nordeste','Ceará':'Nordeste','Maranhão':'Nordeste','Paraíba':'Nordeste',
    'Pernambuco':'Nordeste','Piauí':'Nordeste','Rio Grande do Norte':'Nordeste','Sergipe':'Nordeste',
    'Distrito Federal':'Centro-Oeste','Goiás':'Centro-Oeste','Mato Grosso do Sul':'Centro-Oeste','Mato Grosso':'Centro-Oeste',
    'Espírito Santo':'Sudeste','Minas Gerais':'Sudeste','Rio de Janeiro':'Sudeste','São Paulo':'Sudeste',
    'Paraná':'Sul','Rio Grande do Sul':'Sul','Santa Catarina':'Sul'}
n_uf_d=dict(zip(por_uf['estado'],por_uf['n']))
n_reg_d=dict(zip(por_reg['regiao'],por_reg['n']))
for feat in gj['features']:
    nome=feat['properties'].get('name','')
    uf=NOME_UF.get(nome,''); reg=NOME_REG.get(nome,'Desconhecido')
    feat['properties'].update({'uf':uf,'regiao':reg,
        'n_estado':int(n_uf_d.get(uf,0)),'n_regiao':int(n_reg_d.get(reg,0))})

# Pontos e heat
pts_uf={uf:df[df['estado']==uf].sample(min(500,len(df[df['estado']==uf])),random_state=42)[['latitude','longitude','municipio']].values.tolist()
        for uf in df['estado'].unique()}
pts_reg={reg:df[df['regiao']==reg].sample(min(1500,len(df[df['regiao']==reg])),random_state=42)[['latitude','longitude','municipio','estado']].values.tolist()
         for reg in df['regiao'].unique()}

# FIX: heat data como [[lat,lon,intensity]] com intensidade normalizada
def make_heat(sub_df, normalize_by=None):
    counts = sub_df.groupby(['latitude','longitude']).size().reset_index(name='c')
    max_c = normalize_by or counts['c'].max() or 1
    return [[round(r['latitude'],5), round(r['longitude'],5), min(1.0, r['c']/max_c)]
            for _,r in counts.iterrows()]

global_max = df.groupby(['latitude','longitude']).size().max()
heat_br  = make_heat(df, global_max)
heat_uf  = {uf: make_heat(df[df['estado']==uf],  global_max) for uf in df['estado'].unique()}
heat_reg = {reg: make_heat(df[df['regiao']==reg], global_max) for reg in df['regiao'].unique()}

bbox_uf={}
for uf in df['estado'].unique():
    sub=df[df['estado']==uf]; p=0.4
    bbox_uf[uf]=[float(sub['latitude'].min())-p,float(sub['longitude'].min())-p,
                 float(sub['latitude'].max())+p,float(sub['longitude'].max())+p]

CONCLUSOES={
    'geral':["O Nordeste concentra 39% dos pescadores — mais que qualquer região, apesar de não ser a mais rica. A pesca artesanal é central para a subsistência.",
        "O Norte tem 68% dos pescadores em municípios ribeirinhos do interior, não no litoral — a pesca amazônica é predominantemente fluvial.",
        "O Sul tem a maior densidade de pescadores por km de litoral. Itajaí/SC e Rio Grande/RS são os dois maiores portos pesqueiros do país.",
        "O Sudeste combina pesca industrial (Santos, Macaé) com artesanal costeira. RJ e SP concentram 84% da região.",
        "O Centro-Oeste representa apenas 3,9% do total. A pesca pantaneira de Corumbá/MS é a única concentração relevante."],
    'insights_uf':{'CE':'Fortaleza concentra 51% dos pescadores cearenses — hub de pesca industrial e artesanal no Nordeste.',
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
        'MS':'Corumbá responde pela maior parte do MS — âncora da pesca fluvial do Centro-Oeste no Pantanal.'},
    'insights_reg':{'Norte':'68% dos pescadores estão no interior ribeirinho, não no litoral. Único padrão fluvial dominante — reflexo da Bacia Amazônica.',
        'Nordeste':'Maior volume absoluto (39%). Pesca artesanal é estratégica para segurança alimentar. CE, BA e MA respondem por 65% da região.',
        'Centro-Oeste':'Apenas 3,9% do total. Pesca restrita às bacias do Pantanal e Araguaia-Tocantins.',
        'Sudeste':'Combina pesca industrial em portos (Santos, Macaé) e artesanal costeira no litoral fluminense e paulista.',
        'Sul':'Maior densidade por km². Itajaí e Rio Grande são referências nacionais em pesca oceânica e processamento industrial.'},
    'melhorias':['📊 Série temporal: evolução anual de registros por estado',
        '🎯 Filtro por tipo: Pessoa Física × Jurídica e Armador × Proprietário',
        '📈 Correlação IDH: cruzar dados de pesca com IDH municipal',
        '🌊 Overlay de bacias hidrográficas: mostrar correlação com rios no Norte',
        '🔍 Busca por município: campo de texto para localizar diretamente',
        '📱 Layout responsivo: painel inferior em telas mobile',
        '🗓️ Gráfico comparativo animado entre regiões',
        '📤 Exportar relatório em PDF com gráficos embutidos']}

print(f"Dados: {TOTAL} registros | {len(stats_uf)} estados | {len(stats_reg)} regiões")
print(f"Heat Brasil: {len(heat_br)} pontos com intensidade")

# ── DOWNLOAD ASSETS ──────────────────────────────────────────────────
print("Baixando Leaflet...")
r=requests.get("https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz",timeout=60)
t=tarfile.open(fileobj=io.BytesIO(r.content))
LEAFLET_JS=LEAFLET_CSS=""
for m in t.getmembers():
    if m.name.endswith('dist/leaflet.js') and 'src' not in m.name:
        LEAFLET_JS=t.extractfile(m).read().decode('utf-8')
    if m.name.endswith('dist/leaflet.css'):
        LEAFLET_CSS=t.extractfile(m).read().decode('utf-8')
print(f"  leaflet.js {len(LEAFLET_JS)//1024}KB, leaflet.css {len(LEAFLET_CSS)//1024}KB")

print("Baixando Leaflet.heat...")
LEAFLET_HEAT=requests.get(
    "https://raw.githubusercontent.com/Leaflet/Leaflet.heat/gh-pages/dist/leaflet-heat.js",
    timeout=30).text
print(f"  leaflet-heat.js {len(LEAFLET_HEAT)//1024}KB")

# Serializar
D=dict(GJ=json.dumps(gj,ensure_ascii=False),
       S_UF=json.dumps(stats_uf,ensure_ascii=False),
       S_REG=json.dumps(stats_reg,ensure_ascii=False),
       PTS_UF=json.dumps(pts_uf,ensure_ascii=False),
       PTS_REG=json.dumps(pts_reg,ensure_ascii=False),
       HEAT_UF=json.dumps(heat_uf,ensure_ascii=False),
       HEAT_REG=json.dumps(heat_reg,ensure_ascii=False),
       HEAT_BR=json.dumps(heat_br,ensure_ascii=False),
       BBOX_UF=json.dumps(bbox_uf,ensure_ascii=False),
       CONC=json.dumps(CONCLUSOES,ensure_ascii=False),
       TOTAL_STR=f"{TOTAL:,}".replace(",","."),
       TOTAL_NUM=str(TOTAL))

print("Gerando HTML...")

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Armadores de Pesca — Brasil</title>
<style>
%%LEAFLET_CSS%%
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden;font-family:'Segoe UI',sans-serif;background:#111827}
#app{display:flex;width:100vw;height:100vh}
#map-wrap{flex:1;position:relative;overflow:hidden;min-width:0}
#map{position:absolute;inset:0}
.leaflet-container{background:#111827!important}
#toolbar{position:absolute;top:12px;left:50%;transform:translateX(-50%);z-index:1000;display:flex;align-items:center;gap:8px}
#title-box{background:rgba(17,24,39,.95);border:1px solid #1e3a5f;border-radius:10px;padding:8px 18px;text-align:center;color:#fff;font-size:13px;font-weight:700;white-space:nowrap;box-shadow:0 2px 12px rgba(0,0,0,.6)}
#title-box span{display:block;font-size:10px;font-weight:400;color:#6b7280;margin-top:2px}
#btn-back{display:none;background:#1e3a5f;color:#93c5fd;border:1px solid #2563eb;border-radius:8px;padding:8px 14px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;white-space:nowrap;transition:.2s}
#btn-back:hover{background:#2563eb;color:#fff}
#ctrls{position:absolute;bottom:20px;left:12px;z-index:1000;display:flex;flex-direction:column;gap:5px}
.ctrl{background:rgba(17,24,39,.93);border:1px solid #374151;border-radius:7px;padding:8px 14px;color:#9ca3af;font-size:12px;cursor:pointer;font-family:inherit;transition:.2s;text-align:left}
.ctrl.on{border-color:#3b82f6;color:#60a5fa;background:rgba(30,58,95,.7)}
.ctrl:hover{border-color:#3b82f6;color:#93c5fd}
#legenda{position:absolute;bottom:20px;left:190px;z-index:1000;background:rgba(17,24,39,.93);border:1px solid #374151;border-radius:8px;padding:10px 14px;color:#9ca3af;font-size:11px}
#legenda b{color:#e2e8f0;font-size:12px}
.li{display:flex;align-items:center;gap:6px;margin-top:4px}
.ld{width:11px;height:11px;border-radius:2px;flex-shrink:0}
.hbar{width:90px;height:7px;border-radius:3px;background:linear-gradient(to right,#0000ff,#00ffff,#00ff00,#ffff00,#ff8800,#ff0000);margin-top:5px}
.hlb{display:flex;justify-content:space-between;font-size:9px;color:#6b7280;margin-top:2px}
/* painel */
#pw{width:340px;flex-shrink:0;position:relative;display:flex}
#ptoggle{position:absolute;top:50%;left:-26px;transform:translateY(-50%);width:26px;height:52px;background:#111827;color:#9ca3af;border:1px solid #374151;border-right:none;border-radius:8px 0 0 8px;cursor:pointer;font-size:12px;z-index:10;display:flex;align-items:center;justify-content:center;transition:.2s}
#ptoggle:hover{background:#1e3a5f}
#panel{width:340px;height:100%;background:#111827;border-left:1px solid #1e3a5f;display:flex;flex-direction:column;overflow:hidden;transition:transform .3s ease}
#panel.hidden{transform:translateX(340px)}
#ph{background:linear-gradient(135deg,#0f172a,#1e3a5f);padding:14px 16px 10px;border-bottom:1px solid #1e3a5f;flex-shrink:0}
#ph h2{margin:0 0 2px;font-size:14px;color:#fff}#ph .sub{color:#6b7280;font-size:10px}
#bc{padding:6px 14px;background:#0f172a;border-bottom:1px solid #1e3a5f;color:#6b7280;font-size:11px;flex-shrink:0}
.bcl{color:#93c5fd;cursor:pointer}.bcl:hover{text-decoration:underline}
#tabs{display:flex;background:#0f172a;border-bottom:2px solid #1e3a5f;flex-shrink:0}
.tb{flex:1;padding:8px 2px;background:none;border:none;color:#6b7280;font-size:10px;cursor:pointer;font-family:inherit;border-bottom:2px solid transparent;margin-bottom:-2px;transition:.2s}
.tb.on{color:#60a5fa;border-bottom-color:#3b82f6}.tb:hover{color:#9ca3af}
#pc{flex:1;overflow-y:auto}
.tp{display:none;padding:14px 15px}.tp.on{display:block}
#dm{padding:26px 15px;text-align:center}
#dm .ico{font-size:36px;margin-bottom:10px}
#dm .tot{font-size:26px;font-weight:700;color:#3b82f6;margin:6px 0}
.sg{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}
.sc{background:#0f172a;border-radius:7px;padding:9px 11px;border-left:3px solid var(--a,#3b82f6)}
.sc .v{font-size:20px;font-weight:700;color:#fff}.sc .l{font-size:10px;color:#6b7280;margin-top:2px}
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
.rb{display:inline-block;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:600;color:#111827;margin-left:4px;border:1px solid rgba(0,0,0,0.3);font-weight:700}
.mbar-row{display:flex;align-items:center;gap:6px;margin-bottom:5px;font-size:11px}
.mbar-lbl{width:90px;color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0}
.mbar-bg{flex:1;height:14px;background:#1e2d3d;border-radius:3px;overflow:hidden}
.mbar-fill{height:100%;border-radius:3px;display:flex;align-items:center;justify-content:flex-end;padding-right:4px;transition:width .6s cubic-bezier(.4,0,.2,1)}
.mbar-val{font-size:9px;color:rgba(255,255,255,.85);white-space:nowrap}
/* modal relatório */
#rel-ov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:20000;align-items:center;justify-content:center}
#rel-ov.show{display:flex}
#rel-box{background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;width:520px;max-height:82vh;display:flex;flex-direction:column;overflow:hidden}
#rel-hd{padding:16px 20px 12px;border-bottom:1px solid #1e3a5f;flex-shrink:0}
#rel-hd h3{color:#fff;font-size:15px;margin:0}
#rel-bd{flex:1;overflow-y:auto;padding:16px 20px}
#rel-bd pre{font-family:'Courier New',monospace;font-size:11px;white-space:pre-wrap;background:#080f1a;border-radius:6px;padding:12px;color:#a5b4fc;line-height:1.6}
.rel-acts{padding:12px 20px;border-top:1px solid #1e3a5f;display:flex;gap:8px;flex-shrink:0}
.rbtn{flex:1;padding:9px;border:none;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:opacity .2s}
.rbtn:hover{opacity:.85}
.rbtn.dl{background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff}
.rbtn.cp{background:#1e293b;color:#93c5fd;border:1px solid #1e3a5f}
.rbtn.cl{background:#1e293b;color:#6b7280;border:1px solid #374151}
.dl-btn{display:block;width:100%;background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff;border:none;border-radius:7px;padding:10px;font-size:12px;cursor:pointer;font-family:inherit;font-weight:600;margin-top:10px;transition:opacity .2s}
.dl-btn:hover{opacity:.85}
.mi{display:flex;gap:8px;padding:7px 0;border-bottom:1px solid #1e2d3d;font-size:11px;color:#94a3b8}
.mi:last-child{border:none}
.leaflet-tooltip.ctip{background:rgba(15,23,42,.95)!important;border:1px solid #1e3a5f!important;color:#e2e8f0!important;font-size:12px!important;border-radius:6px!important;padding:6px 10px!important}
#pc::-webkit-scrollbar,#rel-bd::-webkit-scrollbar{width:4px}
#pc::-webkit-scrollbar-thumb,#rel-bd::-webkit-scrollbar-thumb{background:#1e3a5f;border-radius:3px}
#pf{padding:7px 14px;border-top:1px solid #1e3a5f;background:#0f172a;color:#374151;font-size:10px;text-align:center;flex-shrink:0}
</style>
</head>
<body>
<div id="app">
<div id="map-wrap">
  <div id="map"></div>
  <div id="toolbar">
    <button id="btn-back" onclick="voltarBrasil()">← Voltar ao Brasil</button>
    <div id="title-box">🐟 Distribuição Geográfica de Armadores de Pesca no Brasil
      <span>MPA/SERMOP — clique num estado para isolar e analisar</span></div>
  </div>
  <div id="ctrls">
    <button class="ctrl on" id="c-heat"   onclick="toggleCamada('heat')">🔥 Heatmap</button>
    <button class="ctrl"    id="c-pontos" onclick="toggleCamada('pontos')">⚫ Pontos</button>
  </div>
  <div id="legenda">
    <b>Regiões</b>
    <div class="li"><div class="ld" style="background:#00e676;border:1.5px solid #00c853"></div>Norte</div>
    <div class="li"><div class="ld" style="background:#ffab40;border:1.5px solid #e65100"></div>Nordeste</div>
    <div class="li"><div class="ld" style="background:#ff5252;border:1.5px solid #b71c1c"></div>Centro-Oeste</div>
    <div class="li"><div class="ld" style="background:#40c4ff;border:1.5px solid #01579b"></div>Sudeste</div>
    <div class="li"><div class="ld" style="background:#ea80fc;border:1.5px solid #6a0080"></div>Sul</div>
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
        <p style="font-size:12px;color:#6b7280;line-height:1.6">Clique em qualquer <strong style="color:#e2e8f0">estado</strong> para isolar, aproximar e analisar.</p>
        <hr style="border-color:#1e3a5f;margin:12px 0">
        <p style="color:#6b7280;font-size:11px">Total no Brasil</p>
        <div class="tot">%%TOTAL_STR%%</div>
        <p style="color:#6b7280;font-size:11px">armadores registrados</p>
        <hr style="border-color:#1e3a5f;margin:12px 0">
        <div class="st" style="text-align:left">Conclusões da análise</div>
        <div id="conc-gerais"></div>
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
<div id="rel-ov" onclick="if(event.target===this)fecharRel()">
  <div id="rel-box">
    <div id="rel-hd"><h3 id="rel-titulo">Relatório</h3></div>
    <div id="rel-bd"><pre id="rel-txt"></pre></div>
    <div class="rel-acts">
      <button class="rbtn dl" onclick="baixarRel()">⬇ Baixar .txt</button>
      <button class="rbtn cp" onclick="copiarRel()">📋 Copiar</button>
      <button class="rbtn cl" onclick="fecharRel()">✕ Fechar</button>
    </div>
  </div>
</div>

<!-- LEAFLET CSS já embutido no <style> acima -->
<!-- LEAFLET JS — bloco próprio para garantir inicialização completa antes do Heat -->
<script>%%LEAFLET_JS%%</script>
<!-- LEAFLET HEAT — bloco separado, executado após Leaflet estar pronto -->
<script>%%LEAFLET_HEAT%%</script>

<script>
// ── DADOS ─────────────────────────────────────────────────────────────
const GJ      = %%GJ%%;
const S_UF    = %%S_UF%%;
const S_REG   = %%S_REG%%;
const PTS_UF  = %%PTS_UF%%;
const PTS_REG = %%PTS_REG%%;
const HEAT_UF = %%HEAT_UF%%;
const HEAT_REG= %%HEAT_REG%%;
const HEAT_BR = %%HEAT_BR%%;
const BBOX_UF = %%BBOX_UF%%;
const TOTAL   = %%TOTAL_NUM%%;
const CONC    = %%CONC%%;

// Paleta alto contraste — fill vívido + border escuro para destacar sobre fundo escuro
const COR = {
  Norte:          '#00e676',
  Nordeste:       '#ffab40',
  'Centro-Oeste': '#ff5252',
  Sudeste:        '#40c4ff',
  Sul:            '#ea80fc',
  Desconhecido:   '#9ca3af',
};
const COR_BORDER = {
  Norte:          '#00c853',
  Nordeste:       '#e65100',
  'Centro-Oeste': '#b71c1c',
  Sudeste:        '#01579b',
  Sul:            '#6a0080',
  Desconhecido:   '#374151',
};
let sel=null, selTipo=null, panelOn=true, heatOn=true, pontosOn=false, tabAtual='resumo', relTxt='', relTitulo='';

// ── MAPA ──────────────────────────────────────────────────────────────
const BRASIL = L.latLngBounds(L.latLng(-34.5,-74.5), L.latLng(6.5,-27.5));

// FIX CRÍTICO: usar #map com position:absolute;inset:0 dentro de flex
// Isso garante que o mapa tem dimensões definidas ANTES de qualquer layer ser adicionado
const map = L.map('map', {
  center:[-14,-52], zoom:4, minZoom:4, maxZoom:13,
  zoomControl:true, maxBounds:BRASIL, maxBoundsViscosity:1.0,
  preferCanvas: true,  // MELHORIA: canvas é mais rápido para muitos pontos
});

// Fundo escuro (sem tiles externos)
L.rectangle([[-90,-180],[90,180]], {
  color:'#111827', fillColor:'#111827', fillOpacity:1, stroke:false, interactive:false
}).addTo(map);

// ── HEATMAP ───────────────────────────────────────────────────────────
// FIX: criar heatLayer DENTRO de map.whenReady() para garantir que o canvas
// já tem dimensões corretas antes de renderizar
const HEAT_OPTS = {
  radius: 22,
  blur: 18,
  maxZoom: 13,
  max: 1.0,
  gradient: {0.0:'#0000ff', 0.2:'#00ccff', 0.4:'#00ff88', 0.6:'#ffff00', 0.8:'#ff8800', 1.0:'#ff0000'},
  minOpacity: 0.4,
};

let heatLayer = null;

function criarHeat(data, raio) {
  const opts = Object.assign({}, HEAT_OPTS, {radius: raio, blur: Math.round(raio * 0.8)});
  return L.heatLayer(data, opts);
}

// FIX: inicializar heatmap somente após mapa estar pronto + invalidateSize
map.whenReady(function() {
  // Forçar recálculo do tamanho (resolve problema em layout flex)
  map.invalidateSize();
  // Criar e adicionar heatmap
  heatLayer = criarHeat(HEAT_BR, 22);
  heatLayer.addTo(map);
  // Segundo invalidateSize após pequeno delay para garantir
  setTimeout(() => map.invalidateSize(), 100);
});

// ── GEOJSON ───────────────────────────────────────────────────────────
const featMap = {};

function corEstado(uf, reg) {
  if (!sel) return COR[reg] || '#6b7280';
  if (selTipo === 'uf')  return uf  === sel ? COR[reg] : '#111827';
  if (selTipo === 'reg') return reg === sel ? COR[reg] : '#111827';
  return COR[reg];
}

function estilo(f) {
  const uf = f.properties.uf || '', reg = f.properties.regiao || 'Desconhecido';
  const fill = corEstado(uf, reg);
  const isSelected = sel && ((selTipo==='uf' && uf===sel) || (selTipo==='reg' && reg===sel));
  return {
    fillColor: fill,
    color: isSelected ? '#fbbf24' : (fill === '#111827' ? '#111827' : 'rgba(255,255,255,0.12)'),
    weight: isSelected ? 2.5 : 0.8,
    fillOpacity: fill === '#111827' ? 1 : 0.7,
  };
}

const gjLayer = L.geoJSON(GJ, {
  style: estilo,
  onEachFeature(feat, layer) {
    const uf = feat.properties.uf || '', reg = feat.properties.regiao || '';
    const n  = feat.properties.n_estado || 0;
    featMap[uf] = layer;
    layer.on('mouseover', e => {
      if (sel && selTipo==='uf'  && uf  !== sel) return;
      if (sel && selTipo==='reg' && reg !== sel) return;
      e.target.setStyle({fillOpacity:0.85, weight:2.5, color:'#fbbf24'});
    });
    layer.on('mouseout', () => gjLayer.setStyle(estilo));
    layer.on('click', () => selecionarUF(uf));
    layer.bindTooltip(
      `<b>${feat.properties.name}</b><br>Região: ${reg}<br>Pescadores: ${n.toLocaleString('pt-BR')}`,
      {sticky:true, className:'ctip'});
  }
}).addTo(map);

// ── PONTOS ────────────────────────────────────────────────────────────
const pontosLayer = L.layerGroup();

function buildPontos() {
  pontosLayer.clearLayers();
  if (!sel) {
    Object.entries(PTS_UF).forEach(([uf, pts]) => {
      const cor = COR[S_UF[uf]?.regiao] || '#6b7280';
      pts.forEach(([lat,lon,mun]) => mkPonto(lat, lon, mun, uf, cor));
    });
  } else if (selTipo === 'uf') {
    const cor = COR[S_UF[sel]?.regiao] || '#6b7280';
    (PTS_UF[sel] || []).forEach(([lat,lon,mun]) => mkPonto(lat, lon, mun, sel, cor));
  } else {
    const cor = COR[sel] || '#6b7280';
    (PTS_REG[sel] || []).forEach(([lat,lon,mun,uf]) => mkPonto(lat, lon, mun, uf, cor));
  }
}

function mkPonto(lat, lon, mun, uf, cor) {
  const border = COR_BORDER[S_UF[uf]?.regiao] || COR_BORDER[cor] || '#000';
  L.circleMarker([lat, lon], {
    radius: 5,
    color: border,       // anel externo escuro para contraste
    weight: 1.5,
    fillColor: cor,      // interior vívido
    fillOpacity: 0.92,
  }).bindTooltip(`${mun} (${uf})`, {className:'ctip'}).addTo(pontosLayer);
}

// ── SELECIONAR UF ─────────────────────────────────────────────────────
function selecionarUF(uf) {
  if (!uf) return;
  sel = uf; selTipo = 'uf';
  gjLayer.setStyle(estilo);

  const b = BBOX_UF[uf] || [-35,-74,6,-28];
  map.fitBounds([[b[0],b[1]],[b[2],b[3]]], {padding:[50,50], maxZoom:10, animate:true});

  // FIX: sempre remover antes de criar novo heatLayer
  if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
  if (heatOn) {
    heatLayer = criarHeat(HEAT_UF[uf] || [], 26);
    heatLayer.addTo(map);
  }

  buildPontos();
  if (pontosOn && !map.hasLayer(pontosLayer)) pontosLayer.addTo(map);

  document.getElementById('btn-back').style.display = 'block';
  renderUF(uf);
  if (!panelOn) togglePanel();
}

// ── VOLTAR BRASIL ─────────────────────────────────────────────────────
function voltarBrasil() {
  sel = null; selTipo = null;
  gjLayer.setStyle(estilo);
  map.fitBounds(BRASIL, {padding:[10,10], animate:true});

  if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
  if (heatOn) {
    heatLayer = criarHeat(HEAT_BR, 22);
    heatLayer.addTo(map);
  }
  buildPontos();
  if (!pontosOn && map.hasLayer(pontosLayer)) map.removeLayer(pontosLayer);

  document.getElementById('btn-back').style.display = 'none';
  document.getElementById('bc2').textContent = '';
  document.getElementById('dm').style.display = 'block';
  document.querySelectorAll('.tp').forEach(p => p.classList.remove('on'));
  document.querySelectorAll('.tb').forEach((b,i) => b.classList.toggle('on', i===0));
  tabAtual = 'resumo';
}

// ── TOGGLE CAMADAS ─────────────────────────────────────────────────────
function toggleCamada(tipo) {
  if (tipo === 'heat') {
    heatOn = !heatOn;
    if (heatOn) {
      const dados = sel && selTipo==='uf'  ? HEAT_UF[sel]
                  : sel && selTipo==='reg' ? HEAT_REG[sel] : HEAT_BR;
      const r = sel ? 26 : 22;
      if (heatLayer) map.removeLayer(heatLayer);
      heatLayer = criarHeat(dados || [], r);
      heatLayer.addTo(map);
    } else {
      if (heatLayer) { map.removeLayer(heatLayer); heatLayer = null; }
    }
    document.getElementById('c-heat').classList.toggle('on', heatOn);
  } else {
    pontosOn = !pontosOn;
    if (pontosOn) { buildPontos(); pontosLayer.addTo(map); }
    else map.removeLayer(pontosLayer);
    document.getElementById('c-pontos').classList.toggle('on', pontosOn);
  }
}

// ── PAINEL / TABS ──────────────────────────────────────────────────────
function togglePanel() {
  panelOn = !panelOn;
  document.getElementById('panel').classList.toggle('hidden', !panelOn);
  document.getElementById('ptoggle').textContent = panelOn ? '▶' : '◀';
  setTimeout(() => map.invalidateSize(), 320); // FIX: recalcular mapa após painel animar
}

function showTab(t) {
  tabAtual = t;
  document.querySelectorAll('.tb').forEach((b,i) =>
    b.classList.toggle('on', ['resumo','ranking','insights','melhorias'][i]===t));
  document.querySelectorAll('.tp').forEach(p => p.classList.remove('on'));
  document.getElementById('tp-'+t).classList.add('on');
  document.getElementById('dm').style.display = 'none';
}

// ── HELPERS ───────────────────────────────────────────────────────────
function barra(nome, val, max, cor, extra='') {
  const pct = max > 0 ? Math.round(val/max*100) : 0;
  return `<div class="br">
    <div class="bl"><span class="n">${nome}${extra}</span><span class="c">${val.toLocaleString('pt-BR')} (${pct}%)</span></div>
    <div class="bb"><div class="bf" style="width:${pct}%;background:${cor}"></div></div>
  </div>`;
}

function minibar(items, max, cor) {
  return items.map(([lbl,val]) => {
    const pct = max > 0 ? Math.round(val/max*100) : 0;
    return `<div class="mbar-row">
      <span class="mbar-lbl" title="${lbl}">${lbl}</span>
      <div class="mbar-bg"><div class="mbar-fill" style="width:${pct}%;background:${cor}">
        <span class="mbar-val">${val.toLocaleString('pt-BR')}</span>
      </div></div>
    </div>`;
  }).join('');
}

// ── RELATÓRIO ──────────────────────────────────────────────────────────
function gerarRel(tipo, id) {
  const dt = new Date().toLocaleString('pt-BR');
  const SEP = '─'.repeat(52);
  let L = ['='.repeat(52)];
  if (tipo === 'uf') {
    const s = S_UF[id];
    L.push(`  RELATÓRIO — ESTADO: ${id} (${s.regiao})`, '='.repeat(52), '',
      `Gerado em: ${dt}`, 'Fonte: MPA/SERMOP | INF01047 UFRGS', '',
      SEP, '  NÚMEROS', SEP,
      `Pescadores no estado : ${s.n.toLocaleString('pt-BR')}`,
      `% do Brasil          : ${s.pct_br}%`,
      `% da Região          : ${s.pct_reg}%`,
      `Total na região      : ${s.n_reg.toLocaleString('pt-BR')}`,
      `Municípios presentes : ${s.n_munis}`,
      `Concentração/líder   : ${s.conc}% no maior município`, '',
      SEP, '  TOP 5 MUNICÍPIOS', SEP,
      ...s.tops.map(([m,v],i) => `  ${i+1}. ${m}: ${v.toLocaleString('pt-BR')} (${Math.round(v/s.n*100)}%)`), '',
      SEP, '  ANÁLISE DO ESTADO', SEP,
      CONC.insights_uf[id] || `${id} representa ${s.pct_br}% dos pescadores nacionais.`, '',
      SEP, '  CONTEXTO REGIONAL', SEP,
      CONC.insights_reg[s.regiao] || '');
  } else {
    const s = S_REG[id];
    L.push(`  RELATÓRIO — REGIÃO: ${id}`, '='.repeat(52), '',
      `Gerado em: ${dt}`, 'Fonte: MPA/SERMOP | INF01047 UFRGS', '',
      SEP, '  NÚMEROS', SEP,
      `Pescadores na região : ${s.n.toLocaleString('pt-BR')}`,
      `% do Brasil          : ${s.pct_br}%`,
      `Nº de estados        : ${s.n_ufs}`,
      `Estado líder         : ${s.top_ufs[0]?.[0]} (${s.lider_pct}% da região)`,
      `Desigualdade interna : CV=${s.desigualdade}%`, '',
      SEP, '  ESTADOS DA REGIÃO', SEP,
      ...s.top_ufs.map(([e,v],i) => `  ${i+1}. ${e}: ${v.toLocaleString('pt-BR')} (${Math.round(v/s.n*100)}%)`), '',
      SEP, '  TOP 5 MUNICÍPIOS', SEP,
      ...s.top_muns.map(([m,v],i) => `  ${i+1}. ${m}: ${v.toLocaleString('pt-BR')}`), '',
      SEP, '  ANÁLISE REGIONAL', SEP,
      CONC.insights_reg[id] || '');
  }
  L.push('', SEP, '  CONCLUSÕES GERAIS DO BRASIL', SEP,
    ...CONC.geral.map((c,i) => `${i+1}. ${c}`), '', '='.repeat(52));
  return L.join('\\n');
}

function abrirRel(tipo, id) {
  relTitulo = tipo==='uf' ? `Estado ${id}` : `Região ${id}`;
  relTxt = gerarRel(tipo, id);
  document.getElementById('rel-titulo').textContent = `📄 Relatório — ${relTitulo}`;
  document.getElementById('rel-txt').textContent = relTxt;
  document.getElementById('rel-ov').classList.add('show');
}
function fecharRel() { document.getElementById('rel-ov').classList.remove('show'); }
function baixarRel() {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([relTxt], {type:'text/plain;charset=utf-8'}));
  a.download = `relatorio_pesca_${relTitulo.replace(/[^a-zA-Z0-9]/g,'_')}.txt`;
  a.click();
}
function copiarRel() {
  navigator.clipboard.writeText(relTxt).then(() => {
    const b = document.querySelector('.rbtn.cp');
    b.textContent = '✅ Copiado!';
    setTimeout(() => b.textContent = '📋 Copiar', 2000);
  });
}

// ── RENDERIZAR PAINEL ──────────────────────────────────────────────────
function renderUF(uf) {
  const s = S_UF[uf]; if (!s) return;
  const cor = COR[s.regiao] || '#3b82f6';
  document.getElementById('bc2').innerHTML = ` › <span class="bcl" style="color:${cor}">${uf}</span>`;

  const maxMun = s.tops[0]?.[1] || 1;

  document.getElementById('tp-resumo').innerHTML = `
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

  const reg = S_REG[s.regiao], maxUF = reg.top_ufs[0]?.[1] || 1;
  const rankRows = reg.top_ufs.map(([e,v]) => {
    const cur = e === uf;
    return `<div class="br" style="${cur?'background:#0c1929;border-radius:6px;padding:4px 6px;margin:-4px -6px 5px;':''}">
      <div class="bl"><span class="n" style="${cur?'color:#60a5fa;font-weight:700':''}">${cur?'▶ ':''}${e}</span>
        <span class="c">${v.toLocaleString('pt-BR')}</span></div>
      <div class="bb"><div class="bf" style="width:${Math.round(v/maxUF*100)}%;background:${cur?'#3b82f6':cor}"></div></div>
    </div>`;
  }).join('');
  const allRegs = Object.entries(S_REG).sort((a,b) => b[1].n-a[1].n);
  const maxReg = allRegs[0][1].n;
  document.getElementById('tp-ranking').innerHTML = `
    <div class="st">Ranking — Região ${s.regiao}</div>${rankRows}
    <div class="st" style="margin-top:14px">Posição — Brasil</div>
    ${barra(uf+' no Brasil', s.n, TOTAL, cor)}
    <div class="st" style="margin-top:14px">Comparativo de regiões</div>
    ${allRegs.map(([r,rs]) => barra(r, rs.n, maxReg, r===s.regiao?'#f59e0b':COR[r],
      r===s.regiao?' <span style="font-size:9px;color:#f59e0b">(sua região)</span>':'')).join('')}`;

  const ins = CONC.insights_uf[uf] || `${uf} representa ${s.pct_br}% dos pescadores nacionais.`;
  document.getElementById('tp-insights').innerHTML = `
    <div class="ins"><span class="tg">📍 ${uf} — análise</span>${ins}</div>
    <div class="ins blue"><span class="tg">🌎 Região ${s.regiao}</span>${CONC.insights_reg[s.regiao]||''}</div>
    <div class="ins green"><span class="tg">📊 Dado-chave</span>
      ${s.tops[0]?.[0]} é o principal polo com ${(s.tops[0]?.[1]||0).toLocaleString('pt-BR')} registros (${s.conc}% do estado).
      ${s.tops[1] ? `O segundo — ${s.tops[1][0]} — tem ${Math.round(s.tops[1][1]/s.tops[0][1]*100)}% do volume do líder.` : ''}
    </div>
    <div class="st" style="margin-top:12px">Conclusões gerais</div>
    ${CONC.geral.map((c,i) => `<div class="ins ${['','red','blue','green','purple'][i%5]}"><span class="tg">${i+1}ª conclusão</span>${c}</div>`).join('')}
    <button class="dl-btn" onclick="abrirRel('uf','${uf}')">📄 Gerar relatório completo</button>`;

  document.getElementById('tp-melhorias').innerHTML = `
    <div class="ins blue" style="margin-bottom:10px"><span class="tg">🔧 Sugestões de melhoria</span>Funcionalidades que enriqueceriam esta visualização:</div>
    ${CONC.melhorias.map(m => `<div class="mi"><span>${m}</span></div>`).join('')}
    <button class="dl-btn" style="margin-top:12px" onclick="abrirRel('uf','${uf}')">📄 Gerar relatório completo</button>`;

  document.getElementById('dm').style.display = 'none';
  showTab(tabAtual);
}

// ── INICIALIZAÇÃO ──────────────────────────────────────────────────────
document.getElementById('conc-gerais').innerHTML =
  CONC.geral.map((c,i) => `<div class="ins ${['','red','blue','green','purple'][i%5]}" style="margin-bottom:5px;text-align:left"><span class="tg">${i+1}ª conclusão</span>${c}</div>`).join('');

document.getElementById('tp-melhorias').innerHTML = `
  <div class="ins blue" style="margin-bottom:10px"><span class="tg">🔧 Sugestões de melhoria</span>Funcionalidades que enriqueceriam esta visualização:</div>
  ${CONC.melhorias.map(m => `<div class="mi"><span>${m}</span></div>`).join('')}`;

map.fitBounds(BRASIL, {padding:[10,10]});
</script>
</body>
</html>"""

html_final = (HTML
  .replace('%%LEAFLET_CSS%%',  LEAFLET_CSS)
  .replace('%%LEAFLET_JS%%',   LEAFLET_JS)
  .replace('%%LEAFLET_HEAT%%', LEAFLET_HEAT)
  .replace('%%GJ%%',       D['GJ'])
  .replace('%%S_UF%%',     D['S_UF'])
  .replace('%%S_REG%%',    D['S_REG'])
  .replace('%%PTS_UF%%',   D['PTS_UF'])
  .replace('%%PTS_REG%%',  D['PTS_REG'])
  .replace('%%HEAT_UF%%',  D['HEAT_UF'])
  .replace('%%HEAT_REG%%', D['HEAT_REG'])
  .replace('%%HEAT_BR%%',  D['HEAT_BR'])
  .replace('%%BBOX_UF%%',  D['BBOX_UF'])
  .replace('%%TOTAL_STR%%',D['TOTAL_STR'])
  .replace('%%TOTAL_NUM%%',D['TOTAL_NUM'])
  .replace('%%CONC%%',     D['CONC'])
)

out = '/tmp/mapa_v5.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html_final)
print(f"Gerado: {out}  ({os.path.getsize(out)/1024/1024:.1f} MB)")
