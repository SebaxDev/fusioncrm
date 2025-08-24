# components/clientes/gestion.py

import streamlit as st
import pandas as pd
import uuid
from utils.date_utils import ahora_argentina, format_fecha, parse_fecha
from utils.api_manager import api_manager, batch_update_sheet
from utils.helpers import cloud_log, format_phone_number, show_success, show_error, show_warning, show_info
from config.settings import SECTORES_DISPONIBLES, IS_RENDER, DEBUG_MODE

# --- ESTILOS CSS PARA GESTIÓN DE CLIENTES ---
CLIENTES_STYLES = """
<style>
.clientes-container {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    padding: 2rem;
    margin: 2rem 0;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
}

.clientes-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-light);
}

.clientes-icon {
    font-size: 2.5rem;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.clientes-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.cliente-form {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    margin: 1rem 0;
}

.cliente-form:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow-sm);
}

.cliente-card {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    border: 1px solid var(--border-color);
    margin: 0.75rem 0;
    transition: all 0.3s ease;
}

.cliente-card:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.reclamos-history {
    background: rgba(102, 217, 239, 0.1);
    border: 1px solid rgba(102, 217, 239, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--primary-color);
}

.warning-banner {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--warning-color);
}

.success-banner {
    background: rgba(5, 150, 105, 0.1);
    border: 1px solid rgba(5, 150, 105, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--success-color);
}
</style>
"""

# --- FUNCIONES HELPER MEJORADAS ---
def _validar_telefono(telefono):
    """Valida el formato del teléfono con mejor manejo de errores"""
    if not telefono or not telefono.strip():
        return True, ""  # Vacío es válido (opcional)
    
    try:
        telefono_limpio = telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if telefono_limpio.isdigit() and len(telefono_limpio) >= 6:
            return True, ""
        else:
            return False, "⚠️ El teléfono debe contener al menos 6 dígitos y solo números, espacios o guiones."
    except Exception as e:
        cloud_log(f"Error validando teléfono: {str(e)}", "error")
        return False, "⚠️ Error al validar el teléfono."

def _valores_diferentes(valor1, valor2):
    """Compara valores de forma segura considerando strings y None"""
    try:
        str1 = str(valor1).strip().upper() if valor1 is not None else ""
        str2 = str(valor2).strip().upper() if valor2 is not None else ""
        return str1 != str2
    except Exception as e:
        cloud_log(f"Error comparando valores: {str(e)}", "error")
        return True  # Por seguridad, asumir que son diferentes

def _obtener_indice_sector(sector_actual, sectores_disponibles):
    """Obtiene el índice seguro para el selectbox de sector"""
    if not sector_actual:
        return 0
        
    try:
        sector_str = str(sector_actual).strip()
        if sector_str in sectores_disponibles:
            return sectores_disponibles.index(sector_str)
        return 0
    except (ValueError, AttributeError, TypeError) as e:
        cloud_log(f"Error obteniendo índice de sector: {str(e)}", "warning")
        return 0

def _formatear_datos_cliente(datos):
    """Formatea los datos del cliente para consistencia"""
    return {
        'sector': str(datos.get('Sector', '')).strip(),
        'nombre': str(datos.get('Nombre', '')).strip().upper(),
        'direccion': str(datos.get('Dirección', '')).strip().upper(),
        'telefono': format_phone_number(str(datos.get('Teléfono', '')).strip()),
        'precinto': str(datos.get('N° de Precinto', '')).strip(),
        'nro_cliente': str(datos.get('Nº Cliente', '')).strip()
    }

