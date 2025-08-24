"""
Módulo para gestión segura de datos con Google Sheets
Versión 3.2 - Con manejo robusto de errores y compatibilidad con API
"""
import streamlit as st
import time
import os
import json
from typing import List, Dict, Union, Optional

class ApiManager:
    def __init__(self):
        self.total_calls = 0
        self.error_count = 0
        self.last_call = 0

    def safe_sheet_operation(self, func, *args, is_batch=False, **kwargs):
        """
        Ejecuta una operación segura sobre la API de Google Sheets
        
        Args:
            func: función de gspread a ejecutar
            *args: argumentos posicionales para la función
            is_batch: bool, si es operación por lote (sólo informativo)
            **kwargs: argumentos clave
        
        Returns:
            tuple: (resultado, error) donde error es None si fue exitoso
        """
        try:
            self.total_calls += 1
            self.last_call = time.time()
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            self.error_count += 1
            return None, str(e)

    def get_api_stats(self):
        """
        Devuelve estadísticas de uso de la API actual
        """
        return {
            "total_calls": self.total_calls,
            "error_count": self.error_count,
            "last_call": self.last_call
        }

def batch_update_sheet(worksheet, updates: List[Dict[str, Union[str, List[List[str]]]]]) -> bool:
    """
    Realiza actualizaciones por lotes en una hoja de cálculo
    
    Args:
        worksheet: objeto de hoja de cálculo de gspread
        updates: lista de diccionarios con formato:
            [{"range": "A1:B2", "values": [["val1", "val2"], ["val3", "val4"]]}]
    
    Returns:
        bool: True si la operación fue exitosa
    """
    if not updates:
        return True
        
    try:
        worksheet.batch_update(updates)
        return True
    except Exception as e:
        st.error(f"Error en batch_update: {str(e)}")
        return False

# Función nueva para obtener credenciales compatibles con Render
def get_google_credentials():
    """
    Obtiene las credenciales de Google Sheets, compatible con Render y local
    """
    try:
        # Para Render: usar variable de entorno
        if 'GOOGLE_SHEETS_CREDENTIALS' in os.environ:
            creds_info = json.loads(os.environ['GOOGLE_SHEETS_CREDENTIALS'])
            return {**creds_info, "private_key": creds_info["private_key"].replace("\\n", "\n")}
        # Para desarrollo local: usar secrets de Streamlit
        else:
            return {**st.secrets["gcp_service_account"], "private_key": st.secrets["gcp_service_account"]["private_key"].replace("\\n", "\n")}
    except Exception as e:
        st.error(f"Error cargando credenciales: {str(e)}")
        return None

# Instancia única global
api_manager = ApiManager()

def init_api_session_state():
    """
    Inicializa api_manager en st.session_state si no existe aún
    """
    if "api_stats" not in st.session_state:
        st.session_state.api_stats = api_manager.get_api_stats()