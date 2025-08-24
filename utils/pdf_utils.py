# utils/pdf_utils.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def agregar_pie_pdf(c, width, height):
    """Agrega marca de agua/pie institucional al PDF optimizado para Render"""
    try:
        # Intentar cargar fuente mejorada si está disponible
        try:
            # Para Render: usar fuentes del sistema o incluidas
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                'utils/fonts/DejaVuSans-Bold.ttf'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVuBold', font_path))
                    c.setFont("DejaVuBold", 9)
                    break
            else:
                # Fallback a fuente estándar
                c.setFont("Helvetica-Bold", 9)
        except:
            c.setFont("Helvetica-Bold", 9)
        
        texto = "Fusion Cable - Chile 450 | Tel: 3725-468892"
        text_width = c.stringWidth(texto, c._fontname, c._fontsize)
        
        # Posicionamiento responsive
        x_position = width - text_width - 40
        if x_position < 20:  # Asegurar que no se salga de la página
            x_position = 20
        
        # Color profesional (gris oscuro)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(x_position, 20, texto)
        
        # Línea decorativa
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(x_position - 10, 25, width - 30, 25)
        
    except Exception as e:
        # Fallback seguro si hay error
        c.setFont("Helvetica-Bold", 9)
        texto = "Fusion Cable - Chile 450 | Tel: 3725-468892"
        c.drawString(50, 20, texto)

# Nueva función para manejo de PDFs en cloud
def setup_pdf_for_cloud():
    """Configuración optimizada de PDF para entornos cloud"""
    try:
        # Pre-registrar fuentes comunes para Render
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('CloudSans', font_path))
                return True
    except:
        pass
    return False