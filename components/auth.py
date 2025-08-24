"""
Componente de autenticación profesional estilo CRM
Versión 3.0 - Optimizado para Render con mejoras de seguridad
"""
import streamlit as st
from utils.data_manager import safe_get_sheet_data
from config.settings import (
    WORKSHEET_USUARIOS,
    COLUMNAS_USUARIOS,
    PERMISOS_POR_ROL,
    IS_RENDER,
    DEFAULT_VALUES
)
import time
from utils.styles import get_loading_spinner
from utils.helpers import cloud_log, is_cloud_environment

def init_auth_session():
    """Inicializa las variables de sesión de forma segura"""
    if 'auth' not in st.session_state:
        st.session_state.auth = {
            'logged_in': False,
            'user_info': None,
            'login_attempts': 0,
            'last_login_attempt': 0
        }

def logout():
    """Cierra la sesión del usuario de forma segura"""
    user_info = st.session_state.auth.get('user_info', {})
    cloud_log(f"Usuario {user_info.get('username', 'unknown')} cerró sesión", "info")
    
    st.session_state.auth = {
        'logged_in': False, 
        'user_info': None,
        'login_attempts': 0,
        'last_login_attempt': 0
    }
    st.cache_data.clear()

def verify_credentials(username, password, sheet_usuarios):
    """Verifica credenciales con seguridad mejorada para Render"""
    try:
        # Protección contra fuerza bruta en Render
        if IS_RENDER and st.session_state.auth.get('login_attempts', 0) >= 3:
            current_time = time.time()
            last_attempt = st.session_state.auth.get('last_login_attempt', 0)
            if current_time - last_attempt < 300:  # 5 minutos de bloqueo
                cloud_log(f"Intento de login bloqueado para {username} - Demasiados intentos", "warning")
                return None
        
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
        
        if df_usuarios.empty:
            cloud_log("No se encontraron usuarios en la base de datos", "error")
            return None
        
        # Normalización robusta de datos
        df_usuarios["username"] = df_usuarios["username"].astype(str).str.strip().str.lower()
        df_usuarios["password"] = df_usuarios["password"].astype(str).str.strip()
        
        # Manejo flexible de campo 'activo'
        df_usuarios["activo"] = df_usuarios["activo"].astype(str).str.upper().isin([
            "SI", "TRUE", "1", "SÍ", "VERDADERO", "YES", "Y", "ACTIVO"
        ])
        
        usuario = df_usuarios[
            (df_usuarios["username"] == username.strip().lower()) & 
            (df_usuarios["password"] == password.strip()) &
            (df_usuarios["activo"])
        ]
        
        if not usuario.empty:
            user_data = usuario.iloc[0]
            cloud_log(f"Login exitoso para {username}", "info")
            
            # Reiniciar contador de intentos
            st.session_state.auth['login_attempts'] = 0
            
            return {
                "username": user_data["username"],
                "nombre": user_data.get("nombre", user_data["username"]),
                "rol": user_data.get("rol", DEFAULT_VALUES['rol_usuario']).lower(),
                "email": user_data.get("email", ""),
                "telefono": user_data.get("telefono", ""),
                "permisos": PERMISOS_POR_ROL.get(
                    user_data.get("rol", "").lower(), 
                    PERMISOS_POR_ROL.get(DEFAULT_VALUES['rol_usuario'], {})
                ).get('permisos', [])
            }
        else:
            # Incrementar contador de intentos fallidos
            st.session_state.auth['login_attempts'] = st.session_state.auth.get('login_attempts', 0) + 1
            st.session_state.auth['last_login_attempt'] = time.time()
            cloud_log(f"Intento de login fallido para {username}", "warning")
            
    except Exception as e:
        cloud_log(f"Error en autenticación: {str(e)}", "error")
        if not IS_RENDER:  # Mostrar error detallado solo en desarrollo
            st.error(f"Error en autenticación: {str(e)}")
    return None

