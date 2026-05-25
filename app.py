import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(
    page_title="Health Dashboard",
    layout="wide"
)

# TÍTULO PRINCIPAL
st.title("📊 Health Monitoring Dashboard")
st.markdown("Sistema de seguimiento de bienestar personal")

st.markdown("---")

# SIDEBAR (PROFESIONAL)
st.sidebar.header("Configuración de Usuario")

nombre = st.sidebar.text_input("Nombre del usuario")
edad = st.sidebar.number_input("Edad", min_value=0, max_value=100, value=25)

st.sidebar.markdown("---")
st.sidebar.info("Complete los datos para evaluar métricas")

# ENTRADAS PRINCIPALES
st.header("📥 Ingreso de Datos")

col1, col2 = st.columns(2)

with col1:
    agua = st.number_input("💧 Consumo de agua (vasos/día)", 0, 15, 5)
    sueno = st.number_input("💤 Horas de sueño", 0, 12, 7)

with col2:
    ejercicio = st.number_input("🏃 Ejercicio (min/día)", 0, 180, 30)
    estres = st.slider("🧘 Nivel de estrés", 1, 10, 5)

st.markdown("---")

# PROCESAMIENTO
if st.button("📈 Generar análisis"):

    # SCORING
    score = 0
    data = []

    if agua >= 6:
        estado_agua = "Óptimo"
        score += 25
    else:
        estado_agua = "Bajo"

    if sueno >= 7:
        estado_sueno = "Óptimo"
        score += 25
    else:
        estado_sueno = "Insuficiente"

    if ejercicio >= 30:
        estado_ejercicio = "Adecuado"
        score += 25
    else:
        estado_ejercicio = "Bajo"

    if estres <= 4:
        estado_estres = "Controlado"
        score += 25
    else:
        estado_estres = "Elevado"

    # DATAFRAME (nivel pro)
    df = pd.DataFrame({
        "Variable": ["Agua", "Sueño", "Ejercicio", "Estrés"],
        "Estado": [estado_agua, estado_sueno, estado_ejercicio, estado_estres],
        "Valor": [agua, sueno, ejercicio, estres]
    })

    # RESULTADOS
    st.header("📊 Resultados del Usuario")

    st.write(f"**Usuario:** {nombre}")
    st.write(f"**Edad:** {edad}")

    st.dataframe(df, use_container_width=True)

    # SCORE GENERAL
    st.markdown("---")
    st.subheader("🎯 Índice de Bienestar")

    st.metric(label="Puntuación total", value=f"{score}/100")

    # INTERPRETACIÓN
    if score >= 75:
        st.success("Estado general: ÓPTIMO")
    elif score >= 50:
        st.warning("Estado general: MODERADO")
    else:
        st.error("Estado general: BAJO")

    # GRÁFICA
    st.markdown("---")
    st.subheader("📈 Visualización")

    chart_data = pd.DataFrame({
        "Valores": [agua, sueno, ejercicio, estres]
    }, index=["Agua", "Sueño", "Ejercicio", "Estrés"])

    st.bar_chart(chart_data)

    # RECOMENDACIONES
    st.markdown("---")
    st.subheader("📌 Recomendaciones")

    if agua < 6:
        st.write("- Incrementar consumo de agua")
    if sueno < 7:
        st.write("- Mejorar hábitos de sueño")
    if ejercicio < 30:
        st.write("- Incrementar actividad física")
    if estres > 4:
        st.write("- Implementar técnicas de manejo de estrés")

    if score >= 75:
        st.write("✅ Mantener hábitos actuales")
