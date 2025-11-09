import streamlit as st

# Comprobación de dependencias (muestra instrucciones si faltan)
missing = []
try:
    import ee
except Exception:
    missing.append("earthengine-api (ee)")

try:
    import geemap.foliumap as geemap
except Exception:
    missing.append("geemap")

try:
    from streamlit_folium import st_folium
except Exception:
    # streamlit_folium es opcional; se usará fallback con components.html
    st_folium = None

if missing:
    st.set_page_config(page_title="Mapa IET Buenos Aires", layout="wide")
    st.title("🌍 Visualización de Índice IET - Buenos Aires 2023")
    st.error(
        "Faltan paquetes necesarios: " + ", ".join(missing) + ".\n\n"
        "Instálalos en tu entorno y autentica Earth Engine:\n\n"
        "pip install earthengine-api geemap streamlit-folium\n\n"
        "Luego ejecuta:\n\n"
        "earthengine authenticate\n\n"
        "Reinicia la aplicación después de instalar y autenticar."
    )
    st.stop()

import json
import tempfile
import os

# Configuración de la página
st.set_page_config(
    page_title="Mapa IET Buenos Aires",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título de la aplicación
st.title("🌍 Visualización de Índice IET - Buenos Aires 2023")

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
        region = ee.FeatureCollection("FAO/GAUL/2015/level1") \
            .filter(ee.Filter.eq('ADM1_NAME', 'Buenos Aires'))

        s2 = ee.ImageCollection("COPERNICUS/S2_SR") \
            .filterBounds(region) \
            .filterDate('2023-01-01', '2023-12-31') \
            .select(['B2', 'B4', 'B8', 'B11']) \
            .median()

        ndmi = s2.normalizedDifference(['B8', 'B11']).rename('NDMI')

        savi = s2.expression(
            '(1 + L) * ((NIR - RED) / (NIR + RED + L))',
            {'NIR': s2.select('B8'), 'RED': s2.select('B4'), 'L': 0.5}
        ).rename('SAVI')

        evi = s2.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
            {'NIR': s2.select('B8'), 'RED': s2.select('B4'), 'BLUE': s2.select('B2')}
        ).rename('EVI')

        ndbi = s2.normalizedDifference(['B11', 'B8']).rename('NDBI')

        iet = ndmi.add(savi).add(evi).divide(ndbi.add(1)).rename('IET')

        return {
            'iet': iet.clip(region),
            'ndmi': ndmi.clip(region),
            'savi': savi.clip(region),
            'evi': evi.clip(region),
            'ndbi': ndbi.clip(region),
            'region': region
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
        ["Índice IET", "NDMI", "SAVI", "EVI", "NDBI"]
    )

    
    # Opciones de visualización
    st.sidebar.subheader("Ajustes de Visualización")
    
    # Crear el mapa
    m = geemap.Map(
        center=[-31.4, -64.2], 
        zoom=7,
        draw_export=False
    )
    # Configuración de paletas y rangos según la capa
    if capa_seleccionada == "Índice IET":
        min_val = st.sidebar.slider("Valor mínimo", 0.0, 0.5, 0.0, 0.01)
        max_val = st.sidebar.slider("Valor máximo", 0.5, 2.0, 1.0, 0.01)
        palette = ['red', 'yellow', 'green']
    elif capa_seleccionada == "NDMI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'blue']
    elif capa_seleccionada == "SAVI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'green']
    elif capa_seleccionada == "EVI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'green']
    elif capa_seleccionada == "NDBI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['green', 'yellow', 'gray']
    else:
        # Valores por defecto si ninguna capa coincide
        min_val = 0
        max_val = 1
        palette = ['blue', 'green', 'red']

    # Configurar parámetros de visualización
    vis_params = {
        'min': min_val,
        'max': max_val,
        'palette': palette
    }

    # Configuración de paletas y rangos según la capa
    if capa_seleccionada == "Índice IET":
        m.addLayer(data['iet'], vis_params, 'Índice IET')
        st.sidebar.info("**IET** = (NDMI + SAVI + EVI) / (1 + NDBI)")
    elif capa_seleccionada == "NDMI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'blue']
    elif capa_seleccionada == "SAVI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'green']
    elif capa_seleccionada == "EVI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['brown', 'yellow', 'green']

    elif capa_seleccionada == "NDBI":
        min_val = st.sidebar.slider("Valor mínimo", -1.0, 0.0, -1.0, 0.1)
        max_val = st.sidebar.slider("Valor máximo", 0.0, 1.0, 1.0, 0.1)
        palette = ['green', 'yellow', 'gray']
    else:
        min_val = 0
        max_val = 1
        palette = ['blue', 'green', 'red']
    
    try:
        with st.spinner('Cargando datos desde Google Earth Engine...'):
            # Obtener TODOS los datos una sola vez
            data = get_all_data()
            
            if data is None:
                st.error("No se pudieron cargar los datos. Intenta recargar la página.")
                return
            
            # Añadir capa según selección (usando los datos ya calculados)
            if capa_seleccionada == "Índice IET":
                m.addLayer(data['iet'], vis_params, 'Índice IET')
                st.sidebar.info("**Índice IET**: (NDMI + SAVI + EVI) / (1 + NDBI)")
                
            elif capa_seleccionada == "NDMI":
                m.addLayer(data['ndmi'], vis_params, 'NDMI')
                st.sidebar.info("**NDMI**: (B8 - B11) / (B8 + B11)")

            elif capa_seleccionada == "SAVI":
                m.addLayer(data['savi'], vis_params, 'SAVI')
                st.sidebar.info("**SAVI**: (1 + L) * ((NIR - RED) / (NIR + RED + L)), L=0.5")

            elif capa_seleccionada == "EVI":
                m.addLayer(data['evi'], vis_params, 'EVI')
                st.sidebar.info("**EVI**: 2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))")
            
            elif capa_seleccionada == "NDBI":
                m.addLayer(data['ndbi'], vis_params, 'NDBI')
                st.sidebar.info("**NDBI**: (B11 - B8) / (B11 + B8)")
            
            # Añadir la región de Buenos Aires como contorno
            m.addLayer(data['region'].style(**{'color': 'black', 'fillColor': '00000000'}), {}, 'Límites Buenos Aires')
            
            # Añadir control de capas
            m.addLayerControl()
            
        # Mostrar el mapa en Streamlit
        st.subheader(f"🗺️ Mapa de {capa_seleccionada} - Buenos Aires 2023")
        
        # Mostrar información estadística básica
        with st.expander("📈 Información estadística"):
            try:
                if capa_seleccionada == "Índice IET":
                    stats = data['iet'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['region'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio IET: {stats.get('IET', 'N/A'):.4f}")
                    
                elif capa_seleccionada == "NDMI":
                    stats = data['ndmi'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['region'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio NDMI: {stats.get('NDMI', 'N/A'):.4f}")
                
                elif capa_seleccionada == "SAVI":
                    stats = data['savi'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['region'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio SAVI: {stats.get('SAVI', 'N/A'):.4f}")
                
                elif capa_seleccionada == "EVI":
                    stats = data['evi'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['region'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio EVI: {stats.get('EVI', 'N/A'):.4f}")

                elif capa_seleccionada == "NDBI":
                    stats = data['ndbi'].reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=data['region'].geometry(),
                        scale=1000
                    ).getInfo()
                    st.write(f"Valor promedio NDBI: {stats.get('NDBI', 'N/A'):.4f}")
                    
            except Exception as e:
                st.write("No se pudieron calcular estadísticas en este momento")
        
        # Mostrar el mapa
        m.to_streamlit(height=600)
            
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