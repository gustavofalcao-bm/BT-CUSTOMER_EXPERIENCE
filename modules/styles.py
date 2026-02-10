"""
Sistema de estilos CSS premium - DARK MODE
"""

import streamlit as st
from modules.config import COLORS

def apply_premium_css():
    """
    Aplica CSS premium DARK MODE ao dashboard CS
    """
    
    st.markdown(f"""
    <style>
        /* ===== OCULTAR BOTÃO DEPLOY ===== */
        .stAppDeployButton {{
            display: none;
        }}
        
        /* ===== 1. CSS VARIABLES (ROOT) ===== */
        :root {{
            --bg-primary: {COLORS['bg_primary']};
            --bg-secondary: {COLORS['bg_secondary']};
            --bg-tertiary: {COLORS['bg_tertiary']};
            --card-bg: {COLORS['card_bg']};
            --text-primary: {COLORS['primary']};
            --text-secondary: {COLORS['secondary']};
            --text-muted: {COLORS['muted']};
            --accent: {COLORS['accent']};
            --accent-light: {COLORS['accent_light']};
            --success: {COLORS['success']};
            --warning: {COLORS['warning']};
            --danger: {COLORS['danger']};
            --border: {COLORS['border']};
            --hover: {COLORS['hover']};
        }}
        
        /* ===== 2. IMPORTS DE FONTES ===== */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Sora:wght@700&display=swap');
        
        /* ===== 3. RESET E BASE ===== */
        * {{
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        /* Background principal */
        .stApp {{
            background: {COLORS['bg_primary']};
            color: {COLORS['primary']};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: {COLORS['bg_secondary']};
            border-right: 1px solid {COLORS['border']};
        }}
        
        [data-testid="stSidebar"] * {{
            color: {COLORS['primary']} !important;
        }}
        
        /* ===== 4. COMPONENTES STREAMLIT ===== */
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['accent']});
            color: white !important;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
            background: linear-gradient(135deg, {COLORS['accent']}, {COLORS['accent_light']});
        }}
        
        /* Primary button (sidebar) */
        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {COLORS['accent']}, {COLORS['accent_light']});
            border-left: 4px solid {COLORS['accent_light']};
        }}
        
        .stButton > button[kind="secondary"] {{
            background: transparent;
            border: 1px solid {COLORS['border']};
            color: {COLORS['secondary']} !important;
        }}
        
        .stButton > button[kind="secondary"]:hover {{
            background: {COLORS['hover']};
            border-color: {COLORS['accent']};
            color: {COLORS['primary']} !important;
        }}
        
        /* Selectbox */
        .stSelectbox > div > div {{
            background: {COLORS['card_bg']};
            border-radius: 12px;
            border: 2px solid {COLORS['border']};
            color: {COLORS['primary']};
        }}
        
        .stSelectbox label {{
            color: {COLORS['secondary']} !important;
        }}
        
        /* Number Input */
        .stNumberInput > div > div {{
            background: {COLORS['card_bg']};
            border-radius: 12px;
            border: 2px solid {COLORS['border']};
        }}
        
        .stNumberInput input {{
            color: {COLORS['primary']} !important;
        }}
        
        /* DataFrame */
        .stDataFrame {{
            background: {COLORS['card_bg']};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }}
        
        .stDataFrame [data-testid="stDataFrameResizable"] {{
            background: {COLORS['card_bg']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 12px;
            padding: 12px 24px;
            background: {COLORS['card_bg']};
            color: {COLORS['secondary']};
            border: 1px solid {COLORS['border']};
            font-weight: 600;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['accent']});
            color: white !important;
            border-color: {COLORS['accent']};
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {COLORS['primary']} !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {COLORS['secondary']} !important;
        }}
        
        /* Info/Warning/Error boxes */
        .stAlert {{
            background: {COLORS['card_bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            color: {COLORS['primary']};
        }}
        
        .stSuccess {{
            background: rgba(16, 185, 129, 0.1);
            border-left: 4px solid {COLORS['success']};
        }}
        
        .stWarning {{
            background: rgba(245, 158, 11, 0.1);
            border-left: 4px solid {COLORS['warning']};
        }}
        
        .stError {{
            background: rgba(239, 68, 68, 0.1);
            border-left: 4px solid {COLORS['danger']};
        }}
        
        .stInfo {{
            background: rgba(59, 130, 246, 0.1);
            border-left: 4px solid {COLORS['accent']};
        }}
        
        /* Spinner */
        .stSpinner > div {{
            border-top-color: {COLORS['accent']} !important;
        }}
        
        /* ===== 5. CUSTOM CLASSES ===== */
        
        /* Page Titles */
        .page-title {{
            font-family: 'Sora', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: {COLORS['primary']};
            margin-bottom: 0.5rem;
        }}
        
        .page-subtitle {{
            font-size: 1.1rem;
            color: {COLORS['secondary']};
            font-weight: 500;
            margin-bottom: 2rem;
        }}
        
        /* Section Titles */
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {COLORS['primary']};
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid {COLORS['accent']};
            display: inline-block;
        }}
        
        /* Gradient Cards */
        .gradient-card {{
            /* Background aplicado diretamente via style inline para compatibilidade com Streamlit Cloud */
            padding: 1.5rem;
            border-radius: 16px;
            color: white;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .gradient-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 32px rgba(59, 130, 246, 0.3);
        }}
        
        .gradient-card-label {{
            font-size: 0.9rem;
            opacity: 0.95;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .gradient-card-value {{
            font-size: 2rem;
            font-weight: 700;
            font-family: 'Sora', sans-serif;
            margin: 0.5rem 0;
        }}
        
        .gradient-card-footer {{
            font-size: 0.85rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }}
        
        /* Stat Card (para métricas soltas) */
        .stat-card {{
            background: {COLORS['card_bg']};
            padding: 1.25rem;
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
            transition: all 0.3s ease;
            margin-bottom: 0.75rem;
        }}
        
        .stat-card:hover {{
            border-color: {COLORS['accent']};
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }}
        
        .stat-card-label {{
            font-size: 0.85rem;
            color: {COLORS['secondary']};
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .stat-card-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {COLORS['primary']};
            font-family: 'Sora', sans-serif;
        }}
        
        .stat-card-footer {{
            font-size: 0.8rem;
            color: {COLORS['muted']};
            margin-top: 0.5rem;
        }}
        
        /* ===== 6. TABELAS HTML CUSTOMIZADAS ===== */
        
        .table-container {{
            max-height: 600px;
            overflow-y: auto;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid {COLORS['border']};
            background: {COLORS['card_bg']};
        }}
        
        .custom-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background: {COLORS['card_bg']};
        }}
        
        .custom-table thead {{
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .custom-table th {{
            background: linear-gradient(135deg, {COLORS['table_header']}, {COLORS['accent']});
            color: white;
            padding: 14px 10px;
            text-align: center;
            font-weight: 600;
            border-bottom: 2px solid {COLORS['accent']};
        }}
        
        .custom-table th:first-child {{
            text-align: left;
            padding-left: 15px;
        }}
        
        .custom-table td {{
            padding: 12px 10px;
            text-align: center;
            border-bottom: 1px solid {COLORS['border']};
            color: {COLORS['primary']};
            background: {COLORS['card_bg']};
        }}
        
        .custom-table td:first-child {{
            text-align: left;
            font-weight: 600;
            padding-left: 15px;
        }}
        
        .custom-table tbody tr:hover {{
            background-color: {COLORS['hover']} !important;
        }}
        
        .custom-table tbody tr:hover td {{
            background-color: {COLORS['hover']} !important;
        }}
        
        /* ===== 7. SCROLLBAR CUSTOMIZADA ===== */
        
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS['bg_tertiary']};
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, {COLORS['gradient_start']}, {COLORS['accent']});
            border-radius: 10px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(180deg, {COLORS['accent']}, {COLORS['accent_light']});
        }}
        
        /* ===== 8. OUTROS AJUSTES ===== */
        
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        
        p, span, div {{
            line-height: 1.6;
            color: {COLORS['primary']};
        }}
        
        a {{
            color: {COLORS['accent']};
            text-decoration: none;
            transition: color 0.2s ease;
        }}
        
        a:hover {{
            color: {COLORS['accent_light']};
            text-decoration: underline;
        }}
        
        hr {{
            border-color: {COLORS['border']};
        }}
        
        /* Labels */
        label {{
            color: {COLORS['secondary']} !important;
        }}
        
        /* Download button */
        .stDownloadButton > button {{
            background: {COLORS['card_bg']};
            border: 1px solid {COLORS['border']};
            color: {COLORS['primary']} !important;
        }}
        
        .stDownloadButton > button:hover {{
            background: {COLORS['hover']};
            border-color: {COLORS['accent']};
        }}
    </style>
    """, unsafe_allow_html=True)
