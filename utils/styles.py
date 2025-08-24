# styles.py - Versión con modo oscuro Monokai y ancho expandido
"""Estilos CSS profesionales tipo CRM con diseño expandido"""

def get_main_styles_v2(dark_mode=True):
    """Devuelve estilos CSS profesionales para modo claro/oscuro con ancho expandido"""
    
    if dark_mode:
        # PALETA MONOKAI (modo oscuro gris)
        theme_vars = """
            --primary-color: #66D9EF;     /* Azul verdoso Monokai */
            --primary-light: #78C6E9;     /* Azul más claro */
            --secondary-color: #F92672;   /* Magenta Monokai */
            --success-color: #A6E22E;     /* Verde Monokai */
            --warning-color: #FD971F;     /* Naranja Monokai */
            --danger-color: #FF6188;      /* Rosa-rojo Monokai */
            --info-color: #AE81FF;        /* Púrpura Monokai */
            
            --bg-primary: #272822;        /* Fondo principal Monokai */
            --bg-secondary: #2D2E27;      /* Fondo secundario */
            --bg-surface: #3E3D32;        /* Superficie de elementos */
            --bg-card: #383830;           /* Tarjetas */
            
            --text-primary: #F8F8F2;      /* Texto principal */
            --text-secondary: #CFCFC2;    /* Texto secundario */
            --text-muted: #75715E;        /* Texto atenuado */
            
            --border-color: #49483E;      /* Color de bordes */
            --border-light: #5E5D56;      /* Bordes claros */
            
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -1px rgba(0,0,0,0.2);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.4), 0 4px 6px -2px rgba(0,0,0,0.25);
            
            --radius-sm: 0.25rem;
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
            --radius-xl: 0.75rem;
        """
    else:
        # PALETA CRM PROFESIONAL (modo claro)
        theme_vars = """
            --primary-color: #2563EB;     /* Azul profesional */
            --primary-light: #3B82F6;     /* Azul más claro */
            --secondary-color: #8B5CF6;   /* Púrpura */
            --success-color: #059669;     /* Verde profesional */
            --warning-color: #D97706;     /* Ámbar */
            --danger-color: #DC2626;      /* Rojo */
            --info-color: #0891B2;        /* Cian */
            
            --bg-primary: #F8FAFC;        /* Fondo principal claro */
            --bg-secondary: #FFFFFF;      /* Fondo secundario */
            --bg-surface: #F1F5F9;        /* Superficie de elementos */
            --bg-card: #FFFFFF;           /* Tarjetas */
            
            --text-primary: #1E293B;      /* Texto principal oscuro */
            --text-secondary: #475569;    /* Texto secundario */
            --text-muted: #64748B;        /* Texto atenuado */
            
            --border-color: #E2E8F0;      /* Color de bordes */
            --border-light: #F1F5F9;      /* Bordes claros */
            
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            
            --radius-sm: 0.25rem;
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
            --radius-xl: 0.75rem;
        """
    
    return f"""
    <style>
    :root {{
        {theme_vars}
    }}
    
    /* Fuentes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body, .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: var(--bg-primary);
        color: var(--text-primary);
        line-height: 1.6;
    }}
    
    /* MEJORAS PARA CONTENEDORES PRINCIPALES - ANCHO EXPANDIDO */
    .main .block-container {{
        max-width: 1800px !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }}
    
    /* Cuando el sidebar está colapsado, expandimos el ancho */
    [data-testid="stSidebarCollapsed"] ~ .main .block-container {{
        max-width: 95% !important;
        padding-left: 4%;
        padding-right: 4%;
    }}
    
    /* HEADER ESTILO CRM */
    .crm-header {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        padding: 2rem;
        border-radius: var(--radius-xl);
        margin-bottom: 2rem;
        color: white;
        box-shadow: var(--shadow-lg);
        text-align: center;
    }}
    
    .crm-header h1 {{
        color: white !important;
        -webkit-text-fill-color: white !important;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
    }}
    
    .crm-header p {{
        opacity: 0.9;
        margin: 0;
        font-size: 1.1rem;
    }}
    
    /* TARJETAS ESTILO CRM */
    .crm-card {{
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .crm-card:hover {{
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }}
    
    .crm-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-light);
    }}
    
    .crm-card-title {{
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    
    /* ESTADÍSTICAS CRM */
    .crm-stat {{
        display: flex;
        flex-direction: column;
        background: var(--bg-surface);
        padding: 1.25rem;
        border-radius: var(--radius-lg);
        border-left: 4px solid var(--primary-color);
        height: 100%;
    }}
    
    .crm-stat-value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }}
    
    .crm-stat-label {{
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 500;
    }}
    
    /* BOTONES CRM */
    .crm-btn {{
        border: none;
        border-radius: var(--radius-lg);
        padding: 0.875rem 1.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: var(--shadow-md);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        text-decoration: none;
    }}
    
    .crm-btn-primary {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
    }}
    
    .crm-btn-primary:hover {{
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        color: white;
    }}
    
    /* NAVEGACIÓN SIDEBAR CRM */
    .crm-nav-item {{
        padding: 0.875rem 1.25rem;
        border-radius: var(--radius-lg);
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }}
    
    .crm-nav-item:hover {{
        background: var(--bg-surface);
        color: var(--primary-color);
    }}
    
    .crm-nav-item.active {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
    }}
    
    /* BADGES CRM */
    .crm-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: var(--radius-xl);
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid transparent;
    }}
    
    .crm-badge-primary {{
        background-color: rgba(37, 99, 235, 0.1);
        color: var(--primary-color);
        border-color: rgba(37, 99, 235, 0.2);
    }}
    
    .crm-badge-success {{
        background-color: rgba(5, 150, 105, 0.1);
        color: var(--success-color);
        border-color: rgba(5, 150, 105, 0.2);
    }}
    
    .crm-badge-warning {{
        background-color: rgba(217, 119, 6, 0.1);
        color: var(--warning-color);
        border-color: rgba(217, 119, 6, 0.2);
    }}
    
    .crm-badge-danger {{
        background-color: rgba(220, 38, 38, 0.1);
        color: var(--danger-color);
        border-color: rgba(220, 38, 38, 0.2);
    }}
    
    /* FORMULARIOS CRM */
    .crm-form-group {{
        margin-bottom: 1.5rem;
    }}
    
    .crm-form-label {{
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.95rem;
    }}
    
    .crm-form-input {{
        width: 100%;
        padding: 0.875rem;
        border: 2px solid var(--border-color);
        border-radius: var(--radius-md);
        background: var(--bg-surface);
        color: var(--text-primary);
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }}
    
    .crm-form-input:focus {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }}
    
    /* TABLAS CRM */
    .crm-table {{
        width: 100%;
        border-collapse: collapse;
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        margin: 1rem 0;
    }}
    
    .crm-table th {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.9rem;
    }}
    
    .crm-table td {{
        padding: 0.875rem 1rem;
        border-bottom: 1px solid var(--border-color);
        background: var(--bg-surface);
        color: var(--text-primary);
        font-size: 0.9rem;
    }}
    
    .crm-table tr:hover td {{
        background: var(--bg-secondary);
    }}
    
    /* BOTONES ORIGINALES (mantener compatibilidad) */
    .stButton > button {{
        border: none;
        border-radius: var(--radius-lg);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: var(--shadow-md);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }}
    
    .stButton > button:first-child {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
        font-weight: 600;
        border: none;
    }}
    
    .stButton > button:first-child:hover {{
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }}
    
    /* RESPONSIVE DESIGN MEJORADO */
    @media (max-width: 1200px) {{
        .main .block-container {{
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100% !important;
        }}
    }}
    
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 1.5rem;
        }}
        
        .crm-header {{
            padding: 1.5rem;
        }}
        
        .crm-header h1 {{
            font-size: 2rem;
        }}
        
        .crm-card {{
            padding: 1.25rem;
        }}
        
        .crm-stat {{
            padding: 1rem;
        }}
        
        .crm-stat-value {{
            font-size: 1.75rem;
        }}
    }}
    
    /* Utilidades de espaciado CRM */
    .crm-mt-1 {{ margin-top: 0.5rem; }}
    .crm-mt-2 {{ margin-top: 1rem; }}
    .crm-mt-3 {{ margin-top: 1.5rem; }}
    .crm-mt-4 {{ margin-top: 2rem; }}
    
    .crm-mb-1 {{ margin-bottom: 0.5rem; }}
    .crm-mb-2 {{ margin-bottom: 1rem; }}
    .crm-mb-3 {{ margin-bottom: 1.5rem; }}
    .crm-mb-4 {{ margin-bottom: 2rem; }}
    
    .crm-p-1 {{ padding: 0.5rem; }}
    .crm-p-2 {{ padding: 1rem; }}
    .crm-p-3 {{ padding: 1.5rem; }}
    .crm-p-4 {{ padding: 2rem; }}
    </style>
    """

def get_loading_spinner():
    """Spinner de carga moderno con estilo Monokai mejorado"""
    return """
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: rgba(39, 40, 34, 0.95);
        z-index: 9999;
        backdrop-filter: blur(8px);
    ">
        <div style="text-align: center;">
            <div style="
                width: 80px;
                height: 80px;
                border: 4px solid rgba(73, 72, 62, 0.3);
                border-radius: 50%;
                border-top-color: #66D9EF;
                border-right-color: #F92672;
                border-bottom-color: #A6E22E;
                animation: spin 1.5s ease-in-out infinite;
                margin-bottom: 1rem;
            "></div>
            <p style="color: #F8F8F2; font-size: 1.1rem; font-weight: 500; margin: 0;">
                Cargando Fusion CRM...
            </p>
            <p style="color: #75715E; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                ⚡ Optimizado para Render
            </p>
        </div>
        <style>
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
    </div>
    """

def loading_indicator(message="Cargando datos..."):
    """Indicador de carga elegante"""
    return f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="
            width: 50px;
            height: 50px;
            border: 3px solid rgba(102, 217, 239, 0.3);
            border-top: 3px solid #66D9EF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        "></div>
        <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">{message}</p>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """