# components/resumen_jornada.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.date_utils import format_fecha, ahora_argentina, parse_fecha
from utils.helpers import cloud_log, get_status_badge
from utils.api_manager import api_manager
from config.settings import DEBUG_MODE, IS_RENDER

def render_resumen_jornada(df_reclamos):
    """Muestra el resumen de la jornada con estilo CRM profesional"""
    
    # Estilos CSS para el resumen de jornada
    resumen_styles = """
    <style>
    .resumen-jornada {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
    }
    
    .resumen-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-light);
    }
    
    .resumen-icon {
        font-size: 2.5rem;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .resumen-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .resumen-metric {
        text-align: center;
        padding: 1.5rem;
        background: var(--bg-surface);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .resumen-metric:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-color);
    }
    
    .resumen-metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .resumen-metric-label {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 600;
    }
    
    .resumen-section {
        margin: 2rem 0;
        padding: 1.5rem;
        background: var(--bg-surface);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
    }
    
    .resumen-section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .tecnico-group {
        padding: 1rem;
        margin: 0.75rem 0;
        background: var(--bg-card);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-light);
        transition: all 0.2s ease;
    }
    
    .tecnico-group:hover {
        background: var(--bg-secondary);
        border-color: var(--primary-color);
    }
    
    .reclamo-antiguo {
        padding: 1rem;
        margin: 0.5rem 0;
        background: rgba(253, 151, 31, 0.1);
        border: 1px solid rgba(253, 151, 31, 0.3);
        border-radius: var(--radius-md);
        border-left: 4px solid var(--warning-color);
    }
    
    .footer-info {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border-light);
        color: var(--text-muted);
        font-size: 0.9rem;
    }
    </style>
    """
    
    st.markdown(resumen_styles, unsafe_allow_html=True)
    
    # Contenedor principal
    st.markdown("""
    <div class="resumen-jornada">
        <div class="resumen-header">
            <div class="resumen-icon">📋</div>
            <h2 class="resumen-title">Resumen de la Jornada</h2>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        # Manejo robusto de fechas
        df_reclamos = df_reclamos.copy()
        df_reclamos["Fecha y hora"] = df_reclamos["Fecha y hora"].apply(
            lambda x: parse_fecha(x) if not pd.isna(x) else pd.NaT
        )
        
        # Filtrar reclamos de hoy
        hoy = ahora_argentina().date()
        df_hoy = df_reclamos[
            df_reclamos["Fecha y hora"].dt.tz_localize(None).dt.date == hoy
        ].copy()
        
        # Filtrar reclamos en curso
        df_en_curso = df_reclamos[df_reclamos["Estado"] == "En curso"].copy()
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="resumen-metric">
                <div class="resumen-metric-value">{len(df_hoy)}</div>
                <div class="resumen-metric-label">📌 Reclamos hoy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="resumen-metric">
                <div class="resumen-metric-value">{len(df_en_curso)}</div>
                <div class="resumen-metric-label">⚙️ En curso</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pendientes = len(df_reclamos[df_reclamos["Estado"] == "Pendiente"])
            st.markdown(f"""
            <div class="resumen-metric">
                <div class="resumen-metric-value">{pendientes}</div>
                <div class="resumen-metric-label">⏳ Pendientes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            completados = len(df_reclamos[df_reclamos["Estado"] == "Completado"])
            st.markdown(f"""
            <div class="resumen-metric">
                <div class="resumen-metric-value">{completados}</div>
                <div class="resumen-metric-label">✅ Completados</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sección de distribución de trabajo
        st.markdown("""
        <div class="resumen-section">
            <h3 class="resumen-section-title">👷 Distribución de Trabajo por Técnicos</h3>
        """, unsafe_allow_html=True)
        
        if not df_en_curso.empty and "Técnico" in df_en_curso.columns:
            # Limpieza y normalización de técnicos
            df_en_curso["Técnico"] = (
                df_en_curso["Técnico"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )
            
            # Filtrar técnicos válidos
            df_con_tecnicos = df_en_curso[df_en_curso["Técnico"] != ""].copy()
            
            if not df_con_tecnicos.empty:
                # Agrupar por técnicos (manejar múltiples técnicos separados por coma)
                conteo_individual = {}
                for _, row in df_con_tecnicos.iterrows():
                    tecnicos = [t.strip() for t in row["Técnico"].split(",") if t.strip()]
                    for tecnico in tecnicos:
                        conteo_individual[tecnico] = conteo_individual.get(tecnico, 0) + 1
                
                # Mostrar distribución
                for tecnico, cantidad in sorted(conteo_individual.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"""
                    <div class="tecnico-group">
                        <strong>👤 {tecnico}</strong>: {cantidad} reclamo{'s' if cantidad != 1 else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Reclamos más antiguos aún en curso
                reclamos_antiguos = df_en_curso.sort_values("Fecha y hora").head(3)
                if not reclamos_antiguos.empty:
                    st.markdown("""
                    <div style="margin-top: 2rem;">
                        <h4 class="resumen-section-title">⏳ Reclamos Más Antiguos en Curso</h4>
                    """, unsafe_allow_html=True)
                    
                    for _, row in reclamos_antiguos.iterrows():
                        fecha_formateada = format_fecha(row["Fecha y hora"])
                        st.markdown(f"""
                        <div class="reclamo-antiguo">
                            <div><strong>{row.get('Nombre', 'N/A')}</strong> ({row.get('Nº Cliente', 'N/A')})</div>
                            <div>📅 Desde: {fecha_formateada}</div>
                            <div>👷 Técnicos: {row.get('Técnico', 'No asignado')}</div>
                            <div>📝 {row.get('Descripción del Reclamo', '')[:100]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ No hay técnicos asignados actualmente a reclamos en curso.")
        else:
            st.info("ℹ️ No hay reclamos en curso en este momento.")
        
        st.markdown("</div>", unsafe_allow_html=True)  # Cierre de sección
        
        # Verificación de reclamos sin asignar
        _notificar_reclamos_no_asignados(df_reclamos)
        
        # Footer informativo
        st.markdown(f"""
        <div class="footer-info">
            <p>Última actualización: {ahora_argentina().strftime('%d/%m/%Y %H:%M')}</p>
            <p style="margin-top: 0.5rem;">© 2025 - Fusion CRM v3.0 | Optimizado para Render</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        error_msg = f"Error al generar resumen: {str(e)}"
        st.error(error_msg)
        cloud_log(error_msg, "error")
        if DEBUG_MODE:
            st.exception(e)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Cierre del contenedor principal

def _notificar_reclamos_no_asignados(df):
    """
    Detecta reclamos sin técnico hace más de 36 horas y notifica globalmente
    """
    if 'notification_manager' not in st.session_state or st.session_state.notification_manager is None:
        return
    
    try:
        ahora = ahora_argentina()
        umbral = ahora - timedelta(hours=36)
        
        # Preparar datos para análisis
        df_analisis = df.copy()
        df_analisis["Fecha y hora"] = df_analisis["Fecha y hora"].apply(
            lambda x: parse_fecha(x) if not pd.isna(x) else pd.NaT
        )
        
        # Filtrar reclamos problemáticos
        df_filtrado = df_analisis[
            (df_analisis["Estado"].isin(["Pendiente", "En curso"])) &
            (df_analisis["Técnico"].isna() | (df_analisis["Técnico"].astype(str).str.strip() == "")) &
            (df_analisis["Fecha y hora"] < umbral)
        ].copy()
        
        if df_filtrado.empty:
            return
        
        # Verificar si ya existe una notificación similar
        notificaciones_existentes = st.session_state.notification_manager.get_for_user(
            "all", unread_only=False, limit=20
        )
        
        ya_existe = any(
            n.get("Tipo") == "unassigned_claim" and 
            n.get("Mensaje", "").startswith(f"Hay {len(df_filtrado)}")
            for n in notificaciones_existentes
        )
        
        if not ya_existe:
            mensaje = f"Hay {len(df_filtrado)} reclamos sin técnico asignado desde hace más de 36 horas."
            success = st.session_state.notification_manager.add(
                notification_type="unassigned_claim",
                message=mensaje,
                user_target="all"
            )
            
            if success:
                cloud_log(f"Notificación de reclamos no asignados enviada: {mensaje}", "info")
                
    except Exception as e:
        error_msg = f"Error en notificación de reclamos no asignados: {str(e)}"
        cloud_log(error_msg, "error")
        if DEBUG_MODE:
            st.warning("⚠️ No se pudo generar la notificación global")