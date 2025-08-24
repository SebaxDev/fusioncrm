"""
Configuración central de la aplicación
Versión 3.1 - Optimizado para Render con GOOGLE_SHEETS_CREDENTIALS
"""

import os
import json
import streamlit as st

from google.oauth2.service_account import Credentials
import gspread

# --------------------------
# DETECCIÓN DE ENTORNO (RENDER vs LOCAL)
# --------------------------
IS_RENDER = 'RENDER' in os.environ or 'PORT' in os.environ
IS_DEVELOPMENT = not IS_RENDER

# --------------------------
# CONFIGURACIÓN DE GOOGLE SHEETS
# --------------------------
# ID de la hoja
SHEET_ID = os.environ.get(
    "GOOGLE_SHEET_ID",
    "13R_3Mdr25Jd-nGhK7CxdcbKkFWLc0LPdYrOLOY8sZJo"  # valor por defecto en desarrollo
)

WORKSHEET_RECLAMOS = "Reclamos"
WORKSHEET_CLIENTES = "Clientes"
WORKSHEET_USUARIOS = "usuarios"
WORKSHEET_NOTIFICACIONES = "Notificaciones"

MAX_NOTIFICATIONS = 15  # Aumentado para mejor UX en CRM

# Cargar credenciales desde variable de entorno en Render
def get_gspread_client():
    """Devuelve un cliente autorizado de gspread"""
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)

    # Fallback para desarrollo local con secrets.toml
    if "google_sheets" in st.secrets:
        creds_dict = dict(st.secrets["google_sheets"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)

    raise RuntimeError("No se encontraron credenciales de Google Sheets")

# --------------------------
# NOTIFICACIONES
# --------------------------
NOTIFICATION_TYPES = {
    "unassigned_claim": {"priority": "alta", "icon": "⏱️", "color": "#FF6B6B"},
    "status_change": {"priority": "media", "icon": "🔄", "color": "#4ECDC4"},
    "duplicate_claim": {"priority": "alta", "icon": "⚠️", "color": "#FFE66D"},
    "new_assignment": {"priority": "media", "icon": "📌", "color": "#45B7D1"},
    "client_update": {"priority": "baja", "icon": "✏️", "color": "#96CEB4"},
    "daily_reminder": {"priority": "baja", "icon": "📅", "color": "#FECA57"},
    "nuevo_reclamo": {"priority": "media", "icon": "🆕", "color": "#54A0FF"},
    "reclamo_asignado": {"priority": "media", "icon": "👷", "color": "#5F27CD"},
    "trabajo_asignado": {"priority": "media", "icon": "🛠️", "color": "#FF9FF3"},
    "cierre_exitoso": {"priority": "media", "icon": "✅", "color": "#10AC84"},
    "alerta_urgente": {"priority": "critica", "icon": "🚨", "color": "#EE5A24"},
}

COLUMNAS_NOTIFICACIONES = [
    "ID", "Tipo", "Prioridad", "Mensaje", 
    "Usuario_Destino", "ID_Reclamo", "Fecha_Hora", "Leída", "Acción", "Color"
]

# --------------------------
# ESTRUCTURAS DE DATOS MEJORADAS
# --------------------------
COLUMNAS_RECLAMOS = [
    "Fecha y hora", "Nº Cliente", "Sector", "Nombre", 
    "Dirección", "Teléfono", "Tipo de reclamo", "Detalles", 
    "Estado", "Técnico", "N° de Precinto", "Atendido por", 
    "Fecha_formateada", "ID Reclamo", "Prioridad", "Notas", "Materiales_Utilizados"
]

COLUMNAS_CLIENTES = [
    "Nº Cliente", "Sector", "Nombre", "Dirección", 
    "Teléfono", "N° de Precinto", "ID Cliente", "Última Modificación",
    "Email", "Observaciones", "Historial_Reclamos"
]

COLUMNAS_USUARIOS = [
    "username", "password", "nombre", "rol", "activo", "modo_oscuro",
    "email", "telefono", "sector_asignado", "ultimo_acceso", "permisos_especiales"
]

# --------------------------
# IDENTIFICADORES ÚNICOS
# --------------------------
COLUMNA_ID_RECLAMO = "ID Reclamo"
COLUMNA_ID_CLIENTE = "ID Cliente"

# --------------------------
# ROLES Y PERMISOS MEJORADOS
# --------------------------
PERMISOS_POR_ROL = {
    'admin': {
        'descripcion': 'Administrador del sistema - Acceso completo',
        'permisos': ['*'],
        'color': '#FF5733',
        'icon': '👑'
    },
    'supervisor': {
        'descripcion': 'Supervisor técnico - Gestión de equipos',
        'permisos': [
            'inicio', 'reclamos_cargados', 'seguimiento_tecnico', 
            'cierre_reclamos', 'dashboard', 'reportes', 'gestion_equipos'
        ],
        'color': '#338AFF',
        'icon': '👔'
    },
    'tecnico': {
        'descripcion': 'Técnico de campo - Ejecución de trabajos',
        'permisos': [
            'inicio', 'reclamos_cargados', 'seguimiento_tecnico', 
            'cierre_reclamos', 'mi_agenda'
        ],
        'color': '#33D1FF',
        'icon': '🔧'
    },
    'oficina': {
        'descripcion': 'Personal administrativo - Atención al cliente',
        'permisos': [
            'inicio', 'reclamos_cargados', 'gestion_clientes',
            'imprimir_reclamos', 'dashboard'
        ],
        'color': '#9D33FF',
        'icon': '💼'
    },
    'consulta': {
        'descripcion': 'Usuario de solo consulta - Visualización',
        'permisos': [
            'inicio', 'reclamos_cargados', 'dashboard'
        ],
        'color': '#FF33A8',
        'icon': '👀'
    }
}

# Mapeo de opciones de navegación a permisos
OPCIONES_PERMISOS = {
    "Inicio": "inicio",
    "Dashboard": "dashboard",
    "Reclamos cargados": "reclamos_cargados",
    "Gestión de clientes": "gestion_clientes",
    "Imprimir reclamos": "imprimir_reclamos",
    "Seguimiento técnico": "seguimiento_tecnico",
    "Cierre de Reclamos": "cierre_reclamos",
    "Reportes": "reportes",
    "Mi Agenda": "mi_agenda",
    "Gestión de Equipos": "gestion_equipos",
    "Configuración": "configuracion"
}

# --------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# --------------------------
SECTORES_DISPONIBLES = [str(n) for n in range(1, 18)] + ["OTRO"]

TECNICOS_DISPONIBLES = [
    "Braian", "Conejo", "Juan", "Junior", "Maxi", 
    "Ramon", "Roque", "Viki", "Oficina", "Base", "Externo"
]

TIPOS_RECLAMO = [
    "Conexion C+I", "Conexion Cable", "Conexion Internet", "Suma Internet",
    "Suma Cable", "Reconexion", "Reconexion C+I", "Reconexion Internet", "Reconexion Cable", "Sin Señal Ambos", "Sin Señal Cable",
    "Sin Señal Internet", "Sintonia", "Interferencia", "Traslado",
    "Extension", "Extension x2", "Extension x3", "Extension x4", "Cambio de Ficha",
    "Cambio de Equipo", "Reclamo", "Cambio de Plan", "Desconexion a Pedido",
    "Mantenimiento Preventivo", "Instalación Especial", "Consulta Técnica"
]

# Prioridades para reclamos
PRIORIDADES_RECLAMO = [
    "Baja", "Normal", "Alta", "Urgente", "Crítica"
]

# --------------------------
# MATERIALES Y EQUIPOS MEJORADOS
# --------------------------
ROUTER_POR_SECTOR = {
    "1": "huawei", "2": "huawei", "3": "huawei", "4": "huawei", "5": "huawei",
    "6": "vsol", "7": "vsol", "8": "vsol", "9": "huawei", "10": "huawei",
    "11": "vsol", "12": "huawei", "13": "huawei", "14": "vsol", "15": "huawei",
    "16": "huawei", "17": "huawei", "OTRO": "huawei"
}

MATERIALES_POR_RECLAMO = {
    "Conexion C+I": {"router_catv": 1, "conector": 2, "ficha_f": 2, "cable_coaxial": 10},
    "Conexion Cable": {"ficha_f": 2, "micro": 1, "cable_coaxial": 5},
    "Conexion Internet": {"router_internet": 1, "conector": 2, "cable_red": 10},
    "Suma Internet": {"router_catv": 1, "conector": 2, "ficha_f": 2, "cable_coaxial": 8},
    "Suma Cable": {"router_catv": 1, "ficha_f": 2, "cable_coaxial": 6},
    "Reconexion": {"ficha_f": 1},
    "Reconexion C+I": {"router_catv": 1, "conector": 2, "cable_coaxial": 3},
    "Reconexion Internet": {"router_internet": 1, "conector": 2, "cable_red": 3},
    "Reconexion Cable": {"ficha_f": 2, "micro": 1, "cable_coaxial": 3},
    "Sin Señal Ambos": {"conector": 1, "ficha_f": 1},
    "Sin Señal Cable": {"ficha_f": 2, "micro": 1, "cable_coaxial": 4},
    "Sin Señal Internet": {"conector": 1, "cable_red": 4},
    "Sintonia": {"ficha_f": 1},
    "Interferencia": {"ficha_f": 2, "filtro": 1},
    "Traslado": {"conector": 2, "ficha_f": 2, "cable_coaxial": 15},
    "Extension": {"cable_coaxial": 10},
    "Extension x2": {"derivador_x2": 1, "ficha_f": 4, "cable_coaxial": 8},
    "Extension x3": {"derivador_x3": 1, "ficha_f": 4, "cable_coaxial": 12},
    "Extension x4": {"derivador_x4": 1, "ficha_f": 8, "cable_coaxial": 16},
    "Cambio de Ficha": {"conector": 1, "ficha_f": 1, "micro": 1},
    "Cambio de Equipo": {"router": 1},
    "Reclamo": {"materiales_variables": 1},
    "Cambio de Plan": {},
    "Desconexion a Pedido": {},
    "Mantenimiento Preventivo": {"limpiador": 1, "ficha_f": 2},
    "Instalación Especial": {"materiales_especiales": 1, "cable_coaxial": 20},
    "Consulta Técnica": {}
}

# --------------------------
# CONFIGURACIÓN DE RENDIMIENTO PARA RENDER
# --------------------------
if IS_RENDER:
    API_DELAY = 1.5  # Menor delay en producción
    BATCH_DELAY = 1.5
    CACHE_TTL = 45  # Segundos para cache en producción
    MAX_ROWS_PER_PAGE = 50  # Paginación para mejor rendimiento
else:
    API_DELAY = 2.0  # Mayor delay en desarrollo
    BATCH_DELAY = 2.0
    CACHE_TTL = 30
    MAX_ROWS_PER_PAGE = 100

SESSION_TIMEOUT = 2700  # 45 minutos de inactividad

# --------------------------
# CONFIGURACIÓN DE ESTILOS CRM
# --------------------------
COLOR_PALETTE = {
    'primary': '#2563EB',      # Azul profesional
    'secondary': '#8B5CF6',    # Púrpura
    'success': '#059669',      # Verde
    'warning': '#D97706',      # Ámbar
    'error': '#DC2626',        # Rojo
    'info': '#0891B2',         # Cian
    'dark': '#1E293B',         # Gris oscuro
    'light': '#F8FAFC'         # Gris claro
}

THEME_CONFIG = {
    'light': {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8FAFC',
        'text_primary': '#1E293B',
        'text_secondary': '#475569'
    },
    'dark': {
        'bg_primary': '#272822',    # Monokai dark
        'bg_secondary': '#2D2E27',
        'text_primary': '#F8F8F2',
        'text_secondary': '#CFCFC2'
    }
}

# --------------------------
# FUNCIONES DE UTILIDAD MEJORADAS
# --------------------------
def obtener_permisos_por_rol(rol):
    """Devuelve los permisos asociados a un rol"""
    return PERMISOS_POR_ROL.get(rol, {}).get('permisos', [])

def rol_tiene_permiso(rol, permiso_requerido):
    """Verifica si un rol tiene un permiso específico"""
    if permiso_requerido == 'admin':
        return rol == 'admin'
    
    permisos = obtener_permisos_por_rol(rol)
    return '*' in permisos or permiso_requerido in permisos

def get_role_config(rol):
    """Obtiene la configuración completa de un rol"""
    return PERMISOS_POR_ROL.get(rol, {
        'descripcion': 'Rol no definido',
        'permisos': [],
        'color': '#64748B',
        'icon': '❓'
    })

def is_cloud_environment():
    """Determina si la aplicación se ejecuta en un entorno cloud"""
    return IS_RENDER

# --------------------------
# CONFIGURACIÓN DE DEPURACIÓN
# --------------------------
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

# --------------------------
# CONFIGURACIÓN DE BACKUP Y LOGGING
# --------------------------
if IS_RENDER:
    LOG_LEVEL = 'INFO'
    BACKUP_ENABLED = True
    AUTO_SAVE_INTERVAL = 300  # 5 minutos
else:
    LOG_LEVEL = 'DEBUG'
    BACKUP_ENABLED = False
    AUTO_SAVE_INTERVAL = 180  # 3 minutos

# --------------------------
# VALORES POR DEFECTO PARA NUEVOS REGISTROS
# --------------------------
DEFAULT_VALUES = {
    'estado_reclamo': 'Pendiente',
    'prioridad_reclamo': 'Normal',
    'tecnico_asignado': 'Sin asignar',
    'sector_cliente': 'OTRO',
    'rol_usuario': 'consulta',
    'activo_usuario': True,
    'modo_oscuro': False
}

# --------------------------
# LIMITES Y RESTRICCIONES
# --------------------------
MAX_CLIENTES_POR_PAGINA = 100
MAX_RECLAMOS_POR_PAGINA = 50
MAX_USUARIOS_POR_PAGINA = 30
MAX_HISTORIAL_CLIENTE = 20

# --------------------------
# CONFIGURACIÓN DE EXPORTACIÓN
# --------------------------
EXPORT_FORMATS = ['PDF', 'Excel', 'CSV', 'Imagen']
EXPORT_DEFAULT = 'PDF'