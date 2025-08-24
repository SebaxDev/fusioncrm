# components/notification_bell.py

import streamlit as st
import uuid
from utils.date_utils import format_fecha
from config.settings import NOTIFICATION_TYPES
from components.notifications import get_cached_notifications
from utils.helpers import cloud_log

def render_notification_bell():
    """Muestra el ícono de notificaciones con estilo CRM profesional"""
    if 'notification_manager' not in st.session_state:
        return
        
    user = st.session_state.auth.get('user_info', {}).get('username')
    if not user:
        return
        
    notifications = get_cached_notifications(user)
    unread_count = len([n for n in notifications if not n.get('Leída', False)])
    
    # Estilos CSS para el componente de notificaciones
    notification_styles = """
    <style>
    .notification-bell {
        position: relative;
        display: inline-flex;
        align-items: center;
        padding: 0.75rem 1rem;
        border-radius: var(--radius-lg);
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 1rem;
        width: 100%;
    }
    
    .notification-bell:hover {
        background: var(--bg-secondary);
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .notification-count {
        position: absolute;
        top: -8px;
        right: -8px;
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--danger-color) 100%);
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        border: 2px solid var(--bg-card);
    }
    
    .notification-item {
        padding: 1rem;
        margin: 0.5rem 0;
        background: var(--bg-surface);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .notification-item:hover {
        background: var(--bg-secondary);
        border-color: var(--primary-color);
    }
    
    .notification-item.unread {
        background: rgba(102, 217, 239, 0.1);
        border-left: 4px solid var(--primary-color);
    }
    
    .notification-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .notification-content {
        flex: 1;
    }
    
    .notification-time {
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }
    
    .notification-actions {
        margin-top: 0.5rem;
        display: flex;
        gap: 0.5rem;
    }
    </style>
    """
    
    st.markdown(notification_styles, unsafe_allow_html=True)
    
    # Ícono en el sidebar con estilo CRM
    with st.sidebar:
        st.markdown("---")
        st.markdown("**📋 Notificaciones**")
        
        # Contenedor principal de la campana
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <div style="font-size: 1.5rem;">🔔</div>
                {f'<div class="notification-count">{unread_count}</div>' if unread_count > 0 else ''}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("Ver notificaciones", 
                        use_container_width=True,
                        help="Mostrar panel de notificaciones",
                        key="notification_toggle_btn"):
                st.session_state.show_notifications = not st.session_state.get('show_notifications', False)
        
        # Panel de notificaciones
        if st.session_state.get('show_notifications'):
            with st.container():
                st.markdown("---")
                
                if not notifications:
                    st.info("🎉 No tienes notificaciones nuevas", icon="ℹ️")
                    return
                
                # Mostrar las 10 notificaciones más recientes
                for idx, notification in enumerate(notifications[:10]):
                    is_unread = not notification.get('Leída', False)
                    icon = NOTIFICATION_TYPES.get(notification.get('Tipo'), {}).get('icon', '📋')
                    
                    # Contenedor de notificación
                    unread_class = "unread" if is_unread else ""
                    st.markdown(f"""
                    <div class="notification-item {unread_class}">
                        <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                            <div class="notification-icon">{icon}</div>
                            <div class="notification-content">
                                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">
                                    {notification.get('Mensaje', '[Sin mensaje]')}
                                </div>
                                <div class="notification-time">
                                    {format_fecha(notification.get('Fecha_Hora'))}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón para marcar como leída (solo para no leídas)
                    if is_unread:
                        notif_id = notification.get("ID", "unknown")
                        unique_suffix = uuid.uuid4().hex[:8]
                        key = f"read_{notif_id}_{idx}_{unique_suffix}"
                        
                        if st.button("✅ Marcar como leída", 
                                   key=key,
                                   use_container_width=True,
                                   type="secondary",
                                   size="small"):
                            if notif_id != "unknown":
                                try:
                                    success = st.session_state.notification_manager.mark_as_read([int(notif_id)])
                                    if success:
                                        cloud_log(f"Notificación {notif_id} marcada como leída por {user}", "info")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al marcar como leída")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                                    cloud_log(f"Error marcando notificación como leída: {str(e)}", "error")
                    
                    if idx < len(notifications[:10]) - 1:
                        st.markdown("---")
                
                # Botón para marcar todas como leídas
                if unread_count > 0:
                    st.markdown("---")
                    if st.button("📭 Marcar todas como leídas", 
                               use_container_width=True,
                               type="primary"):
                        unread_ids = [n['ID'] for n in notifications if not n.get('Leída', False) and n.get('ID') != 'unknown']
                        if unread_ids:
                            success = st.session_state.notification_manager.mark_as_read(unread_ids)
                            if success:
                                cloud_log(f"{len(unread_ids)} notificaciones marcadas como leídas por {user}", "info")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Error al marcar todas como leídas")