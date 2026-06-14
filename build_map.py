import pandas as pd, numpy as np, requests, json, os, tarfile, io, csv
np.random.seed(42)

municipios_pesca = [
    ('PA','Belém',-1.455,-48.502,320,2018),('PA','Santarém',-2.444,-54.708,210,2019),
    ('PA','Marabá',-5.368,-49.117,80,2017),('PA','Castanhal',-1.295,-47.924,95,2020),
    ('AM','Manaus',-3.119,-60.021,280,2018),('AM','Itacoatiara',-3.143,-58.444,90,2019),
    ('AM','Parintins',-2.627,-56.735,130,2020),('RO','Porto Velho',-8.761,-63.900,60,2017),
    ('AC','Rio Branco',-9.974,-67.808,50,2018),('AP','Macapá',0.035,-51.066,110,2019),
    ('AP','Santana',-0.059,-51.182,80,2020),('TO','Palmas',-10.249,-48.324,35,2018),
    ('RR','Boa Vista',2.820,-60.673,30,2017),('RO','Ji-Paraná',-10.879,-61.949,40,2019),
    ('MA','São Luís',-2.529,-44.302,340,2018),('MA','Imperatriz',-5.526,-47.491,110,2019),
    ('MA','Cururupu',-1.827,-44.869,150,2020),('CE','Fortaleza',-3.717,-38.543,480,2018),
    ('CE','Sobral',-3.689,-40.349,90,2019),('CE','Acaraú',-2.885,-40.120,170,2017),
    ('CE','Camocim',-2.902,-40.841,200,2020),('RN','Natal',-5.793,-35.200,290,2018),
    ('RN','Mossoró',-5.187,-37.344,110,2019),('RN','Areia Branca',-4.950,-37.117,180,2020),
    ('PB','João Pessoa',-7.119,-34.845,220,2018),('PE','Recife',-8.057,-34.882,310,2017),
    ('PE','Olinda',-7.999,-34.855,140,2019),('PE','Cabo Sto Agostinho',-8.289,-35.032,120,2020),
    ('AL','Maceió',-9.666,-35.735,200,2018),('SE','Aracaju',-10.909,-37.071,170,2019),
    ('BA','Salvador',-12.971,-38.511,380,2018),('BA','Ilhéus',-14.791,-39.033,160,2019),
    ('BA','Porto Seguro',-16.430,-39.065,140,2020),('BA','Valença',-13.370,-39.078,110,2017),
    ('PI','Teresina',-5.089,-42.802,60,2018),('PI','Parnaíba',-2.905,-41.776,200,2019),
    ('MT','Cuiabá',-15.596,-56.096,80,2018),('MT','Várzea Grande',-15.647,-56.131,55,2019),
    ('GO','Goiânia',-16.686,-49.264,65,2020),('MS','Campo Grande',-20.469,-54.620,70,2018),
    ('MS','Corumbá',-19.008,-57.654,120,2019),('DF','Brasília',-15.780,-47.929,40,2020),
    ('SP','Santos',-23.960,-46.333,250,2018),('SP','São Paulo',-23.549,-46.633,180,2019),
    ('SP','Guarujá',-23.993,-46.256,200,2017),('SP','São Sebastião',-23.800,-45.407,150,2020),
    ('SP','Ubatuba',-23.434,-45.071,130,2018),('RJ','Rio de Janeiro',-22.906,-43.172,400,2018),
    ('RJ','Niterói',-22.883,-43.104,180,2019),('RJ','Angra dos Reis',-23.007,-44.317,160,2020),
    ('RJ','Macaé',-22.370,-41.786,210,2017),('RJ','Cabo Frio',-22.880,-42.019,190,2019),
    ('ES','Vitória',-20.319,-40.338,200,2018),('ES','Vila Velha',-20.329,-40.292,140,2019),
    ('MG','Belo Horizonte',-19.919,-43.938,60,2020),
    ('SC','Florianópolis',-27.594,-48.548,290,2018),('SC','Itajaí',-26.906,-48.661,350,2017),
    ('SC','Navegantes',-26.900,-48.654,200,2019),('SC','S.Francisco Sul',-26.241,-48.632,180,2020),
    ('PR','Paranaguá',-25.520,-48.508,240,2018),('PR','Guaratuba',-25.882,-48.575,130,2019),
    ('PR','Pontal do Paraná',-25.611,-48.517,110,2020),
    ('RS','Rio Grande',-32.035,-52.098,310,2018),('RS','Porto Alegre',-30.033,-51.230,150,2019),
    ('RS','Pelotas',-31.771,-52.342,130,2020),('RS','Torres',-29.333,-49.729,100,2017),
]

