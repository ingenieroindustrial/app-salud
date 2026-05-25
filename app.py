import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG
st.set_page_config(page_title="Health Analytics Dashboard", layout="wide")

# 🎨 ESTILO PASTEL PRO
st.markdown("""
<style>
body {
    background-color: #f7f7fb;
}
h1, h2, h3 {
    color: #6c5ce7;
}
[data-testid="stSidebar"] {
    background-color: #eaeafc;
}
</style>
""", unsafe_allow_html=True)

# TÍTULO
st.title("📊 Health Analytics Dashboard")
st.markdown("### Monitoreo y análisis de bienestar personal")

# SIDEBAR
st.sidebar.header("👤 Perfil")
nombre = st.sidebar.text_input("Nombre")
edad = st.sidebar.number_input("Edad", 0, 100, 25)

# INPUTS
st.header("📥 Datos de entrada")

col1, col2 = st.columns(2)

with col1:
    agua = st.slider("💧 Agua (vasos)", 0, 10, 5)
    sueno = st.slider("💤 Sueño (horas)", 0, 12, 7)

with col2:
    ejercicio = st.slider("🏃 Ejercicio (min)", 0, 120, 30)
    estres = st.slider("🧘 Estrés", 1, 10, 5)

st.markdown("---")

# BOTÓN
if st.button("📈 Ejecutar análisis"):

    # SCORING
    score = 0

    estado_agua = "Óptimo" if agua >= 6 else "Bajo"
    estado_sueno = "Óptimo" if sueno >= 7 else "Bajo"
    estado_ejercicio = "Adecuado" if ejercicio >= 30 else "Bajo"
    estado_estres = "Controlado" if estres <= 4 else "Alto"

    score += 25 if agua >= 6 else 0
    score += 25 if sueno >= 7 else 0
    score += 25 if ejercicio >= 30 else 0
    score += 25 if estres <= 4 else 0

    # DATAFRAME
    df = pd.DataFrame({
        "Variable": ["Agua", "Sueño", "Ejercicio", "Estrés"],
        "Valor": [agua, sueno, ejercicio, estres]
    })

    st.markdown("## 📊 Dashboard de resultados")

    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("💧 Agua", agua)
    kpi2.metric("💤 Sueño", sueno)
    kpi3.metric("🏃 Ejercicio", ejercicio)
    kpi4.metric("🧘 Estrés", estres)

    st.markdown("---")

    # SCORE
    st.subheader("🎯 Índice de bienestar")
    st.metric("Score total", f"{score}/100")

    # INTERPRETACIÓN
    if score >= 75:
        st.success("Estado: Óptimo")
    elif score >= 50:
        st.warning("Estado: Medio")
    else:
        st.error("Estado: Bajo")

    st.markdown("---")

    # GRÁFICAS
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Variables de salud")

        fig, ax = plt.subplots()
        ax.bar(df["Variable"], df["Valor"], color=["#a29bfe", "#81ecec", "#fab1a0", "#74b9ff"])
        ax.set_ylabel("Nivel")
        st.pyplot(fig)

    with col2:
        st.subheader("📉 Distribución")

        fig2, ax2 = plt.subplots()
        ax2.pie(df["Valor"], labels=df["Variable"], autopct='%1.1f%%',
                colors=["#a29bfe", "#81ecec", "#fab1a0", "#74b9ff"])
        st.pyplot(fig2)

    st.markdown("---")

    # TABLA
    st.subheader("📋 Datos procesados")
    st.dataframe(df, use_container_width=True)

    # INSIGHTS (esto te posiciona como analista)
    st.markdown("---")
    st.subheader("🧠 Insights")

    if agua < 6:
        st.write("🔎 Hidratación por debajo del nivel recomendado")
    if sueno < 7:
        st.write("🔎 Déficit de sueño detectado")
    if ejercicio < 30:
        st.write("🔎 Nivel bajo de actividad física")
    if estres > 4:
        st.write("🔎 Nivel de estrés elevado")

    if score >= 75:
        st.write("✅ Perfil de salud equilibrado")