def render_login(sheet_usuarios):
    """Formulario de login con diseño profesional CRM optimizado para Render"""
    
    login_styles = """
    <style>
    .login-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 2.5rem;
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        text-align: center;
    }
    
    .login-header {
        margin-bottom: 2rem;
    }
    
    .login-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .login-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: var(--text-primary);
    }
    
    .login-subtitle {
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .login-form {
        text-align: left;
    }
    
    .login-input {
        margin-bottom: 1.5rem;
    }
    
    .login-button {
        width: 100%;
        margin-top: 1rem;
        padding: 0.875rem;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .login-footer {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border-light);
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    .login-error {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: var(--error-color);
        padding: 1rem;
        border-radius: var(--radius-md);
        margin: 1rem 0;
        text-align: center;
    }
    
    .login-warning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: var(--warning-color);
        padding: 1rem;
        border-radius: var(--radius-md);
        margin: 1rem 0;
        text-align: center;
    }
    
    @media (max-width: 480px) {
        .login-container {
            margin: 1rem;
            padding: 2rem 1.5rem;
        }
    }
    </style>
    """
    
    st.markdown(login_styles, unsafe_allow_html=True)
    
    # Inicializar estado de autenticación
    init_auth_session()
    
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <div class="login-logo">📋</div>
            <h1 class="login-title">Fusion CRM</h1>
            <p class="login-subtitle">Sistema profesional de gestión de reclamos</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Mostrar advertencia de múltiples intentos
    login_attempts = st.session_state.auth.get('login_attempts', 0)
    if login_attempts >= 2:
        st.markdown(f"""
        <div class="login-warning">
            ⚠️ {login_attempts} intentos fallidos. Después de 3 intentos, el acceso se bloqueará temporalmente.
        </div>
        """, unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input(
            "👤 Usuario",
            placeholder="Ingresa tu nombre de usuario",
            help="Tu nombre de usuario del sistema"
        ).strip()
        
        password = st.text_input(
            "🔒 Contraseña", 
            type="password",
            placeholder="Ingresa tu contraseña",
            help="Tu contraseña de acceso"
        )
        
        submitted = st.form_submit_button(
            "🚀 Iniciar Sesión", 
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not username or not password:
                st.error("❌ Usuario y contraseña son requeridos")
            else:
                with st.spinner("🔐 Verificando credenciales..."):
                    user_info = verify_credentials(username, password, sheet_usuarios)
                    
                    if user_info:
                        st.session_state.auth.update({
                            'logged_in': True,
                            'user_info': user_info,
                            'login_attempts': 0
                        })
                        st.success(f"✅ Bienvenido, {user_info['nombre']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas o usuario inactivo")
    
    st.markdown("""
        <div class="login-footer">
            <p>© 2025 Fusion CRM • v3.0</p>
            <p style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.7;">
                Optimizado para Render • Sistema seguro
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def check_authentication():
    """Verifica si el usuario está autenticado de forma segura"""
    init_auth_session()
    return st.session_state.auth['logged_in']

def has_permission(required_permission):
    """Verifica permisos del usuario con seguridad mejorada"""
    if not check_authentication():
        return False
        
    user_info = st.session_state.auth.get('user_info')
    if not user_info:
        return False
        
    # Admin tiene acceso completo
    if user_info.get('rol') == 'admin':
        return True
        
    return required_permission in user_info.get('permisos', [])

def render_user_info():
    """Renderiza información del usuario con diseño CRM profesional"""
    if not check_authentication():
        return
        
    user_info = st.session_state.auth['user_info']
    role_config = PERMISOS_POR_ROL.get(user_info.get('rol', '').lower(), {})
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 1.5rem 1rem; margin-bottom: 1rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, {role_config.get('color', '#2563EB')}, #66D9EF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {role_config.get('icon', '👤')}
        </div>
        <h3 style="margin: 0; color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
            {user_info.get('nombre', 'Usuario')}
        </h3>
        <div style="background: {role_config.get('color', '#2563EB')}20; 
                  color: {role_config.get('color', '#2563EB')}; 
                  padding: 0.4rem 1rem; 
                  border-radius: 20px; 
                  font-size: 0.8rem; 
                  font-weight: 600;
                  margin: 0.75rem 0;
                  display: inline-block;
                  border: 1px solid {role_config.get('color', '#2563EB')}40;">
            {role_config.get('descripcion', 'Usuario').split(' - ')[0]}
        </div>
        <p style="color: var(--text-secondary); margin: 0.5rem 0; font-size: 0.85rem;">
            @{user_info.get('username', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button(
        "🚪 Cerrar Sesión", 
        use_container_width=True, 
        key="logout_btn_sidebar"
    ):
        logout()
        st.rerun()