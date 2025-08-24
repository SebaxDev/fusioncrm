"""Componentes de UI reutilizables con estilo CRM profesional"""

import streamlit as st
from datetime import datetime
from utils.helpers import cloud_log

def card(title, content, icon=None, actions=None, variant="default"):
    """Componente de tarjeta elegante con variantes de estilo"""
    variant_classes = {
        "default": "bg-card",
        "surface": "bg-surface", 
        "primary": "bg-primary-subtle",
        "success": "bg-success-subtle",
        "warning": "bg-warning-subtle",
        "danger": "bg-danger-subtle"
    }
    
    bg_class = variant_classes.get(variant, "bg-card")
    
    icon_html = f"<div style='font-size: 2rem; color: var(--primary-color); margin-bottom: 1rem;'>{icon}</div>" if icon else ""
    
    actions_html = ""
    if actions:
        actions_html = "<div style='margin-top: 1.5rem; display: flex; gap: 0.5rem;'>"
        for action in actions:
            actions_html += f"""
            <button style='
                padding: 0.5rem 1rem;
                border: 1px solid var(--border-color);
                border-radius: var(--radius-md);
                background: var(--bg-surface);
                color: var(--text-primary);
                cursor: pointer;
                transition: all 0.2s ease;
            ' onmouseover="this.style.background='var(--bg-secondary)'; this.style.borderColor='var(--primary-color)';"
            onmouseout="this.style.background='var(--bg-surface)'; this.style.borderColor='var(--border-color)';">
                {action["label"]}
            </button>
            """
        actions_html += "</div>"
    
    return f"""
    <div style='
        background: var(--{bg_class});
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    ' onmouseover="this.style.boxShadow='var(--shadow-md)'; this.style.transform='translateY(-2px)';"
    onmouseout="this.style.boxShadow='var(--shadow-sm)'; this.style.transform='translateY(0)';">
        {icon_html}
        <h3 style='margin: 0 0 1rem 0; color: var(--text-primary); font-size: 1.25rem;'>{title}</h3>
        <div style='color: var(--text-secondary); line-height: 1.6;'>{content}</div>
        {actions_html}
    </div>
    """

def metric_card(value, label, icon, trend=None, subtitle=None, help_text=None):
    """Tarjeta de métrica elegante optimizada para CRM"""
    
    trend_html = ""
    if trend:
        trend_color = "var(--success-color)" if trend.get('positive', True) else "var(--danger-color)"
        trend_icon = "📈" if trend.get('positive', True) else "📉"
        trend_html = f"""
        <div style='color: {trend_color}; font-size: 0.85rem; margin-top: 0.5rem;
                    display: flex; align-items: center; gap: 0.25rem; font-weight: 600;'>
            {trend_icon} {trend['value']}
            {trend.get('label', '')}
        </div>
        """
    
    subtitle_html = f"<div style='color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem;'>{subtitle}</div>" if subtitle else ""
    
    help_html = f"<div style='color: var(--text-muted); font-size: 0.8rem; margin-top: 0.5rem;'>{help_text}</div>" if help_text else ""
    
    return f"""
    <div style='
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ' onmouseover="this.style.boxShadow='var(--shadow-md)'; this.style.borderColor='var(--primary-color)';"
    onmouseout="this.style.boxShadow='none'; this.style.borderColor='var(--border-color)';">
        <div style='
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        '>
            {icon}
        </div>
        <div style='
            font-size: 2.25rem;
            font-weight: 800;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            line-height: 1.1;
        '>
            {value}
        </div>
        <div style='
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.25rem;
            line-height: 1.3;
        '>
            {label}
        </div>
        {subtitle_html}
        {trend_html}
        {help_html}
    </div>
    """

def badge(text, type="primary", icon=None, size="md"):
    """Badge elegante con tamaños y variantes"""
    size_map = {
        "sm": "0.7rem",
        "md": "0.8rem", 
        "lg": "0.9rem"
    }
    
    color_map = {
        "primary": "var(--primary-color)",
        "success": "var(--success-color)",
        "warning": "var(--warning-color)",
        "danger": "var(--danger-color)",
        "info": "var(--info-color)",
        "secondary": "var(--text-muted)"
    }
    
    icon_html = f"<span style='margin-right: 0.25rem; font-size: {size_map[size]};'>{icon}</span>" if icon else ""
    
    return f"""
    <span style='
        background-color: rgba({color_map[type].replace('var(', '').replace(')', '')}, 0.15);
        color: {color_map[type]};
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.8rem;
        border-radius: var(--radius-xl);
        font-size: {size_map[size]};
        font-weight: 600;
        border: 1px solid rgba({color_map[type].replace('var(', '').replace(')', '')}, 0.3);
        white-space: nowrap;
    '>
        {icon_html}{text}
    </span>
    """

