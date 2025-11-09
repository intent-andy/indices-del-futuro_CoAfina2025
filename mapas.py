import streamlit as st
import ee
import geemap.foliumap as geemap
# from streamlit_folium import st_folium
import json
import tempfile
import os

# Configuración de la página
st.set_page_config(
    page_title="Mapa IET Córdoba",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título de la aplicación
st.markdown('<h1 style="text-align: center;">🌍 Mapa Interactivo del Índice IET</h1>', unsafe_allow_html=True)

# Inicializar Earth Engine para Streamlit Cloud
def initialize_ee():
    """
    Intenta inicializar EE con credenciales de servicio en st.secrets.
    - Soporta clave JSON completa (dict o string) o clave privada PEM con newlines.
    - Escribe la clave a un archivo temporal y pasa la ruta a ee.ServiceAccountCredentials,
      luego borra el archivo temporal.
    - Si faltan secretos, cae en initialize_ee_interactive().
    """
    try:
        service_account = st.secrets["EE_SERVICE_ACCOUNT"]
        private_key = st.secrets["EE_PRIVATE_KEY"]
    except Exception:
        # No hay secretos: intentar inicialización interactiva (local)
        return initialize_ee_interactive()

    # Helper para escribir un objeto/str a archivo temporal
    def _write_temp(content, suffix):
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix, encoding="utf-8")
        tmp.write(content)
        tmp.close()
        return tmp.name

    # Si la clave es un dict (ej. secrets devuelve dict), volcar a JSON
    if isinstance(private_key, dict):
        try:
            key_path = _write_temp(json.dumps(private_key), ".json")
            creds = ee.ServiceAccountCredentials(service_account, key_path)
            ee.Initialize(creds)
            os.remove(key_path)
            return True
        except Exception as e:
            if os.path.exists(key_path):
                os.remove(key_path)
            st.error(f"Error inicializando EE con clave JSON: {e}")
            return False

    # Si la clave es string, intentar parsear como JSON; si falla, tratar como PEM
    if isinstance(private_key, str):
        # intentar JSON
        try:
            key_obj = json.loads(private_key)
            key_path = _write_temp(json.dumps(key_obj), ".json")
            creds = ee.ServiceAccountCredentials(service_account, key_path)
            ee.Initialize(creds)
            os.remove(key_path)
            return True
        except Exception:
            # No es JSON: escribir el contenido tal cual (PEM) y pasar la ruta
            try:
                key_path = _write_temp(private_key, ".pem")
                creds = ee.ServiceAccountCredentials(service_account, key_path)
                ee.Initialize(creds)
                os.remove(key_path)
                return True
            except Exception as e:
                if os.path.exists(key_path):
                    os.remove(key_path)
                st.error(f"Error inicializando EE con clave PEM: {e}")
                return False

    # Si llega aquí, no se pudo usar el secreto; intentar modo interactivo
    return initialize_ee_interactive()

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

# Función para obtener TODOS los datos del script original
def get_all_data():
    try:
        # Definir la región de Córdoba (EXACTO como tu script)
        cordoba = ee.FeatureCollection("FAO/GAUL/2024/level2") \
            .filter(ee.Filter.eq('ADM2_NAME', 'Córdoba'))
        
        # Obtener imágenes Sentinel-2 (EXACTO como tu script)
        s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
            .filterBounds(cordoba) \
            .filterDate('2023-01-01', '2023-12-31') \
            .select(['B4', 'B8', 'B11']) \
            .median()
        
        # Calcular NDVI y NDMI (EXACTO como tu script)
        ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ndmi = s2.normalizedDifference(['B8', 'B11']).rename('NDMI')
        
        # Obtener datos de precipitación CHIRPS (EXACTO como tu script)
        chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterBounds(cordoba) \
            .filterDate('2023-01-01', '2023-12-31') \
            .sum() \
            .rename('Precipitation')
        
        # Obtener datos de áreas urbanas (EXACTO como tu script)
        urban = ee.Image("ESA/WorldCover/v100/2020") \
            .select('Map') \
            .eq(50) \
            .rename('Urban')
        
        # Calcular Índice IET (EXACTO como tu script)
        iet = ndvi \
            .multiply(ndmi) \
            .multiply(chirps) \
            .divide(urban.add(1)) \
            .rename('IET')
        
        return {
            'iet': iet.clip(cordoba),
            'ndvi': ndvi.clip(cordoba),
            'ndmi': ndmi.clip(cordoba),
            'precipitation': chirps.clip(cordoba),
            'cordoba': cordoba
        }
        
    except Exception as e:
        st.error(f"Error obteniendo datos de GEE: {e}")
        return None

