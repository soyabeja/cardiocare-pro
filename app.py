import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# Configuración de la página
st.set_page_config(
    page_title="CardioCare Pro - Control Cardiovascular",
    page_icon="🫀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para mantener la estética clínica y moderna
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        background-color: #7c3aed;
        color: white;
    }
    .stButton>button:hover {
        background-color: #6d28d9;
        color: white;
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
if "condition" not in st.session_state:
    st.session_state.condition = "HIPERTENSION ESENCIAL (PRIMARIA)"
if "vitals" not in st.session_state:
    st.session_state.vitals = [
        {"date": "22 Sep 08:30", "sys": 124, "dias": 82, "bpm": 74, "status": "Normal-Alto"},
        {"date": "23 Sep 09:00", "sys": 118, "dias": 78, "bpm": 70, "status": "Óptima"},
        {"date": "24 Sep 08:15", "sys": 122, "dias": 80, "bpm": 72, "status": "Normal"}
    ]
if "meds" not in st.session_state:
    st.session_state.meds = [
        {"name": "Losartán", "dose": "50 mg", "freq": "Cada 24h", "stock": 28},
        {"name": "Aspirina Protect", "dose": "100 mg", "freq": "Cada 24h", "stock": 45}
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.markdown("### 🫀 CardioCare Pro")
st.sidebar.info(f"**Paciente:** {st.session_state.patient_name}\n\n**ID:** {st.session_state.patient_id}\n\n**Sangre:** {st.session_state.patient_blood}")

with st.sidebar.expander("⚙️ Editar Datos del Paciente"):
    st.session_state.patient_name = st.text_input("Nombre Completo", st.session_state.patient_name)
    st.session_state.patient_id = st.text_input("ID / Cédula", st.session_state.patient_id)
    st.session_state.patient_blood = st.selectbox("Tipo de Sangre", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], index=0)
    st.session_state.patient_phone = st.text_input("Teléfono de Emergencia", st.session_state.patient_phone)

# Selector de condición médica
conditions_list = [
    "HIPERTENSION ESENCIAL (PRIMARIA)",
    "HIPERTENSIÓN ARTERIAL GRADO 1",
    "HIPERTENSIÓN ARTERIAL GRADO 2",
    "FIBRILACION Y ALETEO AURICULAR",
    "INSUFICIENCIA CARDIACA CONGESTIVA",
    "CARDIOMIOPATIA ISQUEMICA"
]
st.session_state.condition = st.sidebar.selectbox("🩺 Diagnóstico Principal", conditions_list)

st.title("CardioCare Pro Cloud ☁️")
st.markdown("Asistente y Control Cardiovascular Inteligente en la Nube")

tab1, tab2, tab3, tab4 = st.tabs(["💊 Medicamentos", "❤️ Presión & Vitales", "🤖 Asistente IA", "📋 Informe Clínico"])

with tab1:
    st.subheader("Gabinete de Fármacos")
    col1, col2 = st.columns(2)
    with col1:
        new_med = st.text_input("Nombre del Fármaco")
        new_dose = st.text_input("Dosis (ej. 50mg)")
    with col2:
        new_freq = st.text_input("Frecuencia", "Cada 24 horas")
        new_stock = st.number_input("Stock actual", min_value=1, value=30)
    
    if st.button("Agregar Medicamento"):
        if new_med:
            st.session_state.meds.append({"name": new_med, "dose": new_dose, "freq": new_freq, "stock": new_stock})
            st.success(f"Fármaco {new_med} agregado correctamente.")

    st.markdown("---")
    for idx, med in enumerate(st.session_state.meds):
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.write(f"**{med['name']}** ({med['dose']}) - {med['freq']}")
        c2.write(f"Stock: **{med['stock']}** tab")
        if c3.button("Consumir", key=f"med_{idx}"):
            st.session_state.meds[idx]["stock"] = max(0, med["stock"] - 1)
            st.rerun()

with tab2:
    st.subheader("Control de Presión Arterial y Pulso")
    with st.form("vital_form"):
        col1, col2, col3 = st.columns(3)
        sys_val = col1.number_input("Sistólica (mmHg)", min_value=60, max_value=250, value=120)
        dias_val = col2.number_input("Diastólica (mmHg)", min_value=40, max_value=150, value=80)
        bpm_val = col3.number_input("Pulso (BPM)", min_value=30, max_value=200, value=72)
        
        submitted = st.form_submit_button("Guardar Lectura")
        if submitted:
            status = "Óptima" if sys_val < 120 and dias_val < 80 else ("Hipertensión" if sys_val >= 140 or dias_val >= 90 else "Normal-Alta")
            now_str = datetime.now().strftime("%d %b %H:%M")
            st.session_state.vitals.append({"date": now_str, "sys": sys_val, "dias": dias_val, "bpm": bpm_val, "status": status})
            st.success("Lectura registrada con éxito.")

    if st.session_state.vitals:
        df_vitals = pd.DataFrame(st.session_state.vitals)
        st.line_chart(df_vitals.set_index("date")[["sys", "dias"]])
        st.dataframe(df_vitals, use_container_width=True)

with tab3:
    st.subheader("Asistente Médico IA (Gemini)")
    st.markdown(f"Diagnóstico activo: **{st.session_state.condition}**")

    # Configuración segura de API Key desde Streamlit Secrets
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu consulta sobre dieta, síntomas o plan médico..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if not api_key:
                response_text = f"⚠️ Falta configurar la `GEMINI_API_KEY` en los secretos de Streamlit Cloud. Como asistente para {st.session_state.condition}, te recomiendo mantener una dieta baja en sodio y registrar tus signos vitales."
                st.markdown(response_text)
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    system_prompt = f"Eres un asistente médico virtual experto en cardiología. El paciente tiene diagnóstico de '{st.session_state.condition}'. Responde con empatía, precisión clínica y rigor científico."
                    response = model.generate_content([system_prompt, prompt])
                    response_text = response.text
                    st.markdown(response_text)
                except Exception as e:
                    response_text = f"Error conectando con la IA: {e}"
                    st.markdown(response_text)

        st.session_state.chat_history.append({"role": "assistant", "content": response_text})

with tab4:
    st.subheader("Reporte Clínico Exportable")
    st.markdown(f"""
    * **Paciente:** {st.session_state.patient_name} (ID: {st.session_state.patient_id})
    * **Tipo de Sangre:** {st.session_state.patient_blood}
    * **Condición Actual:** {st.session_state.condition}
    * **Teléfono de Confianza:** {st.session_state.patient_phone}
    """)
    st.markdown("---")
    st.markdown("### Historial de Fármacos y Vitals")
    st.write(f"Total de registros de presión: {len(st.session_state.vitals)}")
    st.write(f"Fármacos activos en gabinete: {len(st.session_state.meds)}")
    if st.button("🖨️ Imprimir / Guardar como PDF"):
        st.info("Usa Ctrl+P (o Cmd+P) en tu navegador para guardar este reporte en PDF.")

st.sidebar.markdown("---")
if st.sidebar.button("🚨 S.O.S EMERGENCIA"):
    st.sidebar.error(f"Llama inmediatamente a emergencias (123) o a tu contacto de confianza: {st.session_state.patient_phone}")
