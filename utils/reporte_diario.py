# utils/reporte_diario.py
"""
Archivo seguro para generar Reporte Diario en PNG y debug de fechas.
Optimizado para Render con manejo robusto de fuentes y recursos.
"""

import io
from datetime import datetime
from typing import Tuple
import os

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

from utils.date_utils import ahora_argentina, format_fecha
from utils.helpers import cloud_log

def _to_datetime_clean(series: pd.Series) -> pd.Series:
    """Limpieza robusta de fechas para entornos cloud"""
    try:
        s = series.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
        s = s.replace({"": None, "nan": None, "NaN": None, "NONE": None, "None": None})
        out = pd.to_datetime(s, errors="coerce", dayfirst=True, infer_datetime_format=True)
        if pd.api.types.is_datetime64tz_dtype(out):
            out = out.dt.tz_convert(None).dt.tz_localize(None)
        return out
    except Exception as e:
        cloud_log(f"Error en limpieza de fechas: {str(e)}", "error")
        return pd.Series([pd.NaT] * len(series))

def _prep_df(df_reclamos: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Timestamp, pd.Timestamp]:
    """Preparación robusta del DataFrame para reportes"""
    try:
        df = df_reclamos.copy()
        df.columns = [str(c).strip() for c in df.columns]
        
        # Columnas requeridas con valores por defecto
        required_columns = {
            "Fecha y hora": pd.NaT,
            "Fecha_formateada": pd.NaT,
            "Estado": "desconocido",
            "Técnico": "Sin técnico",
            "Tipo de reclamo": "Sin tipo"
        }
        
        for col, default_val in required_columns.items():
            if col not in df.columns:
                df[col] = default_val
            else:
                # Limpieza de datos
                df[col] = df[col].fillna(default_val)
                if col in ["Estado", "Técnico", "Tipo de reclamo"]:
                    df[col] = df[col].astype(str).str.strip()
        
        # Conversión de fechas
        df["Fecha y hora"] = _to_datetime_clean(df["Fecha y hora"])
        df["Fecha_formateada"] = _to_datetime_clean(df["Fecha_formateada"])
        
        # Normalización de estados
        df["Estado"] = df["Estado"].str.lower().str.strip()
        
        ahora_ts = pd.Timestamp(ahora_argentina()).tz_localize(None)
        hace_24h = ahora_ts - pd.Timedelta(hours=24)
        
        return df, ahora_ts, hace_24h
        
    except Exception as e:
        cloud_log(f"Error en preparación de DataFrame: {str(e)}", "error")
        # Devolver DataFrame vacío pero estructurado
        empty_df = pd.DataFrame(columns=["Fecha y hora", "Fecha_formateada", "Estado", "Técnico", "Tipo de reclamo"])
        ahora_ts = pd.Timestamp.now()
        return empty_df, ahora_ts, ahora_ts - pd.Timedelta(hours=24)

def _get_fonts_for_cloud():
    """Obtiene fuentes disponibles optimizadas para Render"""
    try:
        # Rutas de fuentes comunes en Render y otros cloud
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
        ]
        
        fonts = {}
        for path in font_paths:
            if os.path.exists(path):
                try:
                    fonts['bold'] = ImageFont.truetype(path, 36)
                    fonts['sub'] = ImageFont.truetype(path, 28)
                    fonts['text'] = ImageFont.truetype(path, 24)
                    return fonts
                except:
                    continue
        
        # Fallback a fuentes por defecto
        fonts['bold'] = ImageFont.load_default()
        fonts['sub'] = ImageFont.load_default()
        fonts['text'] = ImageFont.load_default()
        return fonts
        
    except Exception as e:
        cloud_log(f"Error cargando fuentes: {str(e)}", "warning")
        fonts = {
            'bold': ImageFont.load_default(),
            'sub': ImageFont.load_default(),
            'text': ImageFont.load_default()
        }
        return fonts

