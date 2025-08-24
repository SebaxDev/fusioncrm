# components/reclamos/gestion.py

import streamlit as st
import pandas as pd
from utils.date_utils import parse_fecha, format_fecha
from utils.api_manager import api_manager, batch_update_sheet
from utils.helpers import cloud_log, show_success, show_error, show_warning, show_info, badge
from config.settings import SECTORES_DISPONIBLES, DEBUG_MODE, IS_RENDER

# --- ESTILOS CSS PARA GESTIÓN DE RECLAMOS ---
GESTION_STYLES = """
<style>
.gestion-container {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    padding: 2rem;
    margin: 2rem 0;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
}

.gestion-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-light);
}

.gestion-icon {
    font-size: 2.5rem;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.gestion-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.stat-card {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.stat-label {
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.9rem;
}

.tipo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.tipo-card {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1rem;
    border: 1px solid var(--border-color);
    transition: all 0.2s ease;
}

.tipo-card:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
}

.tipo-name {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.tipo-count {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--primary-color);
}

.filter-section {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    margin: 1.5rem 0;
}

.edicion-section {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    margin: 1.5rem 0;
}

.reclamo-info {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    margin: 1rem 0;
}

.form-group {
    margin-bottom: 1.25rem;
}

.form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.95rem;
}

.form-input {
    width: 100%;
    padding: 0.875rem;
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 0.95rem;
    transition: all 0.2s ease;
}

.form-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    outline: none;
}

.desconexion-item {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    border: 1px solid var(--border-color);
    margin: 0.75rem 0;
    transition: all 0.3s ease;
}

.desconexion-item:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
}
</style>
"""

