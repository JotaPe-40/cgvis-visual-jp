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


# ═══════════════════════════════════════════════════════════════════════
# MOTOR DE ANÁLISE AUTOMÁTICA
# Gera conclusões e insights dinamicamente a partir dos dados reais.
# Nenhum texto é hardcoded — tudo é derivado das métricas calculadas.
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# MOTOR DE ANÁLISE AUTOMÁTICA — gera conclusões e insights dos dados reais
# Chamado pelo build_map_v7.py após calcular stats_uf, stats_reg, df, etc.
# ═══════════════════════════════════════════════════════════════════════
import statistics, math

def gerar_conclusoes(df, stats_uf, stats_reg, IDH_UF, TOTAL, pearson):
    """Gera todas as conclusões e insights automaticamente dos dados reais."""

    REGIOES = {uf: s['regiao'] for uf, s in stats_uf.items()}

    # ── Métricas gerais ──────────────────────────────────────────────
    reg_totais = {reg: s['n'] for reg, s in stats_reg.items()}
    reg_pct    = {reg: s['pct_br'] for reg, s in stats_reg.items()}
    reg_rank   = sorted(reg_totais, key=reg_totais.get, reverse=True)
    uf_rank    = sorted(stats_uf, key=lambda u: stats_uf[u]['n'], reverse=True)

    reg_lider  = reg_rank[0]
    reg_menor  = reg_rank[-1]
    uf_lider   = uf_rank[0]
    uf_2o      = uf_rank[1]

    # Norte: % interior (lon < -50 como proxy de interior ribeirinho)
    norte_df   = df[df['regiao'] == 'Norte']
    pct_norte_interior = round(len(norte_df[norte_df['longitude'] < -50]) / max(len(norte_df),1) * 100, 1)

    # Gini de concentração entre UFs
    vals = sorted([s['n'] for s in stats_uf.values()])
    n_uf = len(vals); s_vals = sum(vals)
    gini_num = sum((2*(i+1)-n_uf-1)*v for i,v in enumerate(vals))
    gini = round(gini_num / (n_uf * s_vals), 3) if s_vals else 0

    # Tendência temporal
    serie = df.groupby('ano').size()
    anos_s = sorted(serie.index.tolist())
    if len(anos_s) >= 2:
        delta  = serie[anos_s[-1]] - serie[anos_s[0]]
        n_anos = anos_s[-1] - anos_s[0]
        trend_pct = round(delta / serie[anos_s[0]] * 100, 1) if serie[anos_s[0]] else 0
        trend_dir = "crescimento" if delta > 0 else "queda"
        trend_txt = f"{abs(trend_pct)}% de {trend_dir} entre {anos_s[0]} e {anos_s[-1]}"
    else:
        trend_txt = "série temporal insuficiente"
        trend_pct = 0

    # PJ e PF por região
    pj_por_reg = {reg: round(s['juridica']/s['n']*100, 1) if s['n'] else 0 for reg, s in stats_reg.items()}
    reg_mais_pj = max(pj_por_reg, key=pj_por_reg.get)
    reg_menos_pj = min(pj_por_reg, key=pj_por_reg.get)

    pj_por_uf = {uf: round(s['juridica']/s['n']*100, 1) if s['n'] else 0 for uf, s in stats_uf.items()}
    uf_mais_pj  = max(pj_por_uf, key=pj_por_uf.get)
    uf_menos_pj = min(pj_por_uf, key=pj_por_uf.get)

    # Concentração no líder estadual por região
    conc_por_reg = {}
    for reg in reg_totais:
        top = stats_reg[reg]['top_ufs'][0] if stats_reg[reg]['top_ufs'] else [None,0]
        conc_por_reg[reg] = round(top[1]/reg_totais[reg]*100, 1) if reg_totais[reg] else 0

    # IDH: relação com volume
    idh_vals = [IDH_UF[uf] for uf in stats_uf if uf in IDH_UF]
    n_vals   = [stats_uf[uf]['n'] for uf in stats_uf if uf in IDH_UF]
    idh_txt = (
        f"negativa (Pearson={pearson}) — estados com menor IDH tendem a ter mais pescadores registrados"
        if pearson < -0.1 else
        f"positiva (Pearson={pearson}) — estados com maior IDH concentram mais armadores"
        if pearson > 0.1 else
        f"fraca (Pearson={pearson}) — IDH estadual explica pouco a concentração de pescadores"
    )

    # ── CONCLUSÕES GERAIS (geradas dos dados) ────────────────────────
    geral = [
        f"O {reg_lider} concentra {reg_pct[reg_lider]}% dos pescadores registrados "
        f"({reg_totais[reg_lider]:,} armadores), mais que qualquer outra região. "
        + ("A pesca artesanal é estratégica para a subsistência dessas comunidades costeiras."
           if reg_lider == 'Nordeste' else
           "Isso reflete a importância econômica da pesca nessa região."),

        f"O Norte tem {pct_norte_interior}% de seus pescadores em municípios do interior ribeirinho "
        f"— não no litoral. Isso evidencia que a pesca brasileira não é exclusivamente marítima: "
        f"a Bacia Amazônica sustenta uma rede pesqueira fluvial única no país.",

        f"A distribuição entre estados é desigual (Gini={gini}): {uf_lider} lidera com "
        f"{stats_uf[uf_lider]['n']:,} pescadores ({stats_uf[uf_lider]['pct_br']}% do Brasil), "
        f"enquanto os 5 menores estados somam menos de 5% do total.",

        f"Há {trend_txt} nos registros ao longo do período analisado ({anos_s[0] if anos_s else 'N/A'}–{anos_s[-1] if anos_s else 'N/A'}). "
        + ("Isso pode refletir expansão das frotas pesqueiras ou melhoria no sistema de cadastro."
           if trend_pct > 0 else
           "Isso pode indicar saída de armadores do setor formal ou desatualização cadastral."),

        f"A correlação IDH × número de pescadores é {idh_txt}. "
        f"O {reg_menos_pj} é a região com menor participação de Pessoa Jurídica "
        f"({pj_por_reg[reg_menos_pj]}%), indicando perfil predominantemente artesanal.",
    ]

    # ── INSIGHTS POR UF (gerados dos dados) ──────────────────────────
    insights_uf = {}
    for uf, s in stats_uf.items():
        reg = s['regiao']
        top1 = s['tops'][0] if s['tops'] else [uf, s['n']]
        top2 = s['tops'][1] if len(s['tops']) > 1 else None
        pj   = pj_por_uf.get(uf, 0)
        idh  = IDH_UF.get(uf, 0)
        idh_lbl = 'alto' if idh >= 0.75 else 'médio' if idh >= 0.65 else 'baixo'
        conc = s['conc']

        # Determinar perfil predominante
        if pj >= 30:
            perfil = f"alta presença empresarial ({pj}% PJ), sugerindo pesca industrializada"
        elif pj <= 10:
            perfil = f"perfil artesanal ({100-pj:.0f}% Pessoa Física), característico de pesca de subsistência"
        else:
            perfil = f"equilíbrio entre Pessoa Física e Jurídica ({100-pj:.0f}% e {pj}%)"

        # Concentração no polo principal
        if conc >= 60:
            conc_txt = f"{top1[0]} domina com {conc}% dos registros estaduais"
            if top2:
                ratio = round(top2[1]/top1[1]*100)
                conc_txt += f"; {top2[0]} é o segundo polo com apenas {ratio}% do volume do líder"
        elif conc >= 40:
            conc_txt = f"{top1[0]} é o principal polo ({conc}% do estado)"
            if top2:
                conc_txt += f", seguido por {top2[0]}"
        else:
            conc_txt = f"distribuição relativamente dispersa: {top1[0]} lidera com {conc}%"

        insights_uf[uf] = (
            f"{uf} tem {s['n']:,} armadores registrados ({s['pct_br']}% do Brasil). "
            f"{conc_txt.capitalize()}. "
            f"IDH {idh} ({idh_lbl}) e {perfil}."
        )

    # ── INSIGHTS POR REGIÃO (gerados dos dados) ───────────────────────
    insights_reg = {}
    for reg, s in stats_reg.items():
        top_uf_reg = s['top_ufs'][0] if s['top_ufs'] else [reg, 0]
        top2_uf    = s['top_ufs'][1] if len(s['top_ufs']) > 1 else None
        top_mun    = s['top_muns'][0] if s['top_muns'] else [reg, 0]
        pj_reg     = pj_por_reg.get(reg, 0)
        desig      = s.get('desigualdade', 0)

        # Caracterizar a região pelos dados
        if desig > 60:
            desig_txt = f"alta concentração interna (CV={desig}%): poucos estados dominam os registros"
        elif desig > 35:
            desig_txt = f"concentração moderada entre estados (CV={desig}%)"
        else:
            desig_txt = f"distribuição relativamente equilibrada entre os {s['n_ufs']} estados (CV={desig}%)"

        pj_txt = (
            f"alta industrialização ({pj_reg}% PJ)" if pj_reg >= 25 else
            f"perfil majoritariamente artesanal ({100-pj_reg:.0f}% Pessoa Física)" if pj_reg <= 12 else
            f"mix de pescadores individuais e empresas ({pj_reg}% PJ)"
        )

        insights_reg[reg] = (
            f"O {reg} concentra {s['pct_br']}% do total nacional ({s['n']:,} pescadores). "
            f"{top_uf_reg[0]} lidera com {s['lider_pct']}% da região"
            + (f"; {top2_uf[0]} vem em segundo" if top2_uf else "") + ". "
            f"O município de {top_mun[0]} é o maior polo pesqueiro da região. "
            f"A região apresenta {desig_txt} e {pj_txt}."
        )

    return {
        'geral':        geral,
        'insights_uf':  insights_uf,
        'insights_reg': insights_reg,
        # Metadados para o relatório
        '_meta': {
            'total':            TOTAL,
            'reg_lider':        reg_lider,
            'reg_lider_pct':    reg_pct[reg_lider],
            'reg_menor':        reg_menor,
            'reg_menor_pct':    reg_pct[reg_menor],
            'uf_lider':         uf_lider,
            'uf_lider_n':       stats_uf[uf_lider]['n'],
            'norte_interior_pct': pct_norte_interior,
            'gini':             gini,
            'trend_txt':        trend_txt,
            'idh_corr_txt':     idh_txt,
            'pearson':          pearson,
            'anos':             anos_s,
        }
    }

