import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Índices del Futuro",
    page_icon=":argentina:",
    layout="wide"
)

# Panel de navegación superior
pages = {
    "Inicio": [st.Page("bienvenida.py", title="Inicio")],
    "Recursos": [
        st.Page("mapas.py", title="Mapas"),
        st.Page("graficos.py", title="Gráficos"),
        st.Page("vid-int.py", title="Videos Interactivos")
    ],
    "Sobre nosotros": [st.Page("about.py", title="Sobre nosotros")]
}

# Crear el panel de navegación
pg = st.navigation(pages, position="top")
pg.run()