def render_gestion_reclamos(df_reclamos, df_clientes, sheet_reclamos, user):
    """
    Muestra la sección de gestión de reclamos cargados con estilo CRM
    
    Args:
        df_reclamos (pd.DataFrame): DataFrame con los reclamos
        df_clientes (pd.DataFrame): DataFrame con los clientes
        sheet_reclamos: Objeto de conexión a la hoja de reclamos
        user (dict): Información del usuario actual
        
    Returns:
        dict: {
            'needs_refresh': bool,  # Si se necesita recargar datos
            'message': str,         # Mensaje para mostrar al usuario
            'data_updated': bool    # Si se modificaron datos
        }
    """
    st.markdown(GESTION_STYLES, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="gestion-container">
        <div class="gestion-header">
            <div class="gestion-icon">📊</div>
            <h2 class="gestion-title">Gestión de Reclamos</h2>
        </div>
    """, unsafe_allow_html=True)

    result = {
        'needs_refresh': False,
        'message': None,
        'data_updated': False
    }
    
    try:
        # Preprocesar datos una sola vez
        df = _preparar_datos(df_reclamos, df_clientes)
        
        # Mostrar estadísticas (no produce cambios)
        _mostrar_estadisticas(df)
        
        # Mostrar filtros y tabla (no produce cambios)
        df_filtrado = _mostrar_filtros_y_tabla(df)
        
        # Sección de edición de reclamos
        cambios_edicion = _mostrar_edicion_reclamo(df_filtrado, sheet_reclamos)
        if cambios_edicion:
            result.update({
                'needs_refresh': True,
                'message': 'Reclamo actualizado correctamente',
                'data_updated': True
            })
            return result
        
        # Gestión de desconexiones
        cambios_desconexiones = _gestionar_desconexiones(df_filtrado, sheet_reclamos)
        if cambios_desconexiones:
            result.update({
                'needs_refresh': True,
                'message': 'Desconexiones actualizadas',
                'data_updated': True
            })
            return result

    except Exception as e:
        error_msg = f"⚠️ Error en la gestión de reclamos: {str(e)}"
        show_error(error_msg)
        cloud_log(error_msg, "error")
        if DEBUG_MODE:
            st.exception(e)
        result['message'] = f"Error: {str(e)}"
    finally:
        st.markdown('</div>', unsafe_allow_html=True)
    
    return result

def _preparar_datos(df_reclamos, df_clientes):
    """Prepara y limpia los datos para su visualización"""
    try:
        # Hacer copias para no modificar los dataframes originales
        df = df_reclamos.copy()
        df_clientes = df_clientes.copy()
        
        # Normalización de datos (una sola vez)
        df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
        df["Nº Cliente"] = df["Nº Cliente"].astype(str).str.strip()
        df["ID Reclamo"] = df["ID Reclamo"].astype(str).str.strip()

        # Optimización: Solo traer las columnas necesarias de clientes
        cols_clientes = ["Nº Cliente", "N° de Precinto", "Teléfono"]
        df_clientes = df_clientes[cols_clientes].drop_duplicates(subset=["Nº Cliente"])

        # Merge más eficiente con datos de clientes
        df = pd.merge(
            df, 
            df_clientes,
            on="Nº Cliente", 
            how="left", 
            suffixes=("", "_cliente")
        )

        # Procesamiento de fechas
        if 'Fecha y hora' in df.columns:
            df["Fecha y hora"] = df["Fecha y hora"].apply(parse_fecha)
            df["Fecha_formateada"] = df["Fecha y hora"].apply(
                lambda x: format_fecha(x, '%d/%m/%Y %H:%M') if pd.notna(x) else "Fecha inválida"
            )

            # Validación de fechas
            if df["Fecha y hora"].isna().any():
                num_fechas_invalidas = df["Fecha y hora"].isna().sum()
                show_warning(f"⚠️ {num_fechas_invalidas} reclamos tienen fechas inválidas o faltantes")

        return df.sort_values("Fecha y hora", ascending=False)
    
    except Exception as e:
        cloud_log(f"Error preparando datos: {str(e)}", "error")
        return df_reclamos.copy()

def _mostrar_estadisticas(df):
    """Muestra estadísticas visuales de reclamos activos con estilo CRM"""
    df_activos = df[df["Estado"].isin(["Pendiente", "En curso"])]
    
    if not df_activos.empty:
        # Detectar clientes con múltiples reclamos
        duplicados = df_activos.duplicated(subset="Nº Cliente", keep=False)
        
        st.markdown("#### 📊 Estadísticas de Reclamos Activos")
        
        # Grid de estadísticas
        st.markdown("""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">Total Activos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">Clientes Únicos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{}</div>
                <div class="stat-label">Clientes Múltiples</div>
            </div>
        </div>
        """.format(
            len(df_activos),
            len(df_activos["Nº Cliente"].unique()),
            duplicados.sum()
        ), unsafe_allow_html=True)
        
        # Distribución por tipo con estilo CRM
        st.markdown("#### 📋 Distribución por Tipo de Reclamo")
        conteo_por_tipo = df_activos["Tipo de reclamo"].value_counts().sort_index()
        
        st.markdown("<div class='tipo-grid'>", unsafe_allow_html=True)
        for tipo, cant in conteo_por_tipo.items():
            color_class = "warning" if cant > 10 else "primary"
            st.markdown(f"""
            <div class="tipo-card">
                <div class="tipo-name">{tipo}</div>
                <div class="tipo-count">{cant}</div>
                <div>{badge('Alerta' if cant > 10 else 'Normal', color_class)}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def _mostrar_filtros_y_tabla(df):
    """Muestra filtros y tabla de reclamos con estilo CRM"""
    st.markdown("""
    <div class="filter-section">
        <h3>🔍 Filtros de Búsqueda</h3>
    """, unsafe_allow_html=True)
    
    # Filtros en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estado = st.selectbox(
            "Estado", 
            ["Todos"] + sorted(df["Estado"].dropna().unique()),
            key="filtro_estado"
        )
    
    with col2:
        sector = st.selectbox(
            "Sector", 
            ["Todos"] + sorted(SECTORES_DISPONIBLES),
            key="filtro_sector"
        )
    
    with col3:
        tipo = st.selectbox(
            "Tipo de reclamo", 
            ["Todos"] + sorted(df["Tipo de reclamo"].dropna().unique()),
            key="filtro_tipo"
        )

    # Aplicar filtros
    df_filtrado = df.copy()
    if estado != "Todos": 
        df_filtrado = df_filtrado[df_filtrado["Estado"] == estado]
    if sector != "Todos": 
        df_filtrado = df_filtrado[df_filtrado["Sector"] == str(sector)]
    if tipo != "Todos": 
        df_filtrado = df_filtrado[df_filtrado["Tipo de reclamo"] == tipo]

    st.markdown(f"**📈 Mostrando {len(df_filtrado)} de {len(df)} reclamos**")

    # Mostrar tabla optimizada
    columnas = [
        "Fecha_formateada", "Nº Cliente", "Nombre", 
        "Sector", "Tipo de reclamo", "Teléfono", "Estado"
    ]
    
    st.dataframe(
        df_filtrado[columnas].rename(columns={"Fecha_formateada": "Fecha y hora"}),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    return df_filtrado

def _mostrar_edicion_reclamo(df, sheet_reclamos):
    """Muestra la interfaz para editar reclamos con experiencia mejorada"""
    st.markdown("""
    <div class="edicion-section">
        <h3>✏️ Edición de Reclamo Puntual</h3>
    """, unsafe_allow_html=True)
    
    # Crear selector mejorado con búsqueda
    df["selector"] = df.apply(
        lambda x: f"{x['Nº Cliente']} - {x['Nombre']} - {x['Tipo de reclamo']} ({x['Estado']})", 
        axis=1
    )
    
    # Búsqueda avanzada
    busqueda = st.text_input(
        "🔍 Buscar por número de cliente, nombre o tipo",
        placeholder="Ej: 1234, Juan, Desconexión...",
        key="busqueda_reclamo"
    )
    
    # Filtrar opciones basadas en la búsqueda
    opciones_filtradas = [""] + df["selector"].tolist()
    if busqueda:
        opciones_filtradas = [""] + [
            opc for opc in df["selector"].tolist() 
            if busqueda.lower() in opc.lower()
        ]
    
    seleccion = st.selectbox(
        "Seleccioná un reclamo para editar", 
        opciones_filtradas,
        index=0,
        key="selector_reclamo"
    )

    if not seleccion:
        st.markdown("</div>", unsafe_allow_html=True)
        return False

    # Obtener el reclamo seleccionado
    numero_cliente = seleccion.split(" - ")[0]
    reclamo_actual = df[df["Nº Cliente"] == numero_cliente].iloc[0]
    reclamo_id = reclamo_actual["ID Reclamo"]

    # Mostrar información del reclamo con estilo CRM
    st.markdown(f"""
    <div class="reclamo-info">
        <h4>📄 Información del Reclamo Seleccionado</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <div class="form-label">📅 Fecha</div>
                <div>{format_fecha(reclamo_actual['Fecha y hora'])}</div>
            </div>
            <div>
                <div class="form-label">👤 Cliente</div>
                <div>{reclamo_actual['Nombre']}</div>
            </div>
            <div>
                <div class="form-label">📍 Sector</div>
                <div>{reclamo_actual['Sector']}</div>
            </div>
            <div>
                <div class="form-label">📌 Tipo</div>
                <div>{reclamo_actual['Tipo de reclamo']}</div>
            </div>
            <div>
                <div class="form-label">⚙️ Estado Actual</div>
                <div>{badge(reclamo_actual['Estado'], 'primary')}</div>
            </div>
            <div>
                <div class="form-label">👷 Técnico</div>
                <div>{reclamo_actual.get('Técnico', 'No asignado')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Formulario de edición mejorado
    with st.form(f"form_editar_{reclamo_id}"):
        st.markdown("#### 📝 Editar Campos del Reclamo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='form-group'>", unsafe_allow_html=True)
            direccion = st.text_input(
                "📍 Dirección *", 
                value=reclamo_actual.get("Dirección", ""),
                help="Dirección completa del cliente",
                key=f"dir_{reclamo_id}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='form-group'>", unsafe_allow_html=True)
            telefono = st.text_input(
                "📞 Teléfono", 
                value=reclamo_actual.get("Teléfono", ""),
                help="Número de contacto del cliente",
                key=f"tel_{reclamo_id}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='form-group'>", unsafe_allow_html=True)
            tipo_reclamo = st.selectbox(
                "📌 Tipo de reclamo *", 
                sorted(df["Tipo de reclamo"].unique()),
                index=sorted(df["Tipo de reclamo"].unique()).index(
                    reclamo_actual["Tipo de reclamo"]
                ),
                key=f"tipo_{reclamo_id}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='form-group'>", unsafe_allow_html=True)
            try:
                sector_normalizado = str(int(str(reclamo_actual.get("Sector", "")).strip()))
                index_sector = SECTORES_DISPONIBLES.index(sector_normalizado) if sector_normalizado in SECTORES_DISPONIBLES else 0
            except Exception:
                index_sector = 0

            sector_edit = st.selectbox(
                "🔢 Sector *",
                options=SECTORES_DISPONIBLES,
                index=index_sector,
                key=f"sector_{reclamo_id}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        detalles = st.text_area(
            "📝 Detalles *", 
            value=reclamo_actual.get("Detalles", ""), 
            height=100,
            help="Descripción detallada del reclamo",
            key=f"det_{reclamo_id}"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        precinto = st.text_input(
            "🔒 N° de Precinto", 
            value=reclamo_actual.get("N° de Precinto", ""),
            help="Número de precinto del medidor",
            key=f"prec_{reclamo_id}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        estado_nuevo = st.selectbox(
            "🔄 Nuevo estado", 
            ["Pendiente", "En curso", "Resuelto"],
            index=["Pendiente", "En curso", "Resuelto"].index(
                reclamo_actual["Estado"]
            ) if reclamo_actual["Estado"] in ["Pendiente", "En curso", "Resuelto"] 
            else 0,
            key=f"estado_{reclamo_id}"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Botones de acción con estilo
        col1, col2 = st.columns(2)
        
        with col1:
            guardar_cambios = st.form_submit_button(
                "💾 Guardar Todos los Cambios",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            cambiar_estado = st.form_submit_button(
                "🔄 Cambiar Solo Estado",
                use_container_width=True,
                type="secondary"
            )

    # Procesar acciones
    if guardar_cambios:
        if not direccion.strip() or not detalles.strip():
            show_warning("⚠️ Dirección y detalles son campos obligatorios")
            st.markdown("</div>", unsafe_allow_html=True)
            return False
        
        return _actualizar_reclamo(
            df, sheet_reclamos, reclamo_id,
            {
                "direccion": direccion,
                "telefono": telefono,
                "tipo_reclamo": tipo_reclamo,
                "detalles": detalles,
                "precinto": precinto,
                "sector": sector_edit,
                "estado": estado_nuevo,
                "nombre": reclamo_actual.get("Nombre", "")
            },
            full_update=True
        )

    if cambiar_estado:
        return _actualizar_reclamo(
            df, sheet_reclamos, reclamo_id,
            {"estado": estado_nuevo},
            full_update=False
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    return False

def _actualizar_reclamo(df, sheet_reclamos, reclamo_id, updates, full_update=False):
    """Actualiza el reclamo en la hoja de cálculo con notificaciones"""
    try:
        fila = df[df["ID Reclamo"] == reclamo_id].index[0] + 2
        updates_list = []
        estado_anterior = df[df["ID Reclamo"] == reclamo_id]["Estado"].values[0]

        if full_update:
            updates_list.extend([
                {"range": f"E{fila}", "values": [[updates['direccion'].upper()]]},
                {"range": f"F{fila}", "values": [[str(updates['telefono'])]]},
                {"range": f"G{fila}", "values": [[updates['tipo_reclamo']]]},
                {"range": f"H{fila}", "values": [[updates['detalles']]]},
                {"range": f"K{fila}", "values": [[updates['precinto']]]},
                {"range": f"C{fila}", "values": [[str(updates['sector'])]]},
            ])

        updates_list.append({"range": f"I{fila}", "values": [[updates['estado']]]})

        if updates['estado'] == "Pendiente":
            updates_list.append({"range": f"J{fila}", "values": [[""]]})

        # Guardar en Google Sheets
        success, error = api_manager.safe_sheet_operation(
            batch_update_sheet, 
            sheet_reclamos, 
            updates_list, 
            is_batch=True
        )

        if success:
            show_success("✅ Reclamo actualizado correctamente")

            # Notificación de cambio de estado
            if updates['estado'] != estado_anterior and 'notification_manager' in st.session_state:
                mensaje = f"El reclamo {reclamo_id} cambió de estado: {estado_anterior} → {updates['estado']}"
                usuario = st.session_state.auth.get('user_info', {}).get('username', 'desconocido')
                
                st.session_state.notification_manager.add(
                    notification_type="status_change",
                    message=mensaje,
                    user_target="all",
                    claim_id=reclamo_id
                )
                
                cloud_log(f"Reclamo {reclamo_id} actualizado por {usuario}", "info")

            return True
        else:
            show_error(f"❌ Error al actualizar: {error}")
            cloud_log(f"Error actualizando reclamo {reclamo_id}: {error}", "error")
            return False

    except Exception as e:
        error_msg = f"❌ Error inesperado: {str(e)}"
        show_error(error_msg)
        cloud_log(f"Error inesperado actualizando reclamo: {str(e)}", "error")
        if DEBUG_MODE:
            st.exception(e)
        return False

def _gestionar_desconexiones(df, sheet_reclamos):
    """Gestiona las desconexiones a pedido con estilo CRM"""
    st.markdown("""
    <div class="edicion-section">
        <h3>🔌 Gestión de Desconexiones a Pedido</h3>
    """, unsafe_allow_html=True)

    desconexiones = df[
        (df["Tipo de reclamo"].str.strip().str.lower() == "desconexion a pedido") &
        (df["Estado"].str.strip().str.lower() == "desconexión")
    ]

    if desconexiones.empty:
        show_success("✅ No hay desconexiones pendientes de marcar como resueltas")
        st.markdown("</div>", unsafe_allow_html=True)
        return False

    show_info(f"📄 Hay {len(desconexiones)} desconexiones cargadas. Ir a Impresión para imprimir listado.")
    
    cambios = False
    
    for i, row in desconexiones.iterrows():
        st.markdown(f"""
        <div class="desconexion-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{row['Nº Cliente']} - {row['Nombre']}</strong>
                    <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">
                        📅 {format_fecha(row['Fecha y hora'])} - Sector {row['Sector']}
                    </div>
                </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Marcar como Resuelto", key=f"resuelto_{i}", use_container_width=True):
            if _marcar_desconexion_como_resuelta(row, sheet_reclamos):
                cambios = True
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        st.markdown("---")
    
    st.markdown("</div>", unsafe_allow_html=True)
    return cambios

def _marcar_desconexion_como_resuelta(row, sheet_reclamos):
    """Marca una desconexión como resuelta con notificación"""
    try:
        fila = row.name + 2
        success, error = api_manager.safe_sheet_operation(
            sheet_reclamos.update, 
            f"I{fila}", 
            [["Resuelto"]]
        )
        
        if success:
            show_success(f"✅ Desconexión de {row['Nombre']} marcada como resuelta")
            
            # Notificación
            if 'notification_manager' in st.session_state:
                st.session_state.notification_manager.add(
                    notification_type="desconexion_resuelta",
                    message=f"Desconexión resuelta: {row['Nº Cliente']} - {row['Nombre']}",
                    user_target="all",
                    claim_id=row.get("ID Reclamo", "")
                )
            
            return True
        else:
            show_error(f"❌ Error al actualizar: {error}")
            return False
    except Exception as e:
        error_msg = f"❌ Error inesperado: {str(e)}"
        show_error(error_msg)
        cloud_log(f"Error marcando desconexión como resuelta: {str(e)}", "error")
        return False