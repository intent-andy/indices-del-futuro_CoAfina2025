import streamlit as st
import ee
import geemap.foliumap as geemap
import json

# Configuración de la página
st.set_page_config(
    page_title="Mapa IET Córdoba",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título de la aplicación
st.title("🌍 Visualización de Índice IET - Córdoba 2023")

# Inicializar Earth Engine para Streamlit Cloud
def initialize_ee():
    try:
        # Para Streamlit Cloud, necesitamos autenticar con service account
        service_account = st.secrets["EE_SERVICE_ACCOUNT"]
        credentials = ee.ServiceAccountCredentials(
            service_account, 
            st.secrets["EE_PRIVATE_KEY"]
        )
        ee.Initialize(credentials)
        return True
    except Exception as e:
        st.error(f"Error inicializando Earth Engine: {e}")
        return False

# Función alternativa para autenticación interactiva (backup)
def initialize_ee_interactive():
    try:
        ee.Initialize()
        return True
    except:
        try:
            ee.Authenticate()
            ee.Initialize()
            return True
        except:
            return False

# Función para obtener el mapa IET
def get_iet_map():
    try:
        # Definir la región de Córdoba
        cordoba = ee.FeatureCollection("FAO/GAUL/2015/level2") \
            .filter(ee.Filter.eq('ADM2_NAME', 'Córdoba'))
        
        # Obtener imágenes Sentinel-2
        s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
            .filterBounds(cordoba) \
            .filterDate('2023-01-01', '2023-12-31') \
            .select(['B4', 'B8', 'B11']) \
            .median()
        
        # Calcular NDVI y NDMI
        ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ndmi = s2.normalizedDifference(['B8', 'B11']).rename('NDMI')
        
        # Obtener datos de precipitación CHIRPS
        chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterBounds(cordoba) \
            .filterDate('2023-01-01', '2023-12-31') \
            .sum() \
            .rename('Precipitation')
        
        # Obtener datos de áreas urbanas
        urban = ee.Image("ESA/WorldCover/v100/2020") \
            .select('Map') \
            .eq(50) \
            .rename('Urban')
        
        # Calcular Índice IET
        iet = ndvi \
            .multiply(ndmi) \
            .multiply(chirps) \
            .divide(urban.add(1)) \
            .rename('IET')
        
        return iet.clip(cordoba), cordoba
    except Exception as e:
        st.error(f"Error obteniendo datos de GEE: {e}")
        return None, None

# Crear la interfaz de la aplicación
def main():
    st.sidebar.title("⚙️ Opciones de Visualización")
    
    # Inicializar Earth Engine
    if not initialize_ee():
        st.warning("""
        ⚠️ No se pudo inicializar Earth Engine automáticamente.
        La aplicación podría no funcionar correctamente en Streamlit Cloud.
        """)
    
    # Selector de capas
    capa_seleccionada = st.sidebar.selectbox(
        "Selecciona la capa a visualizar:",
        ["Índice IET", "NDVI", "NDMI", "Precipitación"]
    )
    
    # Opciones de visualización
    st.sidebar.subheader("Ajustes de Visualización")
    
    if capa_seleccionada == "Índice IET":
        min_val = st.sidebar.slider("Valor mínimo", 0.0, 0.5, 0.0, 0.01)
        max_val = st.sidebar.slider("Valor máximo", 0.5, 2.0, 1.0, 0.01)
    elif capa_seleccionada == "NDVI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
    elif capa_seleccionada == "NDMI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
    else:  # Precipitación
        min_val = st.sidebar.slider("Valor mínimo (mm)", 0, 500, 0, 10)
        max_val = st.sidebar.slider("Valor máximo (mm)", 500, 2000, 1500, 10)
    
    try:
        with st.spinner('Cargando datos desde Google Earth Engine...'):
            # Obtener los datos
            iet, cordoba = get_iet_map()
            
            if iet is None or cordoba is None:
                st.error("No se pudieron cargar los datos. Intenta recargar la página.")
                return
            
            # Crear el mapa
            m = geemap.Map(
                center=[-31.4, -64.2], 
                zoom=7,
                draw_export=False,
                layout={'height': '600px'}
            )
            
            # Configurar parámetros de visualización según la capa seleccionada
            if capa_seleccionada == "Índice IET":
                vis_params = {
                    'min': min_val,
                    'max': max_val,
                    'palette': ['red', 'yellow', 'green', 'darkgreen']
                }
                m.addLayer(iet, vis_params, 'Índice IET')
                
            elif capa_seleccionada == "NDVI":
                # Calcular NDVI para mostrar
                s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                    .filterBounds(cordoba) \
                    .filterDate('2023-01-01', '2023-12-31') \
                    .select(['B4', 'B8']) \
                    .median()
                ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
                vis_params = {
                    'min': min_val,
                    'max': max_val,
                    'palette': ['brown', 'yellow', 'green', 'darkgreen']
                }
                m.addLayer(ndvi.clip(cordoba), vis_params, 'NDVI')
                
            elif capa_seleccionada == "NDMI":
                # Calcular NDMI para mostrar
                s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
                    .filterBounds(cordoba) \
                    .filterDate('2023-01-01', '2023-12-31') \
                    .select(['B8', 'B11']) \
                    .median()
                ndmi = s2.normalizedDifference(['B8', 'B11']).rename('NDMI')
                vis_params = {
                    'min': min_val,
                    'max': max_val,
                    'palette': ['brown', 'yellow', 'blue', 'darkblue']
                }
                m.addLayer(ndmi.clip(cordoba), vis_params, 'NDMI')
                
            elif capa_seleccionada == "Precipitación":
                # Obtener precipitación
                chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
                    .filterBounds(cordoba) \
                    .filterDate('2023-01-01', '2023-12-31') \
                    .sum() \
                    .rename('Precipitation')
                vis_params = {
                    'min': min_val,
                    'max': max_val,
                    'palette': ['white', 'lightblue', 'blue', 'darkblue', 'purple']
                }
                m.addLayer(chirps.clip(cordoba), vis_params, 'Precipitación 2023')
            
            # Añadir la región de Córdoba como contorno
            m.addLayer(cordoba.style(**{'color': 'black', 'fillColor': '00000000'}), {}, 'Límites Córdoba')
            
            # Añadir control de capas
            m.addLayerControl()
            
        # Mostrar el mapa en Streamlit
        st.subheader(f"🗺️ Mapa de {capa_seleccionada} - Córdoba 2023")
        m.to_streamlit(height=600)
        
        # Información adicional
        with st.expander("📊 Información sobre los índices"):
            st.markdown("""
            ### **Índice IET** 
            Índice compuesto que combina múltiples factores ambientales:
            
            - **NDVI** (Índice de Vegetación de Diferencia Normalizada) - Salud de la vegetación
            - **NDMI** (Índice de Humedad del Suelo) - Contenido de humedad
            - **Precipitación** (datos CHIRPS) - Lluvia acumulada anual
            - **Áreas urbanas** (para normalización) - Influencia urbana
            
            **Fórmula**: `IET = (NDVI × NDMI × Precipitación) / (Áreas Urbanas + 1)`
            
            **Interpretación**:
            - 🟢 **Valores altos**: Mejor condición ambiental
            - 🟡 **Valores medios**: Condición moderada  
            - 🔴 **Valores bajos**: Peor condición ambiental
            
            **Período analizado**: Enero - Diciembre 2023
            **Resolución**: 30 metros
            """)
            
    except Exception as e:
        st.error(f"❌ Error al generar el mapa: {str(e)}")
        st.info("""
        🔧 **Solución de problemas:**
        - Verifica que Earth Engine esté correctamente configurado
        - Recarga la página
        - Si el problema persiste, contacta al administrador
        """)

if __name__ == "__main__":
    main()