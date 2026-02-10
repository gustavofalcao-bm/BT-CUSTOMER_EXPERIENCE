"""
Configurações globais do Dashboard CS
"""

from pathlib import Path

# ==================== CORES (DARK MODE) ====================
COLORS = {
    # Backgrounds
    'bg_primary': '#0A1628',      # Fundo principal (azul escuro profundo)
    'bg_secondary': '#1E3A5F',    # Sidebar/cards (azul médio escuro)
    'bg_tertiary': '#162541',     # Alternativo
    'card_bg': '#1E293B',         # Cards/containers
    
    # Textos
    'primary': '#E2E8F0',         # Texto principal (branco suave)
    'secondary': '#94A3B8',       # Texto secundário (cinza claro)
    'muted': '#64748B',           # Texto discreto
    
    # Destaques
    'accent': '#3B82F6',          # Azul claro (botões, links)
    'accent_light': '#60A5FA',    # Azul hover
    'accent_dark': '#2563EB',     # Azul pressed
    
    # Status
    'success': '#10B981',         # Verde
    'warning': '#F59E0B',         # Amarelo/Laranja
    'danger': '#EF4444',          # Vermelho
    'info': '#3B82F6',            # Info (azul)
    
    # Estrutura
    'border': '#334155',          # Bordas
    'divider': '#1E293B',         # Divisores
    'hover': '#1E3A5F',           # Hover state
    'gray_light': '#475569',      # Cinza claro (compatibilidade)
    
    # Gradientes
    'gradient_start': '#1E40AF',
    'gradient_end': '#3B82F6',
    
    # Tabelas
    'table_header': '#1E40AF',
    'table_row_even': '#1E293B',
    'table_row_odd': '#0F172A',
}

# ==================== ÍCONES ====================
ICONS = {
    'dashboard': '📊',
    'users': '👥',
    'phone': '📞',
    'calendar': '📅',
    'alert': '⚠️',
    'check': '✅',
    'fire': '🔥',
    'heart': '❤️',
    'trending_up': '📈',
    'trending_down': '📉',
    'dollar': '💰',
    'target': '🎯',
    'clock': '⏰',
    'shield': '🛡️',
    'settings': '⚙️',
    'chart': '📊',
    'file': '📄',
    'search': '🔍',
    'star': '⭐'
}

# ==================== PATHS ====================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
ASSETS_DIR = BASE_DIR / 'assets'

# ==================== CONFIGURAÇÕES ====================
CONFIG = {
    'page_title': 'Base Telco | Dashboard CS',
    'page_icon': '🛡️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# ==================== HEALTH SCORE WEIGHTS ====================
HEALTH_WEIGHTS = {
    'contato': 25,
    'incidentes': 30,
    'sla': 25,
    'flags': 20
}

# ==================== FAIXAS DE CONTATO ====================
FAIXAS_CONTATO = {
    '0-30': {'label': '0-30 dias', 'color': COLORS['success'], 'pontos': 25},
    '30-90': {'label': '30-90 dias', 'color': COLORS['warning'], 'pontos': 15},
    '90+': {'label': '90+ dias', 'color': COLORS['danger'], 'pontos': 5}
}
