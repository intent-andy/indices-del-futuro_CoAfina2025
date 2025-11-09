import streamlit as st

# Título de la página del Indice de Equilibrio Territorial (IET)
st.markdown('<h1 style="text-align: center;">Índice de Equilibrio Territorial (IET)</h1>', unsafe_allow_html=True)

# Divisor
st.divider()

# Descripción del IET
st.markdown("""
<p style="text-align: justify;">El Índice de Equilibrio Territorial (IET) es un índice que permite evaluar los efectos de la humedad, el desarrollo de la vegetación y el impacto del desarrollo urbano, entendido como construcciones.</p>

<p style="text-align: justify;">Dicha evaluación se hace con la combinación de índices establecidos en la literatura de análisis por sensores remotos, específicamente con el satélite Sentinel-2.</p>

<p style="text-align: justify;">La humedad se evalúa con el NDMI (Normalized Difference Moisture Index), que mezcla las reflectancias del infrarrojo cercano (NIR) e infrarrojo de onda corta (SWIR) para monitorear el cambio del contenido de agua dentro del tejido de las hojas de las plantas.</p>

<p style="text-align: justify;">Para trabajar con la vegetación, usamos los índices SAVI (Solo Adjusted Vegetation Index), que es índice ajustado para minimizar la influencia del brillo del suelo en los índices espectrales de vegetación que involucren longitudes de onda rojo e infrarrojo. Este índice es de especial importancia porque nos permite observar con más detalle la vegetación típica de las zonas periurbanas, conocidas por tener vegetación de bajo porte, dónde la deforestación y desarrollo agricola son mucho más frecuentes.</p>

<p style="text-align: justify;">Adicionalmente, el EVI (Enhanced Vegetation Index) estima la composición de la vegetación en áreas con dosel alto y tiene correccion para el reflejo del suelo.</p>

<p style="text-align: justify;">Para el urbanismo se usa el índice construido NDBI a partir de NIR y SWIR que permite diferenciar la presencia de estructuras artificiales.</p>
""", unsafe_allow_html=True)

# Divisor
st.divider()

# Ecuación del IET
st.markdown('<h2 style="text-align: center;">Cálculo del IET</h2>', unsafe_allow_html=True)
st.markdown("""
<p style="text-align: justify;"><p style="text-align: justify;">El IET se compone de una suma de los índices de vegetación y humedad divididos por el índice de urbanismo + 1, de la siguiente manera:</p>
""", unsafe_allow_html=True)

st.latex(r"""IET = \frac{\text{NDMI} + \text{SAVI} + \text{EVI}}{\text{NDBI} + 1}""" )

st.markdown('<p style="text-align: justify;">Donde:</p', unsafe_allow_html=True)
st.latex(r"""
NDBI = \frac{\text{SWIR} - \text{NIR}}{\text{SWIR} + \text{NIR}}
""")
st.markdown("""<p style="text-align: justify;"> Esta suma en el denominador nos permite evitar dividir entre cero y penaliza la presencia de construcciones disminuyendo la magnitud del IVT. Si hay muchas construcciones, NDIR es cercano a 1 y si hay pocas, es cercano a 0.</p>
<p style="text-align: justify;">Así el IVT nos hace enfasis en vegetación baja, típica de las zonas periurbanas que suelen presentar aumento de la frontera agricola y aumento de las construcciones""", unsafe_allow_html=True)