"""
View: Visão Executiva (Master)
Overview estratégico para gestão
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.config import COLORS, ICONS
from modules.utils import format_currency, format_number, format_percent, calcular_health_score, get_health_label

def render_visao_executiva(df_info, df_chamados):
    """
    Renderiza Visão Executiva
    
    Args:
        df_info: DataFrame de informações gerais
        df_chamados: DataFrame de chamados consolidado
    """
    
    # ========== HEADER ==========
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                {ICONS['dashboard']} Visão Executiva
            </h1>
            <p class='page-subtitle'>
                Overview estratégico da base de clientes
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if df_info.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # ========== KPIs PRINCIPAIS ==========
    
    # Filtrar apenas ativos
    df_ativos = df_info[~df_info['CANCELADO']]
    
    total_clientes = len(df_ativos)
    clientes_at_risk = (df_ativos['AT_RISK'] == 'SIM').sum()
    clientes_churn_risk = (df_ativos['CHURN_RISK'] == 'SIM').sum()
    
    receita_total = df_ativos['VALOR_CONTRATO'].sum()
    receita_em_risco = df_ativos[
        (df_ativos['AT_RISK'] == 'SIM') | (df_ativos['CHURN_RISK'] == 'SIM')
    ]['VALOR_CONTRATO'].sum()
    
    # Cards principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['gradient_start']}, {COLORS['accent']});'>
                <div class='gradient-card-label'>{ICONS['users']} CLIENTES ATIVOS</div>
                <div class='gradient-card-value'>{total_clientes}</div>
                <div class='gradient-card-footer'>Base ativa</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['warning']}, #F97316);'>
                <div class='gradient-card-label'>{ICONS['alert']} AT-RISK</div>
                <div class='gradient-card-value'>{clientes_at_risk}</div>
                <div class='gradient-card-footer'>{format_percent(clientes_at_risk/total_clientes*100) if total_clientes > 0 else '0%'} da base</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['danger']}, #DC2626);'>
                <div class='gradient-card-label'>{ICONS['fire']} CHURN RISK</div>
                <div class='gradient-card-value'>{clientes_churn_risk}</div>
                <div class='gradient-card-footer'>{format_percent(clientes_churn_risk/total_clientes*100) if total_clientes > 0 else '0%'} da base</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['success']}, #10B981);'>
                <div class='gradient-card-label'>{ICONS['dollar']} RECEITA MRR</div>
                <div class='gradient-card-value'>{format_currency(receita_total)}</div>
                <div class='gradient-card-footer'>Mensal recorrente</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== RECEITA EM RISCO + ÚLTIMO CONTATO (REORDENADO: MAIOR PRA MENOR) ==========
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class='section-title'>
                {ICONS['calendar']} Último Contato
            </div>
        """, unsafe_allow_html=True)
        
        # Distribuição de último contato
        contato_dist = df_ativos['FAIXA_CONTATO'].value_counts().reindex(['0-30', '30-90', '90+'], fill_value=0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=contato_dist.index,
                y=contato_dist.values,
                marker_color=[COLORS['success'], COLORS['warning'], COLORS['danger']],
                text=contato_dist.values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Distribuição por Faixa (dias)",
            xaxis_title="Dias desde último contato",
            yaxis_title="Quantidade de clientes",
            height=350,
            showlegend=False,
            paper_bgcolor=COLORS['bg_primary'],
            plot_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        clientes_90_mais = (df_ativos['FAIXA_CONTATO'] == '90+').sum()
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Clientes 90+ dias</div>
                <div class='stat-card-value' style='color: {COLORS['danger']};'>{clientes_90_mais}</div>
                <div class='stat-card-footer'>{format_percent(clientes_90_mais/total_clientes*100) if total_clientes > 0 else '0%'} da base</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        perc_risco = (receita_em_risco / receita_total * 100) if receita_total > 0 else 0
        
        st.markdown(f"""
            <div class='section-title'>
                {ICONS['target']} Receita em Risco
            </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=perc_risco,
            title={'text': "% da Receita em Risco", 'font': {'color': COLORS['primary']}},
            delta={'reference': 10, 'increasing': {'color': COLORS['danger']}},
            gauge={
                'axis': {'range': [None, 100], 'tickcolor': COLORS['primary']},
                'bar': {'color': COLORS['danger']},
                'steps': [
                    {'range': [0, 10], 'color': COLORS['success']},
                    {'range': [10, 30], 'color': COLORS['warning']},
                    {'range': [30, 100], 'color': COLORS['danger']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor=COLORS['bg_primary'],
            font=dict(color=COLORS['primary'])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Valor em Risco (MRR)</div>
                <div class='stat-card-value' style='color: {COLORS['danger']};'>{format_currency(receita_em_risco)}</div>
                <div class='stat-card-footer'>{format_number(clientes_at_risk + clientes_churn_risk)} clientes</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== NOVOS CLIENTES (COM CARDS) ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['star']} Novos Clientes (Últimos 90 dias)
        </div>
    """, unsafe_allow_html=True)
    
    hoje = pd.Timestamp.now()
    df_ativos['DIAS_ATIVACAO'] = (hoje - df_ativos['DATA_ATIVACAO']).dt.days
    
    novos_30 = (df_ativos['DIAS_ATIVACAO'] <= 30).sum()
    novos_60 = ((df_ativos['DIAS_ATIVACAO'] > 30) & (df_ativos['DIAS_ATIVACAO'] <= 60)).sum()
    novos_90 = ((df_ativos['DIAS_ATIVACAO'] > 60) & (df_ativos['DIAS_ATIVACAO'] <= 90)).sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>0-30 dias</div>
                <div class='stat-card-value' style='color: {COLORS['success']};'>{novos_30}</div>
                <div class='stat-card-footer'>Novíssimos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>30-60 dias</div>
                <div class='stat-card-value' style='color: {COLORS['accent']};'>{novos_60}</div>
                <div class='stat-card-footer'>Em onboarding</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>60-90 dias</div>
                <div class='stat-card-value' style='color: {COLORS['warning']};'>{novos_90}</div>
                <div class='stat-card-footer'>Recentes</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== CONTRATOS PRÓXIMOS DO VENCIMENTO (COM CARDS) ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['clock']} Contratos Próximos do Vencimento
        </div>
    """, unsafe_allow_html=True)
    
    vencimento_dist = df_ativos['ALERTA_VENCIMENTO'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        vencidos = vencimento_dist.get('VENCIDO', 0)
        st.markdown(f"""
            <div class='stat-card' style='border-color: {COLORS['danger']};'>
                <div class='stat-card-label'>Vencidos</div>
                <div class='stat-card-value' style='color: {COLORS['danger']};'>{vencidos}</div>
                <div class='stat-card-footer'>Urgente!</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        v30 = vencimento_dist.get('30_DIAS', 0)
        st.markdown(f"""
            <div class='stat-card' style='border-color: {COLORS['warning']};'>
                <div class='stat-card-label'>30 dias</div>
                <div class='stat-card-value' style='color: {COLORS['warning']};'>{v30}</div>
                <div class='stat-card-footer'>Atenção</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        v60 = vencimento_dist.get('60_DIAS', 0)
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>60 dias</div>
                <div class='stat-card-value' style='color: {COLORS['accent']};'>{v60}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        v90 = vencimento_dist.get('90_DIAS', 0)
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>90 dias</div>
                <div class='stat-card-value' style='color: {COLORS['success']};'>{v90}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== TOP 10 PRIORIDADE ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['target']} Top 10 Clientes Prioritários
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Ranking baseado em**: Health Score (saúde) + Impacto Financeiro (% da receita)")
    
    # Calcular Health Score para cada cliente
    health_scores = []
    
    for _, cliente_row in df_ativos.iterrows():
        cliente = cliente_row['CLIENTE']
        df_cliente_chamados = df_chamados[df_chamados['CLIENTE'] == cliente]
        
        health_result = calcular_health_score(cliente_row, df_cliente_chamados)
        health_scores.append({
            'CLIENTE': cliente,
            'HEALTH_SCORE': health_result['score'],
            'VALOR_CONTRATO': cliente_row['VALOR_CONTRATO'],
            'AT_RISK': cliente_row['AT_RISK'],
            'CHURN_RISK': cliente_row['CHURN_RISK'],
            'FAIXA_CONTATO': cliente_row['FAIXA_CONTATO']
        })
    
    df_health = pd.DataFrame(health_scores)
    
    # Calcular impacto (% da receita)
    df_health['IMPACTO_%'] = (df_health['VALOR_CONTRATO'] / receita_total * 100) if receita_total > 0 else 0
    
    # Priority Score = inverso do health * impacto
    df_health['PRIORITY_SCORE'] = (100 - df_health['HEALTH_SCORE']) * (1 + df_health['IMPACTO_%'] / 10)
    
    # Top 10
    df_top10 = df_health.nlargest(10, 'PRIORITY_SCORE')
    
    # Tabela formatada
    df_display = df_top10[['CLIENTE', 'HEALTH_SCORE', 'IMPACTO_%', 'VALOR_CONTRATO', 'AT_RISK', 'CHURN_RISK', 'FAIXA_CONTATO']].copy()
    df_display['HEALTH_SCORE'] = df_display['HEALTH_SCORE'].apply(lambda x: f"{x:.0f}")
    df_display['IMPACTO_%'] = df_display['IMPACTO_%'].apply(lambda x: f"{x:.1f}%")
    df_display['VALOR_CONTRATO'] = df_display['VALOR_CONTRATO'].apply(format_currency)
    
    df_display.columns = ['Cliente', 'Health', 'Impacto %', 'MRR', 'At-Risk', 'Churn Risk', 'Último Contato']
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