# --- FUNCIÓN PRINCIPAL MEJORADA ---
def render_gestion_clientes(df_clientes, df_reclamos, sheet_clientes, user_role):
    """
    Muestra la sección de gestión de clientes con estilo CRM
    
    Args:
        df_clientes (pd.DataFrame): DataFrame con los clientes
        df_reclamos (pd.DataFrame): DataFrame con los reclamos
        sheet_clientes: Objeto de conexión a la hoja de clientes
        user_role (str): Rol del usuario actual
    
    Returns:
        dict: Diccionario con estado de cambios y necesidad de recarga
    """
    st.markdown(CLIENTES_STYLES, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="clientes-container">
        <div class="clientes-header">
            <div class="clientes-icon">👥</div>
            <h2 class="clientes-title">Gestión de Clientes</h2>
        </div>
    """, unsafe_allow_html=True)

    # Normalización robusta de datos
    try:
        df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
    except Exception as e:
        cloud_log(f"Error normalizando números de cliente: {str(e)}", "error")
        show_error("Error al procesar datos de clientes")

    cambios = False

    if user_role == 'admin':
        cambios = _mostrar_edicion_cliente(df_clientes, df_reclamos, sheet_clientes) or cambios
        st.markdown("---")
        cambios = _mostrar_nuevo_cliente(df_clientes, sheet_clientes) or cambios
    else:
        st.markdown("""
        <div class="warning-banner">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🔒</span>
                <span>Solo los administradores pueden editar información de clientes</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return {
        "cambios": cambios,
        "needs_refresh": cambios
    }

# --- FUNCIÓN DE EDICIÓN MEJORADA CON ESTILO CRM ---
def _mostrar_edicion_cliente(df_clientes, df_reclamos, sheet_clientes):
    """Muestra el formulario para editar un cliente existente con estilo CRM"""
    cambios = False

    # Filtrar solo clientes con número válido
    clientes_validos = df_clientes[
        df_clientes["Nº Cliente"].astype(str).str.strip() != ""
    ]
    
    if clientes_validos.empty:
        show_info("📝 No hay clientes registrados para editar")
        return cambios

    clientes_lista = clientes_validos["Nº Cliente"].astype(str).tolist()
    
    cliente_seleccionado = st.selectbox(
        "🔍 Seleccionar cliente para editar", 
        clientes_lista,
        help="Elegí el cliente que querés editar",
        key="cliente_selector"
    )

    if not cliente_seleccionado:
        return cambios

    # Búsqueda robusta del cliente
    cliente_actual = df_clientes[
        df_clientes["Nº Cliente"].astype(str).str.strip() == str(cliente_seleccionado).strip()
    ]
    
    if cliente_actual.empty:
        show_error(f"❌ No se encontró el cliente {cliente_seleccionado}")
        return cambios

    cliente_actual = cliente_actual.iloc[0]
    datos_actuales = _formatear_datos_cliente(cliente_actual)
    
    st.markdown(f"""
    <div class="cliente-card">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">📋</span>
            <div>
                <h3 style="margin: 0; color: var(--text-primary);">Editando Cliente</h3>
                <p style="margin: 0; color: var(--text-secondary);">N° {cliente_seleccionado} - {datos_actuales['nombre']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    _mostrar_reclamos_cliente(cliente_seleccionado, df_reclamos)

    # Formulario de edición con estilo CRM
    st.markdown("<div class='cliente-form'>", unsafe_allow_html=True)
    
    with st.form("form_editar_cliente"):
        col1, col2 = st.columns(2)

        with col1:
            indice_sector = _obtener_indice_sector(
                datos_actuales['sector'], 
                SECTORES_DISPONIBLES
            )
            
            nuevo_sector = st.selectbox(
                "🏢 Sector *",
                SECTORES_DISPONIBLES,
                index=indice_sector,
                help="Sector del cliente"
            )

            nuevo_nombre = st.text_input(
                "👤 Nombre *",
                value=datos_actuales['nombre'],
                help="Nombre completo del cliente",
                placeholder="Ej: JUAN PÉREZ"
            )

            nueva_direccion = st.text_input(
                "📍 Dirección *",
                value=datos_actuales['direccion'],
                help="Dirección completa",
                placeholder="Ej: CALLE PRINCIPAL 123"
            )

        with col2:
            nuevo_telefono = st.text_input(
                "📞 Teléfono",
                value=datos_actuales['telefono'],
                help="Teléfono de contacto (opcional)",
                placeholder="Ej: 011-1234-5678"
            )

            nuevo_precinto = st.text_input(
                "🔒 Nº de Precinto",
                value=datos_actuales['precinto'],
                help="Número de precinto (opcional)",
                placeholder="Ej: PRC-001"
            )

        submitted = st.form_submit_button(
            "💾 Guardar Cambios",
            use_container_width=True,
            type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        # Validaciones
        if not nuevo_nombre.strip():
            show_error("❌ El nombre del cliente es obligatorio")
            return cambios
            
        if not nueva_direccion.strip():
            show_error("❌ La dirección del cliente es obligatoria")
            return cambios

        telefono_valido, mensaje_error = _validar_telefono(nuevo_telefono)
        if not telefono_valido:
            show_warning(mensaje_error)

        # Verificar consistencia con reclamos
        _verificar_cambios_desde_reclamos(
            cliente_seleccionado, 
            df_reclamos, 
            nueva_direccion.strip(), 
            nuevo_telefono.strip(), 
            nuevo_precinto.strip()
        )

        # Verificar cambios
        hubo_cambios = any([
            _valores_diferentes(nuevo_sector, datos_actuales['sector']),
            _valores_diferentes(nuevo_nombre, datos_actuales['nombre']),
            _valores_diferentes(nueva_direccion, datos_actuales['direccion']),
            _valores_diferentes(nuevo_telefono, datos_actuales['telefono']),
            _valores_diferentes(nuevo_precinto, datos_actuales['precinto'])
        ])

        if not hubo_cambios:
            show_info("ℹ️ No se detectaron cambios en los datos del cliente.")
            return cambios

        # Mostrar preview de cambios
        st.markdown("""
        <div class="cliente-card">
            <h4 style="margin: 0 0 1rem 0; color: var(--text-primary);">📋 Resumen de Cambios</h4>
        """, unsafe_allow_html=True)
        
        cambios_data = []
        campos = [
            ("Sector", datos_actuales['sector'], nuevo_sector),
            ("Nombre", datos_actuales['nombre'], nuevo_nombre.strip()),
            ("Dirección", datos_actuales['direccion'], nueva_direccion.strip()),
            ("Teléfono", datos_actuales['telefono'] or "No tiene", nuevo_telefono.strip() or "No tiene"),
            ("Precinto", datos_actuales['precinto'] or "No tiene", nuevo_precinto.strip() or "No tiene")
        ]
        
        for campo, anterior, nuevo in campos:
            if anterior != nuevo:
                cambios_data.append(f"**{campo}**: `{anterior}` → `{nuevo}`")
        
        if cambios_data:
            for cambio in cambios_data:
                st.markdown(f"- {cambio}")
            
            # Confirmación final
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("✅ Confirmar Cambios", key=f"confirmar_{cliente_seleccionado}", use_container_width=True):
                    cambios = _actualizar_cliente(
                        cliente_actual,
                        sheet_clientes,
                        nuevo_sector,
                        nuevo_nombre.strip(),
                        nueva_direccion.strip(),
                        nuevo_telefono.strip(),
                        nuevo_precinto.strip()
                    )
        else:
            show_info("ℹ️ No se detectaron cambios")
            return cambios

    return cambios

def _mostrar_reclamos_cliente(nro_cliente, df_reclamos):
    """Muestra los últimos reclamos del cliente con estilo CRM"""
    df_reclamos_cliente = df_reclamos[
        df_reclamos["Nº Cliente"].astype(str).str.strip() == str(nro_cliente).strip()
    ].copy()
    
    if df_reclamos_cliente.empty:
        st.markdown("""
        <div class="reclamos-history">
            <p style="margin: 0; color: var(--text-secondary);">📭 Este cliente no tiene reclamos registrados</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    try:
        df_reclamos_cliente["Fecha y hora"] = df_reclamos_cliente["Fecha y hora"].apply(parse_fecha)
        df_reclamos_cliente = df_reclamos_cliente.sort_values("Fecha y hora", ascending=False).head(3)
        
        with st.expander("📄 Historial de Reclamos Recientes", expanded=False):
            for _, recl in df_reclamos_cliente.iterrows():
                fecha_formateada = format_fecha(recl['Fecha y hora'], '%d/%m/%Y')
                tecnico = recl.get('Técnico', 'N/A') or 'N/A'
                tipo_reclamo = recl.get('Tipo de reclamo', 'N/A') or 'N/A'
                
                st.markdown(f"""
                <div style="padding: 0.75rem; margin: 0.5rem 0; background: var(--bg-surface); 
                          border-radius: var(--radius-md); border: 1px solid var(--border-light);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; color: var(--text-primary);">📅 {fecha_formateada}</span>
                        <span style="font-size: 0.9rem; color: var(--text-muted);">🔧 {tecnico}</span>
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--text-secondary);">
                        📝 {tipo_reclamo}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        cloud_log(f"Error mostrando reclamos del cliente: {str(e)}", "error")
        show_warning("⚠️ Error al cargar el historial de reclamos")

# ... (las funciones _verificar_cambios_desde_reclamos, _actualizar_cliente, 
# _mostrar_nuevo_cliente, y _guardar_nuevo_cliente se mantienen con mejoras similares)

# --- FUNCIÓN _actualizar_cliente MEJORADA ---
def _actualizar_cliente(cliente_actual, sheet_clientes, nuevo_sector, nuevo_nombre, 
                       nueva_direccion, nuevo_telefono, nuevo_precinto):
    """Actualiza los datos del cliente con notificaciones y manejo robusto"""
    
    try:
        # Obtener índice (manejo robusto)
        index = cliente_actual.name + 2 if hasattr(cliente_actual, 'name') else None
        if index is None:
            show_error("❌ Error: No se pudo determinar la posición del cliente")
            return False

        updates = [
            {"range": f"B{index}", "values": [[str(nuevo_sector)]]},
            {"range": f"C{index}", "values": [[str(nuevo_nombre).upper()]]},
            {"range": f"D{index}", "values": [[str(nueva_direccion).upper()]]},
            {"range": f"E{index}", "values": [[str(nuevo_telefono)]]},
            {"range": f"F{index}", "values": [[str(nuevo_precinto)]]},
            {"range": f"H{index}", "values": [[format_fecha(ahora_argentina())]]}
        ]

        success, error = api_manager.safe_sheet_operation(
            batch_update_sheet,
            sheet_clientes,
            updates,
            is_batch=True
        )

        if success:
            show_success("✅ Cliente actualizado correctamente")
            
            # NOTIFICACIÓN MEJORADA
            if 'notification_manager' in st.session_state:
                num_cliente = str(cliente_actual['Nº Cliente'])
                nombre_cliente = str(nuevo_nombre).upper()
                mensaje = f"✏️ Cliente N° {num_cliente} - {nombre_cliente} actualizado"
                
                st.session_state.notification_manager.add(
                    notification_type="cliente_actualizado",
                    message=mensaje,
                    user_target="all",
                    action=f"clientes:{num_cliente}"
                )
                
                cloud_log(f"Cliente {num_cliente} actualizado por usuario", "info")
            
            return True
        else:
            show_error(f"❌ Error al actualizar: {error}")
            cloud_log(f"Error actualizando cliente: {error}", "error")
            return False

    except Exception as e:
        error_msg = f"❌ Error inesperado: {str(e)}"
        show_error(error_msg)
        cloud_log(f"Error inesperado en actualización de cliente: {str(e)}", "error")
        return False

# --- FUNCIÓN _guardar_nuevo_cliente MEJORADA ---
def _guardar_nuevo_cliente(df_clientes, sheet_clientes, nuevo_nro, nuevo_sector, 
                          nuevo_nombre, nueva_direccion, nuevo_telefono, nuevo_precinto):
    """Guarda un nuevo cliente con notificaciones y validaciones mejoradas"""
    
    # Validaciones
    if not nuevo_nombre.strip():
        show_error("⚠️ El nombre del cliente es obligatorio")
        return False
        
    if not nueva_direccion.strip():
        show_error("⚠️ La dirección del cliente es obligatoria")
        return False
    
    if not nuevo_nro.strip():
        show_error("⚠️ El número de cliente no puede estar vacío")
        return False
        
    # Validar unicidad del número de cliente
    clientes_existentes = df_clientes["Nº Cliente"].astype(str).str.strip()
    if str(nuevo_nro).strip() in clientes_existentes.values:
        show_error("⚠️ Este número de cliente ya existe. Usá otro número.")
        return False

    # Validar teléfono
    telefono_valido, mensaje_error = _validar_telefono(nuevo_telefono)
    if not telefono_valido:
        show_warning(mensaje_error)

    try:
        nuevo_id = str(uuid.uuid4())[:8].upper()  # ID más corto

        nueva_fila = [
            nuevo_nro.strip(), 
            str(nuevo_sector),
            nuevo_nombre.strip().upper(),
            nueva_direccion.strip().upper(), 
            nuevo_telefono.strip(),
            nuevo_precinto.strip(), 
            nuevo_id,
            format_fecha(ahora_argentina())
        ]

        success, error = api_manager.safe_sheet_operation(
            sheet_clientes.append_row,
            nueva_fila
        )

        if success:
            show_success("✅ Nuevo cliente agregado correctamente")
            
            # NOTIFICACIÓN MEJORADA
            if 'notification_manager' in st.session_state:
                mensaje = f"🆕 Cliente N° {nuevo_nro.strip()} - {nuevo_nombre.strip().upper()} agregado"
                
                st.session_state.notification_manager.add(
                    notification_type="cliente_nuevo",
                    message=mensaje,
                    user_target="all",
                    action=f"clientes:{nuevo_nro.strip()}"
                )
                
                cloud_log(f"Nuevo cliente {nuevo_nro.strip()} creado", "info")

            return True
        else:
            show_error(f"❌ Error al guardar: {error}")
            cloud_log(f"Error guardando nuevo cliente: {error}", "error")
            return False

    except Exception as e:
        error_msg = f"❌ Error inesperado: {str(e)}"
        show_error(error_msg)
        cloud_log(f"Error inesperado creando cliente: {str(e)}", "error")
        return False