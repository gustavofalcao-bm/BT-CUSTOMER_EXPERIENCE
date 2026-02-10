"""
Sistema de carregamento e processamento de dados CS
ETL executado ao rodar o app
"""

import re
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
ARQ_CS = DATA_DIR / "BASE-CS.xlsx"

MESES_MAP = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}

def _to_sim_nao(x):
    """Normaliza flag para SIM/NÃO"""
    s = str(x).strip().upper()
    if s in {"SIM", "S", "YES", "Y", "TRUE", "1"}:
        return "SIM"
    if s in {"NÃO", "NAO", "N", "NO", "FALSE", "0", "-", "", "NAN"}:
        return "NÃO"
    return "NÃO"

def _parse_ultimo_contato(v):
    """
    Normaliza 'ÚLTIMO CONTATO' que pode ser:
    - Data real (datetime)
    - Texto tipo 'A 1 SEMANA ATRÁS', 'A 4 MESES ATRAS'
    """
    if pd.isna(v):
        return pd.NaT
    
    # caso já seja data
    try:
        ts = pd.to_datetime(v, errors="raise")
        if not pd.isna(ts):
            return ts
    except Exception:
        pass
    
    s = str(v).strip().upper()
    # padrões simples: "A 1 SEMANA", "A 4 MESES"
    m = re.search(r"A\s*(\d+)\s*(SEMANA|SEMANAS|MES|MESES)", s)
    if m:
        n = int(m.group(1))
        unidade = m.group(2)
        hoje = pd.Timestamp(date.today())
        if "SEMANA" in unidade:
            return hoje - pd.Timedelta(days=7 * n)
        if "MES" in unidade:
            return hoje - pd.Timedelta(days=30 * n)
    
    return pd.NaT

def _normalizar_nome_coluna(col):
    """Normaliza nome de coluna para busca"""
    return str(col).strip().upper().replace('\n', ' ')

def _encontrar_coluna(df, palavras_chave):
    """
    Encontra coluna que contenha todas as palavras-chave
    
    Args:
        df: DataFrame
        palavras_chave: lista de strings que devem estar no nome da coluna
    
    Returns:
        nome original da coluna ou None
    """
    for col in df.columns:
        col_norm = _normalizar_nome_coluna(col)
        if all(palavra.upper() in col_norm for palavra in palavras_chave):
            return col
    return None