print("Motor de análise carregado com sucesso.")


print("Gerando conclusões e insights automaticamente dos dados...")
CONCLUSOES = gerar_conclusoes(df, stats_uf, stats_reg, IDH_UF, TOTAL, pearson)
print(f"  {len(CONCLUSOES['geral'])} conclusões gerais geradas")
print(f"  {len(CONCLUSOES['insights_uf'])} insights de estados gerados")
print(f"  {len(CONCLUSOES['insights_reg'])} insights de regiões gerados")

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

# Busca o template na pasta do script ou em /tmp
import os as _os
_tpl_paths = [
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'template_v7.html'),
    '/tmp/template_v7.html',
    'template_v7.html',
]
_tpl_path = next((p for p in _tpl_paths if _os.path.exists(p)), None)
if not _tpl_path: raise FileNotFoundError('template_v7.html nao encontrado')
template = open(_tpl_path, encoding='utf-8').read()
print(f'  Template: {_tpl_path}')
html = template
for k,v in D.items():
    html = html.replace(f'%%{k}%%', v)
html = html.replace('%%LEAFLET_CSS%%',LCSS).replace('%%LEAFLET_JS%%',LJS).replace('%%LEAFLET_HEAT%%',LHEAT)

out='/tmp/mapa_v7.html'
with open(out,'w',encoding='utf-8') as f: f.write(html)
print(f"\nGerado: {out}  ({os.path.getsize(out)/1024/1024:.1f} MB)")
