import streamlit as st
from pathlib import Path

# Título de la página de inicio
st.markdown('<h1 style="text-align:center">Bienvenid@ a "nombre de la app"</h1>', unsafe_allow_html=True)

# Sobre el proyecto
st.markdown('<h2 style="text-align:center"><em>¿Qué pasaría si pudiéramos ver cómo cambia el lugar donde vivimos?</em></h2>', unsafe_allow_html=True)

st.markdown("""
<p style="text-align: justify;">
Este proyecto nace de la interdisciplinaridad, la biología que comprende los ecosistemas, la física que traduce los datos y la antropología que conecta con las personas.
</p>
<p style="text-align: justify;">
Juntas, estas perspectivas se integran para convertir datos en información simple y accesible: cómo crecen las ciudades, cuánta vegetación se pierde y donde se intensifica el impacto ambiental, así acercamos el conocimiento a la ciudadanía.
</p>
<p style="text-align: justify;">
Nuestras métricas, obtenidas gracias a los datos abiertos y reproducibles, pueden ser usadas por alcaldías, comunidades y cualquier persona que quiera entender su territorio, reconocer los cambios que se producen y participar activamente en la toma de decisiones y la planificación de políticas públicas.
</p>
<p style="text-align: justify;">
No se trata solo de medir el territorio: <em><strong>se trata de darle a la gente los datos para cuidar su lugar en el mundo</strong></em>.
</p>
""", unsafe_allow_html=True)

# Conexión con los Objetivos de Desarrollo Sostenible
st.markdown('<h2 style="text-align:center">Conexión con los Objetivos de Desarrollo Sostenible (ODS)</h2>', unsafe_allow_html=True)

# Logos de los ODS
banner = Path(__file__).parent / "images" / "S_SDG_logo_without_UN_emblem_horizontal_Transparent_WEB.png"
ods_11 = Path(__file__).parent / "images" / "S_SDG_Icons_Inverted_Transparent_WEB-11.png"
ods_13 = Path(__file__).parent / "images" / "S_SDG_Icons_Inverted_Transparent_WEB-13.png"
ods_15 = Path(__file__).parent / "images" / "S_SDG_Icons_Inverted_Transparent_WEB-15.png"
ods_16 = Path(__file__).parent / "images" / "S_SDG_Icons_Inverted_Transparent_WEB-16.png"

# Mostrar banner de los ODS
st.image(str(banner), use_container_width=True)

# Mostrar los ODS en dos columnas
icon, explanation = st.columns([1, 4], vertical_alignment="center")
with icon:
    st.image(str(ods_11), use_container_width=True)
with explanation:
    st.markdown('<p style="text-align: justify;">Al elegir zonas periurbanas para nuestro proyecto, los resultados pueden ser utilizados para apoyar la planificación sostenible y monitorear variables urbanas y ambientales, contribuyendo así a ciudades y comunidades más sostenibles.</p>', unsafe_allow_html=True)

icon, explanation = st.columns([1, 4], vertical_alignment="center")
with icon:
    st.image(str(ods_15), use_container_width=True)
with explanation:
    st.markdown('<p style="text-align: justify;">El uso de datos abiertos permite conocer y evaluar la degradación y conservación de los ecosistemas, vegetación y uso del suelo; lo que permite orientar estrategias de manejo sostenible y conservación de la vida de ecosistemas terrestres.</p>', unsafe_allow_html=True)

icon, explanation = st.columns([1, 4], vertical_alignment="center")
with icon:
    st.image(str(ods_13), use_container_width=True)
with explanation:
    st.markdown('<p style="text-align: justify;">El proyecto contribuye a monitorear y evaluar el impacto ambiental mediante el uso de datos satelitales abiertos, estas métricas facilitan la toma de decisiones adaptadas al cambio climático.</p>', unsafe_allow_html=True)

icon, explanation = st.columns([1, 4], vertical_alignment="center")
with icon:
    st.image(str(ods_16), use_container_width=True)
with explanation:
    st.markdown('<p style="text-align: justify;">La democratización de la acción climática al brindar conocimiento a la ciudadanía para ejercer voto inteligente, que les permita participar de forma activa en la resolución de problemas ambientales.</p>', unsafe_allow_html=True)