def _verticalizar_chamados(df_raw):
    """
    Verticaliza planilha de chamados
    """
    if df_raw.empty or df_raw.shape[1] < 6:
        return pd.DataFrame(columns=["CLIENTE", "ANO", "MES", "MES_NOME", "MES_REF", "CATEGORIA", "VALOR"])
    
    linha_datas, linha_cats, linha_dados = 0, 1, 2
    
    # Pegar clientes (primeira coluna, a partir da linha 2)
    clientes = df_raw.iloc[linha_dados:, 0].dropna().astype(str).str.strip()
    clientes = clientes[clientes.ne("") & clientes.ne("nan")]
    
    # CORREÇÃO: Se não há clientes, retornar vazio
    if clientes.empty:
        return pd.DataFrame(columns=["CLIENTE", "ANO", "MES", "MES_NOME", "MES_REF", "CATEGORIA", "VALOR"])
    
    num_cols = df_raw.shape[1]
    num_meses = (num_cols - 1) // 5
    
    categorias_map = {
        0: "CHAMADOS",
        1: "INCIDENTES",
        2: "SOLICITACOES",
        3: "DENTRO_SLA",
        4: "FORA_SLA",
    }
    
    out = []
    
    for mes_idx in range(num_meses):
        col_inicio = 1 + mes_idx * 5
        col_fim = col_inicio + 5
        
        # Ler data do mês
        data_mes = df_raw.iloc[linha_datas, col_inicio]
        
        if pd.isna(data_mes):
            continue
        
        data_mes = pd.to_datetime(data_mes, errors="coerce")
        
        if pd.isna(data_mes):
            continue
        
        # CORREÇÃO: Ignorar dados futuros (2026 vazio)
        hoje = pd.Timestamp.now()
        if data_mes > hoje:
            continue
        
        ano = int(data_mes.year)
        mes = int(data_mes.month)
        mes_ref = data_mes.normalize()
        
        # Para cada cliente
        for i, cliente in enumerate(clientes.tolist()):
            linha = linha_dados + i
            
            if linha >= df_raw.shape[0]:
                break
            
            # Pegar valores das 5 categorias
            valores = df_raw.iloc[linha, col_inicio:col_fim].tolist()
            
            for cat_idx, cat in categorias_map.items():
                v = valores[cat_idx] if cat_idx < len(valores) else 0
                
                # Normalizar valor
                if pd.isna(v):
                    v = 0
                elif isinstance(v, str):
                    if v.strip().upper() in {"NÃO TEM", "NAO TEM", "", "IMPLANTAÇÃO", "IMPLANTACAO"}:
                        v = 0
                    else:
                        v = pd.to_numeric(v, errors="coerce")
                        v = 0 if pd.isna(v) else float(v)
                else:
                    v = pd.to_numeric(v, errors="coerce")
                    v = 0 if pd.isna(v) else float(v)
                
                out.append({
                    "CLIENTE": str(cliente).strip(),
                    "ANO": ano,
                    "MES": mes,
                    "MES_NOME": MESES_MAP.get(mes, str(mes)),
                    "MES_REF": mes_ref,
                    "CATEGORIA": cat,
                    "VALOR": float(v),
                })
    
    return pd.DataFrame(out)

