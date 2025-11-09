import streamlit as st

# Título de la página "Sobre nosotros"
st.markdown('<h1 style="text-align: center;">Sobre nosotros</h1>', unsafe_allow_html=True)

# Divisor
st.divider()

# Descripción del equipo
st.markdown("""
<p style="text-align: justify;">Somos un equipo multidisciplinario de estudiantes universitarios que nace en 2023 con el objetivo de desarrollar una solución innovadora al problema "Quantum Eco-Quest" del Hackathon CoAfina 2023. Desde nuestros inicios, hemos estado comprometidos con la creación de herramientas que integren tecnología y sostenibilidad ambiental, promoviendo la participación ciudadana y el uso de datos abiertos para la conservación del medio ambiente.</p>

<p style="text-align: justify;">Nuestro equipo está compuesto por estudiantes de diversas disciplinas: física, biología y antropología. Esta diversidad de conocimientos y experiencias nos permite abordar los desafíos ambientales desde múltiples perspectivas, enriqueciendo nuestras soluciones y fomentando la colaboración interdisciplinaria.</p>

<p style="text-align: justify;">En esta oportunidad, bajo el pseudónimo "Neotropical 3.0", hemos desarrollado una solución al reto "Índices del Futuro: Tierra y mar argentinos" del Hackathon CoAfina 2025. Nuestra propuesta se centra en la creación de índices innovadores que integren datos satelitales y una interfaz amigable para los usuarios, facilitando la comprensión y el análisis de la salud ambiental tanto terrestre como marina en Argentina.</p>
""", unsafe_allow_html=True)

# Divisor
st.divider()

# Integrantes del equipo
st.markdown('<h2 style="text-align: center;">Integrantes del equipo</h2>', unsafe_allow_html=True)
st.markdown("""
<ul>
    <li><strong>Cristian Usca:</strong> Estudiante de Física de la Escuela Superior Politécnica de Chimborazo, Ecuador.
    <li><strong>Isabella Sánchez:</strong> Estudiante de Antropología de la Universidad Central de Venezuela.
    <li><strong>Rubén Niño:</strong> Estudiante de Biología de la Universidad Central de Venezuela.
    <li><strong>Emilio Toledo:</strong> Estudiante de Biología de la Universidad de Los Andes, Venezuela.
    <li><strong>Andrés Caña:</strong> Estudiante de Física de la Universidad Simón Bolívar, Venezuela.
</ul>
""", unsafe_allow_html=True)