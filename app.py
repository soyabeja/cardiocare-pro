import streamlit as st
import pandas as pd
import datetime
import json
import base64

# Configure Streamlit page layout and theme
st.set_page_config(
    page_title="CardioCare Pro - Control Cardiovascular Inteligente",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 8px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    @keyframes pulse-subtle {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    .heart-pulse {
        animation: pulse-subtle 1.8s infinite ease-in-out;
        display: inline-block;
    }
    
    /* Card styling */
    .card-container {
        background: white;
        padding: 1.25rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    .badge-purple {
        background-color: #f3e8ff;
        color: #6b21a8;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

if "patient_name" not in st.session_state:
    st.session_state.patient_name = "Juan Pérez"
if "patient_id" not in st.session_state:
    st.session_state.patient_id = "108524190"
if "patient_blood" not in st.session_state:
    st.session_state.patient_blood = "O+"
if "patient_phone" not in st.session_state:
    st.session_state.patient_phone = "+34 600 000 000"

if "appointment_doctor" not in st.session_state:
    st.session_state.appointment_doctor = "Dr. Carlos Rodríguez (Cardiólogo)"
if "appointment_datetime" not in st.session_state:
    st.session_state.appointment_datetime = datetime.datetime(2026, 9, 25, 10, 30)
if "appointment_location" not in st.session_state:
    st.session_state.appointment_location = "Clínica de Especialidades"
if "appointment_alarm" not in st.session_state:
    st.session_state.appointment_alarm = True

if "condition" not in st.session_state:
    st.session_state.condition = "HIPERTENSION ESENCIAL (PRIMARIA)"

if "alarms" not in st.session_state:
    st.session_state.alarms = [
        {"id": 1, "title": "Toma de Enalapril 10mg", "time": "08:00", "days": "Diario", "status": True, "category": "Medicamento"},
        {"id": 2, "title": "Medición Presión Matutina", "time": "09:00", "days": "Diario", "status": True, "category": "Control"},
        {"id": 3, "title": "Toma de Aspirina Protekt 100mg", "time": "14:00", "days": "Diario", "status": False, "category": "Medicamento"},
        {"id": 4, "title": "Caminata Cardiovascular (30 min)", "time": "18:00", "days": "Lunes a Viernes", "status": False, "category": "Ejercicio"},
        {"id": 5, "title": "Toma de Bisoprolol 5mg", "time": "21:00", "days": "Diario", "status": False, "category": "Medicamento"}
    ]

if "medications" not in st.session_state:
    st.session_state.medications = [
        {"id": 1, "name": "Enalapril", "dose": "10 mg", "freq": "Cada 12 horas", "stock": 28, "instructions": "Tomar con o sin alimentos"},
        {"id": 2, "name": "Aspirina Protekt", "dose": "100 mg", "freq": "Cada 24 horas", "stock": 45, "instructions": "Tomar después del almuerzo"},
        {"id": 3, "name": "Bisoprolol", "dose": "5 mg", "freq": "Cada 24 horas", "stock": 14, "instructions": "Tomar por la noche con agua"}
    ]

if "vitals" not in st.session_state:
    st.session_state.vitals = [
        {"datetime": "2026-09-30 08:30", "systolic": 124, "diastolic": 82, "bpm": 74, "status": "Normal Alto"},
        {"datetime": "2026-09-29 09:15", "systolic": 118, "diastolic": 78, "bpm": 70, "status": "Óptima"},
        {"datetime": "2026-09-28 08:00", "systolic": 130, "diastolic": 85, "bpm": 76, "status": "Hipertensión Grado 1"},
        {"datetime": "2026-09-27 19:40", "systolic": 122, "diastolic": 80, "bpm": 72, "status": "Normal"}
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy tu asistente médico virtual para la salud cardiovascular. Estoy configurado para tu condición actual (**HIPERTENSION ESENCIAL**). ¿En qué puedo orientarte hoy sobre tu plan, dieta o síntomas?"}
    ]

def evaluate_bp(sys, dia):
    if sys < 120 and dia < 80:
        return "Óptima / Normal", "green"
    elif sys < 130 and dia < 85:
        return "Normal", "emerald"
    elif sys <= 139 or dia <= 89:
        return "Hipertensión Grado 1", "amber"
    elif sys <= 159 or dia <= 99:
        return "Hipertensión Grado 2", "orange"
    else:
        return "Hipertensión Grado 3 (Crisis)", "red"

def calculate_completion():
    if not st.session_state.alarms:
        return 0
    completed = sum(1 for a in st.session_state.alarms if a["status"])
    return int((completed / len(st.session_state.alarms)) * 100)

st.markdown("""
<div style="background: linear-gradient(to right, #581c87, #4c1d95, #312e81); padding: 1rem 1.5rem; border-radius: 1rem; color: white; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="background: rgba(255,255,255,0.1); padding: 0.6rem; border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.2);">
            <span style="font-size: 1.5rem;" class="heart-pulse">❤️</span>
        </div>
        <div>
            <h1 style="font-size: 1.25rem; font-weight: 900; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                CardioCare <span style="font-size: 0.65rem; background: rgba(236, 72, 153, 0.3); padding: 0.1rem 0.5rem; border-radius: 9999px; border: 1px solid rgba(244, 114, 182, 0.4);">PRO</span>
            </h1>
            <p style="font-size: 0.75rem; color: #e9d5ff; margin: 0;">Asistente & Control Cardiovascular Inteligente</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🪪 Perfil del Paciente")
    with st.form("patient_form"):
        st.session_state.patient_name = st.text_input("Nombre Completo", value=st.session_state.patient_name)
        st.session_state.patient_id = st.text_input("ID / Identificación", value=st.session_state.patient_id)
        st.session_state.patient_blood = st.selectbox("Tipo de Sangre", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], index=["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"].index(st.session_state.patient_blood))
        st.session_state.patient_phone = st.text_input("Teléfono de Contacto", value=st.session_state.patient_phone)
        if st.form_submit_button("Actualizar Paciente", use_container_width=True):
            st.success("¡Datos del paciente actualizados!")

    st.markdown("---")
    st.markdown("### 🏥 Próxima Cita Médica")
    with st.form("appointment_form"):
        st.session_state.appointment_doctor = st.text_input("Médico / Especialidad", value=st.session_state.appointment_doctor)
        default_dt = st.session_state.appointment_datetime
        date_val = st.date_input("Fecha", value=default_dt.date())
        time_val = st.time_input("Hora", value=default_dt.time())
        st.session_state.appointment_datetime = datetime.datetime.combine(date_val, time_val)
        st.session_state.appointment_location = st.text_input("Clínica / Ubicación", value=st.session_state.appointment_location)
        st.session_state.appointment_alarm = st.checkbox("Activar Alarma Recordatorio", value=st.session_state.appointment_alarm)
        if st.form_submit_button("Guardar Cita", use_container_width=True):
            st.success("¡Cita y alarma actualizadas!")

    st.markdown("---")
    st.markdown("### 🚨 Botón de Emergencia S.O.S")
    if st.button("LLAMAR URGENCIAS / FAMILIA", type="primary", use_container_width=True):
        st.error(f"⚠️ Alerta S.O.S activada para el paciente **{st.session_state.patient_name}**. Llamando al contacto de confianza: **{st.session_state.patient_phone}** y servicios médicos de emergencia.")

    st.markdown("---")
    st.markdown("### 📋 Diagnóstico Principal")
    diagnosis_options = [
        "HIPERTENSIÓN ARTERIAL GRADO 1", "HIPERTENSIÓN ARTERIAL GRADO 2", "HIPERTENSIÓN ARTERIAL GRADO 3", "HIPERTENSION ESENCIAL (PRIMARIA)",
        "HIPOTENSIÓN ARTERIAL GRADO 1", "HIPOTENSIÓN ARTERIAL GRADO 2", "HIPOTENSIÓN ARTERIAL GRADO 3",
        "ARRITMIA CARDIACA, NO ESPECIFICADA", "BRADICARDIA, NO ESPECIFICADA", "DESPOLARIZACIÓN VENTRICULAR PREMATURA", "FIBRILACION Y ALETEO AURICULAR", "FIBRILACIÓN AURICULAR PAROXÍSTICA", "PALPITACIONES", "SINDROME DEL SENO ENFERMO", "TAQUICARDIA, NO ESPECIFICADA",
        "CARDIOMIOPATIA DILATADA", "CARDIOMIOPATIA ISQUEMICA", "CARDIOMIOPATIA ALCOHOLICA", "CARDIOMIOPATIA HIPERTROFICA OBSTRUCTIVA", "CARDIOMIOPATIA, NO ESPECIFICADA",
        "INSUFICIENCIA (DE LA VALVULA) MITRAL", "PROLAPSO (DE LA VALVULA) MITRAL", "ESTENOSIS (DE LA VALVULA) AORTICA", "INSUFICIENCIA TRICUSPIDE",
        "INSUFICIENCIA CARDIACA CONGESTIVA", "INSUFICIENCIA VENTRICULAR IZQUIERDA",
        "ANGINA INESTABLE", "DEFECTO DEL TABIQUE AURICULAR (CIA)", "DOLOR PRECORDIAL", "SINCOPE Y COLAPSO",
        "PRESENCIA DE VALVULA CARDIACA PROTESICA", "PRESENCIA DE MARCAPASO CARDIACO", "PRESENCIA DE ANGIOPLASTIA Y PROTESIS CORONARIAS",
        "DIABETES MELLITUS NO INSULINODEPENDIENTE", "HIPERCOLESTEROLEMIA PURA", "HIPERLIPIDEMIA MIXTA (DLP)", "OBESIDAD DEBIDA A EXCESO DE CALORIAS", "APNEA DEL SUENO", "ENFERMEDAD PULMONAR OBSTRUCTIVA CRONICA (EPOC)", "HIPOTIROIDISMO, NO ESPECIFICADO"
    ]
    if st.session_state.condition not in diagnosis_options:
        diagnosis_options.insert(0, st.session_state.condition)
    st.session_state.condition = st.selectbox("Condición Médica Asignada", diagnosis_options, index=diagnosis_options.index(st.session_state.condition))

comp_rate = calculate_completion()
col_sum1, col_sum2 = st.columns([3, 1])

with col_sum1:
    st.markdown(f"""
    <div style="background: linear-gradient(to right, rgba(147, 51, 234, 0.1), rgba(79, 70, 229, 0.1)); border: 1px solid rgba(192, 132, 252, 0.4); padding: 1rem; border-radius: 1rem; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <span class="badge-purple">Paciente Activo</span>
            <h3 style="margin: 0.25rem 0 0 0; font-size: 1.1rem; color: #1e293b;">{st.session_state.patient_name}</h3>
            <p style="margin: 0; font-size: 0.8rem; color: #64748b;">🪪 ID: {st.session_state.patient_id} | 🩸 Sangre: {st.session_state.patient_blood} | 📞 {st.session_state.patient_phone}</p>
        </div>
        <div style="text-align: right; border-left: 1px solid #cbd5e1; padding-left: 1rem;">
            <div style="font-size: 0.75rem; font-weight: bold; color: #4b5563;">PRÓXIMA CITA</div>
            <div style="font-size: 0.85rem; font-weight: 800; color: #7c2d12;">{st.session_state.appointment_datetime.strftime('%d %b, %H:%M')}</div>
            <div style="font-size: 0.7rem; color: #6b7280;">{st.session_state.appointment_doctor}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_sum2:
    st.markdown(f"""
    <div style="background: linear-gradient(to right, #4c1d95, #312e81); padding: 1rem; border-radius: 1rem; color: white; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 1.8rem; font-weight: 900; color: #f472b6;">{comp_rate}%</div>
        <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #e9d5ff;">Cumplimiento Hoy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔔 Alarmas y Horarios", 
    "💊 Medicamentos", 
    "❤️ Presión & Vitals", 
    "🤖 Asistente IA"
])

with tab1:
    col_t1_1, col_t1_2 = st.columns([3, 1])
    with col_t1_1:
        st.markdown("### 🕒 Cronograma de Tomas y Tareas Diarias")
        st.markdown("Gestiona tus horarios de medicamentos y actividades cardiosaludables.")
    with col_t1_2:
        if st.button("➕ Nueva Alarma", use_container_width=True):
            st.session_state.show_new_alarm = True

    # Modal / Expandable creator for new alarm
    if st.session_state.get("show_new_alarm", False):
        with st.form("new_alarm_form"):
            st.markdown("#### Programar Nueva Alarma o Toma")
            new_title = st.text_input("Título (ej. Pastilla Losartán 50mg)")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                new_time = st.time_input("Hora programada", value=datetime.time(8, 0))
            with col_a2:
                new_cat = st.selectbox("Categoría", ["Medicamento", "Control", "Ejercicio", "Dieta"])
            new_days = st.text_input("Frecuencia (ej. Diario, Lunes a Viernes)", value="Diario")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.form_submit_button("Guardar Alarma", use_container_width=True):
                    new_id = max([a["id"] for a in st.session_state.alarms], default=0) + 1
                    st.session_state.alarms.append({
                        "id": new_id,
                        "title": new_title,
                        "time": new_time.strftime("%H:%M"),
                        "days": new_days,
                        "status": False,
                        "category": new_cat
                    })
                    st.session_state.show_new_alarm = False
                    st.rerun()
            with col_b2:
                if st.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state.show_new_alarm = False
                    st.rerun()

    st.markdown("---")
    for idx, alarm in enumerate(st.session_state.alarms):
        col_card1, col_card2, col_card3 = st.columns([0.1, 2.5, 0.8])
        with col_card1:
            checked = st.checkbox("", value=alarm["status"], key=f"alarm_chk_{alarm['id']}")
            if checked != alarm["status"]:
                st.session_state.alarms[idx]["status"] = checked
                st.rerun()
        with col_card2:
            status_style = "text-decoration: line-through; color: #94a3b8;" if alarm["status"] else "font-weight: bold; color: #1e293b;"
            st.markdown(f"""
            <div>
                <div style="font-size: 0.75rem; color: #7c3aed; font-weight: 700;">⏰ {alarm['time']} | 📅 {alarm['days']} ({alarm['category']})</div>
                <div style="font-size: 0.95rem; {status_style}">{alarm['title']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_card3:
            if st.button("🗑️ Eliminar", key=f"del_alarm_{alarm['id']}"):
                st.session_state.alarms.pop(idx)
                st.rerun()
        st.markdown("<hr style='margin: 0.5rem 0; border-color: #f1f5f9;'>", unsafe_allow_html=True)

with tab2:
    col_t2_1, col_t2_2 = st.columns([3, 1])
    with col_t2_1:
        st.markdown("### 💊 Gabinete de Fármacos y Control Diario")
        st.markdown("Control de inventario de medicamentos recetados por tu cardiólogo.")
    with col_t2_2:
        if st.button("➕ Agregar Fármaco", use_container_width=True):
            st.session_state.show_new_med = True

    if st.session_state.get("show_new_med", False):
        with st.form("new_med_form"):
            st.markdown("#### Registrar Nuevo Fármaco")
            m_name = st.text_input("Nombre del Fármaco")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                m_dose = st.text_input("Dosis (ej. 10 mg)")
                m_stock = st.number_input("Pastillas en Stock", min_value=1, value=30)
            with col_m2:
                m_freq = st.text_input("Frecuencia (ej. Cada 12 horas)")
                m_inst = st.text_input("Instrucciones", value="Tomar con agua")
            
            col_mb1, col_mb2 = st.columns(2)
            with col_mb1:
                if st.form_submit_button("Guardar Medicamento", use_container_width=True):
                    new_m_id = max([m["id"] for m in st.session_state.medications], default=0) + 1
                    st.session_state.medications.append({
                        "id": new_m_id, "name": m_name, "dose": m_dose, "freq": m_freq, "stock": m_stock, "instructions": m_inst
                    })
                    st.session_state.show_new_med = False
                    st.rerun()
            with col_mb2:
                if st.form_submit_button("Cancelar", use_container_width=True):
                    st.session_state.show_new_med = False
                    st.rerun()

    st.markdown("---")
    med_cols = st.columns(3)
    for idx, med in enumerate(st.session_state.medications):
        with med_cols[idx % 3]:
            st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 1rem; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #581c87; font-size: 1rem; font-weight: 800;">{med['name']}</h4>
                    <span style="background: #ede9fe; color: #6d28d9; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.7rem; font-weight: bold;">{med['dose']}</span>
                </div>
                <p style="margin: 0.5rem 0; font-size: 0.8rem; color: #475569;">🕒 {med['freq']}</p>
                <p style="margin: 0 0 0.5rem 0; font-size: 0.8rem; color: #475569;">📦 Stock: <b>{med['stock']} unidades</b></p>
                <p style="margin: 0; font-size: 0.75rem; color: #64748b; font-style: italic;">💡 {med['instructions']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🗑️ Eliminar Fármaco", key=f"del_med_{med['id']}"):
                st.session_state.medications.pop(idx)
                st.rerun()

with tab3:
    col_v1, col_v2 = st.columns([1, 2])
    with col_v1:
        st.markdown("### ❤️ Registrar Presión")
        with st.form("vital_form"):
            sys_val = st.number_input("Presión Sistólica (Alta - mmHg)", min_value=50, max_value=260, value=120)
            dia_val = st.number_input("Presión Diastólica (Baja - mmHg)", min_value=30, max_value=160, value=80)
            bpm_val = st.number_input("Ritmo Cardíaco (BPM / Pulso)", min_value=30, max_value=230, value=72)
            
            if st.form_submit_button("Guardar Lectura", use_container_width=True):
                status_label, _ = evaluate_bp(sys_val, dia_val)
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.vitals.insert(0, {
                    "datetime": now_str,
                    "systolic": sys_val,
                    "diastolic": dia_val,
                    "bpm": bpm_val,
                    "status": status_label
                })
                st.success("¡Lectura registrada correctamente!")
                st.rerun()

    with col_v2:
        st.markdown("### 📈 Histórico de Lecturas & Gráfico")
        if st.session_state.vitals:
            df_vitals = pd.DataFrame(st.session_state.vitals)
            # Render Streamlit Line Chart for Systolic & Diastolic
            chart_data = df_vitals.set_index("datetime")[["systolic", "diastolic"]]
            st.line_chart(chart_data)
            
            st.markdown("#### Histórico detallado")
            for idx, v in enumerate(st.session_state.vitals):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem;">
                    <div><b>{v['datetime']}</b></div>
                    <div>Sist/Diast: <b>{v['systolic']}/{v['diastolic']} mmHg</b></div>
                    <div>Pulso: <b>{v['bpm']} BPM</b></div>
                    <div><span style="background: #f3e8ff; color: #6b21a8; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{v['status']}</span></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Eliminar", key=f"del_vital_{idx}"):
                    st.session_state.vitals.pop(idx)
                    st.rerun()
        else:
            st.info("No hay registros de presión arterial aún.")

with tab4:
    st.markdown("### 🤖 Asistente Cardiovascular IA")
    st.markdown(f"Resuelve dudas sobre síntomas, dieta, medicamentos y hábitos cardioprotectores. Configurado para condición: **{st.session_state.condition}**.")

    # Quick prompt buttons
    q_col1, q_col2, q_col3 = st.columns(3)
    preset_prompt = None
    with q_col1:
        if st.button("🥗 Dieta Cardioprotectora", use_container_width=True):
            preset_prompt = "¿Qué alimentos debo consumir y evitar para controlar mi presión arterial?"
    with q_col2:
        if st.button("⚠️ Síntomas y Mareos", use_container_width=True):
            preset_prompt = "¿Qué debo hacer si siento ligeras palpitaciones o mareo leve?"
    with q_col3:
        if st.button("💊 Olvido de Dosis", use_container_width=True):
            preset_prompt = "¿Cómo debo tomar mis antihipertensivos si olvido una dosis?"

    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_query = st.chat_input("Escribe tu consulta médica o nutricional...")
    if preset_prompt:
        user_query = preset_prompt

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analizando con Asistente Médico IA..."):
                try:
                    # Construct Gemini API payload
                    system_prompt = f"Act as an expert cardiologist assistant. The patient {st.session_state.patient_name} has the condition {st.session_state.condition}. Provide concise, medically sound, and safe recommendations in Spanish."
                    
                    chat_history_payload = []
                    for turn in st.session_state.chat_history:
                        chat_history_payload.append({
                            "role": "user" if turn["role"] == "user" else "model",
                            "parts": [{"text": turn["content"]}]
                        })

                    payload = {
                        "contents": chat_history_payload,
                        "systemInstruction": {
                            "parts": [{"text": system_prompt}]
                        },
                        "tools": [{"google_search": {}}]
                    }

                    # Using gemini-3-flash-preview via the standard runtime endpoint
                    api_key = ""
                    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
                    
                    import urllib.request
                    req = urllib.request.Request(
                        api_url,
                        data=json.dumps(payload).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    with urllib.request.urlopen(req) as response:
                        res_data = json.loads(response.read().decode('utf-8'))
                        candidate = res_data.get("candidates", [])[0]
                        ai_response_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "No se pudo generar una respuesta.")
                except Exception as e:
                    ai_response_text = f"Hola, como asistente médico virtual para **{st.session_state.condition}**, te recomiendo mantener una dieta baja en sodio, realizar caminatas diarias de 30 minutos y registrar tu presión puntualmente. (Nota: Modo offline / respaldo activo)."

                st.markdown(ai_response_text)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response_text})

st.markdown("---")
if st.button("📊 Generar Informe Semanal para Médico", type="secondary", use_container_width=True):
    st.markdown(f"""
    <div style="background: white; border: 2px solid #581c87; padding: 1.5rem; border-radius: 1rem; margin-top: 1rem;">
        <h3 style="color: #581c87; margin-top: 0;">📋 INFORME CLÍNICO SEMANAL - CARDIOCARE PRO</h3>
        <p><b>Paciente:</b> {st.session_state.patient_name} (ID: {st.session_state.patient_id})</p>
        <p><b>Diagnóstico:</b> {st.session_state.condition}</p>
        <p><b>Tipo de Sangre:</b> {st.session_state.patient_blood} | <b>Teléfono:</b> {st.session_state.patient_phone}</p>
        <hr>
        <h4 style="color: #312e81;">Resumen de Adherencia y Vitals</h4>
        <p><b>Cumplimiento diario promedio:</b> {comp_rate}%</p>
        <p><b>Últimas tomas completadas:</b> {sum(1 for a in st.session_state.alarms if a['status'])} de {len(st.session_state.alarms)} tareas</p>
        <p><b>Última Presión Registrada:</b> {st.session_state.vitals[0]['systolic']}/{st.session_state.vitals[0]['diastolic']} mmHg (Pulso: {st.session_state.vitals[0]['bpm']} BPM) - {st.session_state.vitals[0]['status']}</p>
        <hr>
        <p style="font-size: 0.8rem; color: #64748b; text-align: center;">Generado automáticamente por CardioCare Pro Intelligence. Presentar este reporte en su próxima cita con {st.session_state.appointment_doctor}.</p>
    </div>
    """, unsafe_allow_html=True)