@st.cache_data
def load_info_gerais():
    """Carrega e processa Informações Gerais"""
    try:
        df = pd.read_excel(ARQ_CS, sheet_name="Informações Gerais")
    except FileNotFoundError:
        st.error(f"❌ Arquivo não encontrado: {ARQ_CS}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao carregar Informações Gerais: {e}")
        return pd.DataFrame()
    
    # Normalizar nomes das colunas (manter originais mas criar mapeamento)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Encontrar colunas dinamicamente
    col_cliente = _encontrar_coluna(df, ["CLIENTE"]) or "CLIENTE"
    col_at_risk = _encontrar_coluna(df, ["AT", "RISK", "CUSTOMER"]) or _encontrar_coluna(df, ["AT-RISK"])
    col_churn_risk = _encontrar_coluna(df, ["CHURN", "RISK"]) or _encontrar_coluna(df, ["CANCELAMENTO"])
    col_ativacao = _encontrar_coluna(df, ["ATIVAÇÃO"]) or _encontrar_coluna(df, ["ATIVACAO"])
    col_vig_inicial = _encontrar_coluna(df, ["VIGÊNCIA", "INICIAL"]) or _encontrar_coluna(df, ["VIGENCIA", "INICIAL"])
    col_vig_final = _encontrar_coluna(df, ["VIGÊNCIA", "FINAL"]) or _encontrar_coluna(df, ["VIGENCIA", "FINAL"])
    col_valor = _encontrar_coluna(df, ["VALOR"])
    col_ultimo_contato = _encontrar_coluna(df, ["ÚLTIMO", "CONTATO"]) or _encontrar_coluna(df, ["ULTIMO", "CONTATO"])
    col_csm = _encontrar_coluna(df, ["CUSTOMER", "SUCCESS"]) or _encontrar_coluna(df, ["CSM"])
    col_gerente = _encontrar_coluna(df, ["GERENTE"])
    col_atividade = _encontrar_coluna(df, ["ATIVIDADE"])
    col_restricao = _encontrar_coluna(df, ["RESTRIÇÃO"]) or _encontrar_coluna(df, ["RESTRICAO"]) or _encontrar_coluna(df, ["SOLUÇÃO"])
    col_unidade = _encontrar_coluna(df, ["UNIDADE"])
    col_contato = _encontrar_coluna(df, ["CONTATO"])
    col_telefone = _encontrar_coluna(df, ["TELEFONE"])
    col_email = _encontrar_coluna(df, ["E-MAIL"]) or _encontrar_coluna(df, ["EMAIL"])
    col_obs = _encontrar_coluna(df, ["OBSERVAÇÃO"]) or _encontrar_coluna(df, ["OBSERVACAO"])
    
    # Filtrar linhas válidas
    if col_cliente and col_cliente in df.columns:
        df["CLIENTE"] = df[col_cliente].astype(str).str.strip()
        df = df[df["CLIENTE"].ne("") & df["CLIENTE"].ne("nan")].copy()
    else:
        st.error("❌ Coluna 'CLIENTE' não encontrada")
        return pd.DataFrame()
    
    # Criar colunas padronizadas
    
    # Flags
    if col_at_risk and col_at_risk in df.columns:
        df["AT_RISK"] = df[col_at_risk].apply(_to_sim_nao)
    else:
        df["AT_RISK"] = "NÃO"
    
    if col_churn_risk and col_churn_risk in df.columns:
        df["CHURN_RISK"] = df[col_churn_risk].apply(_to_sim_nao)
    else:
        df["CHURN_RISK"] = "NÃO"
    
    # Datas/valor
    if col_ativacao and col_ativacao in df.columns:
        df["DATA_ATIVACAO"] = pd.to_datetime(df[col_ativacao], errors="coerce")
    else:
        df["DATA_ATIVACAO"] = pd.NaT
    
    if col_vig_inicial and col_vig_inicial in df.columns:
        df["VIGENCIA_INICIAL"] = pd.to_datetime(df[col_vig_inicial], errors="coerce")
    else:
        df["VIGENCIA_INICIAL"] = pd.NaT
    
    if col_vig_final and col_vig_final in df.columns:
        df["VIGENCIA_FINAL"] = pd.to_datetime(df[col_vig_final], errors="coerce")
    else:
        df["VIGENCIA_FINAL"] = pd.NaT
    
    if col_valor and col_valor in df.columns:
        df["VALOR_CONTRATO"] = pd.to_numeric(df[col_valor], errors="coerce").fillna(0.0)
    else:
        df["VALOR_CONTRATO"] = 0.0
    
    # Último contato
    if col_ultimo_contato and col_ultimo_contato in df.columns:
        df["ULTIMO_CONTATO_DT"] = df[col_ultimo_contato].apply(_parse_ultimo_contato)
    else:
        df["ULTIMO_CONTATO_DT"] = pd.NaT
    
    hoje = pd.Timestamp(date.today())
    df["DIAS_SEM_CONTATO"] = (hoje - df["ULTIMO_CONTATO_DT"]).dt.days
    df["FAIXA_CONTATO"] = pd.cut(
        df["DIAS_SEM_CONTATO"],
        bins=[-999999, 30, 90, 999999],
        labels=["0-30", "30-90", "90+"]
    )
    
    # Campos extras para views
    if col_csm and col_csm in df.columns:
        df["Customer Success Manager"] = df[col_csm]
    else:
        df["Customer Success Manager"] = "N/A"
    
    if col_gerente and col_gerente in df.columns:
        df["GERENTE RESPONSÁVEL"] = df[col_gerente]
    else:
        df["GERENTE RESPONSÁVEL"] = "N/A"
    
    if col_atividade and col_atividade in df.columns:
        df["ATIVIDADE PRINCIPAL "] = df[col_atividade]
    else:
        df["ATIVIDADE PRINCIPAL "] = "N/A"
    
    if col_restricao and col_restricao in df.columns:
        df["RESTRIÇÃO/SOLUÇÃO"] = df[col_restricao]
    else:
        df["RESTRIÇÃO/SOLUÇÃO"] = "N/A"
    
    if col_unidade and col_unidade in df.columns:
        df["UNIDADE"] = df[col_unidade]
    else:
        df["UNIDADE"] = "N/A"
    
    if col_contato and col_contato in df.columns:
        df["CONTATO"] = df[col_contato]
    else:
        df["CONTATO"] = "N/A"
    
    if col_telefone and col_telefone in df.columns:
        df["TELEFONE"] = df[col_telefone]
    else:
        df["TELEFONE"] = "N/A"
    
    if col_email and col_email in df.columns:
        df["E-MAIL"] = df[col_email]
    else:
        df["E-MAIL"] = "N/A"
    
    if col_obs and col_obs in df.columns:
        df["OBSERVAÇÃO"] = df[col_obs]
    else:
        df["OBSERVAÇÃO"] = ""
    
    # Cancelados (detecta texto "cancelado")
    def _is_cancelado(row):
        for c in [col_ativacao, col_vig_inicial, col_vig_final, col_valor]:
            if c and c in row.index:
                val = row[c]
                if isinstance(val, str) and "CANCEL" in val.upper():
                    return True
        return False
    
    df["CANCELADO"] = df.apply(_is_cancelado, axis=1)
    
    # Dias até vencimento do contrato
    df["DIAS_ATE_VENCIMENTO"] = (df["VIGENCIA_FINAL"] - hoje).dt.days
    df["ALERTA_VENCIMENTO"] = df["DIAS_ATE_VENCIMENTO"].apply(
        lambda x: "VENCIDO" if pd.notna(x) and x < 0
        else "30_DIAS" if pd.notna(x) and x <= 30
        else "60_DIAS" if pd.notna(x) and x <= 60
        else "90_DIAS" if pd.notna(x) and x <= 90
        else "OK"
    )
    
    return df

