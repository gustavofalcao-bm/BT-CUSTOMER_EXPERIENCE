"""
Funções utilitárias reutilizáveis
"""

import pandas as pd

def format_currency(value):
    """Formata valor como moeda brasileira"""
    if pd.isna(value) or value == 0:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value):
    """Formata número com separador de milhares"""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}".replace(",", ".")

def format_percent(value, decimals=1):
    """Formata valor como percentual"""
    if pd.isna(value):
        return "0.0%"
    return f"{value:.{decimals}f}%"

def calcular_health_score(row, df_chamados_cliente):
    """
    Calcula Health Score de um cliente (0-100)
    Usa os últimos 3 meses COM DADOS (ignora meses vazios)
    
    Args:
        row: linha do DataFrame de informações gerais
        df_chamados_cliente: DataFrame filtrado com chamados deste cliente
    
    Returns:
        dict com score e detalhamento
    """
    score = 0
    detalhes = {}
    
    # 1. PONTOS POR ÚLTIMO CONTATO (0-25)
    dias_sem_contato = row.get('DIAS_SEM_CONTATO', 999)
    
    if pd.isna(dias_sem_contato) or dias_sem_contato > 90:
        pontos_contato = 5
    elif dias_sem_contato <= 30:
        pontos_contato = 25
    elif dias_sem_contato <= 90:
        pontos_contato = 15
    else:
        pontos_contato = 5
    
    score += pontos_contato
    detalhes['contato'] = pontos_contato
    
    # 2. PONTOS POR INCIDENTES (0-30)
    if not df_chamados_cliente.empty:
        # CORREÇÃO: Identificar meses COM DADOS (total de chamados > 0)
        df_chamados_por_mes = df_chamados_cliente[
            df_chamados_cliente['CATEGORIA'] == 'CHAMADOS'
        ].groupby('MES_REF')['VALOR'].sum().reset_index()
        
        # Filtrar apenas meses com chamados > 0
        meses_com_dados = df_chamados_por_mes[df_chamados_por_mes['VALOR'] > 0]['MES_REF'].tolist()
        
        # Pegar últimos 3 meses COM DADOS
        meses_com_dados = sorted(meses_com_dados, reverse=True)[:3]
        
        if len(meses_com_dados) > 0:
            df_recente = df_chamados_cliente[df_chamados_cliente['MES_REF'].isin(meses_com_dados)]
            
            total_chamados = df_recente[df_recente['CATEGORIA'] == 'CHAMADOS']['VALOR'].sum()
            total_incidentes = df_recente[df_recente['CATEGORIA'] == 'INCIDENTES']['VALOR'].sum()
            
            if total_chamados > 0:
                taxa_incidentes = (total_incidentes / total_chamados) * 100
                
                if taxa_incidentes == 0:
                    pontos_incidentes = 30
                elif taxa_incidentes < 10:
                    pontos_incidentes = 25
                elif taxa_incidentes < 25:
                    pontos_incidentes = 15
                elif taxa_incidentes < 50:
                    pontos_incidentes = 8
                else:
                    pontos_incidentes = 3
            else:
                pontos_incidentes = 30
        else:
            pontos_incidentes = 30
        
        score += pontos_incidentes
        detalhes['incidentes'] = pontos_incidentes
    else:
        score += 30
        detalhes['incidentes'] = 30
    
    # 3. PONTOS POR SLA (0-25)
    if not df_chamados_cliente.empty:
        # CORREÇÃO: Identificar meses COM DADOS de SLA (dentro + fora > 0)
        df_sla_por_mes = df_chamados_cliente[
            df_chamados_cliente['CATEGORIA'].isin(['DENTRO_SLA', 'FORA_SLA'])
        ].groupby('MES_REF')['VALOR'].sum().reset_index()
        
        # Filtrar apenas meses com SLA > 0
        meses_com_sla = df_sla_por_mes[df_sla_por_mes['VALOR'] > 0]['MES_REF'].tolist()
        
        # Pegar últimos 3 meses COM DADOS de SLA
        meses_com_sla = sorted(meses_com_sla, reverse=True)[:3]
        
        if len(meses_com_sla) > 0:
            df_recente = df_chamados_cliente[df_chamados_cliente['MES_REF'].isin(meses_com_sla)]
            
            dentro_sla = df_recente[df_recente['CATEGORIA'] == 'DENTRO_SLA']['VALOR'].sum()
            fora_sla = df_recente[df_recente['CATEGORIA'] == 'FORA_SLA']['VALOR'].sum()
            total_sla = dentro_sla + fora_sla
            
            if total_sla > 0:
                taxa_dentro_sla = (dentro_sla / total_sla) * 100
                
                if taxa_dentro_sla >= 95:
                    pontos_sla = 25
                elif taxa_dentro_sla >= 85:
                    pontos_sla = 18
                elif taxa_dentro_sla >= 70:
                    pontos_sla = 10
                else:
                    pontos_sla = 3
            else:
                pontos_sla = 25
        else:
            pontos_sla = 25
        
        score += pontos_sla
        detalhes['sla'] = pontos_sla
    else:
        score += 25
        detalhes['sla'] = 25
    
    # 4. PENALIDADES POR FLAGS (0-20)
    pontos_flags = 20
    
    if row.get('AT_RISK') == 'SIM':
        pontos_flags -= 8
    
    if row.get('CHURN_RISK') == 'SIM':
        pontos_flags -= 12
    
    score += max(0, pontos_flags)
    detalhes['flags'] = max(0, pontos_flags)
    
    return {
        'score': min(100, max(0, score)),
        'detalhes': detalhes
    }

