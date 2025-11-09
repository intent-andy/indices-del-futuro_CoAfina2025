import streamlit as st
import pandas as pd
import csv
from pathlib import Path

# Título de la página de gráficos
st.markdown('<h1 style="text-align: center;">Gráficos</h1>', unsafe_allow_html=True)

# Selección de provincia
graph = st.selectbox("**Seleccione el gráfico que desea visualizar:**",
                     ["Pérdida de Vegetación", "Vegetación secundaria", "Cobertura de suelo"], index=None, placeholder="Seleccione un gráfico")

if graph == "Pérdida de Vegetación":
    # Título del gráfico
    st.markdown('<h2 style="text-align: center;">Pérdida de Vegetación en Argentina</h2>', unsafe_allow_html=True)

    # Seleccionar las series a visualizar
    st.markdown("**Seleccione las series que desea visualizar:**")
    primary_loss = st.checkbox("Pérdida de vegetación primaria", value=True, key="veg_loss_primary")
    secondary_loss = st.checkbox("Pérdida de vegetación secundaria", value=True, key="veg_loss_secondary")

    # Rango de años
    year_range = st.slider("**Seleccione el rango de años**", 1985, 2024, (2000, 2024), step=1)

    # Cargar datos
    file = Path(__file__).parent / "time-series_data" / "vegetation_loss_completo_1985_2024.csv"
    data = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)

    
    # Definir ejes y valores: filtrar filas por el rango de años para asegurar listas de igual longitud
    headers = data[0]
    # Filtrar filas válidas dentro del rango seleccionado
    filtered_rows = [row for row in data[1:] if row and len(row) > 2 and row[2].strip() and year_range[0] <= int(row[2]) <= year_range[1]]
    years = [int(row[2]) for row in filtered_rows]

    if primary_loss and secondary_loss:
        primary_loss_values = [float(row[0]) for row in filtered_rows]
        secondary_loss_values = [float(row[1]) for row in filtered_rows]
    elif primary_loss:
        primary_loss_values = [float(row[0]) for row in filtered_rows]
        secondary_loss_values = [0.0] * len(years)
    elif secondary_loss:
        primary_loss_values = [0.0] * len(years)
        secondary_loss_values = [float(row[1]) for row in filtered_rows]
    else:
        # Ninguna serie seleccionada: mostrar ceros para evitar errores
        primary_loss_values = [0.0] * len(years)
        secondary_loss_values = [0.0] * len(years)

    # Crear un DataFrame para graficar
    df = pd.DataFrame({
        'Año': years,
        'Pérdida de Vegetación Primaria': primary_loss_values,
        'Pérdida de Vegetación Secundaria': secondary_loss_values

    }).set_index('Año')
    
    # Mostrar el gráfico con nombres en los ejes o informar si no hay datos
    if df.empty:
        st.info("No hay datos para el rango de años seleccionado.")
    else:
        st.line_chart(df, x_label='Año', y_label='Pérdida de Vegetación (%)')

elif graph == "Vegetación secundaria":
    # Título del gráfico
    st.markdown('<h2 style="text-align: center;">Vegetación Secundaria en Argentina</h2>', unsafe_allow_html=True)

    # Seleccionar las series a visualizar
    st.markdown("**Seleccione las series que desea visualizar:**")
    consolidated_veg = st.checkbox("Consolidación de vegetación secundaria", value=True, key="consolidated_veg")
    recovering_veg = st.checkbox("Recuperación de vegetación secundaria", value=True, key="recovering_veg")

    # Rango de años
    year_range = st.slider("**Seleccione el rango de años**", 1985, 2024, (2000, 2024), step=1)

    # Cargar datos
    file = Path(__file__).parent / "time-series_data" / "secondary_vegetation_completo_1985_2024.csv"
    data = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)

    
    # Definir ejes y valores: filtrar filas por el rango de años para asegurar listas de igual longitud
    headers = data[0]
    # Filtrar filas válidas dentro del rango seleccionado
    filtered_rows = [row for row in data[1:] if row and len(row) > 2 and row[2].strip() and year_range[0] <= int(row[2]) <= year_range[1]]
    years = [int(row[2]) for row in filtered_rows]

    if consolidated_veg and recovering_veg:
        consolidated_veg_values = [float(row[0]) for row in filtered_rows]
        recovering_veg_values = [float(row[1]) for row in filtered_rows]
    elif consolidated_veg:
        consolidated_veg_values = [float(row[0]) for row in filtered_rows]
        recovering_veg_values = [0.0] * len(years)
    elif recovering_veg:
        consolidated_veg_values = [0.0] * len(years)
        recovering_veg_values = [float(row[1]) for row in filtered_rows]
    else:
        # Ninguna serie seleccionada: mostrar ceros para evitar errores
        consolidated_veg_values = [0.0] * len(years)
        recovering_veg_values = [0.0] * len(years)

    # Crear un DataFrame para graficar
    df = pd.DataFrame({
        'Año': years,
        'Consolidación de Vegetación Secundaria': consolidated_veg_values,
        'Recuperación de Vegetación Secundaria': recovering_veg_values
    }).set_index('Año')

    # Mostrar el gráfico con nombres en los ejes o informar si no hay datos
    if df.empty:
        st.info("No hay datos para el rango de años seleccionado.")
    else:
        st.line_chart(df, x_label='Año', y_label='Vegetación Secundaria (%)')

elif graph == "Cobertura de suelo":
    # Título del gráfico
    st.markdown('<h2 style="text-align: center;">Cobertura de Suelo en Argentina</h2>', unsafe_allow_html=True)

    # Rango de años
    year_range = st.slider("**Seleccione el rango de años**", 1985, 2024, (2000, 2024), step=1)

    # Cargar datos
    file = Path(__file__).parent / "time-series_data" / "coverage_completo_1985_2024.csv"
    data = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    
    # Definir ejes y valores: filtrar filas por el rango de años para asegurar listas de igual longitud
    headers = data[0]
    # Filtrar filas válidas dentro del rango seleccionado
    filtered_rows = [row for row in data[1:] if row and len(row) > 4 and row[6].strip() and year_range[0] <= int(row[6]) <= year_range[1]]
    years = [int(row[6]) for row in filtered_rows]
    natural_veg_values = [float(row[0]) for row in filtered_rows]
    forest_values = [float(row[1]) for row in filtered_rows]
    agriculture_values = [float(row[2]) for row in filtered_rows]
    non_veg_values = [float(row[3]) for row in filtered_rows]
    water_values = [float(row[4]) for row in filtered_rows]
    non_data_values = [float(row[5]) for row in filtered_rows]
    # Crear un DataFrame para graficar
    df = pd.DataFrame({
        'Año': years,
        'Vegetación Natural': natural_veg_values,
        'Bosques': forest_values,
        'Agricultura': agriculture_values,
        'No Vegetación': non_veg_values,
        'Agua': water_values,
        'Sin Datos': non_data_values
    }).set_index('Año')
    # Mostrar el gráfico con nombres en los ejes o informar si no hay datos
    if df.empty:
        st.info("No hay datos para el rango de años seleccionado.")
    else:
        st.line_chart(df, x_label='Año', y_label='Cobertura de Suelo (%)')