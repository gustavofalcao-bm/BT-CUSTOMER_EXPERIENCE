# 🧭 Dashboard Customer Success (CS) — GUIA COMPLETO DO PROJETO

> **Objetivo deste guia**: permitir que qualquer pessoa (ou outra conversa do zero) entenda rapidamente o projeto, execute localmente, saiba onde mexer, como os dados são carregados, como cada página funciona e quais pontos são críticos.

---

## 1) 🎯 Visão Executiva

Este projeto é um **dashboard de Customer Success** construído em **Streamlit** para acompanhamento de:

- **Saúde do cliente (Health Score)**
- **Risco (AT_RISK / CHURN_RISK)**
- **Relacionamento** (cadência e “dias sem contato”)
- **Suporte & Qualidade** (chamados, incidentes, SLA)
- **Risco financeiro** (priorização por impacto/valor)
- **Investigação individual** (Cliente 360)

O dashboard lê dados principalmente do arquivo Excel **`BASE-CS.xlsx`** (aba de informações gerais + abas de chamados mensais) e transforma esses dados em dataframes padronizados que alimentam as páginas.

---

## 2) 🧱 Arquitetura do Projeto

### 2.1 Estrutura (arquivos principais)

Arquivos fornecidos/atuais no projeto:

- `app.py` (entrada principal do Streamlit — não foi anexado aqui, mas ele importa as views)
- `modules/data_loader.py` — **ETL / carga e normalização** do Excel
- `modules/utils.py` — funções utilitárias e **cálculos (Health Score, labels)**
- `modules/config.py` — cores, ícones e constantes
- `modules/styles.py` — CSS e layout visual
- `views/visao_executiva.py` — página “Visão Executiva”
- `views/relacionamento.py` — página “Relacionamento”
- `views/suporte_qualidade.py` — página “Suporte & Qualidade”
- `views/risco_financeiro.py` — página “Risco Financeiro”
- `views/cliente_360.py` — página “Cliente 360”

### 2.2 Fluxo de dados (alto nível)

1) `data_loader.load_info_gerais()` carrega e padroniza a aba **Informações Gerais**.
2) `data_loader.load_chamados_all()` carrega abas de chamados (2025/2026) e **verticaliza** a matriz mensal.
3) As páginas recebem `df_info` e `df_chamados` e constroem KPIs e gráficos.
4) O Health Score é calculado com `utils.calcular_health_score()`.

---

## 3) 📦 Dependências e Execução

### 3.1 Requisitos

Pacotes típicos:

- `streamlit`
- `pandas`
- `plotly`
- `openpyxl` (para ler Excel)

### 3.2 Como rodar

```bash
# instalar dependências (exemplo)
pip install streamlit pandas plotly openpyxl

# executar
streamlit run app.py
```

---

## 4) 🗂️ Fonte de Dados (Excel)

### 4.1 Arquivo

- `data/BASE-CS.xlsx` (no projeto local pode estar em `/data/BASE-CS.xlsx`)

### 4.2 Abas esperadas

- **Informações Gerais**
- **Chamados Mensais 2025**
- **Chamados Mensais 2026**

### 4.3 “Informações Gerais” — colunas importantes (padronizadas)

O `data_loader.py` tenta localizar colunas por palavras-chave e cria colunas padrão:

- `CLIENTE`
- `AT_RISK` (SIM/NÃO)
- `CHURN_RISK` (SIM/NÃO)
- `VALOR_CONTRATO`
- `ULTIMO_CONTATO_DT` (data normalizada)
- `DIAS_SEM_CONTATO`
- `FAIXA_CONTATO` (0-30 / 30-90 / 90+)
- `CANCELADO` (bool)
- `VIGENCIA_INICIAL`, `VIGENCIA_FINAL`
- `DIAS_ATE_VENCIMENTO`, `ALERTA_VENCIMENTO`

### 4.4 “Chamados Mensais” — modelo de dados após ETL

O loader transforma as planilhas em um dataframe vertical com:

- `CLIENTE`
- `ANO`
- `MES`
- `MES_NOME`
- `MES_REF` (timestamp do mês)
- `CATEGORIA` ∈ {`CHAMADOS`, `INCIDENTES`, `SOLICITACOES`, `DENTRO_SLA`, `FORA_SLA`}
- `VALOR` (numérico)

---

## 5) 🧪 Pontos críticos já mapeados (bugs e correções)

### 5.1 Bug: “últimos 3 meses” pegava 3 linhas

Como `df_chamados_cliente` tem várias linhas por mês (uma por categoria), usar:

```python
df_recente = df_chamados_cliente.nlargest(3, 'MES_REF')
```

é **ERRADO**, porque seleciona 3 linhas e pode pegar só 1 mês (duplicado) + 1 linha de outro mês.

✅ Correção aplicada: selecionar os **últimos 3 meses únicos**, e adicionalmente **ignorar meses vazios**.

### 5.2 Bug: meses futuros ou vazios aparecendo nos gráficos

Quando uma aba de 2026 existe mas está sem dados (todos 0), ela pode:

- aparecer em gráficos
- interferir em métricas se for considerada como “mês recente”

✅ Correção aplicada no Health Score: usar os **últimos meses COM DADOS**, não simplesmente os últimos por data.

---

