# helpers.py - Funciones utilitarias para la aplicación

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import re

def show_warning(message):
    """Muestra un warning elegante"""
    st.warning(f"⚠️ {message}")

def show_error(message):
    """Muestra un error elegante"""
    st.error(f"❌ {message}")

def show_success(message):
    """Muestra un mensaje de éxito elegante"""
    st.success(f"✅ {message}")

def show_info(message):
    """Muestra un mensaje informativo elegante"""
    st.info(f"ℹ️ {message}")

def format_phone_number(phone):
    """Formatea un número de teléfono argentino"""
    if pd.isna(phone) or phone == '':
        return ''
    
    phone_str = str(phone).strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Remover caracteres no numéricos
    phone_str = re.sub(r'[^\d]', '', phone_str)
    
    if phone_str.startswith('54'):
        phone_str = phone_str[2:]
    
    if phone_str.startswith('0'):
        phone_str = phone_str[1:]
    
    if len(phone_str) == 10:
        return f"+54 {phone_str[:3]} {phone_str[3:7]} {phone_str[7:]}"
    elif len(phone_str) == 8:
        return f"+54 11 {phone_str[:4]} {phone_str[4:]}"
    elif len(phone_str) == 11 and phone_str.startswith('15'):
        return f"+54 9 {phone_str[2:4]} {phone_str[4:7]} {phone_str[7:]}"
    else:
        return phone_str

def format_dni(dni):
    """Formatea un DNI con puntos"""
    if pd.isna(dni) or dni == '':
        return ''
    
    dni_str = str(dni).strip().replace('.', '')
    # Remover caracteres no numéricos
    dni_str = re.sub(r'[^\d]', '', dni_str)
    
    if len(dni_str) > 3:
        parts = []
        # Formatear con puntos cada 3 dígitos desde el final
        for i in range(len(dni_str), 0, -3):
            start = max(0, i - 3)
            parts.insert(0, dni_str[start:i])
        return '.'.join(parts)
    return dni_str

def get_current_datetime():
    """Obtiene la fecha y hora actual de Argentina"""
    return datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))

def format_datetime(dt, format_str='%d/%m/%Y %H:%M'):
    """Formatea un datetime object"""
    if pd.isna(dt):
        return ''
    try:
        return dt.strftime(format_str)
    except:
        return ''

def truncate_text(text, max_length=50):
    """Trunca texto muy largo"""
    if pd.isna(text) or text == '':
        return ''
    text_str = str(text)
    if len(text_str) > max_length:
        return text_str[:max_length] + '...'
    return text_str

def is_valid_email(email):
    """Valida formato básico de email"""
    if pd.isna(email) or email == '':
        return False
    email_str = str(email).strip()
    # Expresión regular mejorada para validación de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email_str) is not None

def safe_float_conversion(value, default=0.0):
    """Convierte seguro a float"""
    try:
        if pd.isna(value) or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value, default=0):
    """Convierte seguro a int"""
    try:
        if pd.isna(value) or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def get_status_badge(status):
    """Devuelve un badge colorizado según el estado"""
    status_colors = {
        'Pendiente': 'warning',
        'En Proceso': 'info', 
        'Resuelto': 'success',
        'Cerrado': 'success',
        'Cancelado': 'danger',
        'Derivado': 'primary',
        'Asignado': 'info',
        'En Curso': 'info',
        'Completado': 'success'
    }
    return status, status_colors.get(status, 'secondary')

def format_currency(amount):
    """Formatea un monto como currency argentino"""
    try:
        amount_float = safe_float_conversion(amount)
        if pd.isna(amount_float):
            return "$0,00"
        return f"${amount_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return str(amount)

def get_breadcrumb_icon(page_name):
    """Devuelve el icono correspondiente para el breadcrumb"""
    icons = {
        "Inicio": "🏠",
        "Reclamos cargados": "📊",
        "Gestión de clientes": "👥", 
        "Imprimir reclamos": "🖨️",
        "Seguimiento técnico": "🔧",
        "Cierre de Reclamos": "✅",
        "Dashboard": "📈",
        "Reportes": "📋",
        "Configuración": "⚙️"
    }
    return icons.get(page_name, "📋")

# Nueva función para entorno cloud
def is_cloud_environment():
    """
    Detecta si la aplicación se está ejecutando en un entorno cloud como Render
    """
    import os
    return 'RENDER' in os.environ or 'DYNO' in os.environ or 'PORT' in os.environ

# Nueva función para logging optimizado en cloud
def cloud_log(message, level='info'):
    """
    Logging optimizado para entornos cloud
    """
    if is_cloud_environment():
        # En cloud, usar print para ver en logs de Render
        print(f"[{level.upper()}] {message}")
    else:
        # En local, usar st.write o mantener silencioso
        if level == 'error':
            st.error(message)
        elif level == 'warning':
            st.warning(message)
        elif level == 'info':
            st.info(message)

# Nueva función para sanitizar datos para Google Sheets
def sanitize_for_sheets(value):
    """
    Sanitiza valores para evitar problemas con Google Sheets
    """
    if pd.isna(value) or value is None:
        return ''
    
    value_str = str(value).strip()
    
    # Remover caracteres problemáticos para Sheets
    problem_chars = ['=', '+', '-', '@']
    if value_str and value_str[0] in problem_chars:
        value_str = "'" + value_str
    
    # Limitar longitud para evitar problemas
    if len(value_str) > 50000:
        value_str = value_str[:50000] + '...'
    
    return value_str