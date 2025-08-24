"""
Componente del dashboard de métricas profesional
Versión 3.1 - Optimizado para Render con métricas avanzadas
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.helpers import cloud_log
from config.settings import IS_RENDER

def metric_card(value, label, icon, trend=None, delta=None, help_text=None):
    """Componente de tarjeta de métrica profesional optimizado"""
    
    trend_color = "var(--success-color)" if (delta or 0) >= 0 else "var(--danger-color)"
    trend_icon = "↗️" if (delta or 0) >= 0 else "↘️"
    
    trend_html = f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 0.25rem; font-size: 0.8rem; margin-top: 0.25rem;'>
        <span style='color: {trend_color}; font-weight: 500;'>
            {trend_icon} {abs(delta or 0)}%
        </span>
    </div>
    """ if trend and delta is not None else ""
    
    help_html = f"""
    <div style='font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;'>
        {help_text}
    </div>
    """ if help_text else ""
    
    return f"""
    <div class='crm-card' style='text-align: center; padding: 1.5rem 1rem; margin: 0; height: 100%;'>
        <div style='font-size: 2.5rem; margin-bottom: 0.75rem; color: var(--primary-color);'>{icon}</div>
        <div style='font-size: 2.25rem; font-weight: 700; color: var(--text-primary); line-height: 1; margin-bottom: 0.5rem;'>{value}</div>
        <div style='color: var(--text-secondary); font-size: 0.9rem; font-weight: 500; margin-bottom: 0.5rem;'>{label}</div>
        {trend_html}
        {help_html}
    </div>
    """

def status_badge(status, count, percentage=None):
    """Badge de estado para métricas con porcentaje opcional"""
    status_config = {
        "Pendiente": {"color": "var(--warning-color)", "icon": "⏳"},
        "En Proceso": {"color": "var(--info-color)", "icon": "🔧"},
        "Resuelto": {"color": "var(--success-color)", "icon": "✅"},
        "Cerrado": {"color": "var(--success-color)", "icon": "🔒"},
        "Cancelado": {"color": "var(--danger-color)", "icon": "❌"},
        "Desconexión": {"color": "var(--error-color)", "icon": "🔌"},
        "Derivado": {"color": "var(--secondary-color)", "icon": "↗️"}
    }
    
    config = status_config.get(status, {"color": "var(--text-muted)", "icon": "❓"})
    
    percentage_html = f"""
    <span style='font-size: 0.8rem; color: {config["color"]}; opacity: 0.8;'>
        ({percentage}%)
    </span>
    """ if percentage is not None else ""
    
    return f"""
    <div style='display: flex; align-items: center; justify-content: space-between; padding: 0.875rem; background: {config["color"]}15; border-radius: var(--radius-md); border: 1px solid {config["color"]}30; margin: 0.375rem 0;'>
        <span style='display: flex; align-items: center; gap: 0.625rem;'>
            <span style='color: {config["color"]}; font-size: 1.1rem;'>{config["icon"]}</span>
            <span style='color: var(--text-primary); font-weight: 500;'>{status}</span>
        </span>
        <span style='display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-weight: 700; color: {config["color"]}; font-size: 1.1rem;'>{count}</span>
            {percentage_html}
        </span>
    </div>
    """