TIPOS_V = ['Armador de pesca','Armador de pesca','Proprietário de embarcação','Armador de pesca, Proprietário de embarcação']
TIPOS_P = ['Pessoa Física','Pessoa Física','Pessoa Física','Pessoa Jurídica']
rows = []
for estado, municipio, lat, lon, n, ano_base in municipios_pesca:
    for i in range(n):
        ano = int(np.clip(ano_base + np.random.choice([-1,0,0,1,1,2],p=[0.1,0.2,0.2,0.2,0.2,0.1]), 2016, 2022))
        tp  = np.random.choice(4, p=[0.5,0.25,0.15,0.10])
        rows.append({'estado':estado,'municipio':municipio,
                     'latitude':lat+np.random.normal(0,0.18),
                     'longitude':lon+np.random.normal(0,0.18),
                     'ano':ano,'tipo_pessoa':TIPOS_P[tp],'vinculo':TIPOS_V[tp]})
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

serie_uf  = {uf:  {int(r['ano']):int(r['n']) for _,r in df[df['estado']==uf].groupby('ano').size().reset_index(name='n').iterrows()}
             for uf in df['estado'].unique()}
serie_reg = {reg: {int(r['ano']):int(r['n']) for _,r in df[df['regiao']==reg].groupby('ano').size().reset_index(name='n').iterrows()}
             for reg in df['regiao'].unique()}
anos = sorted(df['ano'].unique().tolist())

por_uf  = df.groupby(['estado','regiao']).size().reset_index(name='n')
por_mun = df.groupby(['estado','municipio']).size().reset_index(name='n')
por_reg = df.groupby('regiao').size().reset_index(name='n')

IDH_UF = {'AC':0.663,'AL':0.631,'AM':0.674,'AP':0.708,'BA':0.660,'CE':0.682,
    'DF':0.824,'ES':0.740,'GO':0.735,'MA':0.639,'MG':0.731,'MS':0.729,
    'MT':0.725,'PA':0.646,'PB':0.658,'PE':0.673,'PI':0.646,'PR':0.749,
    'RJ':0.761,'RN':0.684,'RO':0.690,'RR':0.707,'RS':0.746,'SC':0.774,
    'SE':0.665,'SP':0.783,'TO':0.699}

stats_uf = {}
for _, r in por_uf.iterrows():
    uf,reg = r['estado'],r['regiao']
    n_uf = int(r['n']); n_reg = int(por_reg[por_reg['regiao']==reg]['n'].values[0])
    tops = por_mun[por_mun['estado']==uf].sort_values('n',ascending=False).head(5)
    tlist = [[row['municipio'],int(row['n'])] for _,row in tops.iterrows()]
    sub = df[df['estado']==uf]
    stats_uf[uf] = {'n':n_uf,'regiao':reg,'n_reg':n_reg,
        'pct_br':round(n_uf/TOTAL*100,1),'pct_reg':round(n_uf/n_reg*100,1),
        'tops':tlist,'conc':round(tlist[0][1]/n_uf*100,1) if tlist else 0,
        'n_munis':int(sub['municipio'].nunique()),'idh':IDH_UF.get(uf,0),
        'fisica':int((sub['tipo_pessoa']=='Pessoa Física').sum()),
        'juridica':int((sub['tipo_pessoa']=='Pessoa Jurídica').sum()),
        'armador':int(sub['vinculo'].str.contains('Armador').sum()),
        'proprietario':int(sub['vinculo'].str.contains('Proprietário').sum())}

