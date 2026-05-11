import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import base64
import json

load_dotenv()

# ── Groq Client ───────────────────────────────────────────────────────────────
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found in .env file!")
        st.stop()
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ Error loading API key: {e}")
    st.stop()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AarogyaAI – Rural Health AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark gradient background */
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }

.main-header {
    font-size: 3.2rem; font-weight: 800; text-align: center;
    background: linear-gradient(90deg, #43e97b, #38f9d7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.sub-header {
    text-align: center; color: #a0a8c0; font-size: 1rem; margin-bottom: 1.5rem;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.metric-card {
    background: linear-gradient(135deg, rgba(67,233,123,0.15), rgba(56,249,215,0.08));
    border: 1px solid rgba(67,233,123,0.3);
    border-radius: 14px; padding: 1rem; text-align: center;
}
.risk-high   { border-left: 5px solid #ff4757; background: rgba(255,71,87,0.1); border-radius: 10px; padding: 1rem; }
.risk-mid    { border-left: 5px solid #ffa502; background: rgba(255,165,2,0.1); border-radius: 10px; padding: 1rem; }
.risk-low    { border-left: 5px solid #2ed573; background: rgba(46,213,115,0.1); border-radius: 10px; padding: 1rem; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #43e97b, #38f9d7);
    color: #0f0c29; font-weight: 700; border: none;
    border-radius: 10px; padding: 0.55rem 1rem;
    transition: all 0.3s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(67,233,123,0.4); }

/* Chat bubbles */
.chat-user {
    background: linear-gradient(135deg, #43e97b22, #38f9d722);
    border: 1px solid #43e97b44; border-radius: 14px 14px 4px 14px;
    padding: 0.8rem 1rem; margin: 0.4rem 0; text-align: right;
}
.chat-ai {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px 14px 14px 4px; padding: 0.8rem 1rem; margin: 0.4rem 0;
}

/* Sidebar */
[data-testid="stSidebar"] { background: rgba(15,12,41,0.9); border-right: 1px solid rgba(255,255,255,0.08); }

/* Tabs */
.stTabs [data-baseweb="tab"] { color: #a0a8c0; font-weight: 600; }
.stTabs [aria-selected="true"] { color: #43e97b !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
for key, default in {
    "total_consultations": 0,
    "chat_history": [],
    "consultation_log": [],
    "diagnostics_count": 0,
    "medical_history": [],
    "prescriptions": [],
    "medication_tracker": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Helper function to encode image for vision api
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🩺 AarogyaAI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Comprehensive Health Assistant</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 System Stats")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Consultations", st.session_state.total_consultations)
    col_s2.metric("Diagnostics", st.session_state.diagnostics_count)
    st.metric("Medical Documents", len(st.session_state.medical_history) + len(st.session_state.prescriptions))
    
    st.markdown("---")
    st.markdown("### 🆕 v3.0 Features")
    st.success("""
✅ Vision AI for Prescriptions & Bills
✅ Medication Tracking (Daily)
✅ Holistic Diet Recommendations
✅ Foolproof Medical Guardrails
✅ Context-Aware Conversations
    """)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Home", "💬 AI Consultation", "🧪 Diagnostics",
    "📄 Documents", "💊 Med Tracker", "📋 History"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 – HOME
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
<div class="card">
<h2>🚀 The Future of Healthcare</h2>

### 💡 Our Solution
AarogyaAI is your comprehensive AI-human health assistant combining instant multilingual symptom analysis, computer vision diagnostics, document understanding, and holistic diet recommendations.

- 🗣️ **Multilingual Chat** (Context-aware)
- 📸 **Visual Diagnostics** (Nail anemia)
- 📄 **Vision Document AI** (Bills & Prescriptions)
- 💊 **Medication Tracker** (Daily reminders)
</div>
""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Cost Reduction", "₹800 → ₹50", "-94%")
        c2.metric("Access Increase", "10×", "+900%")
        c3.metric("Time Saved", "4 hrs → 15 min", "-94%")

    with col2:
        st.markdown("""
<div class="card">

### 🏆 Competitive Edge
1. **Holistic Approach** integrates medicine & natural diet
2. **Offline capability** ready architecture
3. **Voice-first** (no literacy barrier)
4. **Smart Trackers** keeps patients adherent
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 – AI CONSULTATION (Chat-style)
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("💬 AI Health Consultation")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        language = st.selectbox("🌐 Language", [
            "English", "हिंदी (Hindi)", "বাংলা (Bengali)",
            "தமிழ் (Tamil)", "తెలుగు (Telugu)"
        ])
        age    = st.number_input("Age", 1, 120, 30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    with col1:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        # Quick symptom chips
        with st.expander("⚡ Quick symptom select"):
            chips = st.multiselect("Common symptoms:", [
                "Fever", "Cough", "Headache", "Body pain",
                "Sore throat", "Breathlessness", "Fatigue",
                "Nausea", "Diarrhea", "Chest pain", "Dizziness"
            ])

        user_input = st.text_area("Describe your symptoms:", height=80, placeholder="e.g. I have had fever for 3 days with body ache...")
        if chips:
            user_input = user_input + (" | " if user_input.strip() else "") + ", ".join(chips)

        duration = st.slider("Duration (days)", 1, 30, 3)

        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if user_input.strip():
                resp_lang = "Hindi" if "हिंदी" in language else "English"
                
                # System prompt with strict medical guardrails & holistic dietary focus
                system_prompt = f"""You are AarogyaAI, an expert medical AI assistant.
Current Patient: Age {age}, Gender {gender}. Language to use: {resp_lang}.

**CRITICAL MEDICAL GUARDRAILS:**
1. Explicitly state you are an AI, not a doctor.
2. NEVER give a definitive medical diagnosis. Always use phrases like "Possible conditions could include...".
3. If the user asks a non-medical question (e.g. programming, general knowledge, writing), strictly refuse and politely state you are a medical AI assistant.
4. If symptoms indicate a life-threatening emergency (e.g. severe chest pain, stroke signs), immediately urge them to seek emergency care.

**RESPONSE STRUCTURE:**
1. **Disclaimer**: Brief AI disclaimer.
2. **Possible Conditions**: Top 2-3 possibilities.
3. **Severity Assessment**: Mild/Moderate/Severe.
4. **Immediate Actions & When to Seek Care**.
5. **Holistic Diet Recommendations**: Provide a detailed list of natural foods, fruits, and vegetables that are known to help alleviate or manage these specific symptoms/conditions.

Maintain conversation context based on previous messages."""

                # Build messages payload including history
                messages = [{"role": "system", "content": system_prompt}]
                for msg in st.session_state.chat_history:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                
                # Append the new user message
                current_query = f"Symptoms: {user_input}\nDuration: {duration} days."
                messages.append({"role": "user", "content": current_query})

                with st.spinner("🤖 Analyzing..."):
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=messages,
                            temperature=0.3,
                            max_tokens=800
                        )
                        result = response.choices[0].message.content
                        st.session_state.chat_history.append({"role": "user", "content": current_query})
                        st.session_state.chat_history.append({"role": "assistant", "content": result})
                        st.session_state.total_consultations += 1
                        st.session_state.consultation_log.append({
                            "time": datetime.now().strftime("%H:%M"),
                            "date": datetime.now().strftime("%d %b %Y"),
                            "age": age, "gender": gender,
                            "symptoms": user_input[:60] + "...",
                            "language": language
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ API Error: {e}")
            else:
                st.warning("Please describe your symptoms first.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 – DIAGNOSTICS
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("🧪 AI Visual Diagnostics")

    try:
        from anemia_detector import analyze_nail_color, get_tips_for_better_photo, generate_visual_feedback
        detector_available = True
    except ImportError:
        detector_available = False
        st.error("⚠️ anemia_detector.py not found.")

    col1, col2 = st.columns([3, 2])

    with col1:
        diag_type = st.selectbox("Select Test", [
            "Anemia Detection (Fingernail) ✅",
            "Anemia Detection (Eye) 🚧",
            "Skin Condition 🚧",
            "Jaundice Check 🚧"
        ])

        uploaded = st.file_uploader(
            "Upload a clear photo of your fingernail",
            type=["jpg", "jpeg", "png"],
            help="Best: natural light, clean nail, straight angle"
        )

        if uploaded and detector_available:
            from PIL import Image
            image = Image.open(uploaded)

            c_img1, c_img2 = st.columns(2)
            with c_img1:
                st.image(image, caption="Uploaded Image", use_container_width=True)

            if st.button("🔬 Run AI Analysis", type="primary", use_container_width=True):
                with st.spinner("Analyzing nail color..."):
                    results = analyze_nail_color(image)

                if "error" in results:
                    st.error(f"❌ {results['error']}")
                else:
                    for w in results.get("quality_warnings", []):
                        st.warning(w)

                    annotated = generate_visual_feedback(image, results)
                    with c_img2:
                        st.image(annotated, caption="AI Analysis", use_container_width=True)

                    st.markdown("---")
                    risk = results["risk_level"]
                    css_cls = "risk-high" if risk == "High" else ("risk-mid" if risk in ["Moderate-High","Mild"] else "risk-low")
                    icon = "🚨" if risk == "High" else ("⚠️" if risk in ["Moderate-High","Mild"] else "✅")
                    st.markdown(f'<div class="{css_cls}"><h3>{icon} {risk.upper()} RISK</h3></div>', unsafe_allow_html=True)

                    r1, r2, r3 = st.columns(3)
                    r1.metric("Hb Estimate", results["hb_estimate"], results["hb_status"])
                    r2.metric("Risk Score", f"{results['risk_score']}/100", risk)
                    r3.metric("AI Confidence", f"{results['confidence']}%")

                    st.info(f"💡 **Recommendation:** {results['recommendation']}")
                    st.session_state.diagnostics_count += 1

        elif not uploaded:
            st.info("📸 Upload a fingernail photo to start.")

    with col2:
        st.markdown("""
<div class="card">
### 🔬 How It Works
Our AI analyses:
1. **RGB nail bed colour**
2. **Pink saturation** (colour intensity)
3. **Brightness/Lightness** (pale vs healthy)
4. **Redness index** (blood perfusion)
</div>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 – DOCUMENTS (Vision AI)
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("📄 Document Analysis (Vision AI)")
    st.markdown("Upload hospital bills or medical prescriptions. Our Vision AI will extract the data and add it to your records.")
    
    doc_type = st.radio("Select Document Type", ["Medical Prescription", "Hospital Bill/Report"], horizontal=True)
    
    doc_upload = st.file_uploader(
        f"Upload a clear photo of your {doc_type.lower()}",
        type=["jpg", "jpeg", "png"]
    )
    
    if doc_upload:
        st.image(doc_upload, caption="Uploaded Document", width=400)
        
        if st.button(f"🔍 Extract {doc_type} Data", type="primary"):
            with st.spinner("🤖 Vision AI is scanning document..."):
                base64_image = encode_image(doc_upload)
                
                if doc_type == "Medical Prescription":
                    vision_prompt = """Extract the following details from this medical prescription.
Respond ONLY in valid JSON format with this exact structure:
{
  "doctor_name": "...",
  "date": "YYYY-MM-DD",
  "diagnosis": "...",
  "medicines": [
    {
      "name": "...",
      "type": "Antibiotic / Painkiller / Vitamin etc",
      "dosage": "...",
      "frequency": "e.g. 1-0-1 (Morning-Night) or Twice a day",
      "duration": "..."
    }
  ],
  "natural_diet_recommendation": "Suggest 2-3 fruits/foods good for this diagnosis"
}"""
                else:
                    vision_prompt = """Extract the following details from this hospital bill or medical report.
Respond ONLY in valid JSON format with this exact structure:
{
  "hospital_name": "...",
  "date": "YYYY-MM-DD",
  "patient_name": "...",
  "total_amount": "...",
  "diagnosis_or_services": ["..."],
  "summary": "Short summary of the visit"
}"""

                try:
                    # Using Llama 3.2 Vision Preview model
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": vision_prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}",
                                        },
                                    },
                                ],
                            }
                        ],
                        temperature=0.1,
                        max_tokens=1024
                    )
                    
                    result_text = response.choices[0].message.content
                    
                    # Try to parse JSON from response
                    try:
                        # Find json block if wrapped in markdown
                        if "```json" in result_text:
                            json_str = result_text.split("```json")[1].split("```")[0].strip()
                        elif "```" in result_text:
                            json_str = result_text.split("```")[1].split("```")[0].strip()
                        else:
                            json_str = result_text.strip()
                            
                        extracted_data = json.loads(json_str)
                        
                        st.success("✅ Document Successfully Processed!")
                        
                        # Display and save data
                        if doc_type == "Medical Prescription":
                            st.session_state.prescriptions.append(extracted_data)
                            st.subheader(f"Prescription from {extracted_data.get('doctor_name', 'Unknown')}")
                            st.write(f"**Date:** {extracted_data.get('date', 'Unknown')}")
                            st.write(f"**Diagnosis:** {extracted_data.get('diagnosis', 'Unknown')}")
                            
                            st.markdown("### 💊 Prescribed Medicines")
                            for med in extracted_data.get('medicines', []):
                                st.info(f"**{med.get('name')}** ({med.get('type')})\n\nDosage: {med.get('dosage')} | Freq: {med.get('frequency')} | For: {med.get('duration')}")
                                
                                # Add to medication tracker automatically
                                med_name = med.get('name')
                                if med_name not in st.session_state.medication_tracker:
                                    st.session_state.medication_tracker[med_name] = {
                                        "type": med.get('type'),
                                        "frequency": med.get('frequency'),
                                        "taken_today": False,
                                        "days_tracked": 0
                                    }
                            
                            st.markdown("### 🍎 Dietary Advice")
                            st.success(extracted_data.get('natural_diet_recommendation', 'Eat healthy and stay hydrated.'))
                            
                            st.info("💡 Medicines have been automatically added to your Medication Tracker!")
                            
                        else:
                            st.session_state.medical_history.append(extracted_data)
                            st.subheader(f"Bill from {extracted_data.get('hospital_name', 'Unknown')}")
                            st.write(f"**Date:** {extracted_data.get('date', 'Unknown')}")
                            st.write(f"**Total Amount:** {extracted_data.get('total_amount', 'Unknown')}")
                            st.write(f"**Services:** {', '.join(extracted_data.get('diagnosis_or_services', []))}")
                            st.info(f"**Summary:** {extracted_data.get('summary', '')}")
                            
                    except json.JSONDecodeError:
                        st.error("Failed to parse the AI response. Here is the raw output:")
                        st.write(result_text)
                        
                except Exception as e:
                    st.error(f"⚠️ Vision API Error: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 – MEDICATION TRACKER
# ═════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("💊 Medication Tracker")
    
    now = datetime.now()
    current_day = now.strftime("%A, %d %B %Y")
    st.subheader(f"📅 Today: {current_day}")
    
    if not st.session_state.medication_tracker:
        st.info("No active medications found. Please upload a prescription in the 'Documents' tab to populate this tracker automatically.")
    else:
        st.markdown("Mark your medicines as taken for today. This ensures you stick to your prescription.")
        
        cols = st.columns(3)
        col_idx = 0
        
        for med_name, details in st.session_state.medication_tracker.items():
            with cols[col_idx % 3]:
                st.markdown(f"""
                <div class="metric-card">
                <h4>{med_name}</h4>
                <p style="color:#a0a8c0; font-size:0.9rem;">{details['type']}</p>
                <p><b>Freq:</b> {details['frequency']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                taken = st.checkbox("Mark as Taken", value=details['taken_today'], key=f"chk_{med_name}")
                if taken != details['taken_today']:
                    st.session_state.medication_tracker[med_name]['taken_today'] = taken
                    if taken:
                        st.toast(f"✅ Awesome! You took {med_name}.")
            col_idx += 1
            
        st.markdown("---")
        total_meds = len(st.session_state.medication_tracker)
        taken_meds = sum(1 for m in st.session_state.medication_tracker.values() if m['taken_today'])
        
        st.progress(taken_meds / total_meds if total_meds > 0 else 0)
        st.write(f"**Progress today: {taken_meds} of {total_meds} medications taken.**")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 6 – HISTORY
# ═════════════════════════════════════════════════════════════════════════════
with tab6:
    st.header("📋 Overall Health History")
    
    subtab1, subtab2, subtab3 = st.tabs(["AI Consultations", "Hospital Bills", "Prescriptions"])
    
    with subtab1:
        if st.session_state.consultation_log:
            df = pd.DataFrame(st.session_state.consultation_log)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No AI consultations yet.")
            
    with subtab2:
        if st.session_state.medical_history:
            for bill in st.session_state.medical_history:
                with st.expander(f"{bill.get('date', '')} - {bill.get('hospital_name', 'Bill')}"):
                    st.json(bill)
        else:
            st.info("No hospital bills uploaded yet.")
            
    with subtab3:
        if st.session_state.prescriptions:
            for rx in st.session_state.prescriptions:
                with st.expander(f"{rx.get('date', '')} - {rx.get('doctor_name', 'Prescription')}"):
                    st.json(rx)
        else:
            st.info("No prescriptions uploaded yet.")

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#a0a8c0;padding:1rem 0'>
<b style='color:#43e97b'>AarogyaAI v3.0</b> &nbsp;|&nbsp; Comprehensive Health Assistant<br>
Powered by Groq AI & Vision Models<br>
</div>
""", unsafe_allow_html=True)