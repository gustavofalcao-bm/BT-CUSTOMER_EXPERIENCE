"""
Dashboard CS - Base Telco
Aplicação Principal
"""

import streamlit as st
from PIL import Image
import base64
import time
from pathlib import Path
from modules.config import COLORS, ICONS, CONFIG, ASSETS_DIR
from modules.styles import apply_premium_css
from modules.data_loader import load_info_gerais, load_chamados_all, load_base_cs_dashboard

# Imports das views
from views.visao_executiva import render_visao_executiva
from views.relacionamento import render_relacionamento
from views.suporte_qualidade import render_suporte_qualidade
from views.risco_financeiro import render_risco_financeiro
from views.cliente_360 import render_cliente_360

logo = Image.open("assets/pageicon.png")

# ==================== FUNÇÃO AUXILIAR ====================
def _get_logo_base64():
    """Carrega logo em base64"""
    try:
        logo_path = ASSETS_DIR / 'logo.gif'
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def mudar_pagina(pagina):
    """Muda de página com spinner visível"""
    st.session_state.pagina_atual = pagina
    # Forçar delay para spinner aparecer
    time.sleep(0.3)

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title=CONFIG['page_title'],
    page_icon=logo,
    layout=CONFIG['layout'],
    initial_sidebar_state=CONFIG['initial_sidebar_state']
)

# ==================== APLICAR CSS ====================
apply_premium_css()

# ==================== INICIALIZAÇÃO DO SESSION STATE ====================
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'visao_executiva'

# ==================== CARREGAR DADOS (COM CACHE) ====================
@st.cache_data
def carregar_dados():
    """Carrega todos os dados necessários"""
    info = load_info_gerais()
    chamados = load_chamados_all()
    dashboard = load_base_cs_dashboard()
    return info, chamados, dashboard

# Carregar dados
try:
    with st.spinner('🔄 Carregando dados...'):
        df_info, df_chamados, df_dashboard = carregar_dados()
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo da Base Telco
    logo_path = ASSETS_DIR / 'logo.gif'
    
    if logo_path.exists():
        logo_b64 = _get_logo_base64()
        if logo_b64:
            st.markdown(f"""
                <div style='text-align: center; padding: 1rem 0 1.5rem 0;'>
                    <img src='data:image/gif;base64,{logo_b64}' 
                         style='width: 180px; border-radius: 12px;' />
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='text-align: center; padding: 1rem 0 2rem 0;'>
                    <h2 style='color: {COLORS['primary']}; font-family: Sora;'>
                        {ICONS['shield']} Dashboard CS
                    </h2>
                    <p style='color: {COLORS['secondary']}; font-size: 0.9rem;'>
                        Customer Success
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem 0 2rem 0;'>
                <h2 style='color: {COLORS['primary']}; font-family: Sora;'>
                    {ICONS['shield']} Dashboard CS
                </h2>
                <p style='color: {COLORS['secondary']}; font-size: 0.9rem;'>
                    Customer Success
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu de navegação
    st.markdown(f"""
        <p style='font-size: 0.9rem; color: {COLORS['secondary']}; 
                  font-weight: 600; margin-bottom: 1rem;'>
            MENU PRINCIPAL
        </p>
    """, unsafe_allow_html=True)
    
    # Botões de navegação (com spinner)
    if st.button(
        f"{ICONS['dashboard']} Visão Executiva",
        key="nav_visao",
        use_container_width=True,
        type="primary" if st.session_state.pagina_atual == 'visao_executiva' else "secondary"
    ):
        with st.spinner('🔄 Carregando Visão Executiva...'):
            mudar_pagina('visao_executiva')
            st.rerun()
    
    if st.button(
        f"{ICONS['phone']} Relacionamento",
        key="nav_relacionamento",
        use_container_width=True,
        type="primary" if st.session_state.pagina_atual == 'relacionamento' else "secondary"
    ):
        with st.spinner('🔄 Carregando Relacionamento...'):
            mudar_pagina('relacionamento')
            st.rerun()
    
    if st.button(
        f"{ICONS['shield']} Suporte & Qualidade",
        key="nav_suporte",
        use_container_width=True,
        type="primary" if st.session_state.pagina_atual == 'suporte' else "secondary"
    ):
        with st.spinner('🔄 Carregando Suporte & Qualidade...'):
            mudar_pagina('suporte')
            st.rerun()
    
    if st.button(
        f"{ICONS['dollar']} Risco Financeiro",
        key="nav_risco",
        use_container_width=True,
        type="primary" if st.session_state.pagina_atual == 'risco' else "secondary"
    ):
        with st.spinner('🔄 Carregando Risco Financeiro...'):
            mudar_pagina('risco')
            st.rerun()
    
    if st.button(
        f"{ICONS['search']} Cliente 360°",
        key="nav_cliente",
        use_container_width=True,
        type="primary" if st.session_state.pagina_atual == 'cliente_360' else "secondary"
    ):
        with st.spinner('🔄 Carregando Cliente 360°...'):
            mudar_pagina('cliente_360')
            st.rerun()
    
    st.markdown("---")
    
    # Informações do sistema (COM CARDS)
    st.markdown(f"""
        <p style='font-size: 0.9rem; color: {COLORS['secondary']}; 
                  font-weight: 600; margin-bottom: 1rem;'>
            ESTATÍSTICAS
        </p>
    """, unsafe_allow_html=True)
    
    if not df_info.empty:
        total_clientes = len(df_info[~df_info['CANCELADO']])
        total_cancelados = df_info['CANCELADO'].sum()
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Clientes Ativos</div>
                <div class='stat-card-value'>{total_clientes}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Clientes Cancelados</div>
                <div class='stat-card-value' style='color: {COLORS['danger']};'>{total_cancelados}</div>
            </div>
        """, unsafe_allow_html=True)
    
    if not df_chamados.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        
        total_chamados = df_chamados[df_chamados['CATEGORIA'] == 'CHAMADOS']['VALOR'].sum()
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-card-label'>Total Chamados</div>
                <div class='stat-card-value'>{total_chamados:.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Botão de refresh
    if st.button("🔄 Atualizar Dados", key="refresh_sidebar", use_container_width=True):
        with st.spinner('🔄 Atualizando dados...'):
            st.cache_data.clear()
            time.sleep(0.5)
            st.rerun()
    
    # Footer
    st.markdown(f"""
        <div style='text-align: center; margin-top: 2rem; padding-top: 1rem; 
                    border-top: 1px solid {COLORS['border']}; color: {COLORS['secondary']}; 
                    font-size: 0.8rem;'>
            <p>Base Telco © 2026</p>
            <p>Dashboard CS v1.0</p>
        </div>
    """, unsafe_allow_html=True)

# ==================== ROTEAMENTO DE PÁGINAS ====================

if st.session_state.pagina_atual == 'visao_executiva':
    render_visao_executiva(df_info, df_chamados)

elif st.session_state.pagina_atual == 'relacionamento':
    render_relacionamento(df_info, df_chamados)

elif st.session_state.pagina_atual == 'suporte':
    render_suporte_qualidade(df_info, df_chamados)

elif st.session_state.pagina_atual == 'risco':
    render_risco_financeiro(df_info, df_chamados)

elif st.session_state.pagina_atual == 'cliente_360':
    render_cliente_360(df_info, df_chamados)

else:
    st.session_state.pagina_atual = 'visao_executiva'
    st.rerun()

