import streamlit as st

st.set_page_config(page_title="Para alguien especial 💖")

st.title("🌸 CuidaTuEnergia 🌸")
st.write("Una app hecha para tu bienestar ✨")

nombre = st.text_input("¿Como te llamas?")

agua = st.slider("💧 Vasos de agua al dia", 0, 10, 5)
sueno = st.slider("💤 Horas de sueño", 0, 12, 7)
ejercicio = st.slider("🏃 Minutos de ejercicio", 0, 120, 30)
estres = st.slider("🧘 Nivel de estres", 1, 10, 5)

if st.button("Evaluar mi salud"):
    st.subheader(f"Resultados para {nombre}")

    if agua >= 6:
        st.success("✅ Buena hidratacion")
    else:
        st.warning("⚠️ Toma mas agua")

    if sueno >= 7:
        st.success("✅ Buen descanso")
    else:
        st.warning("⚠️ Trata de dormir mas")

    if ejercicio >= 30:
        st.success("✅ Buen nivel de actividad")
    else:
        st.warning("⚠️ Muevete un poco mas")

    if estres <= 4:
        st.success("✅ Poco estres")
    else:
        st.warning("⚠️ Relajate un poco")

    st.markdown("---")
    st.info("💌 Cuidate mucho… porque haces el mundo mas bonito ✨")