# Crear la interfaz de la aplicación
def main():
    st.sidebar.title("⚙️ Opciones de Visualización")
    
    # Inicializar Earth Engine
    if not initialize_ee():
        st.warning("""
        ⚠️ No se pudo inicializar Earth Engine automáticamente.
        La aplicación podría no funcionar correctamente en Streamlit Cloud.
        """)
        return
    
    # Selector de capas
    capa_seleccionada = st.sidebar.selectbox(
        "Selecciona la capa a visualizar:",
        ["Índice IET", "NDVI", "NDMI", "Precipitación"]
    )
    
    # Opciones de visualización
    st.sidebar.subheader("Ajustes de Visualización")
    
    # Configuración de paletas y rangos según la capa
    if capa_seleccionada == "Índice IET":
        min_val = st.sidebar.slider("Valor mínimo", 0.0, 0.5, 0.0, 0.01)
        max_val = st.sidebar.slider("Valor máximo", 0.5, 2.0, 1.0, 0.01)
        palette = ['red', 'yellow', 'green']
    elif capa_seleccionada == "NDVI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['red', 'yellow', 'green']
    elif capa_seleccionada == "NDMI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'blue']
    else:  # Precipitación
        min_val = st.sidebar.slider("Valor mínimo (mm)", 0, 500, 0, 10)
        max_val = st.sidebar.slider("Valor máximo (mm)", 500, 2000, 1500, 10)
        palette = ['white', 'lightblue', 'blue', 'darkblue']
    
    try:
        with st.spinner('Cargando datos desde Google Earth Engine...'):
            # Obtener TODOS los datos una sola vez
            data = get_all_data()
            
            if data is None:
                st.error("No se pudieron cargar los datos. Intenta recargar la página.")
                return
            
            # Crear el mapa
            m = geemap.Map(
                center=[-31.4, -64.2], 
                zoom=7,
                draw_export=False
            )
            
            # Configurar parámetros de visualización
            vis_params = {
                'min': min_val,
                'max': max_val,
                'palette': palette
            }
            
            # Añadir capa según selección (usando los datos ya calculados)
            if capa_seleccionada == "Índice IET":
                m.addLayer(data['iet'], vis_params, 'Índice IET')
                st.sidebar.info("**Índice IET**: (NDVI × NDMI × Precipitación) / (Áreas Urbanas + 1)")
                
            elif capa_seleccionada == "NDVI":
                m.addLayer(data['ndvi'], vis_params, 'NDVI')
                st.sidebar.info("**NDVI**: (B8 - B4) / (B8 + B4)")
                
            elif capa_seleccionada == "NDMI":
                m.addLayer(data['ndmi'], vis_params, 'NDMI')
                st.sidebar.info("**NDMI**: (B8 - B11) / (B8 + B11)")
                
            elif capa_seleccionada == "Precipitación":
                m.addLayer(data['precipitation'], vis_params, 'Precipitación 2023')
                st.sidebar.info("**Precipitación**: Acumulado anual CHIRPS")
            
            # Añadir la región de Córdoba como contorno
            m.addLayer(data['cordoba'].style(**{'color': 'black', 'fillColor': '00000000'}), {}, 'Límites Córdoba')
            
            # Añadir control de capas
            m.addLayerControl()
            
        # Mostrar el mapa en Streamlit
        st.subheader(f"🗺️ Mapa de {capa_seleccionada} - Córdoba 2023")
        
        # Mostrar información estadística básica
        with st.expander("📈 Información estadística"):
            try:
                if capa_seleccionada == "Índice IET":
                    stats = data['iet'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['cordoba'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio IET: {stats.get('IET', 'N/A'):.4f}")
                    
                elif capa_seleccionada == "NDVI":
                    stats = data['ndvi'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['cordoba'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio NDVI: {stats.get('NDVI', 'N/A'):.4f}")
                    
                elif capa_seleccionada == "NDMI":
                    stats = data['ndmi'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['cordoba'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio NDMI: {stats.get('NDMI', 'N/A'):.4f}")
                    
                elif capa_seleccionada == "Precipitación":
                    stats = data['precipitation'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['cordoba'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Precipitación promedio: {stats.get('Precipitation', 'N/A'):.0f} mm")
                    
            except Exception as e:
                st.write("No se pudieron calcular estadísticas en este momento")
        
        # Mostrar el mapa
        m.to_streamlit(height=600)
        
        # Información adicional
        with st.expander("📊 Información sobre los índices"):
            st.markdown("""
            ### **Índice IET** 
            **Fórmula exacta del script original**: 
            ```javascript
            var iet = ndvi.multiply(ndmi)
                         .multiply(chirps)
                         .divide(urban.add(1))
                         .rename('IET');
            ```
            
            **Componentes**:
            - **NDVI** (Índice de Vegetación): `(B8 - B4) / (B8 + B4)`
            - **NDMI** (Índice de Humedad): `(B8 - B11) / (B8 + B11)`  
            - **Precipitación**: Acumulado anual CHIRPS
            - **Áreas urbanas**: Clase 50 de ESA WorldCover
            
            **Interpretación**:
            - 🟢 **Valores altos**: Mejor condición ambiental
            - 🟡 **Valores medios**: Condición moderada  
            - 🔴 **Valores bajos**: Peor condición ambiental
            
            **Período**: Enero - Diciembre 2023
            **Fuentes**: Sentinel-2, CHIRPS, ESA WorldCover
            """)
            
    except Exception as e:
        st.error(f"❌ Error al generar el mapa: {str(e)}")
        st.info("""
        🔧 **Solución de problemas:**
        - Verifica que Earth Engine esté correctamente configurado
        - Recarga la página
        - Verifica los secrets en Streamlit Cloud
        """)

if __name__ == "__main__":
    main()