def render_metrics_dashboard(df_reclamos, is_mobile=False):
    """Renderiza el dashboard de métricas profesional optimizado para Render"""
    try:
        if df_reclamos.empty:
            st.warning("📊 No hay datos de reclamos para mostrar")
            return

        df = df_reclamos.copy()
        
        # Limpieza y normalización de datos
        df["Estado"] = df["Estado"].fillna("Desconocido").astype(str).str.strip()
        
        # Cálculo de métricas principales
        total_reclamos = len(df)
        reclamos_activos = df[df["Estado"].isin(["Pendiente", "En Proceso"])]
        total_activos = len(reclamos_activos)
        
        # Métricas por estado
        estado_counts = df["Estado"].value_counts()
        pendientes = estado_counts.get("Pendiente", 0)
        en_proceso = estado_counts.get("En Proceso", 0)
        resueltos = estado_counts.get("Resuelto", 0) + estado_counts.get("Cerrado", 0)
        cancelados = estado_counts.get("Cancelado", 0)
        
        # Métricas de eficiencia
        porcentaje_resueltos = (resueltos / total_reclamos * 100) if total_reclamos > 0 else 0
        porcentaje_activos = (total_activos / total_reclamos * 100) if total_reclamos > 0 else 0
        
        # Métricas temporales (últimas 24/48 horas)
        try:
            df_fechas = df.copy()
            df_fechas["Fecha y hora"] = pd.to_datetime(df_fechas["Fecha y hora"], errors='coerce')
            ultimas_24h = df_fechas[df_fechas["Fecha y hora"] >= (datetime.now() - timedelta(hours=24))]
            reclamos_24h = len(ultimas_24h)
        except:
            reclamos_24h = 0

        # Header del dashboard
        st.markdown("""
        <div class="crm-card" style="margin-bottom: 2rem; padding: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2.5rem; color: var(--primary-color);">📈</div>
                <div>
                    <h2 style="margin: 0; color: var(--text-primary);">Dashboard de Métricas</h2>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">
                        Resumen general de la gestión de reclamos en tiempo real
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Diseño responsive
        if is_mobile:
            # Móviles - 2 columnas
            cols = st.columns(2)
            metrics = [
                (total_reclamos, "Total Reclamos", "📋", "Total de reclamos en el sistema"),
                (total_activos, "Activos", "📄", "Reclamos pendientes o en proceso"),
                (pendientes, "Pendientes", "⏳", "Esperando asignación o acción"),
                (en_proceso, "En Proceso", "🔧", "Trabajando en la resolución"),
                (resueltos, "Resueltos", "✅", "Reclamos completados exitosamente"),
                (f"{porcentaje_resueltos:.1f}%", "Tasa Éxito", "🎯", "Porcentaje de resolución")
            ]
            
            for i, (value, label, icon, help_text) in enumerate(metrics):
                with cols[i % 2]:
                    st.markdown(metric_card(value, label, icon, help_text=help_text), unsafe_allow_html=True)
            
        else:
            # Desktop - 3 columnas para mejor uso del espacio
            cols = st.columns(3)
            metrics = [
                (total_reclamos, "Total Reclamos", "📋", "Total histórico de reclamos"),
                (total_activos, "Activos", "📄", "Requieren atención inmediata"),
                (reclamos_24h, "Últimas 24h", "🕒", "Nuevos reclamos recientes"),
                (pendientes, "Pendientes", "⏳", "Esperando asignación"),
                (en_proceso, "En Proceso", "🔧", "En trabajo activo"),
                (resueltos, "Resueltos", "✅", "Completados exitosamente"),
                (f"{porcentaje_resueltos:.1f}%", "Tasa Resolución", "🎯", "Eficiencia general"),
                (f"{porcentaje_activos:.1f}%", "Tasa Activos", "📊", "Carga de trabajo actual"),
                (cancelados, "Cancelados", "❌", "Reclamos cancelados")
            ]
            
            for i, (value, label, icon, help_text) in enumerate(metrics):
                with cols[i % 3]:
                    st.markdown(metric_card(value, label, icon, help_text=help_text), unsafe_allow_html=True)

        # Sección de distribución por estado
        st.markdown("""
        <div class="crm-card" style="margin-top: 2rem; padding: 1.5rem;">
            <h3 style="margin: 0 0 1.5rem 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                <span>📊</span> Distribución por Estado
            </h3>
        """, unsafe_allow_html=True)
        
        # Calcular porcentajes para cada estado
        estado_stats = []
        for estado, count in estado_counts.items():
            percentage = (count / total_reclamos * 100) if total_reclamos > 0 else 0
            estado_stats.append((estado, count, percentage))
        
        # Ordenar por cantidad descendente
        estado_stats.sort(key=lambda x: x[1], reverse=True)
        
        # Mostrar badges de estado
        for estado, count, percentage in estado_stats:
            if count > 0:  # Solo mostrar estados con reclamos
                st.markdown(status_badge(estado, count, f"{percentage:.1f}"), unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        cloud_log(f"Error en dashboard de métricas: {str(e)}", "error")
        st.error("❌ Error al cargar el dashboard de métricas")
        if not IS_RENDER:  # Mostrar detalles del error solo en desarrollo
            st.exception(e)