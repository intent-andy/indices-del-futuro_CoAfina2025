import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="TERRAMETRICS",
    page_icon=":argentina:",
    layout="wide"
)

# Panel de navegación superior
pages = {
    "Inicio": [st.Page("inicio.py", title="Inicio")],
    "Índices": [
        st.Page("iet.py", title="Índice de Equilibrio Territorial (IET)"),
        st.Page("ipmi.py", title="Índice de Presión Marina Integrado (IPMI) - Pronto")
    ],
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