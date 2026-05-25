import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y DISEÑO
# ==========================================
st.set_page_config(page_title="Mi Salud App", layout="centered")

st.markdown("""
<style>
    .main { background-color: #f9f9f9; }
    h1 { color: #1e3a8a; }
    .stButton > button { background-color: #1e3a8a; color: white; border-radius: 20px; }
    .suggestion-box {
        background-color: #e0f2fe;
        border-left: 5px solid #0284c7;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("💙 Mi Salud App")
st.caption("Registra tus hábitos diarios y recibe un puntaje de bienestar con consejos útiles")

# ==========================================
# 2. BASE DE DATOS SQLITE
# ==========================================
DB_NAME = "salud.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT,
                    edad INTEGER,
                    creado TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS mediciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    fecha TIMESTAMP,
                    agua_vasos REAL,
                    sueno_horas REAL,
                    ejercicio_min INTEGER,
                    estres_nivel INTEGER
                )''')
    conn.commit()
    conn.close()

init_db()

def guardar_usuario(nombre, edad):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM usuarios")
    c.execute("INSERT INTO usuarios (nombre, edad, creado) VALUES (?, ?, ?)",
              (nombre, edad, datetime.now()))
    conn.commit()
    conn.close()

def obtener_usuario():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, nombre, edad FROM usuarios LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nombre": row[1], "edad": row[2]}
    return None

def guardar_medicion(usuario_id, agua, sueno, ejercicio, estres):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO mediciones 
                 (usuario_id, fecha, agua_vasos, sueno_horas, ejercicio_min, estres_nivel)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (usuario_id, datetime.now(), agua, sueno, ejercicio, estres))
    conn.commit()
    conn.close()

def cargar_mediciones(usuario_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM mediciones WHERE usuario_id = ? ORDER BY fecha", conn, params=(usuario_id,))
    conn.close()
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
    return df

# ==========================================
# 3. LÓGICA DE CÁLCULO Y SUGERENCIAS
# ==========================================
def calcular_wellness_score(agua, sueno, ejercicio, estres):
    score_agua = min(100, (agua / 8) * 100)
    score_sueno = min(100, (sueno / 8) * 100)
    score_ejercicio = min(100, (ejercicio / 30) * 100)
    score_estres = max(0, (10 - estres) / 9 * 100)
    return round((score_agua + score_sueno + score_ejercicio + score_estres) / 4, 1)

def obtener_sugerencias(ultima_medicion):
    """Genera recomendaciones simples basadas en la última medición"""
    sugerencias = []
    agua = ultima_medicion['agua_vasos']
    sueno = ultima_medicion['sueno_horas']
    ejercicio = ultima_medicion['ejercicio_min']
    estres = ultima_medicion['estres_nivel']
    
    if agua < 6:
        sugerencias.append("💧 Bebe más agua (intenta llegar a 8 vasos al día). Una buena hidratación mejora la energía y concentración.")
    elif agua >= 6 and agua < 8:
        sugerencias.append("💧 Vas bien con el agua, pero aún puedes aumentar un poco más. ¡Recuerda que 8 vasos es la meta!")
    else:
        sugerencias.append("💧 ¡Excelente hidratación! Sigue así.")
    
    if sueno < 6:
        sugerencias.append("😴 Duermes poco. Intenta dormir al menos 7 horas para que tu cuerpo se recupere.")
    elif sueno >= 6 and sueno < 8:
        sugerencias.append("😴 Tu sueño está cerca de lo recomendado. Intenta llegar a 8 horas para sentirte más descansado/a.")
    else:
        sugerencias.append("😴 ¡Buen hábito! Dormir bien es clave para la salud mental y física.")
    
    if ejercicio < 20:
        sugerencias.append("🏃 Intenta realizar al menos 30 minutos de ejercicio diario (caminar, bailar, o algún deporte).")
    elif ejercicio < 30:
        sugerencias.append("🏃 Buen nivel de actividad, pero puedes llegar a 30 minutos fácilmente. ¡Un poco más cada día!")
    else:
        sugerencias.append("🏃 ¡Fantástico! Cumples con la recomendación de ejercicio diario.")
    
    if estres > 7:
        sugerencias.append("🧘 Tu nivel de estrés es alto. Prueba respirar profundamente o dar un paseo al aire libre.")
    elif estres > 4:
        sugerencias.append("🧘 Tu estrés es moderado. Dedica 5 minutos al día para relajarte o escuchar música.")
    else:
        sugerencias.append("🧘 Manejas bien el estrés. Sigue practicando actividades que te gusten.")
    
    return sugerencias

# ==========================================
# 4. INTERFAZ DE STREAMLIT
# ==========================================
# --- Perfil del usuario ---
with st.sidebar:
    st.header("👤 Tu perfil")
    nombre = st.text_input("Nombre", value="Ana")
    edad = st.number_input("Edad", min_value=18, max_value=100, value=30)
    if st.button("Guardar perfil"):
        guardar_usuario(nombre, edad)
        st.success("Perfil guardado")

usuario = obtener_usuario()
if usuario is None:
    st.info("Completa tu perfil en la barra lateral para comenzar.")
    st.stop()

st.sidebar.success(f"Bienvenid@ {usuario['nombre']} ({usuario['edad']} años)")

# --- Formulario de registro diario ---
st.subheader("📝 Registro de hoy")
with st.form("registro"):
    col1, col2 = st.columns(2)
    with col1:
        agua = st.number_input("💧 Vasos de agua (250 ml)", 0.0, 15.0, 6.0, 0.5)
        sueno = st.number_input("😴 Horas de sueño", 0.0, 12.0, 7.5, 0.5)
    with col2:
        ejercicio = st.number_input("🏃 Minutos de ejercicio", 0, 180, 30, 5)
        estres = st.slider("🧘 Nivel de estrés (1 = mínimo, 10 = máximo)", 1, 10, 4)
    enviado = st.form_submit_button("Guardar medición")
    if enviado:
        guardar_medicion(usuario["id"], agua, sueno, ejercicio, estres)
        st.success("¡Registro guardado! ✅")
        st.balloons()

# --- Mostrar historial y gráficos ---
df = cargar_mediciones(usuario["id"])
if df.empty:
    st.info("Aún no hay registros. Usa el formulario para agregar tu primera medición.")
else:
    # Calcular score
    df["score"] = df.apply(lambda row: calcular_wellness_score(
        row["agua_vasos"], row["sueno_horas"], row["ejercicio_min"], row["estres_nivel"]), axis=1)
    
    ultimo = df.iloc[-1]
    
    st.subheader("📊 Tu estado actual")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏆 Puntaje de bienestar de hoy", f"{ultimo['score']}/100")
    with col2:
        st.metric("📅 Última medición", ultimo['fecha'].strftime("%d/%m/%Y"))
    
    # Mostrar sugerencias personalizadas
    sugerencias = obtener_sugerencias(ultimo)
    st.markdown("### 💡 Consejos para mejorar")
    for sug in sugerencias:
        st.markdown(f'<div class="suggestion-box">{sug}</div>', unsafe_allow_html=True)
    
    # Gráfico de evolución del score
    fig = px.line(df, x="fecha", y="score", markers=True,
                  title="Evolución de tu bienestar",
                  labels={"fecha": "Fecha", "score": "Puntaje (0-100)"})
    fig.update_layout(template="simple_white", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de últimos registros
    with st.expander("Ver historial completo"):
        tabla = df[["fecha", "agua_vasos", "sueno_horas", "ejercicio_min", "estres_nivel", "score"]].rename(columns={
            "fecha": "Fecha", "agua_vasos": "Agua (vasos)", "sueno_horas": "Sueño (horas)",
            "ejercicio_min": "Ejercicio (min)", "estres_nivel": "Estrés", "score": "Score"
        })
        st.dataframe(tabla.sort_values("Fecha", ascending=False), use_container_width=True)

# --- Generar informe PDF (incluye sugerencias) ---
st.subheader("📄 Descargar informe PDF")
if st.button("Generar informe con los últimos datos"):
    ultimos = df.tail(5).copy()
    ultimos["fecha_str"] = ultimos["fecha"].dt.strftime("%d/%m/%Y")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1e3a8a'))
    normal_style = styles['Normal']
    
    story = []
    story.append(Paragraph("Informe de Salud Personal", titulo_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"<b>Nombre:</b> {usuario['nombre']}", normal_style))
    story.append(Paragraph(f"<b>Edad:</b> {usuario['edad']} años", normal_style))
    story.append(Paragraph(f"<b>Fecha del informe:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 0.8*cm))
    
    # Último registro destacado
    ultimo_reg = df.iloc[-1]
    story.append(Paragraph("<b>Último registro</b>", styles['Heading2']))
    datos_ultimo = [
        ["Agua", f"{ultimo_reg['agua_vasos']} vasos"],
        ["Sueño", f"{ultimo_reg['sueno_horas']} horas"],
        ["Ejercicio", f"{ultimo_reg['ejercicio_min']} min"],
        ["Estrés", f"{ultimo_reg['estres_nivel']}/10"],
        ["Puntaje de bienestar", f"{ultimo_reg['score']}/100"]
    ]
    tabla_ult = Table(datos_ultimo, colWidths=[4*cm, 6*cm])
    tabla_ult.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(tabla_ult)
    story.append(Spacer(1, 0.5*cm))
    
    # Sugerencias personalizadas (iguales a las de la app)
    story.append(Paragraph("<b>Recomendaciones según tu último registro</b>", styles['Heading2']))
    for sug in sugerencias:
        # Limpiar emojis para reportlab (funciona pero los muestra como texto)
        story.append(Paragraph(sug, normal_style))
        story.append(Spacer(1, 0.2*cm))
    
    # Resumen simple
    story.append(Paragraph("<b>Resumen de los últimos días</b>", styles['Heading2']))
    promedio_score = ultimos["score"].mean()
    story.append(Paragraph(f"Promedio de bienestar: {promedio_score:.1f}/100", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    
    st.download_button(
        label="📥 Descargar informe PDF",
        data=buffer,
        file_name=f"informe_salud_{usuario['nombre']}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
    st.success("Informe generado correctamente")
