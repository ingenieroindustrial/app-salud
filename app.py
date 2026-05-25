import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# CONFIGURACIÓN
st.set_page_config(page_title="Health Analytics Dashboard", layout="wide")

# 🎨 ESTILO PROFESIONAL CLARO (CORREGIDO)
st.markdown("""
<style>

/* FONDO GENERAL */
.stApp {
    background-color: #f4f6fb;
}

/* TEXTO GENERAL */
html, body, [class*="css"] {
    color: #111827 !important;
    font-family: 'Segoe UI', sans-serif;
}

/* TITULOS */
h1 {
    color: #111827 !important;
    font-weight: 700 !important;
}
h2, h3 {
    color: #1f2937 !important;
    font-weight: 600 !important;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}

/* INPUTS */
input, .stNumberInput {
    background-color: #ffffff !important;
}

/* BOTÓN */
.stButton > button {
    background-color: #6366f1;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 16px;
}
.stButton > button:hover {
    background-color: #4f46e5;
}

/* TARJETAS KPI */
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# HEADER
st.title("📊 Health Analytics Dashboard")
st.write("Sistema de análisis de bienestar personal")

st.markdown("---")

# SIDEBAR
st.sidebar.header("👤 Perfil de usuario")
nombre = st.sidebar.text_input("Nombre")
edad = st.sidebar.number_input("Edad", 0, 100, 25)

st.sidebar.markdown("---")
st.sidebar.caption("Ingrese datos para generar análisis")

# INPUTS
st.subheader("📥 Datos de entrada")

col1, col2 = st.columns(2)

with col1:
    agua = st.number_input("💧 Agua (vasos/día)", 0, 10, 5)
    sueno = st.number_input("💤 Sueño (horas)", 0, 12, 7)

with col2:
    ejercicio = st.number_input("🏃 Ejercicio (minutos/día)", 0, 120, 30)
    estres = st.slider("🧘 Nivel de estrés", 1, 10, 5)

st.markdown("---")

# BOTÓN
if st.button("📈 Generar análisis"):

    # SCORE
    score = 0
    score += 25 if agua >= 6 else 0
    score += 25 if sueno >= 7 else 0
    score += 25 if ejercicio >= 30 else 0
    score += 25 if estres <= 4 else 0

    # DATAFRAME
    df = pd.DataFrame({
        "Variable": ["Agua", "Sueño", "Ejercicio", "Estrés"],
        "Valor": [agua, sueno, ejercicio, estres]
    })

    st.subheader("📊 Dashboard de resultados")

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💧 Agua", agua)
    k2.metric("💤 Sueño", sueno)
    k3.metric("🏃 Ejercicio", ejercicio)
    k4.metric("🧘 Estrés", estres)

    st.markdown("---")

    # SCORE
    st.subheader("🎯 Índice de bienestar")
    st.metric("Score total", f"{score}/100")

    if score >= 75:
        st.success("Estado general: Óptimo")
    elif score >= 50:
        st.warning("Estado general: Moderado")
    else:
        st.error("Estado general: Bajo")

    st.markdown("---")

    # GRÁFICAS
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Variables de salud")

        fig, ax = plt.subplots()
        ax.bar(df["Variable"], df["Valor"], color="#6366f1")
        ax.set_facecolor("#ffffff")
        fig.patch.set_facecolor('#ffffff')
        st.pyplot(fig)

    with col2:
        st.subheader("📈 Distribución")

        fig2, ax2 = plt.subplots()
        ax2.pie(
            df["Valor"],
            labels=df["Variable"],
            autopct='%1.1f%%',
            colors=["#6366f1", "#60a5fa", "#34d399", "#fbbf24"]
        )
        fig2.patch.set_facecolor('#ffffff')
        st.pyplot(fig2)

    st.markdown("---")

    # TABLA
    st.subheader("📋 Datos procesados")
    st.dataframe(df, use_container_width=True)

    # INSIGHTS
    st.markdown("---")
    st.subheader("🧠 Insights")

    if agua < 6:
        st.write("• Consumo de agua por debajo del nivel recomendado")
    if sueno < 7:
        st.write("• Déficit de sueño detectado")
    if ejercicio < 30:
        st.write("• Nivel bajo de actividad física")
    if estres > 4:
        st.write("• Nivel de estrés elevado")

    if score >= 75:
        st.write("✅ Perfil de salud equilibrado")
