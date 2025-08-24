"""
Componente de navegación profesional con iconos y estados activos
Versión 3.1 - Optimizado para Render con navegación CRM
"""
import streamlit as st
from utils.permissions import has_permission
from utils.helpers import cloud_log
from config.settings import PERMISOS_POR_ROL, IS_RENDER

def render_sidebar_navigation():
    """Renderiza la navegación lateral profesional optimizada para Render"""
    
    menu_items = [
        {"icon": "🏠", "label": "Dashboard", "key": "Inicio", "permiso": "dashboard"},
        {"icon": "📊", "label": "Reclamos", "key": "Reclamos cargados", "permiso": "reclamos_cargados"},
        {"icon": "👥", "label": "Clientes", "key": "Gestión de clientes", "permiso": "gestion_clientes"},
        {"icon": "🖨️", "label": "Impresiones", "key": "Imprimir reclamos", "permiso": "imprimir_reclamos"},
        {"icon": "🔧", "label": "Seguimiento", "key": "Seguimiento técnico", "permiso": "seguimiento_tecnico"},
        {"icon": "✅", "label": "Cierre", "key": "Cierre de Reclamos", "permiso": "cierre_reclamos"},
        {"icon": "📋", "label": "Reportes", "key": "Reportes", "permiso": "reportes"},
        {"icon": "⚙️", "label": "Configuración", "key": "Configuración", "permiso": "configuracion"}
    ]
    
    # Filtrar items según permisos del usuario
    filtered_items = [
        item for item in menu_items 
        if has_permission(item["permiso"])
    ]
    
    if not filtered_items:
        st.sidebar.warning("No tienes permisos para acceder a ninguna sección")
        return
    
    # Header de navegación
    st.sidebar.markdown("""
    <div style="padding: 1rem 0; margin-bottom: 1rem;">
        <h3 style="margin: 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.2rem;">🧭</span>
            <span style="font-size: 1rem;">Navegación</span>
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de navegación
    current_page = st.session_state.get('current_page', 'Inicio')
    
    for item in filtered_items:
        is_active = current_page == item["key"]
        
        button_css = f"""
        <style>
        .nav-btn-{item['key'].replace(' ', '-').lower()} {{
            background: {'linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%)' if is_active else 'var(--bg-surface)'} !important;
            color: {'white' if is_active else 'var(--text-primary)'} !important;
            border: 1px solid {'var(--primary-color)' if is_active else 'var(--border-color)'} !important;
            border-radius: var(--radius-lg) !important;
            padding: 0.75rem 1rem !important;
            margin: 0.25rem 0 !important;
            font-weight: {500 if is_active else 400} !important;
            transition: all 0.2s ease !important;
        }}
        .nav-btn-{item['key'].replace(' ', '-').lower()}:hover {{
            background: {'var(--primary-dark)' if is_active else 'var(--bg-secondary)'} !important;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }}
        </style>
        """
        
        st.sidebar.markdown(button_css, unsafe_allow_html=True)
        
        if st.sidebar.button(
            f"{item['icon']} {item['label']}", 
            key=f"nav_{item['key'].replace(' ', '_').lower()}",
            use_container_width=True,
            help=f"Ir a {item['label']}"
        ):
            st.session_state.current_page = item["key"]
            cloud_log(f"Navegación a: {item['label']}", "info")
            st.rerun()
    
    st.sidebar.markdown("---")

# Función de compatibilidad mantenida
def render_navigation():
    """Renderiza navegación horizontal (compatibilidad con versiones anteriores)"""
    st.markdown("""
    <div style="margin: 1.5rem 0; padding: 1rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
        <h3 style="margin: 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
            <span>🧭</span> Navegación Rápida
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    opciones = [
        "🏠 Dashboard", 
        "📊 Reclamos", 
        "👥 Clientes",  
        "🖨️ Impresiones", 
        "🔧 Seguimiento", 
        "✅ Cierre"
    ]
    
    # Filtrar opciones basadas en permisos
    filtered_opciones = []
    permission_map = {
        "🏠 Dashboard": "dashboard",
        "📊 Reclamos": "reclamos_cargados", 
        "👥 Clientes": "gestion_clientes",
        "🖨️ Impresiones": "imprimir_reclamos",
        "🔧 Seguimiento": "seguimiento_tecnico",
        "✅ Cierre": "cierre_reclamos"
    }
    
    for opcion in opciones:
        permiso = permission_map.get(opcion)
        if permiso and has_permission(permiso):
            filtered_opciones.append(opcion)
    
    if filtered_opciones:
        opcion = st.radio(
            "Selecciona una sección:",
            filtered_opciones,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Mapear de vuelta a keys originales
        key_map = {
            "🏠 Dashboard": "Inicio",
            "📊 Reclamos": "Reclamos cargados",
            "👥 Clientes": "Gestión de clientes",
            "🖨️ Impresiones": "Imprimir reclamos", 
            "🔧 Seguimiento": "Seguimiento técnico",
            "✅ Cierre": "Cierre de Reclamos"
        }
        
        return key_map.get(opcion, "Inicio")
    
    return "Inicio"