"""
View: Risco Financeiro
Análise de impacto e priorização por valor
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.config import COLORS, ICONS
from modules.utils import format_currency, format_number, format_percent, calcular_health_score, get_health_label

def render_risco_financeiro(df_info, df_chamados):
    """
    Renderiza página de Risco Financeiro
    
    Args:
        df_info: DataFrame de informações gerais
        df_chamados: DataFrame de chamados consolidado
    """
    
    # ========== HEADER ==========
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                {ICONS['dollar']} Risco Financeiro
            </h1>
            <p class='page-subtitle'>
                Análise de impacto e priorização por valor de contrato
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if df_info.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # Filtrar apenas ativos
    df_ativos = df_info[~df_info['CANCELADO']]
    
    receita_total = df_ativos['VALOR_CONTRATO'].sum()
    
    # ========== KPIs FINANCEIROS ==========
    
    receita_at_risk = df_ativos[df_ativos['AT_RISK'] == 'SIM']['VALOR_CONTRATO'].sum()
    receita_churn_risk = df_ativos[df_ativos['CHURN_RISK'] == 'SIM']['VALOR_CONTRATO'].sum()
    receita_total_risco = df_ativos[
        (df_ativos['AT_RISK'] == 'SIM') | (df_ativos['CHURN_RISK'] == 'SIM')
    ]['VALOR_CONTRATO'].sum()
    
    ticket_medio = df_ativos['VALOR_CONTRATO'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['gradient_start']}, {COLORS['accent']});'>
                <div class='gradient-card-label'>{ICONS['dollar']} RECEITA TOTAL (MRR)</div>
                <div class='gradient-card-value'>{format_currency(receita_total)}</div>
                <div class='gradient-card-footer'>{len(df_ativos)} clientes ativos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        perc_at = (receita_at_risk / receita_total * 100) if receita_total > 0 else 0
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['warning']}, #F97316);'>
                <div class='gradient-card-label'>{ICONS['alert']} AT-RISK (MRR)</div>
                <div class='gradient-card-value'>{format_currency(receita_at_risk)}</div>
                <div class='gradient-card-footer'>{format_percent(perc_at)} do total</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        perc_churn = (receita_churn_risk / receita_total * 100) if receita_total > 0 else 0
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['danger']}, #DC2626);'>
                <div class='gradient-card-label'>{ICONS['fire']} CHURN RISK (MRR)</div>
                <div class='gradient-card-value'>{format_currency(receita_churn_risk)}</div>
                <div class='gradient-card-footer'>{format_percent(perc_churn)} do total</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['success']}, #10B981);'>
                <div class='gradient-card-label'>{ICONS['chart']} TICKET MÉDIO</div>
                <div class='gradient-card-value'>{format_currency(ticket_medio)}</div>
                <div class='gradient-card-footer'>Por cliente</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== CONCENTRAÇÃO DE RECEITA ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['target']} Concentração de Receita
        </div>
    """, unsafe_allow_html=True)
    
    # Agrupar por cliente ÚNICO (soma dos valores se houver duplicatas)
    df_ativos_grouped = df_ativos.groupby('CLIENTE').agg({
        'VALOR_CONTRATO': 'sum'
    }).reset_index()
    
    # Calcular participação de cada cliente
    df_ativos_sorted = df_ativos_grouped.sort_values('VALOR_CONTRATO', ascending=False).copy()
    df_ativos_sorted['PARTICIPACAO_%'] = (df_ativos_sorted['VALOR_CONTRATO'] / receita_total * 100) if receita_total > 0 else 0
    df_ativos_sorted['PARTICIPACAO_ACUM_%'] = df_ativos_sorted['PARTICIPACAO_%'].cumsum()
    
    # Top 10
    df_top10_valor = df_ativos_sorted.head(10)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # GRÁFICO ORDENADO: MAIOR → MENOR (de cima para baixo)
        df_top10_plot = df_top10_valor.sort_values('VALOR_CONTRATO', ascending=True)  # ascending=True para horizontal
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_top10_plot['CLIENTE'],
            x=df_top10_plot['VALOR_CONTRATO'],
            orientation='h',
            marker_color=COLORS['accent'],
            text=df_top10_plot['VALOR_CONTRATO'].apply(format_currency),
            textposition='auto',
            name='MRR'
        ))
        
        fig.update_layout(
            title="Top 10 Clientes por MRR (Maior no Topo)",
            xaxis_title="Valor (R$)",
            yaxis_title="Cliente",
            height=450,
            paper_bgcolor=COLORS['bg_primary'],
            plot_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Concentração")
        
        top3_valor = df_top10_valor.head(3)['VALOR_CONTRATO'].sum()
        top5_valor = df_top10_valor.head(5)['VALOR_CONTRATO'].sum()
        top10_valor = df_top10_valor['VALOR_CONTRATO'].sum()
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Top 3</div>
                <div class='stat-card-value'>{format_currency(top3_valor)}</div>
                <div class='stat-card-footer'>{format_percent(top3_valor/receita_total*100 if receita_total > 0 else 0)} da receita</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Top 5</div>
                <div class='stat-card-value'>{format_currency(top5_valor)}</div>
                <div class='stat-card-footer'>{format_percent(top5_valor/receita_total*100 if receita_total > 0 else 0)} da receita</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Top 10</div>
                <div class='stat-card-value'>{format_currency(top10_valor)}</div>
                <div class='stat-card-footer'>{format_percent(top10_valor/receita_total*100 if receita_total > 0 else 0)} da receita</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Curva ABC
        st.markdown("##### Curva ABC")
        
        clientes_80 = (df_ativos_sorted['PARTICIPACAO_ACUM_%'] <= 80).sum()
        clientes_95 = (df_ativos_sorted['PARTICIPACAO_ACUM_%'] <= 95).sum()
        
        st.write(f"**Classe A (80%):** {clientes_80} clientes")
        st.write(f"**Classe B (95%):** {clientes_95 - clientes_80} clientes")
        st.write(f"**Classe C (resto):** {len(df_ativos_sorted) - clientes_95} clientes")
    
    st.markdown("---")
    
    # ========== MATRIZ RISCO × IMPACTO ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['shield']} Matriz Risco × Impacto
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Eixo X**: Impacto (% da receita) | **Eixo Y**: Risco (100 - Health Score)")
    
    # Calcular Health Score para cada cliente ÚNICO
    df_ativos_unique = df_ativos.drop_duplicates(subset=['CLIENTE'])
    
    health_scores = []
    
    for _, cliente_row in df_ativos_unique.iterrows():
        cliente = cliente_row['CLIENTE']
        df_cliente_chamados = df_chamados[df_chamados['CLIENTE'] == cliente]
        
        # Pegar valor total do cliente (soma se houver múltiplos contratos)
        valor_total = df_ativos_grouped[df_ativos_grouped['CLIENTE'] == cliente]['VALOR_CONTRATO'].iloc[0]
        
        health_result = calcular_health_score(cliente_row, df_cliente_chamados)
        
        health_scores.append({
            'CLIENTE': cliente,
            'HEALTH_SCORE': health_result['score'],
            'VALOR_CONTRATO': valor_total,
            'AT_RISK': cliente_row['AT_RISK'],
            'CHURN_RISK': cliente_row['CHURN_RISK']
        })
    
    df_matriz = pd.DataFrame(health_scores)
    
    # Calcular impacto e risco
    df_matriz['IMPACTO_%'] = (df_matriz['VALOR_CONTRATO'] / receita_total * 100) if receita_total > 0 else 0
    df_matriz['RISCO_SCORE'] = 100 - df_matriz['HEALTH_SCORE']
    
    # Cores por quadrante
    def get_cor_quadrante(row):
        if row['IMPACTO_%'] > 5 and row['RISCO_SCORE'] > 40:
            return COLORS['danger']  # Alto impacto + Alto risco
        elif row['IMPACTO_%'] > 5:
            return COLORS['warning']  # Alto impacto + Baixo risco
        elif row['RISCO_SCORE'] > 40:
            return '#F97316'  # Baixo impacto + Alto risco
        else:
            return COLORS['success']  # Baixo impacto + Baixo risco
    
    df_matriz['COR'] = df_matriz.apply(get_cor_quadrante, axis=1)
    
    # Scatter plot
    fig = go.Figure()
    
    for cor in df_matriz['COR'].unique():
        df_temp = df_matriz[df_matriz['COR'] == cor]
        
        fig.add_trace(go.Scatter(
            x=df_temp['IMPACTO_%'],
            y=df_temp['RISCO_SCORE'],
            mode='markers+text',
            marker=dict(size=df_temp['VALOR_CONTRATO']/100, color=cor, opacity=0.7),
            text=df_temp['CLIENTE'],
            textposition='top center',
            textfont=dict(size=9),
            hovertemplate='<b>%{text}</b><br>Impacto: %{x:.2f}%<br>Risco: %{y:.1f}<br>MRR: ' + 
                         df_temp['VALOR_CONTRATO'].apply(format_currency) + '<extra></extra>',
            name=''
        ))
    
    # Linhas de referência
    fig.add_hline(y=40, line_dash="dash", line_color="gray", annotation_text="Risco Moderado")
    fig.add_vline(x=5, line_dash="dash", line_color="gray", annotation_text="Impacto 5%")
    
    fig.update_layout(
        title="Matriz Risco × Impacto (tamanho = valor MRR)",
        xaxis_title="Impacto (% da Receita)",
        yaxis_title="Risco (100 - Health Score)",
        height=600,
        showlegend=False,
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['card_bg'],
        font=dict(color=COLORS['primary'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Quadrantes críticos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 Quadrante Crítico")
        st.markdown("**Alto Impacto + Alto Risco**")
        
        df_critico = df_matriz[(df_matriz['IMPACTO_%'] > 5) & (df_matriz['RISCO_SCORE'] > 40)]
        
        if not df_critico.empty:
            st.warning(f"⚠️ **{len(df_critico)} clientes** neste quadrante!")
            
            df_display = df_critico.sort_values('RISCO_SCORE', ascending=False)
            df_display['VALOR_CONTRATO_FMT'] = df_display['VALOR_CONTRATO'].apply(format_currency)
            
            st.dataframe(
                df_display[['CLIENTE', 'IMPACTO_%', 'HEALTH_SCORE', 'VALOR_CONTRATO_FMT']].rename(columns={
                    'CLIENTE': 'Cliente',
                    'IMPACTO_%': 'Impacto (%)',
                    'HEALTH_SCORE': 'Health',
                    'VALOR_CONTRATO_FMT': 'MRR'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ Nenhum cliente neste quadrante!")
    
    with col2:
        st.markdown("#### 🟡 Quadrante Atenção")
        st.markdown("**Alto Impacto + Baixo Risco**")
        
        df_atencao = df_matriz[(df_matriz['IMPACTO_%'] > 5) & (df_matriz['RISCO_SCORE'] <= 40)]
        
        if not df_atencao.empty:
            st.info(f"📌 **{len(df_atencao)} clientes** para manter atenção")
            
            df_display = df_atencao.sort_values('IMPACTO_%', ascending=False)
            df_display['VALOR_CONTRATO_FMT'] = df_display['VALOR_CONTRATO'].apply(format_currency)
            
            st.dataframe(
                df_display[['CLIENTE', 'IMPACTO_%', 'HEALTH_SCORE', 'VALOR_CONTRATO_FMT']].rename(columns={
                    'CLIENTE': 'Cliente',
                    'IMPACTO_%': 'Impacto (%)',
                    'HEALTH_SCORE': 'Health',
                    'VALOR_CONTRATO_FMT': 'MRR'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📌 Nenhum cliente de alto impacto com baixo risco")
    
    st.markdown("---")
    
    # ========== DISTRIBUIÇÃO DE RECEITA ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['chart']} Distribuição de Receita
        </div>
    """, unsafe_allow_html=True)
    
    # Criar faixas de valor
    df_ativos_grouped['FAIXA_VALOR'] = pd.cut(
        df_ativos_grouped['VALOR_CONTRATO'],
        bins=[0, 1000, 3000, 5000, 10000, float('inf')],
        labels=['< R$ 1k', 'R$ 1-3k', 'R$ 3-5k', 'R$ 5-10k', '> R$ 10k']
    )
    
    faixa_dist = df_ativos_grouped.groupby('FAIXA_VALOR').agg({
        'CLIENTE': 'count',
        'VALOR_CONTRATO': 'sum'
    }).reset_index()
    
    faixa_dist.columns = ['Faixa', 'Qtd Clientes', 'Receita Total']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(data=[
            go.Pie(
                labels=faixa_dist['Faixa'],
                values=faixa_dist['Qtd Clientes'],
                hole=0.4,
                marker=dict(colors=[COLORS['success'], COLORS['info'], COLORS['accent'], 
                                   COLORS['warning'], COLORS['danger']])
            )
        ])
        
        fig.update_layout(
            title="Distribuição por Faixa (Quantidade)",
            height=400,
            paper_bgcolor=COLORS['bg_primary'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[
            go.Pie(
                labels=faixa_dist['Faixa'],
                values=faixa_dist['Receita Total'],
                hole=0.4,
                marker=dict(colors=[COLORS['success'], COLORS['info'], COLORS['accent'], 
                                   COLORS['warning'], COLORS['danger']])
            )
        ])
        
        fig.update_layout(
            title="Distribuição por Faixa (Receita)",
            height=400,
            paper_bgcolor=COLORS['bg_primary'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