def breadcrumb(current_page, show_date=True, show_icon=True):
    """Breadcrumb optimizado para ancho expandido con estilo CRM"""
    icons = {
        "Inicio": "🏠",
        "Reclamos cargados": "📊", 
        "Gestión de clientes": "👥",
        "Imprimir reclamos": "🖨️",
        "Seguimiento técnico": "🔧",
        "Cierre de Reclamos": "✅",
        "Nuevo Reclamo": "➕"
    }
    
    date_section = ""
    if show_date:
        date_section = f"""
        <div style="flex: 1;"></div>
        <span style="color: var(--text-muted); font-size: 0.85rem; font-weight: 500;">
            {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </span>
        """
    
    icon_section = ""
    if show_icon and current_page in icons:
        icon_section = f"<span style='font-size: 1.2rem; margin-right: 0.5rem;'>{icons[current_page]}</span>"
    
    return f"""
    <div style="
        display: flex; 
        align-items: center; 
        gap: 0.75rem; 
        margin: 2rem 0 1.5rem 0; 
        padding: 1.25rem; 
        background: var(--bg-card); 
        border-radius: var(--radius-xl); 
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        font-size: 0.95rem;
    ">
        <span style="color: var(--text-muted); display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.1rem;">📋</span>
            <span>Navegación:</span>
        </span>
        
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.25rem;
                    background: linear-gradient(135deg, var(--bg-surface), var(--bg-secondary));
                    border-radius: var(--radius-lg); border: 1px solid var(--border-light);
                    box-shadow: var(--shadow-sm);">
            {icon_section}
            <span style="color: var(--primary-color); font-weight: 700; font-size: 1.05rem;">
                {current_page}
            </span>
        </div>
        
        {date_section}
    </div>
    """

def loading_indicator(message="Cargando datos...", size="lg"):
    """Indicador de carga elegante con diferentes tamaños"""
    size_map = {
        "sm": "30px",
        "md": "40px", 
        "lg": "50px"
    }
    
    return f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="
            width: {size_map[size]};
            height: {size_map[size]};
            border: 3px solid rgba(102, 217, 239, 0.3);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        "></div>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem; font-weight: 500;">{message}</p>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """

def grid_container(columns=3, gap="1rem", responsive=True):
    """Contenedor de grid optimizado con responsive design"""
    responsive_style = "repeat(auto-fit, minmax(250px, 1fr))" if responsive else f"repeat({columns}, 1fr)"
    
    return f"""
    <div style="
        display: grid;
        grid-template-columns: {responsive_style};
        gap: {gap};
        width: 100%;
        margin: 1.5rem 0;
    ">
    """

def grid_item():
    """Item de grid para contenedor"""
    return "<div style='width: 100%;'>"

def grid_end():
    """Cierre del contenedor de grid"""
    return "</div>"

def expandable_section(title, content, expanded=False, icon="📦", variant="default"):
    """Sección expandible optimizada con variantes de estilo"""
    variant_styles = {
        "default": "var(--bg-card)",
        "surface": "var(--bg-surface)",
        "primary": "rgba(37, 99, 235, 0.1)"
    }
    
    bg_color = variant_styles.get(variant, "var(--bg-card)")
    
    expand_icon = "▼" if expanded else "►"
    
    return f"""
    <div style="
        background: {bg_color};
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        margin: 1rem 0;
        overflow: hidden;
        transition: all 0.3s ease;
    ">
        <div style="
            padding: 1.25rem 1.5rem;
            background: var(--bg-surface);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 600;
            color: var(--text-primary);
            transition: all 0.2s ease;
        " onmouseover="this.style.background='var(--bg-secondary)';"
        onmouseout="this.style.background='var(--bg-surface)';">
            <span style="font-size: 1.2rem; color: var(--primary-color);">{icon}</span>
            <span style="flex: 1; font-size: 1.05rem;">{title}</span>
            <span style="font-size: 0.9rem; color: var(--text-muted);">{expand_icon}</span>
        </div>
        <div style="padding: 1.5rem; display: {'block' if expanded else 'none'};">
            {content}
        </div>
    </div>
    """

def status_pill(status, size="md"):
    """Píldora de estado con colores semánticos"""
    status_config = {
        "Pendiente": {"color": "warning", "icon": "⏳"},
        "En curso": {"color": "info", "icon": "⚙️"},
        "Completado": {"color": "success", "icon": "✅"},
        "Cancelado": {"color": "danger", "icon": "❌"},
        "Revisión": {"color": "secondary", "icon": "🔍"}
    }
    
    config = status_config.get(status, {"color": "secondary", "icon": "📋"})
    
    return badge(status, config["color"], config["icon"], size)