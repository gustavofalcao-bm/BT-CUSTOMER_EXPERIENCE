"""
View: Suporte & Qualidade
Análise de chamados, incidentes e SLA
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.config import COLORS, ICONS
from modules.utils import format_number, format_percent, format_currency, classificar_perfil_incidentes

def render_suporte_qualidade(df_info, df_chamados):
    """
    Renderiza página de Suporte & Qualidade
    
    Args:
        df_info: DataFrame de informações gerais
        df_chamados: DataFrame de chamados consolidado
    """
    
    # ========== HEADER ==========
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                {ICONS['shield']} Suporte & Qualidade
            </h1>
            <p class='page-subtitle'>
                Análise de chamados, incidentes e performance de SLA
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if df_chamados.empty:
        st.warning("⚠️ Nenhum dado de chamados disponível")
        return
    
    # ========== KPIs GERAIS ==========
    
    total_chamados = df_chamados[df_chamados['CATEGORIA'] == 'CHAMADOS']['VALOR'].sum()
    total_incidentes = df_chamados[df_chamados['CATEGORIA'] == 'INCIDENTES']['VALOR'].sum()
    total_solicitacoes = df_chamados[df_chamados['CATEGORIA'] == 'SOLICITACOES']['VALOR'].sum()
    
    dentro_sla = df_chamados[df_chamados['CATEGORIA'] == 'DENTRO_SLA']['VALOR'].sum()
    fora_sla = df_chamados[df_chamados['CATEGORIA'] == 'FORA_SLA']['VALOR'].sum()
    total_sla = dentro_sla + fora_sla
    taxa_sla = (dentro_sla / total_sla * 100) if total_sla > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['gradient_start']}, {COLORS['accent']});'>
                <div class='gradient-card-label'>{ICONS['chart']} TOTAL CHAMADOS</div>
                <div class='gradient-card-value'>{format_number(total_chamados)}</div>
                <div class='gradient-card-footer'>Histórico completo</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        perc_inc = (total_incidentes / total_chamados * 100) if total_chamados > 0 else 0
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['danger']}, #EF4444);'>
                <div class='gradient-card-label'>{ICONS['alert']} INCIDENTES</div>
                <div class='gradient-card-value'>{format_number(total_incidentes)}</div>
                <div class='gradient-card-footer'>{format_percent(perc_inc)} do total</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        perc_sol = (total_solicitacoes / total_chamados * 100) if total_chamados > 0 else 0
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['success']}, #10B981);'>
                <div class='gradient-card-label'>{ICONS['check']} SOLICITAÇÕES</div>
                <div class='gradient-card-value'>{format_number(total_solicitacoes)}</div>
                <div class='gradient-card-footer'>{format_percent(perc_sol)} do total</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        cor_sla = COLORS['success'] if taxa_sla >= 90 else COLORS['warning'] if taxa_sla >= 75 else COLORS['danger']
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {cor_sla}, {cor_sla});'>
                <div class='gradient-card-label'>{ICONS['clock']} TAXA SLA</div>
                <div class='gradient-card-value'>{format_percent(taxa_sla)}</div>
                <div class='gradient-card-footer'>{format_number(dentro_sla)} dentro / {format_number(fora_sla)} fora</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== EVOLUÇÃO TEMPORAL ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['trending_up']} Evolução Mensal
        </div>
    """, unsafe_allow_html=True)
    
    # Agrupar por mês
    df_mensal = df_chamados.groupby(['MES_REF', 'CATEGORIA'])['VALOR'].sum().reset_index()
    df_mensal = df_mensal.sort_values('MES_REF')
    
    # Pivot para facilitar visualização
    df_pivot = df_mensal.pivot(index='MES_REF', columns='CATEGORIA', values='VALOR').fillna(0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de chamados totais
        fig = go.Figure()
        
        if 'CHAMADOS' in df_pivot.columns:
            fig.add_trace(go.Scatter(
                x=df_pivot.index,
                y=df_pivot['CHAMADOS'],
                mode='lines+markers',
                name='Chamados Totais',
                line=dict(color=COLORS['accent'], width=3),
                marker=dict(size=8)
            ))
        
        if 'INCIDENTES' in df_pivot.columns:
            fig.add_trace(go.Scatter(
                x=df_pivot.index,
                y=df_pivot['INCIDENTES'],
                mode='lines+markers',
                name='Incidentes',
                line=dict(color=COLORS['danger'], width=2),
                marker=dict(size=6)
            ))
        
        if 'SOLICITACOES' in df_pivot.columns:
            fig.add_trace(go.Scatter(
                x=df_pivot.index,
                y=df_pivot['SOLICITACOES'],
                mode='lines+markers',
                name='Solicitações',
                line=dict(color=COLORS['success'], width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title="Chamados, Incidentes e Solicitações",
            xaxis_title="Mês",
            yaxis_title="Quantidade",
            height=400,
            hovermode='x unified',
            paper_bgcolor=COLORS['bg_primary'],
            plot_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de SLA
        fig = go.Figure()
        
        if 'DENTRO_SLA' in df_pivot.columns and 'FORA_SLA' in df_pivot.columns:
            fig.add_trace(go.Bar(
                x=df_pivot.index,
                y=df_pivot['DENTRO_SLA'],
                name='Dentro do SLA',
                marker_color=COLORS['success']
            ))
            
            fig.add_trace(go.Bar(
                x=df_pivot.index,
                y=df_pivot['FORA_SLA'],
                name='Fora do SLA',
                marker_color=COLORS['danger']
            ))
        
        fig.update_layout(
            title="Performance de SLA Mensal",
            xaxis_title="Mês",
            yaxis_title="Quantidade",
            barmode='stack',
            height=400,
            paper_bgcolor=COLORS['bg_primary'],
            plot_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========== ANÁLISE POR CLIENTE ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['users']} Análise por Cliente
        </div>
    """, unsafe_allow_html=True)
    
    # Agrupar por cliente
    df_por_cliente = df_chamados.groupby(['CLIENTE', 'CATEGORIA'])['VALOR'].sum().reset_index()
    df_cliente_pivot = df_por_cliente.pivot(index='CLIENTE', columns='CATEGORIA', values='VALOR').fillna(0)
    
    # Calcular métricas
    df_cliente_pivot['TOTAL_CHAMADOS'] = df_cliente_pivot.get('CHAMADOS', 0)
    df_cliente_pivot['TAXA_INCIDENTES'] = (
        (df_cliente_pivot.get('INCIDENTES', 0) / df_cliente_pivot['TOTAL_CHAMADOS'] * 100)
        .fillna(0)
    )
    
    total_sla_cliente = df_cliente_pivot.get('DENTRO_SLA', 0) + df_cliente_pivot.get('FORA_SLA', 0)
    df_cliente_pivot['TAXA_SLA'] = (
        (df_cliente_pivot.get('DENTRO_SLA', 0) / total_sla_cliente * 100)
        .replace([float('inf'), -float('inf')], 0)
        .fillna(0)
    )
    
    # Classificar perfil de incidentes (ÚNICO POR CLIENTE)
    df_ativos = df_info[~df_info['CANCELADO']]
    
    # Pegar lista única de clientes
    clientes_unicos = df_ativos['CLIENTE'].drop_duplicates().tolist()
    
    perfis = []
    for cliente in clientes_unicos:
        df_cliente_chamados = df_chamados[df_chamados['CLIENTE'] == cliente]
        perfil = classificar_perfil_incidentes(df_cliente_chamados)
        perfis.append({'CLIENTE': cliente, 'PERFIL_INCIDENTES': perfil})
    
    df_perfis = pd.DataFrame(perfis)
    
    # Tabs para diferentes visões
    tab1, tab2, tab3 = st.tabs(["📊 Top Clientes por Volume", "🔴 Perfil de Incidentes", "📉 SLA Crítico"])
    
    with tab1:
        # Top 20 clientes por chamados (ORDENADO CORRETAMENTE: MAIOR → MENOR)
        df_top20 = df_cliente_pivot.nlargest(20, 'TOTAL_CHAMADOS').reset_index()
        df_top20 = df_top20.sort_values('TOTAL_CHAMADOS', ascending=True)  # ascending=True para gráfico horizontal (menor embaixo)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=df_top20['CLIENTE'],
            x=df_top20['TOTAL_CHAMADOS'],
            orientation='h',
            marker_color=COLORS['accent'],
            text=df_top20['TOTAL_CHAMADOS'].apply(lambda x: f"{x:.0f}"),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Top 20 Clientes - Total de Chamados (Maior no Topo)",
            xaxis_title="Quantidade",
            yaxis_title="Cliente",
            height=600,
            paper_bgcolor=COLORS['bg_primary'],
            plot_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("#### Distribuição por Perfil de Incidentes")
        
        perfil_dist = df_perfis['PERFIL_INCIDENTES'].value_counts()
        
        perfil_map = {
            'SEM_INCIDENTES': ('🟢 Sem Incidentes', COLORS['success']),
            'ESPORADICO': ('🟡 Esporádico', COLORS['warning']),
            'RECORRENTE': ('🟠 Recorrente', '#F97316'),
            'CRESCENTE': ('🔴 Crescente', COLORS['danger'])
        }
        
        labels = [perfil_map.get(p, (p, '#6B7280'))[0] for p in perfil_dist.index]
        colors = [perfil_map.get(p, (p, '#6B7280'))[1] for p in perfil_dist.index]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            for perfil, count in perfil_dist.items():
                label, cor = perfil_map.get(perfil, (perfil, '#6B7280'))
                perc = (count / len(df_perfis) * 100) if len(df_perfis) > 0 else 0
                
                st.markdown(f"""
                    <div class='stat-card'>
                        <div class='stat-card-label'>{label}</div>
                        <div class='stat-card-value' style='color: {cor};'>{count}</div>
                        <div class='stat-card-footer'>{perc:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=perfil_dist.values,
                    hole=0.4,
                    marker=dict(colors=colors),
                    textinfo='label+percent',
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Distribuição de Perfis",
                height=400,
                paper_bgcolor=COLORS['bg_primary'],
                font=dict(color=COLORS['primary'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Lista de clientes críticos (recorrente/crescente) - JÁ ÚNICO
        df_criticos_inc = df_perfis[df_perfis['PERFIL_INCIDENTES'].isin(['RECORRENTE', 'CRESCENTE'])].copy()
        
        if not df_criticos_inc.empty:
            st.warning(f"⚠️ **{len(df_criticos_inc)} clientes únicos** com incidentes recorrentes ou crescentes")
            
            # Merge com info para pegar CSM (pegar primeiro registro por cliente)
            df_ativos_unique = df_ativos.drop_duplicates(subset=['CLIENTE'])
            
            df_display = df_criticos_inc.merge(
                df_ativos_unique[['CLIENTE', 'Customer Success Manager', 'VALOR_CONTRATO']],
                on='CLIENTE',
                how='left'
            )
            
            df_display = df_display.merge(
                df_cliente_pivot[['TOTAL_CHAMADOS', 'TAXA_INCIDENTES']].reset_index(),
                on='CLIENTE',
                how='left'
            )
            
            df_display['PERFIL_INCIDENTES'] = df_display['PERFIL_INCIDENTES'].map(
                lambda x: perfil_map.get(x, (x, ''))[0]
            )
            
            # Formatar MRR
            df_display['VALOR_CONTRATO_FMT'] = df_display['VALOR_CONTRATO'].apply(format_currency)
            
            df_display = df_display.sort_values('TAXA_INCIDENTES', ascending=False)
            
            st.dataframe(
                df_display[['CLIENTE', 'PERFIL_INCIDENTES', 'Customer Success Manager', 
                           'TOTAL_CHAMADOS', 'TAXA_INCIDENTES', 'VALOR_CONTRATO_FMT']].rename(columns={
                    'CLIENTE': 'Cliente',
                    'PERFIL_INCIDENTES': 'Perfil',
                    'Customer Success Manager': 'CSM',
                    'TOTAL_CHAMADOS': 'Chamados',
                    'TAXA_INCIDENTES': 'Taxa Inc. (%)',
                    'VALOR_CONTRATO_FMT': 'MRR'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        # Clientes com SLA < 80% E TAXA_SLA > 0 (IGNORA OS 0/0)
        df_sla_critico = df_cliente_pivot[
            (df_cliente_pivot['TAXA_SLA'] < 80) & 
            (df_cliente_pivot['TAXA_SLA'] > 0)
        ].reset_index()
        
        df_sla_critico = df_sla_critico.sort_values('TAXA_SLA', ascending=True)  # Menores primeiro (para horizontal)
        
        if not df_sla_critico.empty:
            st.warning(f"⚠️ **{len(df_sla_critico)} clientes** com SLA abaixo de 80% (excluindo 0/0)")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=df_sla_critico['CLIENTE'],
                x=df_sla_critico['TAXA_SLA'],
                orientation='h',
                marker_color=COLORS['danger'],
                text=df_sla_critico['TAXA_SLA'].apply(lambda x: f"{x:.1f}%"),
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Clientes com SLA Crítico (< 80%, excluindo 0/0)",
                xaxis_title="Taxa SLA (%)",
                yaxis_title="Cliente",
                height=max(400, len(df_sla_critico) * 25),
                paper_bgcolor=COLORS['bg_primary'],
                plot_bgcolor=COLORS['card_bg'],
                font=dict(color=COLORS['primary'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada (ÚNICO POR CLIENTE + MRR FORMATADO)
            df_ativos_unique = df_ativos.drop_duplicates(subset=['CLIENTE'])
            
            df_display = df_sla_critico.merge(
                df_ativos_unique[['CLIENTE', 'Customer Success Manager', 'AT_RISK', 'CHURN_RISK']],
                on='CLIENTE',
                how='left'
            )
            
            st.dataframe(
                df_display[['CLIENTE', 'Customer Success Manager', 'TAXA_SLA', 
                           'DENTRO_SLA', 'FORA_SLA', 'AT_RISK', 'CHURN_RISK']].rename(columns={
                    'CLIENTE': 'Cliente',
                    'Customer Success Manager': 'CSM',
                    'TAXA_SLA': 'SLA (%)',
                    'DENTRO_SLA': 'Dentro',
                    'FORA_SLA': 'Fora',
                    'AT_RISK': 'At-Risk',
                    'CHURN_RISK': 'Churn Risk'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ Todos os clientes com SLA >= 80% (ou sem dados válidos)!")
