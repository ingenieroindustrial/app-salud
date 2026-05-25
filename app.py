import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3
from datetime import datetime
import hashlib
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import warnings
warnings.filterwarnings('ignore')

# ========================= CONFIGURACIÓN =========================
st.set_page_config(page_title="HealthTrack Pro", page_icon="💙", layout="wide")

# CSS profesional minimalista
st.markdown("""
<style>
    /* Fuente y fondo */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    
    /* Tarjetas */
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
    }
    
    /* Métricas */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        border: 1px solid #eef2f6;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1e293b; }
    .metric-label { font-size: 0.85rem; color: #64748b; }
    
    /* Botón principal */
    .stButton > button {
        background: #0f172a;
        color: white;
        border-radius: 40px;
        padding: 0.5rem 1.2rem;
        font-weight: 500;
        border: none;
        transition: 0.2s;
    }
    .stButton > button:hover { background: #1e293b; transform: scale(1.02); }
    
    hr { margin: 1rem 0; border-color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ========================= BASE DE DATOS =========================
DB_NAME = "health_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    created_at TIMESTAMP)''')
    # Mediciones
    c.execute('''CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date TIMESTAMP,
                    water_glasses REAL,
                    sleep_hours REAL,
                    exercise_mins INTEGER,
                    stress_level INTEGER,
                    weight_kg REAL,
                    steps INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    # Objetivos personalizados
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
                    user_id TEXT PRIMARY KEY,
                    goal_water REAL,
                    goal_sleep REAL,
                    goal_exercise INTEGER,
                    goal_stress INTEGER,
                    goal_weight REAL,
                    goal_steps INTEGER,
                    updated_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def get_user_id(name, age):
    return hashlib.md5(f"{name}_{age}".encode()).hexdigest()[:8]

def save_measurement(user_id, data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO measurements 
                 (user_id, date, water_glasses, sleep_hours, exercise_mins, stress_level, weight_kg, steps)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, datetime.now(), data['water'], data['sleep'], data['exercise'],
               data['stress'], data['weight'], data['steps']))
    conn.commit()
    conn.close()

def load_measurements(user_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM measurements WHERE user_id = ? ORDER BY date", conn, params=(user_id,))
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

def get_goals(user_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM goals WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    if df.empty:
        return {'water': 8.0, 'sleep': 8.0, 'exercise': 30, 'stress': 3, 'weight': 70.0, 'steps': 8000}
    row = df.iloc[0]
    return {'water': float(row['goal_water']), 'sleep': float(row['goal_sleep']),
            'exercise': int(row['goal_exercise']), 'stress': int(row['goal_stress']),
            'weight': float(row['goal_weight']), 'steps': int(row['goal_steps'])}

def save_goals(user_id, goals_dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO goals 
                 (user_id, goal_water, goal_sleep, goal_exercise, goal_stress, goal_weight, goal_steps, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, goals_dict['water'], goals_dict['sleep'], goals_dict['exercise'],
               goals_dict['stress'], goals_dict['weight'], goals_dict['steps'], datetime.now()))
    conn.commit()
    conn.close()

# ========================= LÓGICA DE NEGOCIO =========================
def calculate_wellness_score(row, goals):
    """Score 0-100 basado en comparación con objetivos"""
    score = 0.0
    # Agua
    water_score = min(100, (row['water_glasses'] / goals['water']) * 100)
    # Sueño (ideal 7-9h, óptimo 8)
    sleep_score = 100 - min(50, abs(row['sleep_hours'] - 8) * 12.5)
    # Ejercicio
    exercise_score = min(100, (row['exercise_mins'] / goals['exercise']) * 100)
    # Estrés (a menor estrés mejor)
    stress_score = max(0, 100 - (row['stress_level'] - 1) * 12.5)
    # Peso (cercanía al objetivo)
    weight_diff = abs(row['weight_kg'] - goals['weight']) / goals['weight']
    weight_score = max(0, 100 - weight_diff * 200)
    # Pasos
    steps_score = min(100, (row['steps'] / goals['steps']) * 100)
    
    # Pesos relativos
    weights = {'water': 0.10, 'sleep': 0.20, 'exercise': 0.25, 'stress': 0.20, 'weight': 0.10, 'steps': 0.15}
    score = (water_score * weights['water'] +
             sleep_score * weights['sleep'] +
             exercise_score * weights['exercise'] +
             stress_score * weights['stress'] +
             weight_score * weights['weight'] +
             steps_score * weights['steps'])
    return round(score, 1)

def get_simple_stats(df, var):
    """Media y tendencia (pendiente)"""
    if df.empty or len(df) < 2:
        return {'mean': None, 'trend': None}
    values = df[var].values
    mean = np.mean(values)
    # Tendencia lineal con numpy
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    return {'mean': round(mean, 2), 'trend': round(slope, 3)}

def generate_insights(last_row, goals):
    """Recomendaciones simples y claras"""
    insights = []
    if last_row['water_glasses'] < goals['water']:
        insights.append(f"💧 Bebe más agua: {goals['water']} vasos al día recomendados.")
    if last_row['sleep_hours'] < 7 or last_row['sleep_hours'] > 9:
        insights.append("😴 Intenta dormir entre 7 y 9 horas cada noche.")
    if last_row['exercise_mins'] < goals['exercise']:
        insights.append(f"🏃 Aumenta el ejercicio a {goals['exercise']} minutos diarios.")
    if last_row['stress_level'] > 5:
        insights.append("🧘 Practica respiración o meditación para reducir el estrés.")
    if last_row['steps'] < goals['steps']:
        insights.append(f"👣 Camina al menos {goals['steps']} pasos al día.")
    if abs(last_row['weight_kg'] - goals['weight']) / goals['weight'] > 0.05:
        insights.append("⚖️ Revisa tu alimentación para acercarte a tu peso objetivo.")
    if not insights:
        insights.append("✅ ¡Excelente! Sigue manteniendo estos hábitos saludables.")
    return insights

# ========================= GENERACIÓN DE PDF =========================
def generate_pdf_report(user_name, age, gender, last_row, goals, score, insights):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0f172a'), spaceAfter=12)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceAfter=8)
    normal_style = styles['Normal']
    
    story = []
    
    # Título
    story.append(Paragraph("Informe de Salud - HealthTrack Pro", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Datos del usuario
    story.append(Paragraph(f"<b>Nombre:</b> {user_name}", normal_style))
    story.append(Paragraph(f"<b>Edad:</b> {age} años", normal_style))
    story.append(Paragraph(f"<b>Sexo:</b> {gender}", normal_style))
    story.append(Paragraph(f"<b>Fecha del informe:</b> {datetime.now().strftime('%d/%m/%Y')}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Última medición
    story.append(Paragraph("Última medición", heading_style))
    data = [
        ["Agua", f"{last_row['water_glasses']} / {goals['water']} vasos"],
        ["Sueño", f"{last_row['sleep_hours']} / {goals['sleep']} horas"],
        ["Ejercicio", f"{last_row['exercise_mins']} / {goals['exercise']} min"],
        ["Estrés", f"{last_row['stress_level']} / 10"],
        ["Peso", f"{last_row['weight_kg']} / {goals['weight']} kg"],
        ["Pasos", f"{last_row['steps']} / {goals['steps']} pasos"]
    ]
    t = Table(data, colWidths=[4*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    
    # Score de bienestar
    story.append(Paragraph(f"<b>Índice de Bienestar:</b> {score}/100", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Insights
    story.append(Paragraph("Recomendaciones personalizadas", heading_style))
    for ins in insights:
        story.append(Paragraph(f"• {ins}", normal_style))
        story.append(Spacer(1, 0.2*cm))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ========================= UI PRINCIPAL =========================
def main():
    # Sidebar: Perfil y objetivos
    with st.sidebar:
        st.markdown("### 🩺 Perfil Clínico")
        name = st.text_input("Nombre completo", value="Paciente Demo")
        age = st.number_input("Edad (años)", 18, 110, 45, step=1)
        gender = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])
        user_id = get_user_id(name, age)
        st.caption(f"ID: {user_id}")
        
        st.markdown("---")
        st.markdown("### 🎯 Objetivos de salud")
        goals = get_goals(user_id)
        col1, col2 = st.columns(2)
        with col1:
            goal_water = st.number_input("💧 Agua (vasos)", 4.0, 12.0, float(goals['water']), 0.5)
            goal_sleep = st.number_input("😴 Sueño (horas)", 6.0, 10.0, float(goals['sleep']), 0.5)
            goal_exercise = st.number_input("🏃 Ejercicio (min)", 0, 120, int(goals['exercise']), 5)
        with col2:
            goal_stress = st.slider("🧘 Estrés objetivo (1-10)", 1, 10, int(goals['stress']))
            goal_weight = st.number_input("⚖️ Peso objetivo (kg)", 40.0, 150.0, float(goals['weight']), 0.5)
            goal_steps = st.number_input("👣 Pasos objetivo", 2000, 15000, int(goals['steps']), 500)
        new_goals = {'water': goal_water, 'sleep': goal_sleep, 'exercise': goal_exercise,
                     'stress': goal_stress, 'weight': goal_weight, 'steps': goal_steps}
        if st.button("Guardar objetivos", use_container_width=True):
            save_goals(user_id, new_goals)
            st.success("Objetivos actualizados")
            st.rerun()
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 1rem; border-radius: 24px; margin-bottom: 1.5rem;">
        <h1 style="color: white; margin: 0; font-size: 1.8rem;">📊 HealthTrack Pro</h1>
        <p style="color: #cbd5e1; margin: 0;">Monitoriza tu salud con datos y objetivos personalizados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab_reg, tab_hist, tab_pdf = st.tabs(["📝 Nuevo registro", "📈 Historial", "📄 Informe PDF"])
    
    # --- TAB 1: Registro ---
    with tab_reg:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Registra tus parámetros de hoy")
        col1, col2, col3 = st.columns(3)
        with col1:
            water = st.number_input("💧 Vasos de agua (250ml)", 0.0, 15.0, 6.0, 0.5)
            sleep = st.number_input("😴 Horas de sueño", 0.0, 12.0, 7.5, 0.5)
            exercise = st.number_input("🏃 Minutos de ejercicio", 0, 180, 30, 5)
        with col2:
            stress = st.slider("🧘 Nivel de estrés (1=mínimo, 10=máximo)", 1, 10, 4)
            weight = st.number_input("⚖️ Peso (kg)", 30.0, 200.0, 72.5, 0.5)
            steps = st.number_input("👣 Número de pasos", 0, 30000, 7000, 500)
        with col3:
            st.markdown("##### ")
            st.caption("Completa todos los campos")
        
        if st.button("Guardar medición", use_container_width=True):
            data = {'water': water, 'sleep': sleep, 'exercise': exercise, 'stress': stress,
                    'weight': weight, 'steps': steps}
            save_measurement(user_id, data)
            st.success("✅ Datos guardados correctamente")
            st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar última medición y score
        df = load_measurements(user_id)
        if not df.empty:
            last = df.iloc[-1]
            score = calculate_wellness_score(last, goals)
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Último índice de bienestar", f"{score}/100")
            with col_b:
                st.metric("Fecha última medición", last['date'].strftime("%d/%m/%Y"))
    
    # --- TAB 2: Historial ---
    with tab_hist:
        df = load_measurements(user_id)
        if df.empty:
            st.info("Aún no hay datos. Registra tu primera medición.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            # Selector de variable
            var_options = {
                'water_glasses': 'Agua (vasos)',
                'sleep_hours': 'Sueño (horas)',
                'exercise_mins': 'Ejercicio (min)',
                'stress_level': 'Estrés (1-10)',
                'weight_kg': 'Peso (kg)',
                'steps': 'Pasos'
            }
            selected = st.selectbox("Selecciona variable a visualizar", list(var_options.keys()), format_func=lambda x: var_options[x])
            
            # Gráfico de evolución
            fig = px.line(df, x='date', y=selected, markers=True, title=f"Evolución de {var_options[selected]}",
                          labels={'date': 'Fecha', selected: var_options[selected]})
            fig.update_layout(template='plotly_white', height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas simples
            stats = get_simple_stats(df, selected)
            col1, col2 = st.columns(2)
            col1.metric("Media", stats['mean'] if stats['mean'] is not None else "—")
            col2.metric("Tendencia (pendiente)", f"{stats['trend']:.2f}" if stats['trend'] is not None else "—")
            
            st.markdown("---")
            st.subheader("Histórico de mediciones")
            st.dataframe(df.sort_values('date', ascending=False).style.format({
                'water_glasses': '{:.1f}', 'sleep_hours': '{:.1f}', 'exercise_mins': '{:.0f}',
                'weight_kg': '{:.1f}', 'steps': '{:.0f}'
            }), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # --- TAB 3: Informe PDF ---
    with tab_pdf:
        df = load_measurements(user_id)
        if df.empty:
            st.warning("No hay datos suficientes para generar un informe. Registra al menos una medición.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Generar informe personalizado en PDF")
            last = df.iloc[-1]
            score = calculate_wellness_score(last, goals)
            insights = generate_insights(last, goals)
            
            # Previsualización de lo que irá en el PDF
            st.markdown("**Resumen del informe:**")
            st.write(f"- **Puntuación de bienestar:** {score}/100")
            st.write(f"- **Última medición:** {last['date'].strftime('%d/%m/%Y')}")
            st.write("- **Recomendaciones principales:**")
            for ins in insights[:3]:
                st.write(f"  • {ins}")
            
            if st.button("📥 Descargar informe PDF", use_container_width=True):
                pdf_buffer = generate_pdf_report(name, age, gender, last, goals, score, insights)
                st.download_button(
                    label="✅ Haz clic para descargar el PDF",
                    data=pdf_buffer,
                    file_name=f"informe_salud_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
