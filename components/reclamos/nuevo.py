# components/reclamos/nuevo.py

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.date_utils import ahora_argentina, format_fecha, parse_fecha
from utils.api_manager import api_manager
from utils.data_manager import batch_update_sheet
from utils.helpers import cloud_log, show_success, show_error, show_warning, show_info, format_phone_number
from config.settings import (
    SECTORES_DISPONIBLES,
    TIPOS_RECLAMO,
    DEBUG_MODE,
    IS_RENDER
)

# --- ESTILOS CSS PARA FORMULARIO DE RECLAMOS ---
RECLAMOS_STYLES = """
<style>
.nuevo-reclamo-container {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    padding: 2rem;
    margin: 2rem 0;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
}

.reclamo-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-light);
}

.reclamo-icon {
    font-size: 2.5rem;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.reclamo-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.reclamo-form {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    margin: 1rem 0;
}

.reclamo-form:hover {
    border-color: var(--primary-color);
    box-shadow: var(--shadow-sm);
}

.reclamo-card {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    border: 1px solid var(--border-color);
    margin: 0.75rem 0;
    transition: all 0.3s ease;
}

.reclamo-card:hover {
    background: var(--bg-secondary);
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.warning-banner {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--warning-color);
}

.error-banner {
    background: rgba(220, 38, 38, 0.1);
    border: 1px solid rgba(220, 38, 38, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--danger-color);
}

.success-banner {
    background: rgba(5, 150, 105, 0.1);
    border: 1px solid rgba(5, 150, 105, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--success-color);
}

.info-banner {
    background: rgba(102, 217, 239, 0.1);
    border: 1px solid rgba(102, 217, 239, 0.3);
    border-radius: var(--radius-md);
    padding: 1rem;
    margin: 1rem 0;
    border-left: 4px solid var(--primary-color);
}
</style>
"""

# --- FUNCIONES HELPER MEJORADAS ---
def _normalizar_datos(df_clientes, df_reclamos, nro_cliente):
    """Normaliza datos solo cuando es necesario con manejo robusto"""
    try:
        if not nro_cliente:
            return df_clientes, df_reclamos
        
        df_clientes_normalizado = df_clientes.copy()
        df_reclamos_normalizado = df_reclamos.copy()
        
        df_clientes_normalizado["Nº Cliente"] = df_clientes_normalizado["Nº Cliente"].astype(str).str.strip()
        df_reclamos_normalizado["Nº Cliente"] = df_reclamos_normalizado["Nº Cliente"].astype(str).str.strip()
        
        return df_clientes_normalizado, df_reclamos_normalizado
    except Exception as e:
        cloud_log(f"Error normalizando datos: {str(e)}", "error")
        return df_clientes, df_reclamos

def _validar_y_normalizar_sector(sector_input):
    """Valida y normaliza el sector ingresado con mejor manejo de errores"""
    try:
        if not sector_input:
            return "1", "⚠️ El sector no puede estar vacío"
            
        sector_limpio = str(sector_input).strip()
        
        # Intentar convertir a número
        try:
            sector_num = int(sector_limpio)
            if 1 <= sector_num <= 17:
                return str(sector_num), None
            else:
                return None, f"⚠️ El sector debe estar entre 1 y 17. Se ingresó: {sector_num}"
        except ValueError:
            # Verificar si es un sector válido de la lista
            if sector_limpio in SECTORES_DISPONIBLES:
                return sector_limpio, None
            else:
                return None, f"⚠️ Sector no válido. Opciones: {', '.join(SECTORES_DISPONIBLES[:5])}..."
            
    except Exception as e:
        cloud_log(f"Error validando sector: {str(e)}", "error")
        return None, "⚠️ Error al validar el sector"

