import streamlit as st
import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="Para alguien especial 💖", layout="centered")

# ESTILO PERSONALIZADO (DISEÑO)
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1 {
    text-align: center;
    color: #ff4b91;
}
</style>
""", unsafe_allow_html=True)

# TITULO
st.title("🌸 CuidaTuEnergía 🌸")
st.write("✨ Una app pensada para tu bienestar ✨")

# INPUT
nombre = st.text_input("¿Cómo te llamas?")

# SLIDERS
agua = st.slider("💧 Vasos de agua al día", 0, 10, 5)
sueno = st.slider("💤 Horas de sueño", 0, 12, 7)
ejercicio = st.slider("🏃 Minutos de ejercicio", 0, 120, 30)
estres = st.slider("🧘 Nivel de estrés", 1, 10, 5)

# BOTÓN
if st.button("💖 Evaluar mi salud"):
    
    st.subheader(f"Resultados para {nombre}")
    
    puntos = 0

    if agua >= 6:
        st.success("✅ Buena hidratación")
        puntos += 1
    else:
        st.warning("⚠️ Toma más agua")

    if sueno >= 7:
        st.success("✅ Buen descanso")
        puntos += 1
    else:
        st.warning("⚠️ Trata de dormir más")

    if ejercicio >= 30:
        st.success("✅ Buen nivel de actividad")
        puntos += 1
    else:
        st.warning("⚠️ Muévete un poco más")

    if estres <= 4:
        st.success("✅ Nivel de estrés bajo")
        puntos += 1
    else:
        st.warning("⚠️ Date un momento para relajarte")

    # SCORE FINAL
    st.markdown("---")
    st.subheader("🌟 Resultado general")

    if puntos == 4:
        st.success("💯 ¡Estás increíble!")
    elif puntos >= 2:
        st.info("😊 Vas por buen camino, sigue así")
    else:
        st.error("💤 ¡Es momento de cuidarte más!")

    # MENSAJE PRO
    st.markdown("---")
    fecha = datetime.date.today()

    if nombre != "":
        st.info(f"💌 {nombre}, recuerda cuidarte… porque eres alguien muy especial ✨")

        st.success(f"""
✨ Esta app fue hecha especialmente para ti 💖  
📅 Fecha: {fecha}
""")
``