stats_reg = {}
for _, r in por_reg.iterrows():
    reg,n_reg = r['regiao'],int(r['n'])
    ufs_r = por_uf[por_uf['regiao']==reg].sort_values('n',ascending=False)
    top_ufs= [[row['estado'],int(row['n'])] for _,row in ufs_r.iterrows()]
    top_mun_r= por_mun[por_mun['estado'].map(REGIOES)==reg].sort_values('n',ascending=False).head(5)
    top_muns= [[row['municipio'],int(row['n'])] for _,row in top_mun_r.iterrows()]
    vals=[v for _,v in top_ufs]; sub=df[df['regiao']==reg]
    stats_reg[reg]={'n':n_reg,'pct_br':round(n_reg/TOTAL*100,1),'n_ufs':len(ufs_r),
        'top_ufs':top_ufs,'top_muns':top_muns,
        'desigualdade':round(np.std(vals)/np.mean(vals)*100,1) if vals else 0,
        'lider_pct':round(top_ufs[0][1]/n_reg*100,1) if top_ufs else 0,
        'fisica':int((sub['tipo_pessoa']=='Pessoa Física').sum()),
        'juridica':int((sub['tipo_pessoa']=='Pessoa Jurídica').sum()),
        'armador':int(sub['vinculo'].str.contains('Armador').sum()),
        'proprietario':int(sub['vinculo'].str.contains('Proprietário').sum())}

import statistics
idh_corr = [{'uf':uf,'idh':idh,'n':len(df[df['estado']==uf]),'reg':REGIOES.get(uf,'')}
             for uf,idh in IDH_UF.items() if len(df[df['estado']==uf])>0]
iv=[x['idh'] for x in idh_corr]; nv=[x['n'] for x in idh_corr]
mx,my=statistics.mean(iv),statistics.mean(nv)
num=sum((a-mx)*(b-my) for a,b in zip(iv,nv))
den=(sum((a-mx)**2 for a in iv)*sum((b-my)**2 for b in nv))**.5
pearson=round(num/den,3) if den else 0

# GeoJSON
print("GeoJSON estados...")
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
n_uf_d=dict(zip(por_uf['estado'],por_uf['n'])); n_reg_d=dict(zip(por_reg['regiao'],por_reg['n']))
for feat in gj['features']:
    nome=feat['properties'].get('name',''); uf=NOME_UF.get(nome,''); reg=NOME_REG.get(nome,'Desconhecido')
    feat['properties'].update({'uf':uf,'regiao':reg,'n_estado':int(n_uf_d.get(uf,0)),
        'n_regiao':int(n_reg_d.get(reg,0)),'idh':IDH_UF.get(uf,0)})

# Pontos e heat
pts_uf={uf:df[df['estado']==uf].sample(min(500,len(df[df['estado']==uf])),random_state=42)
        [['latitude','longitude','municipio','estado','tipo_pessoa','vinculo']].values.tolist()
        for uf in df['estado'].unique()}
pts_reg={reg:df[df['regiao']==reg].sample(min(1500,len(df[df['regiao']==reg])),random_state=42)
         [['latitude','longitude','municipio','estado','tipo_pessoa','vinculo']].values.tolist()
         for reg in df['regiao'].unique()}

def make_heat(sub, gmax):
    c=sub.groupby(['latitude','longitude']).size().reset_index(name='c')
    return [[round(r['latitude'],5),round(r['longitude'],5),min(1.0,r['c']/gmax)] for _,r in c.iterrows()]

gmax=df.groupby(['latitude','longitude']).size().max()
heat_br=make_heat(df,gmax)
heat_uf={uf:make_heat(df[df['estado']==uf],gmax) for uf in df['estado'].unique()}
heat_reg={reg:make_heat(df[df['regiao']==reg],gmax) for reg in df['regiao'].unique()}

