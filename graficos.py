import streamlit as st
import pandas as pd
import csv

# Cargar datos desde un archivo CSV
def load_data(file):
    data = []
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Mostrar los datos en un gráfico
def show_chart(data, primary_loss=True, secondary_loss=True, start_year=1985, end_year=2024):
    # Definir ejes y valores
    headers = data[0]
    # Filtrar por rango de años
    years = [int(row[0]) for row in data[1:] if start_year <= int(row[0]) <= end_year]
    if primary_loss and secondary_loss:
        primary_loss = [float(row[1]) for row in data[1:] if start_year <= int(row[0]) <= end_year]
        secondary_loss = [float(row[2]) for row in data[1:] if start_year <= int(row[0]) <= end_year]
    elif primary_loss:
        primary_loss = [float(row[1]) for row in data[1:] if start_year <= int(row[0]) <= end_year]
        secondary_loss = [0]*len(years)
    elif secondary_loss:
        primary_loss = [0]*len(years)
        secondary_loss = [float(row[2]) for row in data[1:] if start_year <= int(row[0]) <= end_year]

    # Crear un DataFrame para graficar
    df = pd.DataFrame({
        'Año': years,
        'Pérdida de Vegetación Primaria': primary_loss,
        'Pérdida de Vegetación Secundaria': secondary_loss

    }).set_index('Año')

    # Mostrar el gráfico con nombres en los ejes
    st.line_chart(df, x_label='Año', y_label='Pérdida de Vegetación (hectáreas)')
    

# Título de la página de gráficos
st.title("Gráficos")

# Selección de provincia
zone = st.selectbox("**Selecciona una provincia**", ["Argentina", "Buenos Aires", "Córdoba", "Santa Fe", "Mendoza", "Tucumán", "La Pampa"], index=None, placeholder="Elige una provincia")

# Opciones de visualización
st.write("**Selecciona las series que deseas visualizar:**")

# Checkboxes para seleccionar las series
st.checkbox("Pérdida de vegetación primaria", value=True, key="veg_loss_primary")
st.checkbox("Pérdida de vegetación secundaria", value=True, key="veg_loss_secondary")

# Slider para seleccionar el rango de años
year_range = st.slider("**Selecciona el rango de años**", 1985, 2024, (2000, 2024), step=1)

# Si no se selecciona ninguna provincia, mostrar el gráfico de Argentina
if zone is None or zone == "Argentina":
    st.header("Pérdida de Vegetación en Argentina")

    data_file = f"..\time-series_data\Time series of Vegetation loss • Annual by class • 1985 - 2024 (Argentina).csv"
    data = load_data(data_file)

    # Mostrar el gráfico con nombres en los ejes
    show_chart(data, primary_loss=st.session_state.veg_loss_primary, secondary_loss=st.session_state.veg_loss_secondary, start_year=year_range[0], end_year=year_range[1])

elif zone:
    st.header(f"Pérdida de Vegetación en {zone}")

    data_file = f"..\time-series_data\Time series of Vegetation loss • Annual by class • 1985 - 2024 ({zone}).csv"
    data = load_data(data_file)

    # Mostrar el gráfico con nombres en los ejes
    show_chart(data, primary_loss=st.session_state.veg_loss_primary, secondary_loss=st.session_state.veg_loss_secondary, start_year=year_range[0], end_year=year_range[1])