def generar_reporte_diario_imagen(df_reclamos: pd.DataFrame) -> io.BytesIO:
    """Genera reporte diario como imagen PNG optimizado para Render"""
    try:
        df, ahora_ts, hace_24h = _prep_df(df_reclamos)
        
        # Cálculos de métricas
        mask_ing_24h = df["Fecha y hora"].notna() & (df["Fecha y hora"] >= hace_24h)
        total_ingresados_24h = int(mask_ing_24h.sum())
        
        mask_res_24h = (
            (df["Estado"].str.lower() == "resuelto") &
            df["Fecha_formateada"].notna() &
            (df["Fecha_formateada"] >= hace_24h)
        )
        resueltos_24h = df.loc[mask_res_24h, ["Técnico", "Estado", "Fecha_formateada"]]
        
        tecnicos_resueltos = (
            resueltos_24h.groupby("Técnico")["Estado"]
            .count()
            .reset_index()
            .rename(columns={"Estado": "Cantidad"})
            .sort_values("Cantidad", ascending=False)
        )
        
        pendientes = df[df["Estado"].str.lower() == "pendiente"]
        total_pendientes = int(len(pendientes))
        
        pendientes_tipo = (
            pendientes.groupby("Tipo de reclamo")["Estado"]
            .count()
            .reset_index()
            .rename(columns={"Estado": "Cantidad", "Tipo de reclamo": "Tipo"})
            .sort_values("Cantidad", ascending=False)
        )

        # Configuración de imagen
        WIDTH, HEIGHT = 1200, 1800  # Mayor altura para más contenido
        BG_COLOR = (39, 40, 34)  # Fondo Monokai
        TEXT_COLOR = (248, 248, 242)  # Texto claro
        HIGHLIGHT_COLOR = (249, 38, 114)  # Magenta Monokai
        ACCENT_COLOR = (102, 217, 239)  # Azul Monokai
        
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Cargar fuentes optimizadas para cloud
        fonts = _get_fonts_for_cloud()
        font_title = fonts.get('bold', ImageFont.load_default())
        font_sub = fonts.get('sub', ImageFont.load_default())
        font_txt = fonts.get('text', ImageFont.load_default())

        y = 50
        line_h = 40

        def _line(text, font, color, dy, x=50):
            nonlocal y
            draw.text((x, y), str(text), font=font, fill=color)
            y += dy

        fecha_str = ahora_ts.strftime("%d/%m/%Y")
        hora_str = ahora_ts.strftime("%H:%M")

        # Header del reporte
        _line(f"■ Reporte Diario - {fecha_str}", font_title, HIGHLIGHT_COLOR, line_h)
        _line(f"Generado a las {hora_str}", font_sub, ACCENT_COLOR, line_h)
        _line("_" * 50, font_txt, TEXT_COLOR, line_h // 2)

        # Métricas principales
        _line(f"■ Reclamos ingresados (24h): {total_ingresados_24h}", font_sub, HIGHLIGHT_COLOR, line_h)
        _line("", font_txt, TEXT_COLOR, line_h // 2)

        # Reporte técnico
        _line("■ Eficiencia técnica (24h):", font_sub, HIGHLIGHT_COLOR, line_h)
        if tecnicos_resueltos.empty:
            _line("No hay reclamos resueltos en las últimas 24h", font_txt, TEXT_COLOR, line_h)
        else:
            for _, r in tecnicos_resueltos.iterrows():
                _line(f"• {r['Técnico']}: {int(r['Cantidad'])} resueltos", font_txt, TEXT_COLOR, line_h)

        _line("", font_txt, TEXT_COLOR, line_h // 2)
        
        # Pendientes
        _line(f"■ Pendientes totales: {total_pendientes}", font_sub, HIGHLIGHT_COLOR, line_h)
        if pendientes_tipo.empty:
            _line("Sin pendientes registrados", font_txt, TEXT_COLOR, line_h)
        else:
            for _, r in pendientes_tipo.iterrows():
                _line(f"• {r['Tipo']}: {int(r['Cantidad'])}", font_txt, TEXT_COLOR, line_h)

        # Footer
        y = HEIGHT - 60
        _line("Fusion CRM - Sistema de Gestión de Reclamos", font_txt, TEXT_COLOR, line_h, x=WIDTH//2 - 200)
        _line(f"Generado automáticamente - {fecha_str}", font_txt, ACCENT_COLOR, line_h, x=WIDTH//2 - 150)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        cloud_log(f"Error generando reporte: {str(e)}", "error")
        # Devolver imagen de error
        img = Image.new("RGB", (800, 200), (255, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "Error generando reporte", fill=(255, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer