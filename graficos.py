import streamlit as st
import pandas as pd
from pathlib import Path
import re

# Ruta del directorio de datos (carpeta dentro del repositorio)
DATA_DIR = Path(__file__).parent / "time-series_data"

def load_data(file_path: Path) -> pd.DataFrame:
    """
    Carga un CSV usando pandas y devuelve un DataFrame.
    Lanza FileNotFoundError si no existe el archivo.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    # Intentamos detectar la codificación por defecto (utf-8) y caemos a latin-1 si falla
    try:
        df = pd.read_csv(file_path)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="latin-1")
    return df

def show_chart(df: pd.DataFrame, primary_loss=True, secondary_loss=True, start_year=1985, end_year=2024):
    """
    Construye y muestra el gráfico a partir de un DataFrame.
    Se asume que:
    - la primera columna es el año
    - la segunda columna corresponde a pérdida primaria
    - la tercera columna corresponde a pérdida secundaria
    """
    if df is None or df.shape[0] == 0:
        st.warning("No hay datos para graficar.")
        return

    # Nombres de columnas según el CSV (por posición)
    year_col = df.columns[0]
    primary_col = df.columns[1] if df.shape[1] > 1 else None
    secondary_col = df.columns[2] if df.shape[1] > 2 else None

    # Normalizar año a entero y filtrar por rango
    df = df.copy()
    df[year_col] = df[year_col].astype(int)
    mask = (df[year_col] >= int(start_year)) & (df[year_col] <= int(end_year))
    df = df.loc[mask]

    # Preparar series (si no existen columnas, usamos ceros)
    if primary_loss and primary_col is not None:
        primary_series = pd.to_numeric(df[primary_col], errors="coerce").fillna(0)
    else:
        primary_series = pd.Series([0] * len(df), index=df.index)

    if secondary_loss and secondary_col is not None:
        secondary_series = pd.to_numeric(df[secondary_col], errors="coerce").fillna(0)
    else:
        secondary_series = pd.Series([0] * len(df), index=df.index)

    plot_df = pd.DataFrame({
        "Año": df[year_col].values,
        "Pérdida de Vegetación Primaria": primary_series.values,
        "Pérdida de Vegetación Secundaria": secondary_series.values
    }).set_index("Año")

    st.line_chart(plot_df, use_container_width=True)

# --- Interfaz de Streamlit ---
st.title("Gráficos")

# Detectar zonas disponibles leyendo los nombres de archivos en la carpeta
available_zones = {"Argentina"}
if DATA_DIR.exists() and DATA_DIR.is_dir():
    for f in sorted(DATA_DIR.glob("*.csv")):
        # Buscamos el texto entre paréntesis al final del nombre de archivo
        m = re.search(r"\((.*?)\)\.csv$", f.name)
        if m:
            available_zones.add(m.group(1))
else:
    st.error(f"No se encontró el directorio de datos: {DATA_DIR}")

zones = sorted(list(available_zones))
default_idx = zones.index("Argentina") if "Argentina" in zones else 0
zone = st.selectbox("Selecciona una provincia", zones, index=default_idx)

st.write("Selecciona las series que deseas visualizar:")
veg_primary = st.checkbox("Pérdida de vegetación primaria", value=True, key="veg_loss_primary")
veg_secondary = st.checkbox("Pérdida de vegetación secundaria", value=True, key="veg_loss_secondary")

year_range = st.slider("Selecciona el rango de años", 1985, 2024, (2000, 2024), step=1)

# Construir el nombre de archivo esperado
filename = f"Time series of Vegetation loss • Annual by class • 1985 - 2024 ({zone}).csv"
file_path = DATA_DIR / filename

# Si el archivo no existe, mostramos lista de archivos disponibles y un error claro
if not file_path.exists():
    st.error(f"No se encontró el archivo de datos esperado: {file_path.name}")
    if DATA_DIR.exists():
        st.write("Archivos disponibles en time-series_data:")
        for f in sorted(DATA_DIR.glob("*.csv")):
            st.write(f"- {f.name}")
else:
    try:
        df = load_data(file_path)
        st.header(f"Pérdida de Vegetación en {zone}")
        show_chart(df, primary_loss=veg_primary, secondary_loss=veg_secondary,
                   start_year=year_range[0], end_year=year_range[1])
    except Exception as e:
        st.exception(e)



