import streamlit as st
from pathlib import Path

# Título de la página de videos interactivos
st.markdown('<h1 style="text-align: center;">Videos Interactivos</h1>', unsafe_allow_html=True)

# Introducción a los videos interactivos
st.markdown('<h2 style="text-align: center;">Hagamos un recorrido a través del tiempo</h2>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Explora la evolución de la cantidad de personas en relación a la cantidad de vegetación en Argentina con Lionel Pulgasi a través de los años</h3>', unsafe_allow_html=True)

# Instrucciones para el usuario
st.markdown("""
<p style="text-align: justify;">
Utiliza el deslizador a continuación para seleccionar el año que deseas visualizar. A medida que mueves el deslizador, el video se actualizará automáticamente para mostrarte cómo ha cambiado la cantidad de personas en relación a la cantidad de vegetación en Argentina a lo largo del tiempo.
</p>
<p style="text-align: justify;">
¡Disfruta del viaje en el tiempo y observa las transformaciones que han ocurrido!
</p>
""", unsafe_allow_html=True)

# Deslizador para seleccionar el año
year = st.slider('Selecciona el año:', min_value=1985, max_value=2024, value=1985, step=1)

# Ruta del video correspondiente al año seleccionado
video = Path(__file__).parent / f"videos/{year}.mp4"

if video.exists():
    video_file = open(video, "rb")
    video_bytes = video_file.read()
    col1, col2, col3 = st.columns(3)
    with col2:
        st.video(video_bytes)
else:
    st.error("Lo sentimos, el video para el año seleccionado no está disponible.")