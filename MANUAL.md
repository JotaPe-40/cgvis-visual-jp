# Como rodar a visualização

## Você vai precisar de

- Conta Google (para usar o Colab — gratuito)
- O arquivo `armadores_pesca.xlsx` (baixado do link no TAREFAS.md)
- Os arquivos deste repositório

---

## Passo a passo

**1. Abra o Google Colab**  
Acesse [colab.research.google.com](https://colab.research.google.com)

**2. Faça upload do notebook**  
Clique em **Arquivo → Fazer upload de notebook** e selecione `visualizacao_pescadores.ipynb`

**3. Faça upload dos arquivos de dados**  
No painel esquerdo, clique no ícone de 📁 pasta e depois em **Upload**.  
Suba os 3 arquivos abaixo na mesma pasta:
- `armadores_pesca.xlsx`
- `build_map_v3.py`

**4. Execute tudo**  
No menu superior: **Runtime → Run all** (ou `Ctrl+F9`)  
Aguarde ~10–15 minutos (a geocodificação dos municípios é a etapa mais demorada)

**5. Baixe o mapa**  
Ao final, o arquivo `mapa_pescadores_brasil.html` será baixado automaticamente.  
Abra-o em qualquer navegador — Chrome, Firefox ou Edge.

---

## Se der algum erro

| Problema | Solução |
|----------|---------|
| "File not found: armadores_pesca.xlsx" | Faça upload do arquivo no painel de arquivos do Colab |
| "Module not found" | Execute apenas a célula 1 (instalação) e tente novamente |
| Geocodificação travou | Re-execute a célula — ela continua do ponto onde parou (usa cache) |
| Mapa abriu em branco | Tente em outro navegador (Chrome funciona melhor) |

---

## Como usar o mapa

- **Clique num estado** → isola ele, aplica zoom e mostra análise no painel direito
- **Botão "← Voltar ao Brasil"** → volta à visão geral
- **🔥 Heatmap / ⚫ Pontos** → liga/desliga camadas (botões no canto inferior esquerdo)
- **📄 Gerar relatório** → abre relatório do estado com opção de baixar em `.txt`
- **◀ ▶** → abre/fecha o painel lateral
