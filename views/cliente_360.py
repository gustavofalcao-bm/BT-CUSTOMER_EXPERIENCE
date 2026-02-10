"""
View: Cliente 360
Visão detalhada individual do cliente
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from modules.config import COLORS, ICONS
from modules.utils import (
    format_currency, format_number, format_percent, 
    calcular_health_score, get_health_label, classificar_perfil_incidentes
)

def render_cliente_360(df_info, df_chamados):
    """
    Renderiza página Cliente 360
    
    Args:
        df_info: DataFrame de informações gerais
        df_chamados: DataFrame de chamados consolidado
    """
    
    # ========== HEADER ==========
    st.markdown(f"""
        <div style='margin-bottom: 2.5rem;'>
            <h1 class='page-title'>
                {ICONS['search']} Cliente 360°
            </h1>
            <p class='page-subtitle'>
                Visão completa e detalhada do cliente selecionado
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if df_info.empty:
        st.warning("⚠️ Nenhum dado disponível")
        return
    
    # Filtrar apenas ativos
    df_ativos = df_info[~df_info['CANCELADO']]
    
    # ========== SELEÇÃO DO CLIENTE ==========
    
    clientes_lista = sorted(df_ativos['CLIENTE'].unique())
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        cliente_selecionado = st.selectbox(
            "🔍 Selecione o Cliente:",
            clientes_lista,
            index=0 if clientes_lista else None
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Atualizar Dados", key="refresh_cliente360", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    if not cliente_selecionado:
        st.info("👈 Selecione um cliente para visualizar os detalhes")
        return
    
    # Dados do cliente
    cliente_row = df_ativos[df_ativos['CLIENTE'] == cliente_selecionado].iloc[0]
    df_cliente_chamados = df_chamados[df_chamados['CLIENTE'] == cliente_selecionado].copy()
    
    st.markdown("---")
    
    # ========== CABEÇALHO DO CLIENTE ==========
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']}); 
                        padding: 1.5rem; border-radius: 16px; color: white;'>
                <h2 style='margin: 0; font-family: Sora;'>{cliente_selecionado}</h2>
                <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
                    {cliente_row.get('ATIVIDADE PRINCIPAL ', 'N/A')}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Health Score
        health_result = calcular_health_score(cliente_row, df_cliente_chamados)
        health_score = health_result['score']
        health_label, health_cor = get_health_label(health_score)
        
        st.markdown(f"""
            <div style='background: {health_cor}; padding: 1.5rem; border-radius: 16px; 
                        color: white; text-align: center;'>
                <div style='font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem;'>HEALTH SCORE</div>
                <div style='font-size: 2.5rem; font-weight: 700; font-family: Sora;'>{health_score:.0f}</div>
                <div style='font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem;'>{health_label}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Valor MRR
        valor_mrr = cliente_row.get('VALOR_CONTRATO', 0)
        
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {COLORS['success']}, #10B981); 
                        padding: 1.5rem; border-radius: 16px; color: white; text-align: center;'>
                <div style='font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem;'>VALOR MRR</div>
                <div style='font-size: 1.8rem; font-weight: 700; font-family: Sora;'>{format_currency(valor_mrr)}</div>
                <div style='font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem;'>Mensal</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== INFORMAÇÕES CADASTRAIS ==========
    
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['file']} Informações Cadastrais
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**👤 Contato:**")
        st.write(cliente_row.get('CONTATO', 'N/A'))
        
        st.markdown("**📞 Telefone:**")
        st.write(cliente_row.get('TELEFONE', 'N/A'))
        
        st.markdown("**📧 E-mail:**")
        st.write(cliente_row.get('E-MAIL', 'N/A'))
    
    with col2:
        st.markdown("**🏢 Unidade:**")
        st.write(cliente_row.get('UNIDADE', 'N/A'))
        
        st.markdown("**👨‍💼 Gerente Responsável:**")
        st.write(cliente_row.get('GERENTE RESPONSÁVEL', 'N/A'))
        
        st.markdown("**🎯 Customer Success Manager:**")
        st.write(cliente_row.get('Customer Success Manager', 'N/A'))
    
    with col3:
        st.markdown("**🔧 Restrição/Solução:**")
        st.write(cliente_row.get('RESTRIÇÃO/SOLUÇÃO', 'N/A'))
        
        st.markdown("**📅 Data de Ativação:**")
        data_ativ = cliente_row.get('DATA_ATIVACAO')
        st.write(data_ativ.strftime('%d/%m/%Y') if pd.notna(data_ativ) else 'N/A')
        
        st.markdown("**📆 Vigência:**")
        vig_inicio = cliente_row.get('VIGENCIA_INICIAL')
        vig_fim = cliente_row.get('VIGENCIA_FINAL')
        if pd.notna(vig_inicio) and pd.notna(vig_fim):
            st.write(f"{vig_inicio.strftime('%d/%m/%Y')} até {vig_fim.strftime('%d/%m/%Y')}")
        else:
            st.write('N/A')
    
    # Observações
    obs = cliente_row.get('OBSERVAÇÃO', '')
    if obs and str(obs).strip() and str(obs).strip().lower() != 'nan':
        st.markdown("**💬 Observações:**")
        st.info(obs)
    
    st.markdown("---")
    
    # ========== FLAGS DE RISCO ==========
    
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['alert']} Status e Alertas
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        at_risk = cliente_row.get('AT_RISK', 'NÃO')
        cor = COLORS['danger'] if at_risk == 'SIM' else COLORS['success']
        st.markdown(f"""
            <div style='background: {cor}; padding: 1rem; border-radius: 12px; 
                        color: white; text-align: center;'>
                <div style='font-size: 0.85rem; margin-bottom: 0.5rem;'>AT-RISK</div>
                <div style='font-size: 1.5rem; font-weight: 700;'>{at_risk}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        churn_risk = cliente_row.get('CHURN_RISK', 'NÃO')
        cor = COLORS['danger'] if churn_risk == 'SIM' else COLORS['success']
        st.markdown(f"""
            <div style='background: {cor}; padding: 1rem; border-radius: 12px; 
                        color: white; text-align: center;'>
                <div style='font-size: 0.85rem; margin-bottom: 0.5rem;'>CHURN RISK</div>
                <div style='font-size: 1.5rem; font-weight: 700;'>{churn_risk}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        dias_sem_contato = cliente_row.get('DIAS_SEM_CONTATO', 999)
        if pd.isna(dias_sem_contato):
            dias_texto = 'N/A'
            cor = COLORS['gray_light']
        elif dias_sem_contato <= 30:
            dias_texto = f"{int(dias_sem_contato)} dias"
            cor = COLORS['success']
        elif dias_sem_contato <= 90:
            dias_texto = f"{int(dias_sem_contato)} dias"
            cor = COLORS['warning']
        else:
            dias_texto = f"{int(dias_sem_contato)} dias"
            cor = COLORS['danger']
        
        st.markdown(f"""
            <div style='background: {cor}; padding: 1rem; border-radius: 12px; 
                        color: white; text-align: center;'>
                <div style='font-size: 0.85rem; margin-bottom: 0.5rem;'>ÚLTIMO CONTATO</div>
                <div style='font-size: 1.5rem; font-weight: 700;'>{dias_texto}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        dias_venc = cliente_row.get('DIAS_ATE_VENCIMENTO', 999)
        if pd.isna(dias_venc):
            venc_texto = 'N/A'
            cor = COLORS['gray_light']
        elif dias_venc < 0:
            venc_texto = 'VENCIDO'
            cor = COLORS['danger']
        elif dias_venc <= 30:
            venc_texto = f"{int(dias_venc)} dias"
            cor = COLORS['danger']
        elif dias_venc <= 90:
            venc_texto = f"{int(dias_venc)} dias"
            cor = COLORS['warning']
        else:
            venc_texto = f"{int(dias_venc)} dias"
            cor = COLORS['success']
        
        st.markdown(f"""
            <div style='background: {cor}; padding: 1rem; border-radius: 12px; 
                        color: white; text-align: center;'>
                <div style='font-size: 0.85rem; margin-bottom: 0.5rem;'>VENCIMENTO</div>
                <div style='font-size: 1.5rem; font-weight: 700;'>{venc_texto}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== DETALHAMENTO DO HEALTH SCORE ==========
    
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['heart']} Detalhamento do Health Score
        </div>
    """, unsafe_allow_html=True)
    
    detalhes = health_result['detalhes']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Contato", f"{detalhes['contato']}/25", f"Peso: 25%")
    
    with col2:
        st.metric("Incidentes", f"{detalhes['incidentes']}/30", f"Peso: 30%")
    
    with col3:
        st.metric("SLA", f"{detalhes['sla']}/25", f"Peso: 25%")
    
    with col4:
        st.metric("Flags", f"{detalhes['flags']}/20", f"Peso: 20%")
    
    # Gráfico de radar do Health Score
    categories = ['Contato', 'Incidentes', 'SLA', 'Flags']
    values = [
        (detalhes['contato'] / 25) * 100,
        (detalhes['incidentes'] / 30) * 100,
        (detalhes['sla'] / 25) * 100,
        (detalhes['flags'] / 20) * 100
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color=health_cor),
        line=dict(color=health_cor, width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False,
        title="Distribuição dos Componentes do Health Score",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========== HISTÓRICO DE CHAMADOS ==========
    
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['chart']} Histórico de Chamados
        </div>
    """, unsafe_allow_html=True)
    
    if not df_cliente_chamados.empty:
        
        # Agrupar por mês
        df_mensal = df_cliente_chamados.groupby(['MES_REF', 'CATEGORIA'])['VALOR'].sum().reset_index()
        df_mensal = df_mensal.sort_values('MES_REF')
        
        # Pivot
        df_pivot = df_mensal.pivot(index='MES_REF', columns='CATEGORIA', values='VALOR').fillna(0)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Evolução Temporal", "📈 Métricas Mensais", "📋 Tabela Detalhada"])
        
        with tab1:
            # Gráfico de linha temporal
            fig = go.Figure()
            
            if 'CHAMADOS' in df_pivot.columns:
                fig.add_trace(go.Scatter(
                    x=df_pivot.index,
                    y=df_pivot['CHAMADOS'],
                    mode='lines+markers',
                    name='Chamados Totais',
                    line=dict(color=COLORS['secondary'], width=3),
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
                title="Evolução Mensal de Chamados",
                xaxis_title="Mês",
                yaxis_title="Quantidade",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Taxa de incidentes
                if 'CHAMADOS' in df_pivot.columns and 'INCIDENTES' in df_pivot.columns:
                    df_pivot['TAXA_INC'] = (df_pivot['INCIDENTES'] / df_pivot['CHAMADOS'] * 100).fillna(0)
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=df_pivot.index,
                        y=df_pivot['TAXA_INC'],
                        marker_color=COLORS['danger'],
                        text=df_pivot['TAXA_INC'].apply(lambda x: f"{x:.1f}%"),
                        textposition='auto'
                    ))
                    
                    fig.update_layout(
                        title="Taxa de Incidentes (%)",
                        xaxis_title="Mês",
                        yaxis_title="Taxa (%)",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # SLA
                if 'DENTRO_SLA' in df_pivot.columns and 'FORA_SLA' in df_pivot.columns:
                    total_sla = df_pivot['DENTRO_SLA'] + df_pivot['FORA_SLA']
                    df_pivot['TAXA_SLA'] = ((df_pivot['DENTRO_SLA'] / total_sla * 100)
                                           .replace([float('inf'), -float('inf')], 0)
                                           .fillna(0))
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df_pivot.index,
                        y=df_pivot['TAXA_SLA'],
                        mode='lines+markers',
                        fill='tozeroy',
                        line=dict(color=COLORS['success'], width=3),
                        marker=dict(size=8)
                    ))
                    
                    fig.add_hline(y=90, line_dash="dash", line_color="red", 
                                 annotation_text="Meta 90%")
                    
                    fig.update_layout(
                        title="Taxa de SLA (%)",
                        xaxis_title="Mês",
                        yaxis_title="Taxa (%)",
                        height=350
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Tabela pivot formatada
            df_display = df_pivot.reset_index()
            df_display['MES_REF'] = pd.to_datetime(df_display['MES_REF']).dt.strftime('%m/%Y')
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'MES_REF': 'Mês/Ano'
                }
            )
        
        # KPIs resumo
        st.markdown("#### 📊 Resumo do Período")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = df_pivot.get('CHAMADOS', pd.Series([0])).sum()
            st.metric("Total Chamados", format_number(total))
        
        with col2:
            total_inc = df_pivot.get('INCIDENTES', pd.Series([0])).sum()
            st.metric("Total Incidentes", format_number(total_inc))
        
        with col3:
            total_sol = df_pivot.get('SOLICITACOES', pd.Series([0])).sum()
            st.metric("Total Solicitações", format_number(total_sol))
        
        with col4:
            dentro = df_pivot.get('DENTRO_SLA', pd.Series([0])).sum()
            fora = df_pivot.get('FORA_SLA', pd.Series([0])).sum()
            total_sla_geral = dentro + fora
            taxa = (dentro / total_sla_geral * 100) if total_sla_geral > 0 else 0
            st.metric("Taxa SLA Média", f"{taxa:.1f}%")
        
        # Perfil de incidentes
        perfil = classificar_perfil_incidentes(df_cliente_chamados)
        
        perfil_map = {
            'SEM_INCIDENTES': ('🟢 Sem Incidentes', COLORS['success']),
            'ESPORADICO': ('🟡 Esporádico', COLORS['warning']),
            'RECORRENTE': ('🟠 Recorrente', '#F97316'),
            'CRESCENTE': ('🔴 Crescente', COLORS['danger'])
        }
        
        label, cor = perfil_map.get(perfil, (perfil, '#6B7280'))
        
        st.markdown(f"""
            <div style='background: {cor}; padding: 1rem; border-radius: 12px; 
                        color: white; text-align: center; margin-top: 1rem;'>
                <div style='font-size: 0.9rem; margin-bottom: 0.5rem;'>PERFIL DE INCIDENTES</div>
                <div style='font-size: 1.5rem; font-weight: 700;'>{label}</div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("📌 Nenhum histórico de chamados disponível para este cliente")
    
    st.markdown("---")
    
    # ========== SUGESTÕES DE AÇÃO ==========
    
    st.markdown(f"""
        <div class='section-title'>
            {ICONS['target']} Sugestões de Ação
        </div>
    """, unsafe_allow_html=True)
    
    sugestoes = []
    
    # Sugestões baseadas em flags
    if at_risk == 'SIM':
        sugestoes.append({
            'prioridade': 'ALTA',
            'acao': 'Cliente marcado como AT-RISK',
            'recomendacao': 'Agendar reunião estratégica imediata com stakeholders'
        })
    
    if churn_risk == 'SIM':
        sugestoes.append({
            'prioridade': 'CRÍTICA',
            'acao': 'Cliente em risco de cancelamento',
            'recomendacao': 'Escalar para gerência e criar plano de retenção urgente'
        })
    
    # Sugestões baseadas em contato
    if dias_sem_contato > 90:
        sugestoes.append({
            'prioridade': 'ALTA',
            'acao': f'{int(dias_sem_contato)} dias sem contato',
            'recomendacao': 'Realizar contato proativo e atualizar cadastro'
        })
    elif dias_sem_contato > 30:
        sugestoes.append({
            'prioridade': 'MÉDIA',
            'acao': f'{int(dias_sem_contato)} dias sem contato',
            'recomendacao': 'Agendar check-in de rotina'
        })
    
    # Sugestões baseadas em vencimento
    if pd.notna(dias_venc):
        if dias_venc < 0:
            sugestoes.append({
                'prioridade': 'CRÍTICA',
                'acao': 'Contrato vencido',
                'recomendacao': 'Contatar imediatamente para renovação'
            })
        elif dias_venc <= 30:
            sugestoes.append({
                'prioridade': 'ALTA',
                'acao': f'Contrato vence em {int(dias_venc)} dias',
                'recomendacao': 'Iniciar processo de renovação com proposta comercial'
            })
        elif dias_venc <= 60:
            sugestoes.append({
                'prioridade': 'MÉDIA',
                'acao': f'Contrato vence em {int(dias_venc)} dias',
                'recomendacao': 'Preparar proposta de renovação'
            })
    
    # Sugestões baseadas em SLA
    if not df_cliente_chamados.empty:
        df_recente = df_cliente_chamados.nlargest(3, 'MES_REF')
        dentro_sla = df_recente[df_recente['CATEGORIA'] == 'DENTRO_SLA']['VALOR'].sum()
        fora_sla = df_recente[df_recente['CATEGORIA'] == 'FORA_SLA']['VALOR'].sum()
        total_sla_calc = dentro_sla + fora_sla
        
        if total_sla_calc > 0:
            taxa_sla_calc = (dentro_sla / total_sla_calc * 100)
            
            if taxa_sla_calc < 80:
                sugestoes.append({
                    'prioridade': 'ALTA',
                    'acao': f'SLA crítico: {taxa_sla_calc:.1f}% (últimos 3 meses)',
                    'recomendacao': 'Revisar processos de atendimento e identificar gargalos'
                })
            elif taxa_sla_calc < 90:
                sugestoes.append({
                    'prioridade': 'MÉDIA',
                    'acao': f'SLA abaixo da meta: {taxa_sla_calc:.1f}%',
                    'recomendacao': 'Monitorar atendimento e otimizar resposta'
                })
    
    # Sugestões baseadas em incidentes
    perfil = classificar_perfil_incidentes(df_cliente_chamados)
    
    if perfil == 'CRESCENTE':
        sugestoes.append({
            'prioridade': 'ALTA',
            'acao': 'Incidentes em tendência crescente',
            'recomendacao': 'Investigar causa raiz e implementar ações preventivas'
        })
    elif perfil == 'RECORRENTE':
        sugestoes.append({
            'prioridade': 'MÉDIA',
            'acao': 'Incidentes recorrentes detectados',
            'recomendacao': 'Analisar padrões e oferecer treinamento ao cliente'
        })
    
    # Exibir sugestões
    if sugestoes:
        for sug in sugestoes:
            if sug['prioridade'] == 'CRÍTICA':
                st.error(f"🔴 **{sug['prioridade']}**: {sug['acao']}\n\n💡 {sug['recomendacao']}")
            elif sug['prioridade'] == 'ALTA':
                st.warning(f"🟠 **{sug['prioridade']}**: {sug['acao']}\n\n💡 {sug['recomendacao']}")
            else:
                st.info(f"🟡 **{sug['prioridade']}**: {sug['acao']}\n\n💡 {sug['recomendacao']}")
    else:
        st.success("✅ Nenhuma ação crítica identificada. Cliente em situação estável!")

