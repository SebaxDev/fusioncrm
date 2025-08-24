"""Utilidades de permisos para evitar importación circular - Optimizado para Render"""

def has_permission(permiso):
    """Verifica permisos del usuario con manejo robusto para entornos cloud"""
    import streamlit as st
    
    try:
        # Verificar si la sesión está inicializada
        if 'auth' not in st.session_state:
            return False
            
        user_info = st.session_state.auth.get('user_info', {})
        user_role = user_info.get('rol', '')
        
        # Permisos optimizados para CRM
        permisos = {
            'admin': [
                'inicio', 'reclamos_cargados', 'gestion_clientes', 
                'imprimir_reclamos', 'seguimiento_tecnico', 'cierre_reclamos',
                'dashboard', 'reportes', 'configuracion', 'administracion'
            ],
            'tecnico': [
                'inicio', 'reclamos_cargados', 'seguimiento_tecnico', 
                'cierre_reclamos', 'dashboard'
            ],
            'usuario': [
                'inicio', 'reclamos_cargados', 'imprimir_reclamos', 'dashboard'
            ],
            'supervisor': [
                'inicio', 'reclamos_cargados', 'seguimiento_tecnico', 
                'cierre_reclamos', 'dashboard', 'reportes'
            ]
        }
        
        # Permisos públicos (sin necesidad de login)
        permisos_publicos = ['login', 'logout', 'error']
        
        if permiso in permisos_publicos:
            return True
            
        return permiso in permisos.get(user_role, [])
        
    except Exception as e:
        # Log seguro en entornos cloud
        import os
        if 'RENDER' in os.environ:
            print(f"Error en permisos: {str(e)}")
        return False

# Nueva función para verificación de roles
def get_user_role():
    """Obtiene el rol del usuario de forma segura"""
    import streamlit as st
    
    try:
        if 'auth' not in st.session_state:
            return 'invitado'
        return st.session_state.auth.get('user_info', {}).get('rol', 'invitado')
    except:
        return 'invitado'

# Nueva función para verificación de permisos múltiples
def has_any_permission(permisos):
    """Verifica si el usuario tiene al menos uno de los permisos especificados"""
    return any(has_permission(perm) for perm in permisos)

# Cache de permisos para mejor rendimiento en Render
def init_permissions_cache():
    """Inicializa cache de permisos para mejor rendimiento"""
    import streamlit as st
    if 'permissions_cache' not in st.session_state:
        st.session_state.permissions_cache = {}