def get_health_label(score):
    """Retorna label e cor baseado no health score"""
    if score >= 80:
        return "EXCELENTE", "#059669"
    elif score >= 60:
        return "BOM", "#10B981"
    elif score >= 40:
        return "ATENÇÃO", "#F59E0B"
    else:
        return "CRÍTICO", "#DC2626"

def classificar_perfil_incidentes(df_chamados_cliente):
    """
    Classifica perfil de incidentes do cliente
    Usa os últimos 6 meses COM DADOS (ignora meses vazios)
    
    Returns:
        str: "SEM_INCIDENTES" | "ESPORADICO" | "RECORRENTE" | "CRESCENTE"
    """
    if df_chamados_cliente.empty:
        return "SEM_INCIDENTES"
    
    # CORREÇÃO: Identificar meses COM DADOS de incidentes
    df_inc = df_chamados_cliente[df_chamados_cliente['CATEGORIA'] == 'INCIDENTES'].copy()
    
    # Agrupar por mês
    df_inc_mensal = df_inc.groupby('MES_REF')['VALOR'].sum().reset_index()
    df_inc_mensal = df_inc_mensal.sort_values('MES_REF', ascending=False)
    
    # Se não houver incidentes
    if df_inc_mensal['VALOR'].sum() == 0:
        return "SEM_INCIDENTES"
    
    # Pegar últimos 6 meses (mesmo os com 0, para análise de tendência)
    df_inc_mensal = df_inc_mensal.head(6)
    
    # Contar meses com incidentes
    meses_com_incidentes = (df_inc_mensal['VALOR'] > 0).sum()
    
    # Verificar tendência crescente (últimos 3 meses)
    if len(df_inc_mensal) >= 3:
        ultimos_3 = df_inc_mensal.head(3)['VALOR'].tolist()
        if len(ultimos_3) == 3:
            # Crescente: cada mês tem mais incidentes que o anterior
            if ultimos_3[0] > ultimos_3[1] > 0 and ultimos_3[1] > ultimos_3[2]:
                return "CRESCENTE"
    
    # Recorrente: 3+ meses com incidentes
    if meses_com_incidentes >= 3:
        return "RECORRENTE"
    
    # Esporádico: 1-2 meses com incidentes
    return "ESPORADICO"