@st.cache_data
def load_chamados_all():
    """Carrega e verticaliza chamados de 2025 e 2026"""
    try:
        # 2025
        raw_2025 = pd.read_excel(ARQ_CS, sheet_name="Chamados Mensais 2025", header=None)
        df_2025 = _verticalizar_chamados(raw_2025)
        
        # 2026 - IGNORAR SE VAZIO
        try:
            raw_2026 = pd.read_excel(ARQ_CS, sheet_name="Chamados Mensais 2026", header=None)
            df_2026 = _verticalizar_chamados(raw_2026)
        except:
            df_2026 = pd.DataFrame()
        
        # Concatenar apenas se 2026 tiver dados
        if not df_2026.empty:
            df = pd.concat([df_2025, df_2026], ignore_index=True)
        else:
            df = df_2025.copy()
        
        if not df.empty:
            df["MES_REF"] = pd.to_datetime(df["MES_REF"], errors="coerce")
            df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")
            df["MES"] = pd.to_numeric(df["MES"], errors="coerce").astype("Int64")
            df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0.0)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar chamados: {e}")
        return pd.DataFrame()

@st.cache_data
def load_base_cs_dashboard():
    """Carrega base consolidada para dashboard"""
    info = load_info_gerais()
    chamados = load_chamados_all()
    
    if info.empty or chamados.empty:
        st.warning("⚠️ Dados insuficientes para consolidação")
        return pd.DataFrame()
    
    df = chamados.merge(
        info[["CLIENTE", "AT_RISK", "CHURN_RISK", "VALOR_CONTRATO", "FAIXA_CONTATO",
              "DIAS_SEM_CONTATO", "CANCELADO", "DIAS_ATE_VENCIMENTO", "ALERTA_VENCIMENTO"]],
        on="CLIENTE",
        how="left"
    )
    
    df["AT_RISK"] = df["AT_RISK"].fillna("NÃO")
    df["CHURN_RISK"] = df["CHURN_RISK"].fillna("NÃO")
    df["VALOR_CONTRATO"] = df["VALOR_CONTRATO"].fillna(0.0)
    df["CANCELADO"] = df["CANCELADO"].fillna(False)
    
    return df
