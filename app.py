import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG
st.set_page_config(page_title="Health Analytics Dashboard", layout="wide")

# 🎨 ESTILO PRO SaaS
st.markdown("""
<style>

/* FONDO */
.stApp {
    background-color: #f8fafc;
}

/* TEXTO */
html, body {
    font-family: 'Segoe UI', sans-serif;
    color: #111827;
}

/* TITULOS */
h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #111827;
}
h2, h3 {
    color: #1f2937;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* TARJETAS */
.card {
    background-color: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* KPI */
div[data-testid="metric-container"] {
    background: white;
    border-radius: 14px;
    padding: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

/* BOTÓN */
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

/</style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.header("👤 Perfil de usuario")
nombre = st.sidebar.text_input("Nombre")
edad = st.sidebar.number_input("Edad", 0, 100, 25)

st.sidebar.markdown("---")
st.sidebar.caption("Ingrese datos para generar análisis")

# HEADER
st.markdown('<div class="card">', unsafe_allow_html=True)
st.title("📊 Health Analytics Dashboard")
st.write("Sistema profesional de análisis de bienestar")
st.markdown('</div>', unsafe_allow_html=True)

# INPUTS
st.markdown('<div class="card">', unsafe_allow_html=True)

st.subheader("📥 Datos de entrada")

col1, col2 = st.columns(2)

with col1:
    agua = st.number_input("💧 Agua (vasos/día)", 0, 10, 5)
    sueno = st.number_input("💤 Sueño (horas)", 0, 12, 7)

with col2:
    ejercicio = st.number_input("🏃 Ejercicio (minutos/día)", 0, 120, 30)
    estres = st.slider("🧘 Nivel de estrés", 1, 10, 5)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# BOTÓN
if st.button("📈 Generar análisis"):

    score = 0
    score += 25 if agua >= 6 else 0
    score += 25 if sueno >= 7 else 0
    score += 25 if ejercicio >= 30 else 0
    score += 25 if estres <= 4 else 0

    df = pd.DataFrame({
        "Variable": ["Agua", "Sueño", "Ejercicio", "Estrés"],
        "Valor": [agua, sueno, ejercicio, estres]
    })

    # DASHBOARD
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📊 Dashboard de resultados")

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Agua", agua)
    k2.metric("Sueño", sueno)
    k3.metric("Ejercicio", ejercicio)
    k4.metric("Estrés", estres)

    st.markdown("---")

    # SCORE
    st.subheader("🎯 Índice de bienestar")
    st.metric("Score total", f"{score}/100")

    if score >= 75:
        st.success("Estado: Óptimo")
    elif score >= 50:
        st.warning("Estado: Moderado")
    else:
        st.error("Estado: Bajo")

    st.markdown("---")

    # GRÁFICAS
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Variables")

        fig, ax = plt.subplots()
        ax.bar(df["Variable"], df["Valor"], color="#6366f1")
        ax.set_facecolor("#ffffff")
        fig.patch.set_facecolor("#ffffff")
        st.pyplot(fig)

    with col2:
        st.subheader("📈 Distribución")

        fig2, ax2 = plt.subplots()
        ax2.pie(df["Valor"],
                labels=df["Variable"],
                autopct='%1.1f%%',
                colors=["#6366f1", "#60a5fa", "#34d399", "#fbbf24"])
        fig2.patch.set_facecolor("#ffffff")
        st.pyplot(fig2)

    st.markdown("---")

    # TABLA
    st.subheader("📋 Datos")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # INSIGHTS
    st.subheader("🧠 Insights")

    if agua < 6:
        st.write("• Bajo consumo de agua")
    if sueno < 7:
        st.write("• Déficit de sueño")
    if ejercicio < 30:
        st.write("• Baja actividad física")
    if estres > 4:
        st.write("• Nivel alto de estrés")
    if score >= 75:
        st.write("✅ Perfil saludable")

    st.markdown('</div>', unsafe_allow_html=True)