def _verificar_reclamos_activos(nro_cliente, df_reclamos):
    """Verifica reclamos activos de forma eficiente con manejo robusto"""
    try:
        if not nro_cliente or df_reclamos.empty:
            return pd.DataFrame()
        
        # Normalizar número de cliente para búsqueda
        nro_cliente_clean = str(nro_cliente).strip()
        
        if nro_cliente_clean not in df_reclamos["Nº Cliente"].values:
            return pd.DataFrame()
        
        reclamos_cliente = df_reclamos[df_reclamos["Nº Cliente"] == nro_cliente_clean].copy()
        
        # Convertir estados a minúsculas para comparación case-insensitive
        estados_activos = ["pendiente", "en curso"]
        reclamos_activos = reclamos_cliente[
            reclamos_cliente["Estado"].astype(str).str.strip().str.lower().isin(estados_activos) |
            (reclamos_cliente["Tipo de reclamo"].astype(str).str.strip().str.lower() == "desconexion a pedido")
        ]
        
        return reclamos_activos
    except Exception as e:
        cloud_log(f"Error verificando reclamos activos: {str(e)}", "error")
        return pd.DataFrame()

def generar_id_unico():
    """Genera un ID único para reclamos"""
    import uuid
    return str(uuid.uuid4())[:8].upper()