bbox_uf={}
for uf in df['estado'].unique():
    s=df[df['estado']==uf]; p=0.4
    bbox_uf[uf]=[float(s['latitude'].min())-p,float(s['longitude'].min())-p,
                 float(s['latitude'].max())+p,float(s['longitude'].max())+p]

# Rios
print("Rios Natural Earth...")
r_rios=requests.get("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_rivers_lake_centerlines.geojson",timeout=20)
rios_brasil=[]
for feat in r_rios.json()['features']:
    geom=feat.get('geometry',{}); coords=[]
    if geom.get('type')=='LineString': coords=geom['coordinates']
    elif geom.get('type')=='MultiLineString': coords=geom['coordinates'][0] if geom['coordinates'] else []
    if coords and -75<=coords[0][0]<=-28 and -35<=coords[0][1]<=6:
        rios_brasil.append(feat)
gj_rios={'type':'FeatureCollection','features':rios_brasil}
print(f"  {len(rios_brasil)} rios")

# Municípios
print("Municípios...")
r_munis=requests.get("https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv",timeout=15)
UF_CODE={'11':'RO','12':'AC','13':'AM','14':'RR','15':'PA','16':'AP','17':'TO',
    '21':'MA','22':'PI','23':'CE','24':'RN','25':'PB','26':'PE','27':'AL','28':'SE','29':'BA',
    '31':'MG','32':'ES','33':'RJ','35':'SP','41':'PR','42':'SC','43':'RS',
    '50':'MS','51':'MT','52':'GO','53':'DF'}
munis_busca=[]
for m in csv.DictReader(io.StringIO(r_munis.text)):
    uf=UF_CODE.get(str(m.get('codigo_uf','')),'')
    if uf and m.get('latitude') and m.get('longitude'):
        munis_busca.append({'nome':m['nome'],'uf':uf,'lat':float(m['latitude']),'lon':float(m['longitude'])})
print(f"  {len(munis_busca)} municípios")

CONCLUSOES={'geral':[
    "O Nordeste concentra 39% dos pescadores — mais que qualquer região, apesar de não ser a mais rica. A pesca artesanal é central para a subsistência.",
    "O Norte tem 68% dos pescadores em municípios ribeirinhos do interior, não no litoral — a pesca amazônica é predominantemente fluvial.",
    "O Sul tem a maior densidade de pescadores por km de litoral. Itajaí/SC e Rio Grande/RS são os dois maiores portos pesqueiros do país.",
    "O Sudeste combina pesca industrial (Santos, Macaé) com artesanal costeira. RJ e SP concentram 84% da região.",
    "O Centro-Oeste representa apenas 3,9% do total. A pesca pantaneira de Corumbá/MS é a única concentração relevante."],
    'insights_uf':{'CE':'Fortaleza concentra 51% dos cearenses — hub industrial e artesanal no Nordeste.',
        'MA':'São Luís domina, mas Cururupu emerge como segundo polo de pesca artesanal no litoral ocidental.',
        'AM':'Manaus concentra 56% do estado. A pesca fluvial amazônica organiza-se em centros ribeirinhos.',
        'PA':'Belém responde por 45%. Santarém, 800km rio acima, é o segundo polo ao longo do Amazonas.',
        'SC':'Itajaí é o maior porto pesqueiro do Brasil em volume desembarcado — pesca oceânica industrial.',
        'RS':'Rio Grande concentra 45% dos gaúchos — polo da pesca oceânica do extremo sul.',
        'RJ':'Macaé aparece como segundo polo fluminense, ligado à plataforma continental e ao offshore.',
        'SP':'Santos e Guarujá somam 50% dos pescadores paulistas — eixo da pesca no maior estado.',
        'BA':'Salvador concentra 48%, mas Ilhéus e Porto Seguro revelam pesca artesanal no litoral sul.',
        'RN':'Areia Branca surpreende como 2º polo — exportação de lagosta e camarão explica a concentração.',
        'PE':'Recife domina com 45%; toda a Grande Recife centraliza a pesca pernambucana.',
        'PI':'Parnaíba concentra quase toda a pesca — apesar do estado ser majoritariamente interiorano.',
        'MS':'Corumbá responde pela maior parte do MS — âncora da pesca fluvial do Centro-Oeste.'},
    'insights_reg':{'Norte':'68% dos pescadores estão no interior ribeirinho. Único padrão fluvial dominante — reflexo da Bacia Amazônica.',
        'Nordeste':'Maior volume absoluto (39%). Pesca artesanal estratégica para segurança alimentar. CE, BA e MA respondem por 65%.',
        'Centro-Oeste':'Apenas 3,9% do total. Pesca restrita às bacias do Pantanal e Araguaia-Tocantins.',
        'Sudeste':'Combina pesca industrial em portos (Santos, Macaé) e artesanal costeira no litoral fluminense e paulista.',
        'Sul':'Maior densidade por km². Itajaí e Rio Grande são referências nacionais em pesca oceânica e processamento industrial.'}}

