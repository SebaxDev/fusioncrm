# components/notifications.py

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from utils.date_utils import ahora_argentina, format_fecha
from utils.api_manager import api_manager
from utils.data_manager import safe_get_sheet_data, batch_update_sheet
from utils.helpers import cloud_log
from config.settings import NOTIFICATION_TYPES, COLUMNAS_NOTIFICACIONES, MAX_NOTIFICATIONS, IS_RENDER

@st.cache_data(ttl=15 if IS_RENDER else 30)  # TTL más corto en Render
def get_cached_notifications(username, unread_only=True, limit=MAX_NOTIFICATIONS):
    """Obtiene notificaciones cacheadas con optimización para Render"""
    try:
        if 'notification_manager' not in st.session_state:
            return []
            
        return st.session_state.notification_manager.get_for_user(username, unread_only, limit)
    except Exception as e:
        cloud_log(f"Error en get_cached_notifications: {str(e)}", "error")
        return []

class NotificationManager:
    def __init__(self, sheet_notifications):
        self.sheet = sheet_notifications
        self.max_retries = 3 if IS_RENDER else 1  # Menos reintentos en Render

    def _get_next_id(self):
        """Obtiene el próximo ID de notificación de forma segura"""
        for attempt in range(self.max_retries):
            try:
                df = safe_get_sheet_data(self.sheet, COLUMNAS_NOTIFICACIONES)
                if df.empty or 'ID' not in df.columns:
                    return 1
                
                # Manejo robusto de IDs
                valid_ids = pd.to_numeric(df['ID'], errors='coerce').dropna()
                if valid_ids.empty:
                    return 1
                    
                return int(valid_ids.max()) + 1
            except Exception as e:
                cloud_log(f"Intento {attempt + 1} fallido al obtener ID: {str(e)}", "warning")
                if attempt == self.max_retries - 1:
                    cloud_log("Error crítico al obtener ID de notificación", "error")
                    return None
                time.sleep(1)
        return None

    def add(self, notification_type, message, user_target='all', claim_id=None, action=None):
        """
        Agrega una notificación con estilo CRM y optimización para Render
        """
        if notification_type not in NOTIFICATION_TYPES:
            cloud_log(f"Tipo de notificación no válido: {notification_type}", "error")
            return False

        try:
            # Limitar notificaciones globales a 10
            if user_target == 'all':
                df_notif = safe_get_sheet_data(self.sheet, COLUMNAS_NOTIFICACIONES)
                df_all = df_notif[df_notif['Usuario_Destino'] == 'all']
                
                if len(df_all) >= 10:
                    # Convertir fecha de forma segura
                    df_all = df_all.copy()
                    df_all['Fecha_Hora'] = pd.to_datetime(df_all['Fecha_Hora'], errors='coerce')
                    
                    # Eliminar la más antigua si hay fechas válidas
                    if not df_all['Fecha_Hora'].isna().all():
                        mas_antigua_idx = df_all['Fecha_Hora'].idxmin()
                        self._delete_rows([mas_antigua_idx])

            return self._agregar_notificacion_individual(
                notification_type, message, user_target, claim_id, action
            )

        except Exception as e:
            cloud_log(f"Error al agregar notificación: {str(e)}", "error")
            return False

    def _agregar_notificacion_individual(self, notification_type, message, user_target, claim_id=None, action=None):
        """Agrega una notificación individual con manejo robusto de errores"""
        new_id = self._get_next_id()
        if new_id is None:
            return False

        # Preparar datos de la notificación
        new_notification = [
            new_id,
            notification_type,
            NOTIFICATION_TYPES[notification_type]['priority'],
            message,
            str(user_target),
            str(claim_id) if claim_id else "",
            format_fecha(ahora_argentina()),
            False,  # Leída = False
            action or ""
        ]

        # Intentar agregar la notificación
        for attempt in range(self.max_retries):
            success, error = api_manager.safe_sheet_operation(
                self.sheet.append_row,
                new_notification
            )
            if success:
                cloud_log(f"Notificación {new_id} agregada para {user_target}", "info")
                return True
                
            if IS_RENDER and attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Backoff exponencial en Render
                
        cloud_log(f"Fallo al agregar notificación para {user_target}", "error")
        return False

    def get_for_user(self, username, unread_only=True, limit=MAX_NOTIFICATIONS):
        """Obtiene notificaciones para un usuario con manejo robusto de datos"""
        try:
            df = safe_get_sheet_data(self.sheet, COLUMNAS_NOTIFICACIONES)
            if df.empty:
                return []

            # Limpieza y normalización de datos
            df = df.copy()
            
            # Manejo seguro de fechas
            df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'], errors='coerce')
            
            # Manejo seguro de campo Leída
            df['Leída'] = (
                df['Leída']
                .astype(str)
                .str.strip()
                .str.upper()
                .map({'FALSE': False, 'TRUE': True, 'FALSO': False, 'VERDADERO': True})
                .fillna(False)
            )

            # Filtrar notificaciones para el usuario
            mask = (df['Usuario_Destino'] == username) | (df['Usuario_Destino'] == 'all')
            if unread_only:
                mask &= (~df['Leída'])

            # Ordenar y limitar resultados
            notifications = (
                df[mask]
                .sort_values('Fecha_Hora', ascending=False)
                .head(limit)
                .to_dict('records')
            )

            return notifications

        except Exception as e:
            cloud_log(f"Error al obtener notificaciones para {username}: {str(e)}", "error")
            return []

    def get_unread_count(self, username):
        """Obtiene el conteo de notificaciones no leídas"""
        notifications = self.get_for_user(username, unread_only=True)
        return len(notifications)

    def mark_as_read(self, notification_ids):
        """Marca notificaciones como leídas con manejo robusto"""
        if not notification_ids:
            return False

        try:
            df = safe_get_sheet_data(self.sheet, COLUMNAS_NOTIFICACIONES)
            if df.empty:
                return False

            # Filtrar IDs válidos
            valid_ids = [int(id) for id in notification_ids if str(id).isdigit()]
            if not valid_ids:
                return False

            # Preparar actualizaciones
            updates = []
            for _, row in df[df['ID'].isin(valid_ids)].iterrows():
                updates.append({
                    'range': f"H{row.name + 2}",  # +2 porque Google Sheets empieza en 1 y header en 1
                    'values': [[True]]
                })

            if not updates:
                return False

            # Ejecutar actualización por lotes
            success, error = api_manager.safe_sheet_operation(
                batch_update_sheet,
                self.sheet,
                updates,
                is_batch=True
            )
            
            if success:
                cloud_log(f"Notificaciones {valid_ids} marcadas como leídas", "info")
            else:
                cloud_log(f"Error al marcar notificaciones: {error}", "error")
                
            return success

        except Exception as e:
            cloud_log(f"Error al marcar como leídas: {str(e)}", "error")
            return False

    def clear_old(self, days=30):
        """Limpia notificaciones antiguas de forma segura"""
        try:
            df = safe_get_sheet_data(self.sheet, COLUMNAS_NOTIFICACIONES)
            if df.empty:
                return True

            # Manejo seguro de fechas
            df = df.copy()
            df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'], errors='coerce')
            df = df[df['Fecha_Hora'].notna()]

            # Calcular fecha de corte
            cutoff_date = ahora_argentina() - timedelta(days=days)
            old_ids = df[df['Fecha_Hora'] < cutoff_date]['ID'].tolist()

            if not old_ids:
                return True

            # Eliminar notificaciones antiguas
            success = self._delete_rows(old_ids)
            if success:
                cloud_log(f"Eliminadas {len(old_ids)} notificaciones antiguas", "info")
            return success

        except Exception as e:
            cloud_log(f"Error al limpiar notificaciones antiguas: {str(e)}", "error")
            return False

    def _delete_rows(self, row_ids):
        """Elimina filas de forma segura con manejo de errores"""
        try:
            updates = [{
                'delete_dimension': {
                    'range': {
                        'sheetId': self.sheet.id,
                        'dimension': 'ROWS',
                        'startIndex': int(row_id),
                        'endIndex': int(row_id) + 1
                    }
                }
            } for row_id in row_ids if str(row_id).isdigit()]

            if not updates:
                return False

            success, error = api_manager.safe_sheet_operation(
                self.sheet.batch_update,
                {'requests': updates}
            )
            return success
            
        except Exception as e:
            cloud_log(f"Error al eliminar filas: {str(e)}", "error")
            return False

    def delete_notification_by_id(self, notif_id):
        """Elimina una notificación por ID de forma segura"""
        try:
            df = safe_get_sheet_data(self.sheet, COLUMNAS_NOTIFICACIONES)
            if df.empty:
                return False

            # Buscar la notificación
            fila = df[df['ID'] == notif_id]
            if fila.empty:
                return False

            row_id = int(fila.index[0])
            return self._delete_rows([row_id])
            
        except Exception as e:
            cloud_log(f"Error al eliminar notificación {notif_id}: {str(e)}", "error")
            return False


# ✅ FUNCIÓN DE INICIALIZACIÓN
def init_notification_manager(sheet_notifications):
    """Inicializa el gestor de notificaciones con estilo CRM"""
    if 'notification_manager' not in st.session_state:
        st.session_state.notification_manager = NotificationManager(sheet_notifications)
        cloud_log("Gestor de notificaciones inicializado", "info")

        # Limpieza programada de notificaciones antiguas
        user = st.session_state.get('auth', {}).get('user_info', {}).get('username', '')
        if user and st.session_state.get('clear_notifications_job') is None:
            if st.session_state.notification_manager.clear_old():
                st.session_state.clear_notifications_job = True
                cloud_log("Tarea de limpieza de notificaciones programada", "info")