# --- FUNCIÓN PRINCIPAL OPTIMIZADA CON ESTILO CRM ---
def render_nuevo_reclamo(df_reclamos, df_clientes, sheet_reclamos, sheet_clientes, current_user=None):
    """
    Muestra la sección para cargar nuevos reclamos con estilo CRM
    """
    st.markdown(RECLAMOS_STYLES, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nuevo-reclamo-container">
        <div class="reclamo-header">
            <div class="reclamo-icon">📝</div>
            <h2 class="reclamo-title">Cargar Nuevo Reclamo</h2>
        </div>
    """, unsafe_allow_html=True)

    estado = {
        'nro_cliente': '',
        'cliente_existente': None,
        'formulario_bloqueado': False,
        'reclamo_guardado': False,
        'cliente_nuevo': False,
        'reclamos_activos': pd.DataFrame()
    }

    # Input de número de cliente
    estado['nro_cliente'] = st.text_input(
        "🔢 N° de Cliente *", 
        placeholder="Ingresa el número de cliente",
        help="Número único del cliente (obligatorio)",
        key="nro_cliente_input"
    ).strip()

    if estado['nro_cliente']:
        # Normalizar datos
        df_clientes_norm, df_reclamos_norm = _normalizar_datos(
            df_clientes, df_reclamos, estado['nro_cliente']
        )
        
        # Buscar cliente
        match = df_clientes_norm[df_clientes_norm["Nº Cliente"] == estado['nro_cliente']]
        
        if not match.empty:
            estado['cliente_existente'] = match.iloc[0].to_dict()
            st.markdown("""
            <div class="success-banner">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">✅</span>
                    <span>Cliente reconocido, datos auto-cargados</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            estado['cliente_nuevo'] = True
            st.markdown("""
            <div class="info-banner">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">ℹ️</span>
                    <span>Este cliente no existe en la base y se cargará como cliente nuevo</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Verificar reclamos activos
        estado['reclamos_activos'] = _verificar_reclamos_activos(estado['nro_cliente'], df_reclamos_norm)
        
        if not estado['reclamos_activos'].empty:
            estado['formulario_bloqueado'] = True
            
            # NOTIFICACIÓN DE INTENTO DE RECLAMO REPETIDO
            if 'notification_manager' in st.session_state:
                st.session_state.notification_manager.add(
                    notification_type="reclamo_repetido",
                    message=f"⚠️ Intento de reclamo duplicado para cliente {estado['nro_cliente']}",
                    user_target="admin",
                    claim_id=estado['nro_cliente']
                )
            
            st.markdown("""
            <div class="error-banner">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <span style="font-size: 1.2rem;">⚠️</span>
                    <span><strong>Este cliente ya tiene reclamos activos</strong></span>
                </div>
            """, unsafe_allow_html=True)
            
            # Mostrar reclamos activos
            for _, reclamo in estado['reclamos_activos'].iterrows():
                fecha_reclamo = format_fecha(reclamo.get('Fecha y hora'), '%d/%m/%Y %H:%M') if pd.notna(reclamo.get('Fecha y hora')) else 'Fecha no disponible'
                
                st.markdown(f"""
                <div class="reclamo-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div>
                            <strong>📅 {fecha_reclamo}</strong>
                        </div>
                        <div style="background: rgba(245, 158, 11, 0.2); padding: 0.25rem 0.75rem; border-radius: var(--radius-md); 
                                  color: var(--warning-color); font-size: 0.85rem; font-weight: 600;">
                            {reclamo.get('Estado', 'Sin estado')}
                        </div>
                    </div>
                    <div style="color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <strong>📌 Tipo:</strong> {reclamo.get('Tipo de reclamo', 'N/A')}
                    </div>
                    <div style="color: var(--text-secondary);">
                        <strong>📝 Detalles:</strong> {reclamo.get('Detalles', 'N/A')[:150]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Cierre del error-banner

    # Mostrar formulario si no está bloqueado
    if estado['reclamo_guardado']:
        st.markdown("""
        <div class="success-banner">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">✅</span>
                <span><strong>Reclamo registrado correctamente</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para nuevo reclamo
        if st.button("📝 Crear Otro Reclamo", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
    elif not estado['formulario_bloqueado'] and estado['nro_cliente']:
        estado = _mostrar_formulario_reclamo(estado, df_clientes, sheet_reclamos, sheet_clientes, current_user)

    st.markdown("</div>", unsafe_allow_html=True)  # Cierre del container
    return estado

# --- FUNCIÓN DE FORMULARIO MEJORADA CON ESTILO CRM ---
def _mostrar_formulario_reclamo(estado, df_clientes, sheet_reclamos, sheet_clientes, current_user):
    """Muestra y procesa el formulario de nuevo reclamo con estilo CRM"""
    
    st.markdown("<div class='reclamo-form'>", unsafe_allow_html=True)
    st.markdown("### 📋 Datos del Reclamo")
    
    with st.form("reclamo_formulario", clear_on_submit=True):
        col1, col2 = st.columns(2)

        # Datos del cliente (existe o nuevo)
        if estado['cliente_existente']:
            cliente_data = estado['cliente_existente']
            
            with col1:
                nombre = st.text_input(
                    "👤 Nombre del Cliente *",
                    value=cliente_data.get("Nombre", ""),
                    help="Nombre completo del cliente",
                    placeholder="JUAN PÉREZ"
                )
                direccion = st.text_input(
                    "📍 Dirección *",
                    value=cliente_data.get("Dirección", ""),
                    help="Dirección completa",
                    placeholder="CALLE PRINCIPAL 123"
                )

            with col2:
                telefono = st.text_input(
                    "📞 Teléfono",
                    value=cliente_data.get("Teléfono", ""),
                    help="Teléfono de contacto (opcional)",
                    placeholder="011-1234-5678"
                )
                
                # Sector con validación mejorada
                sector_existente = cliente_data.get("Sector", "1")
                sector_normalizado, error_sector = _validar_y_normalizar_sector(sector_existente)
                
                if error_sector:
                    show_warning(error_sector)
                    sector = st.text_input("🔢 Sector (1-17) *", value="1", help="Sector entre 1 y 17")
                else:
                    sector = st.text_input("🔢 Sector (1-17) *", value=sector_normalizado, help="Sector entre 1 y 17")

        else:
            with col1:
                nombre = st.text_input(
                    "👤 Nombre del Cliente *", 
                    placeholder="Nombre completo",
                    help="Campo obligatorio"
                )
                direccion = st.text_input(
                    "📍 Dirección *", 
                    placeholder="Dirección completa",
                    help="Campo obligatorio"
                )
            
            with col2:
                telefono = st.text_input(
                    "📞 Teléfono", 
                    placeholder="Número de contacto",
                    help="Opcional - solo números, espacios o guiones"
                )
                sector = st.text_input(
                    "🔢 Sector (1-17) *", 
                    placeholder="Ej: 5",
                    help="Sector entre 1 y 17 (obligatorio)"
                )

        # Campos del reclamo
        st.markdown("---")
        tipo_reclamo = st.selectbox(
            "📌 Tipo de Reclamo *", 
            TIPOS_RECLAMO,
            help="Selecciona el tipo de reclamo"
        )
        
        detalles = st.text_area(
            "📝 Detalles del Reclamo", 
            placeholder="Describe el problema, síntomas, horarios, etc...",
            height=120,
            help="Descripción detallada del problema (opcional pero recomendado)"
        )

        col3, col4 = st.columns(2)
        with col3:
            precinto = st.text_input(
                "🔒 N° de Precinto",
                value=estado['cliente_existente'].get("N° de Precinto", "") if estado['cliente_existente'] else "",
                placeholder="Número de precinto",
                help="Opcional"
            )
        
        with col4:
            atendido_por = st.text_input(
                "👤 Atendido por *", 
                placeholder="Nombre de quien atiende", 
                value=current_user or "",
                help="Persona que recibe el reclamo (obligatorio)"
            )

        enviado = st.form_submit_button(
            "✅ Guardar Reclamo", 
            use_container_width=True,
            type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if enviado:
        estado = _procesar_envio_formulario(
            estado, nombre, direccion, telefono, sector, 
            tipo_reclamo, detalles, precinto, atendido_por,
            df_clientes, sheet_reclamos, sheet_clientes
        )
    
    return estado

# --- FUNCIÓN DE PROCESAMIENTO OPTIMIZADA CON NOTIFICACIONES ---
def _procesar_envio_formulario(estado, nombre, direccion, telefono, sector, tipo_reclamo, 
                              detalles, precinto, atendido_por, df_clientes, sheet_reclamos, sheet_clientes):
    """Procesa el envío del formulario de manera optimizada"""
    
    # Validar campos obligatorios
    campos_obligatorios = {
        "Nombre": nombre.strip(),
        "Dirección": direccion.strip(),
        "Sector": str(sector).strip(),
        "Tipo de reclamo": tipo_reclamo.strip(),
        "Atendido por": atendido_por.strip()
    }
    
    campos_vacios = [campo for campo, valor in campos_obligatorios.items() if not valor]
    
    if campos_vacios:
        show_error(f"❌ Campos obligatorios vacíos: {', '.join(campos_vacios)}")
        return estado

    # Validar y normalizar sector
    sector_normalizado, error_sector = _validar_y_normalizar_sector(sector)
    if error_sector:
        show_error(error_sector)
        return estado

    with st.spinner("🔄 Guardando reclamo..."):
        try:
            # Preparar datos del reclamo
            fecha_hora = ahora_argentina()
            estado_reclamo = "Desconexión" if "desconexion a pedido" in tipo_reclamo.lower() else "Pendiente"
            id_reclamo = generar_id_unico()

            # Formatear teléfono si existe
            telefono_formateado = format_phone_number(telefono.strip()) if telefono.strip() else ""

            fila_reclamo = [
                format_fecha(fecha_hora),                    # Fecha y hora
                estado['nro_cliente'],                      # Nº Cliente
                sector_normalizado,                         # Sector
                nombre.upper(),                             # Nombre
                direccion.upper(),                          # Dirección
                telefono_formateado,                        # Teléfono (puede estar vacío)
                tipo_reclamo,                               # Tipo de reclamo
                detalles.upper() if detalles else "",       # Detalles (puede estar vacío)
                estado_reclamo,                             # Estado
                "",                                         # Técnico (vacío inicialmente)
                precinto.strip() if precinto else "",       # Precinto (puede estar vacío)
                atendido_por.upper(),                       # Atendido por
                "", "", "",                                 # Campos adicionales
                id_reclamo                                  # ID único
            ]

            # Guardar reclamo
            success, error = api_manager.safe_sheet_operation(
                sheet_reclamos.append_row,
                fila_reclamo
            )

            if success:
                estado.update({
                    'reclamo_guardado': True,
                    'formulario_bloqueado': True
                })
                
                # NOTIFICACIÓN DE NUEVO RECLAMO
                if 'notification_manager' in st.session_state:
                    st.session_state.notification_manager.add(
                        notification_type="nuevo_reclamo",
                        message=f"📝 Nuevo reclamo {id_reclamo} - {tipo_reclamo} para cliente {estado['nro_cliente']}",
                        user_target="all",
                        claim_id=id_reclamo
                    )
                
                cloud_log(f"Nuevo reclamo {id_reclamo} creado por {atendido_por}", "info")
                
                # Gestionar cliente (nuevo o actualización)
                _gestionar_cliente(
                    estado['nro_cliente'], sector_normalizado, nombre, 
                    direccion, telefono_formateado, precinto, df_clientes, sheet_clientes
                )
                
                # Limpiar cache y forzar recarga
                st.cache_data.clear()
                st.rerun()
                
            else:
                show_error(f"❌ Error al guardar: {error}")
                cloud_log(f"Error guardando reclamo: {error}", "error")

        except Exception as e:
            error_msg = f"❌ Error inesperado: {str(e)}"
            show_error(error_msg)
            cloud_log(f"Error inesperado en nuevo reclamo: {str(e)}", "error")
            if DEBUG_MODE:
                st.exception(e)
    
    return estado

def _gestionar_cliente(nro_cliente, sector, nombre, direccion, telefono, precinto, df_clientes, sheet_clientes):
    """Gestiona la creación o actualización del cliente con notificaciones"""
    try:
        cliente_existente = df_clientes[df_clientes["Nº Cliente"].astype(str).str.strip() == str(nro_cliente).strip()]
        
        if cliente_existente.empty:
            # Crear nuevo cliente
            nuevo_id = str(uuid.uuid4())[:8].upper()
            fila_cliente = [
                nro_cliente, 
                sector,
                nombre.upper(),
                direccion.upper(), 
                telefono,
                precinto if precinto else "", 
                nuevo_id,
                format_fecha(ahora_argentina())
            ]
            
            success, error = api_manager.safe_sheet_operation(sheet_clientes.append_row, fila_cliente)
            if success:
                show_info("ℹ️ Nuevo cliente registrado automáticamente")
                
                # NOTIFICACIÓN DE NUEVO CLIENTE
                if 'notification_manager' in st.session_state:
                    st.session_state.notification_manager.add(
                        notification_type="cliente_nuevo",
                        message=f"🆕 Cliente N° {nro_cliente} - {nombre.upper()} creado desde reclamo",
                        user_target="admin",
                        action=f"clientes:{nro_cliente}"
                    )
        else:
            # Actualizar cliente existente si hay cambios
            updates = []
            idx = cliente_existente.index[0] + 2
            
            campos_actualizar = {
                "B": sector,
                "C": nombre.upper(),
                "D": direccion.upper(),
                "E": telefono,
                "F": precinto if precinto else ""
            }
            
            for col, nuevo_valor in campos_actualizar.items():
                campo_name = ["Sector", "Nombre", "Dirección", "Teléfono", "N° de Precinto"][list(campos_actualizar.keys()).index(col)]
                valor_actual = str(cliente_existente.iloc[0][campo_name]).strip() if campo_name in cliente_existente.columns else ""
                if valor_actual != str(nuevo_valor).strip():
                    updates.append({"range": f"{col}{idx}", "values": [[nuevo_valor]]})
            
            if updates:
                success, error = api_manager.safe_sheet_operation(
                    batch_update_sheet, sheet_clientes, updates, is_batch=True
                )
                if success:
                    show_info("🔁 Datos del cliente actualizados automáticamente")
                    
    except Exception as e:
        cloud_log(f"Error gestionando cliente desde reclamo: {str(e)}", "error")
        # No mostrar error al usuario para no interrumpir el flujo del reclamo