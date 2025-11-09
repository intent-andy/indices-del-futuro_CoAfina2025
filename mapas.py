import streamlit as st
import ee
import folium
import geemap.foliumap as geemap_folium
from streamlit_folium import st_folium
from google.oauth2 import service_account

# --- 0. Configuración de la Página ---
st.set_page_config(page_title="Índice IET en GEE", layout="wide")
st.title("Visualizador de Google Earth Engine en Streamlit")
st.markdown("Mostrando el índice IET para Córdoba (2023) calculado en GEE.")

# --- 1. Inicialización de Earth Engine ---
# Intentamos inicializar. Si falla, es probable que no esté autenticado.
try:
    # Obtener las credenciales desde los Secrets de Streamlit
    # st.secrets["google_credentials"] hace referencia a la sección [google_credentials] en tu TOML
    creds_dict = st.secrets["google_credentials"]
    
    # Crear un objeto de credenciales de Google
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    
    # Inicializar Earth Engine con esas credenciales
    ee.Initialize(credentials=credentials)
    
    st.success("¡Autenticación con Google Earth Engine exitosa!")

except Exception as e:
    st.error(f"Error al autenticar o inicializar GEE: {e}")
    st.error("Asegúrate de que: \n"
             "1. El 'Secret' esté configurado correctamente en Streamlit Cloud. \n"
             "2. La cuenta de servicio esté registrada en GEE (earthengine.google.com/signup).")
    st.stop()


# --- 2. Tu Código GEE (Traducido a la API de Python) ---
# La sintaxis de JS y Python es casi idéntica.
cordoba = ee.FeatureCollection("FAO/GAUL/2015/level2") \
    .filter(ee.Filter.eq('ADM2_NAME', 'Córdoba'))

s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
    .filterBounds(cordoba) \
    .filterDate('2023-01-01', '2023-12-31') \
    .select(['B4', 'B8', 'B11']) \
    .median() # Usamos median() para tener una sola imagen sin nubes

ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
ndmi = s2.normalizedDifference(['B8', 'B11']).rename('NDMI')

chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
    .filterBounds(cordoba) \
    .filterDate('2023-01-01', '2023-12-31') \
    .sum() \
    .rename('Precipitation')

urban = ee.Image("ESA/WorldCover/v100/2020") \
    .select('Map') \
    .eq(50) \
    .rename('Urban')

iet = ndvi \
    .multiply(ndmi) \
    .multiply(chirps) \
    .divide(urban.add(1)) \
    .rename('IET')

# Recortamos la imagen final a la geometría de Córdoba
iet_clipped = iet.clip(cordoba)

# --- 3. Parámetros de Visualización ---
# Los mismos que usaste en tu código JS
vis_params = {
    'min': 0,
    'max': 1,
    'palette': ['red', 'yellow', 'green']
}

# --- 4. Centrado del Mapa ---
# En lugar de Map.centerObject (que es del Code Editor),
# obtenemos las coordenadas del centro para Folium.
# Usamos .getInfo() para traer la información del servidor GEE a Python.
try:
    region_info = cordoba.geometry().bounds().getInfo()
    # Calcular el centroide de la caja delimitadora (bounds)
    coords = region_info['coordinates'][0]
    center_lon = (coords[0][0] + coords[2][0]) / 2
    center_lat = (coords[0][1] + coords[1][1]) / 2
    map_center = [center_lat, center_lon]
    zoom_start = 7
except Exception as e:
    st.warning(f"No se pudo centrar el mapa en Córdoba: {e}. Usando centro por defecto.")
    map_center = [0, 0] # Un valor por defecto si falla
    zoom_start = 2


# --- 5. Creación y Visualización del Mapa ---

# Crear un mapa base de Folium
m = folium.Map(location=map_center, zoom_start=zoom_start)

# Añadir tu capa GEE al mapa Folium usando geemap
# geemap se encarga de obtener el Tile URL de GEE y añadirlo
geemap_folium.add_ee_layer(
    m,                # El mapa folium
    iet_clipped,      # Tu imagen de GEE
    vis_params,       # Parámetros de visualización
    'Índice IET'      # Nombre de la capa
)

# También añadimos el contorno de Córdoba para contexto
m.add_child(folium.GeoJson(
    data=cordoba.geometry().getInfo(),
    style_function=lambda x: {'fillColor': 'none', 'color': 'blue', 'weight': 2},
    name="Límite Córdoba"
))

# Añadir un control de capas al mapa
folium.LayerControl().add_to(m)

# Mostrar el mapa en Streamlit usando st_folium
st_folium(m, width=1000, height=600, returned_objects=[])