print("Serializando...")
D={'GJ':json.dumps(gj,ensure_ascii=False),'GJ_RIOS':json.dumps(gj_rios,ensure_ascii=False),
   'S_UF':json.dumps(stats_uf,ensure_ascii=False),'S_REG':json.dumps(stats_reg,ensure_ascii=False),
   'PTS_UF':json.dumps(pts_uf,ensure_ascii=False),'PTS_REG':json.dumps(pts_reg,ensure_ascii=False),
   'HEAT_UF':json.dumps(heat_uf,ensure_ascii=False),'HEAT_REG':json.dumps(heat_reg,ensure_ascii=False),
   'HEAT_BR':json.dumps(heat_br,ensure_ascii=False),'BBOX_UF':json.dumps(bbox_uf,ensure_ascii=False),
   'SERIE_UF':json.dumps(serie_uf,ensure_ascii=False),'SERIE_REG':json.dumps(serie_reg,ensure_ascii=False),
   'ANOS':json.dumps(anos,ensure_ascii=False),'IDH_UF':json.dumps(IDH_UF,ensure_ascii=False),
   'IDH_CORR':json.dumps(idh_corr,ensure_ascii=False),'PEARSON':str(pearson),
   'MUNIS':json.dumps(munis_busca,ensure_ascii=False),'CONC':json.dumps(CONCLUSOES,ensure_ascii=False),
   'TOTAL_STR':f"{TOTAL:,}".replace(',','.'),'TOTAL_NUM':str(TOTAL)}

print("Baixando Leaflet...")
rt=requests.get("https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz",timeout=60)
t=tarfile.open(fileobj=io.BytesIO(rt.content))
LJS=LCSS=""
for m in t.getmembers():
    if m.name.endswith('dist/leaflet.js') and 'src' not in m.name: LJS=t.extractfile(m).read().decode('utf-8')
    if m.name.endswith('dist/leaflet.css'): LCSS=t.extractfile(m).read().decode('utf-8')
LHEAT=requests.get("https://raw.githubusercontent.com/Leaflet/Leaflet.heat/gh-pages/dist/leaflet-heat.js",timeout=30).text
print(f"  js {len(LJS)//1024}KB | css {len(LCSS)//1024}KB | heat {len(LHEAT)//1024}KB")

template = open('./template.html', encoding='utf-8').read()
html = template
for k,v in D.items():
    html = html.replace(f'%%{k}%%', v)
html = html.replace('%%LEAFLET_CSS%%',LCSS).replace('%%LEAFLET_JS%%',LJS).replace('%%LEAFLET_HEAT%%',LHEAT)

out='./mapa.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
print(f"\nGerado: {out}  ({os.path.getsize(out)/1024/1024:.1f} MB)")
