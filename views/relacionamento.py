"""
View: Relacionamento & Cadência
Foco em operação do time CS
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.config import COLORS, ICONS
from modules.utils import format_number, format_percent

def render_relacionamento(df_info, df_chamados):
    """
    Renderiza página de Relacionamento & Cadência
    
    Args:
        df_info: DataFrame de informações gerais
        df_chamados: DataFrame de chamados consolidado
    """
    
    # ========== HEADER ==========
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                {ICONS['phone']} Relacionamento & Cadência
            </h1>
            <p class='page-subtitle'>
                Gestão de contatos e relacionamento com clientes
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if df_info.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # Filtrar apenas ativos
    df_ativos = df_info[~df_info['CANCELADO']]
    total_clientes = len(df_ativos)
    
    # ========== KPIs DE CADÊNCIA ==========
    
    clientes_0_30 = (df_ativos['FAIXA_CONTATO'] == '0-30').sum()
    clientes_30_90 = (df_ativos['FAIXA_CONTATO'] == '30-90').sum()
    clientes_90_mais = (df_ativos['FAIXA_CONTATO'] == '90+').sum()
    sem_contato = df_ativos['ULTIMO_CONTATO_DT'].isna().sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['success']}, #10B981);'>
                <div class='gradient-card-label'>{ICONS['check']} 0-30 DIAS</div>
                <div class='gradient-card-value'>{clientes_0_30}</div>
                <div class='gradient-card-footer'>{format_percent(clientes_0_30/total_clientes*100) if total_clientes > 0 else '0%'}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['warning']}, #F97316);'>
                <div class='gradient-card-label'>{ICONS['clock']} 30-90 DIAS</div>
                <div class='gradient-card-value'>{clientes_30_90}</div>
                <div class='gradient-card-footer'>{format_percent(clientes_30_90/total_clientes*100) if total_clientes > 0 else '0%'}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, {COLORS['danger']}, #DC2626);'>
                <div class='gradient-card-label'>{ICONS['alert']} 90+ DIAS</div>
                <div class='gradient-card-value'>{clientes_90_mais}</div>
                <div class='gradient-card-footer'>{format_percent(clientes_90_mais/total_clientes*100) if total_clientes > 0 else '0%'}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='gradient-card' style='background: linear-gradient(145deg, #6B7280, #4B5563);'>
                <div class='gradient-card-label'>{ICONS['search']} SEM REGISTRO</div>
                <div class='gradient-card-value'>{sem_contato}</div>
                <div class='gradient-card-footer'>{format_percent(sem_contato/total_clientes*100) if total_clientes > 0 else '0%'}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== ANÁLISE POR CSM (REORDENADO: GRÁFICO MAIOR PRIMEIRO) ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['users']} Distribuição por CSM
        </div>
    """, unsafe_allow_html=True)
    
    # Agrupar por CSM
    if 'Customer Success Manager' in df_ativos.columns:
        df_csm = df_ativos.groupby('Customer Success Manager').agg({
            'CLIENTE': 'count',
            'FAIXA_CONTATO': lambda x: (x == '90+').sum()
        }).reset_index()
        
        df_csm.columns = ['CSM', 'Total Clientes', 'Clientes 90+']
        df_csm['% Críticos'] = (df_csm['Clientes 90+'] / df_csm['Total Clientes'] * 100).round(1)
        
        # INVERTIDO: Gráfico maior primeiro
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Total Clientes',
                x=df_csm['CSM'],
                y=df_csm['Total Clientes'],
                marker_color=COLORS['accent'],
                text=df_csm['Total Clientes'],
                textposition='auto'
            ))
            
            fig.add_trace(go.Bar(
                name='Críticos (90+)',
                x=df_csm['CSM'],
                y=df_csm['Clientes 90+'],
                marker_color=COLORS['danger'],
                text=df_csm['Clientes 90+'],
                textposition='auto'
            ))
            
            fig.update_layout(
                title="Carteira por CSM",
                xaxis_title="Customer Success Manager",
                yaxis_title="Quantidade de Clientes",
                barmode='group',
                height=400,
                paper_bgcolor=COLORS['bg_primary'],
                plot_bgcolor=COLORS['card_bg'],
                font=dict(color=COLORS['primary'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Resumo por CSM")
            st.dataframe(
                df_csm[['CSM', 'Total Clientes', 'Clientes 90+', '% Críticos']],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("📌 Coluna 'Customer Success Manager' não disponível")
    
    st.markdown("---")
    
    # ========== ANÁLISE POR UNIDADE ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['target']} Distribuição por Unidade
        </div>
    """, unsafe_allow_html=True)
    
    if 'UNIDADE' in df_ativos.columns:
        df_unidade = df_ativos.groupby('UNIDADE').agg({
            'CLIENTE': 'count',
            'FAIXA_CONTATO': lambda x: (x == '90+').sum()
        }).reset_index()
        
        df_unidade.columns = ['Unidade', 'Total', 'Críticos 90+']
        df_unidade = df_unidade.sort_values('Total', ascending=False).head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Total',
            y=df_unidade['Unidade'],
            x=df_unidade['Total'],
            orientation='h',
            marker_color=COLORS['accent'],
            text=df_unidade['Total'],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Críticos',
            y=df_unidade['Unidade'],
            x=df_unidade['Críticos 90+'],
            orientation='h',
            marker_color=COLORS['danger'],
            text=df_unidade['Críticos 90+'],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Top 10 Unidades",
            xaxis_title="Quantidade",
            yaxis_title="Unidade",
            height=400,
            barmode='group',
            paper_bgcolor=COLORS['bg_primary'],
            plot_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['primary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📌 Coluna 'UNIDADE' não disponível")
    
    st.markdown("---")
    
    # ========== LISTA ACIONÁVEL: CLIENTES 90+ DIAS (HIGHLIGHT CORRIGIDO) ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['alert']} Ação Necessária: Clientes 90+ dias sem contato
        </div>
    """, unsafe_allow_html=True)
    
    df_criticos = df_ativos[df_ativos['FAIXA_CONTATO'] == '90+'].copy()
    
    if not df_criticos.empty:
        st.warning(f"⚠️ **{len(df_criticos)} clientes** necessitam contato urgente!")
        
        # Colunas para exibição
        colunas_exibir = ['CLIENTE', 'Customer Success Manager', 'UNIDADE', 
                          'CONTATO', 'TELEFONE', 'E-MAIL', 'DIAS_SEM_CONTATO', 'OBSERVAÇÃO']
        
        colunas_disponiveis = [c for c in colunas_exibir if c in df_criticos.columns]
        
        df_display = df_criticos[colunas_disponiveis].copy()
        df_display = df_display.sort_values('DIAS_SEM_CONTATO', ascending=False)
        
        # Renomear para exibição
        rename_map = {
            'CLIENTE': 'Cliente',
            'Customer Success Manager': 'CSM',
            'UNIDADE': 'Unidade',
            'CONTATO': 'Contato',
            'TELEFONE': 'Telefone',
            'E-MAIL': 'E-mail',
            'DIAS_SEM_CONTATO': 'Dias',
            'OBSERVAÇÃO': 'Observação'
        }
        
        df_display = df_display.rename(columns=rename_map)
        
        # HIGHLIGHT CORRIGIDO: Vermelho escuro com contraste
        def highlight_critico(row):
            if row.get('Dias', 0) > 150:
                # Vermelho escuro para dark mode
                return [f'background-color: #7F1D1D; color: #FEE2E2; font-weight: 600;'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            df_display.style.apply(highlight_critico, axis=1),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Botão de download
        csv = df_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar Lista (CSV)",
            data=csv,
            file_name="clientes_90dias_sem_contato.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ Nenhum cliente com 90+ dias sem contato!")
    
    st.markdown("---")
    
    # ========== HYGIENE DE DADOS (COM CARDS) ==========
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['settings']} Qualidade dos Dados
        </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Data Hygiene**: % de clientes com dados cadastrais completos")
    
    # Calcular completude
    total = len(df_ativos)
    
    com_contato = df_ativos['CONTATO'].notna().sum()
    com_telefone = df_ativos['TELEFONE'].notna().sum()
    com_email = df_ativos['E-MAIL'].notna().sum()
    com_ultimo_contato = df_ativos['ULTIMO_CONTATO_DT'].notna().sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        perc = (com_contato / total * 100) if total > 0 else 0
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Com Contato</div>
                <div class='stat-card-value'>{com_contato}/{total}</div>
                <div class='stat-card-footer'>{perc:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        perc = (com_telefone / total * 100) if total > 0 else 0
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Com Telefone</div>
                <div class='stat-card-value'>{com_telefone}/{total}</div>
                <div class='stat-card-footer'>{perc:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        perc = (com_email / total * 100) if total > 0 else 0
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Com E-mail</div>
                <div class='stat-card-value'>{com_email}/{total}</div>
                <div class='stat-card-footer'>{perc:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        perc = (com_ultimo_contato / total * 100) if total > 0 else 0
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Com Data Contato</div>
                <div class='stat-card-value'>{com_ultimo_contato}/{total}</div>
                <div class='stat-card-footer'>{perc:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de completude
    dados_hygiene = {
        'Campo': ['Contato', 'Telefone', 'E-mail', 'Último Contato'],
        'Completo': [com_contato, com_telefone, com_email, com_ultimo_contato],
        'Incompleto': [total - com_contato, total - com_telefone, total - com_email, total - com_ultimo_contato]
    }
    
    df_hygiene = pd.DataFrame(dados_hygiene)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Completo',
        x=df_hygiene['Campo'],
        y=df_hygiene['Completo'],
        marker_color=COLORS['success']
    ))
    
    fig.add_trace(go.Bar(
        name='Incompleto',
        x=df_hygiene['Campo'],
        y=df_hygiene['Incompleto'],
        marker_color=COLORS['danger']
    ))
    
    fig.update_layout(
        title="Completude dos Dados Cadastrais",
        barmode='stack',
        height=350,
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['card_bg'],
        font=dict(color=COLORS['primary'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
