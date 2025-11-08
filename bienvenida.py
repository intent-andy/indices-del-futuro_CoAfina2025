import streamlit as st
import pandas as pd
import numpy as np

# Título de la página de bienvenida
st.title("Bienvenido a la aplicación")

st.title("📊 Análisis en Vivo")
st.write("Visualización de datos en tiempo real y métricas clave")

# Simulated data for line chart
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Series A', 'Series B', 'Series C']
)

st.subheader("Time Series Data")
st.line_chart(chart_data)

# Additional metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average A", f"{chart_data['Series A'].mean():.2f}")
with col2:
    st.metric("Average B", f"{chart_data['Series B'].mean():.2f}")
with col3:
    st.metric("Average C", f"{chart_data['Series C'].mean():.2f}")


st.title("🤖 AI Model")
st.write("Interact with the AI model for predictions")

# Text input area
user_input = st.text_area(
    "Enter your data or query:",
    placeholder="Type your data here...",
    height=150
)

# Process button
if st.button("Generate AI Output", type="primary"):
    if user_input:
        # Simulated AI output
        st.success("Processing complete!")
        
        with st.expander("📋 AI Results", expanded=True):
            st.write("**Input received:**")
            st.code(user_input)
            
            st.write("**Simulated AI Analysis:**")
            # Simulated prediction
            prediction_score = np.random.uniform(0.7, 0.99)
            st.write(f"- Confidence Score: {prediction_score:.2%}")
            st.write(f"- Input Length: {len(user_input)} characters")
            st.write(f"- Word Count: {len(user_input.split())} words")
            
            # Simulated classification
            categories = ["Environmental", "Economic", "Social", "Technological"]
            predicted_category = np.random.choice(categories)
            st.write(f"- Predicted Category: **{predicted_category}**")
            
            # Progress bar for visual effect
            st.progress(prediction_score)
    else:
        st.warning("Please enter some data before generating output.")

# Additional info
st.info("💡 Tip: This is a demonstration with simulated AI output. In production, this would connect to a real machine learning model.")