## 6) ❤️ Health Score — especificação detalhada

### 6.1 Escala e componentes

O Health Score varia de **0 a 100** e é soma de 4 blocos:

1) **Contato** (0–25)
2) **Incidentes** (0–30)
3) **SLA** (0–25)
4) **Flags** (0–20)

### 6.2 Regra “últimos meses com dados” (IMPORTANTE)

Para evitar considerar meses vazios (ex.: Janeiro 2026 ainda sem preenchimento), usamos:

- Para incidentes: meses onde `CHAMADOS > 0`
- Para SLA: meses onde `(DENTRO_SLA + FORA_SLA) > 0`

E então pegamos os **últimos 3 meses** desses conjuntos.

### 6.3 Pontuação: Contato

Baseado em `DIAS_SEM_CONTATO`:

- `<= 30` → 25 pts
- `<= 90` → 15 pts
- `> 90` ou NaN → 5 pts

### 6.4 Pontuação: Incidentes (últimos 3 meses com chamados)

Cálculo:

`taxa_incidentes = incidentes / chamados`

Faixas:

- 0% → 30
- <10% → 25
- <25% → 15
- <50% → 8
- ≥50% → 3

### 6.5 Pontuação: SLA (últimos 3 meses com SLA)

Cálculo:

`taxa_sla = dentro / (dentro + fora)`

Faixas:

- ≥95% → 25
- ≥85% → 18
- ≥70% → 10
- <70% → 3

### 6.6 Pontuação: Flags

Começa com 20 pontos e subtrai:

- `AT_RISK == SIM` → -8
- `CHURN_RISK == SIM` → -12

### 6.7 Labels

- 80+ → EXCELENTE
- 60–79 → BOM
- 40–59 → ATENÇÃO
- <40 → CRÍTICO

---

## 7) 📄 Páginas do Dashboard (o que cada uma faz)

### 7.1 Visão Executiva (`views/visao_executiva.py`)

Objetivo: panorama geral para liderança.

Típicos blocos:

- KPIs gerais: total clientes, cancelados/ativos, risco, distribuição de saúde
- gráficos: saúde por faixa, evolução de chamados, distribuição por perfil

### 7.2 Relacionamento (`views/relacionamento.py`)

Objetivo: cadência de CS.

- Clientes por faixa de contato (0-30, 30-90, 90+)
- possíveis rankings por CSM/gerente

### 7.3 Suporte & Qualidade (`views/suporte_qualidade.py`)

Objetivo: operação e SLA.

- KPIs: total chamados, incidentes, solicitações, taxa SLA
- Evolução mensal (linhas)
- Barras de SLA mensal (dentro vs fora)
- análises por cliente (perfil de incidentes)

### 7.4 Risco Financeiro (`views/risco_financeiro.py`)

Objetivo: priorizar por impacto.

- cruza risco e saúde com `VALOR_CONTRATO`
- lista de “clientes prioritários”

### 7.5 Cliente 360 (`views/cliente_360.py`)

Objetivo: investigação individual.

- escolhe cliente
- mostra cards: valor, risco, health score detalhado
- histórico de chamados/incidentes e SLA
- perfil de incidentes (classificação)

---

## 8) 🧰 Convenções e Boas Práticas

### 8.1 Sempre padronizar strings de cliente

- `.astype(str).str.strip()`

### 8.2 Sempre tratar meses vazios

- nunca usar apenas “maior MES_REF”
- usar “meses com dados” no cálculo

### 8.3 Cache Streamlit

O projeto usa `@st.cache_data` no loader. Ao mudar Excel ou lógica, pode precisar:

- limpar cache (botão/recarga) ou reiniciar o `streamlit run`.

---

## 9) 🔧 Checklist de Troubleshooting

### Sintoma: Health Score alto demais para todo mundo

- Verificar se `df_chamados_cliente` realmente está filtrado por `CLIENTE`
- Verificar se o cálculo está pegando meses corretos
- Verificar se meses vazios (2026 sem dados) estão entrando

### Sintoma: SLA “cai do nada”

- Conferir se meses sem SLA (total 0) estão sendo incluídos
- Conferir se a aba 2026 tem estrutura correta

---

## 10) 🔜 Próximos Passos (Roadmap sugerido)

- Validar estrutura 2026 (garantir idêntica a 2025)
- Criar testes automáticos do ETL (pandas) para detectar meses vazios
- Adicionar validação no loader: “mês válido = pelo menos 1 cliente com chamados > 0”
- Export de relatórios (PDF/DOCX) direto no app

---

## 11) 📌 Apêndice — Por que “meses com dados” é essencial

O dashboard é mensal e cada mês possui 5 categorias por cliente.

Se você adicionar meses futuros na planilha (ex.: Jan 2026) mas ainda estiver tudo vazio, os gráficos podem mostrar o mês e o cálculo pode:

- considerar esses meses como “recentes”
- gerar taxas erradas (por falta de denominador ou por seleção incorreta)

Por isso, o cálculo de Health Score e métricas relacionadas devem sempre selecionar:

- **últimos 3 meses com chamados > 0** para incidentes
- **últimos 3 meses com SLA > 0** para SLA

Isso garante que o dashboard “aguarde” dados reais e se atualize automaticamente quando os meses forem preenchidos.
