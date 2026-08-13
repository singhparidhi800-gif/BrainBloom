import streamlit as st
import random
from datetime import datetime
from groq import Groq
import time
from fpdf import FPDF
import streamlit.components.v1 as components
import urllib.parse
import os
import json

# Must be first Streamlit command
st.set_page_config(page_title="BrainBloom - EduGenie", page_icon="✨", layout="wide")

# ==========================================
# 💳 YOUR UPI PAYMENT CONFIGURATION
# ==========================================
MY_UPI_ID = st.secrets.get("UPI_ID", "anugya@upi")

# --- DATA PERSISTENCE SYSTEM ---
DATA_FILE = "brainbloom_data.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "user_name": "Future Topper",
        "total_time": 0,
        "study_sessions": 0,
        "streak": 1,
        "is_vip": False
    }

def save_user_data():
    data = {
        "user_name": st.session_state.get("user_name", "Future Topper"),
        "total_time": st.session_state.get("total_time", 0),
        "study_sessions": st.session_state.get("study_sessions", 0),
        "streak": st.session_state.get("streak", 1),
        "is_vip": st.session_state.get("is_vip", False)
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Initialize Session State
saved_data = load_user_data()
if 'user_name' not in st.session_state: st.session_state.user_name = saved_data.get("user_name", "Future Topper")
if 'total_time' not in st.session_state: st.session_state.total_time = saved_data.get("total_time", 0)
if 'study_sessions' not in st.session_state: st.session_state.study_sessions = saved_data.get("study_sessions", 0)
if 'streak' not in st.session_state: st.session_state.streak = saved_data.get("streak", 1)
if 'is_vip' not in st.session_state: st.session_state.is_vip = saved_data.get("is_vip", False)
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'active_speech' not in st.session_state: st.session_state.active_speech = ""
if 'flashcards_data' not in st.session_state: st.session_state.flashcards_data = []

# Safe API Client Setup
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

# --- UNIVERSAL VOICE PLAYER HELPER WITH WORKING MUTE ---
def render_voice_controls(text_content, key_prefix="default", language="Hindi"):
    col_v1, col_v2 = st.columns([1, 1])
    lang_code = 'hi-IN' if language == "Hindi" else 'en-US'
    clean_text = text_content.replace("'", "").replace("\n", " ").replace('"', '')
    
    with col_v1:
        if st.button(f"🔊 Listen Voice", key=f"play_{key_prefix}"):
            js_code = f"""
            <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = '{lang_code}';
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            </script>
            """
            components.html(js_code, height=0)
            
    with col_v2:
        if st.button(f"🔇 Stop Voice", key=f"stop_{key_prefix}"):
            js_code = """
            <script>
                window.speechSynthesis.cancel();
            </script>
            """
            components.html(js_code, height=0)

# --- CLEAN HD BRANDING LOGO (Fixed Screenshot Bug) ---
def display_logo():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 12px;'>
        <div style='
            display: inline-block;
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
            padding: 18px 28px;
            border-radius: 24px;
            box-shadow: 0 12px 30px rgba(139, 92, 246, 0.3);
            border: 2px solid #FFFFFF;
        '>
            <span style='font-size: 38px;'>🌸</span>
            <span style='font-size: 26px; font-weight: 800; color: #FFFFFF; font-family: "Plus Jakarta Sans"; margin-left: 8px;'>BrainBloom</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- AI & HD IMAGE GENERATOR ---
def get_ai_answer(prompt, language="English"):
    if not client:
        return "GROQ API Key missing in Streamlit Secrets! Please add GROQ_API_KEY."
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

def generate_3d_hd_image(topic, step_text=""):
    seed = random.randint(10000, 99999)
    # High-quality Pixar 3D digital render prompt engineering
    clean_prompt = f"3d digital artwork render of {topic}, {step_text}, vibrant colors, smooth lighting, educational textbook visual, detailed 8k, cute animated style"
    safe_prompt = urllib.parse.quote(clean_prompt)
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?seed={seed}&nologo=true&width=800&height=450"

def create_pdf(notes, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"BrainBloom Study Notes: {topic}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    clean_notes = notes.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_notes)
    file_name = f"{topic.replace(' ', '_')}_Notes.pdf"
    pdf.output(file_name)
    return file_name

def study_timer():
    placeholder = st.empty()
    if st.session_state.start_time is None:
        if placeholder.button("▶️ Start Focus Session", use_container_width=True):
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        placeholder.success(f"⏰ Active Focus Time: {int(elapsed//60)} min {int(elapsed%60)} sec")
        if st.button("⏹️ Stop & Save Time", use_container_width=True):
            st.session_state.total_time += elapsed
            st.session_state.study_sessions += 1
            st.session_state.start_time = None
            save_user_data()
            st.rerun()
        time.sleep(1)
        if st.session_state.start_time is not None:
            st.rerun()

def get_user_rank(seconds):
    hours = seconds / 3600
    if hours < 1: return "🐣 Novice Learner"
    elif hours < 5: return "⚡ Backbencher Se Topper"
    elif hours < 15: return "🔥 Study Machine"
    else: return "🧠 Einstein Pro Max"

FUNNY_MOTIVATIONS = [
    "Padhle bhai, crush bhi topper ke sath hi baithti hai! 😉",
    "Dimaag overheat ho raha hai? Thoda paani piyo aur phir dhoom machao! ☕🔥",
    "Mummy ko bol do: 'Sharma ji ke beta ko bolna ab competition tough hai!' 😎",
    "Gyaan wo amrit hai jo sirf padhne se milta hai, reels scroll karne se nahi! 📱❌",
    "Aapka dimaag 100% active hai, bas isko thoda Instagram se door rakho! 🚀"
]

# --- VIBRANT & INTERACTIVE STYLING ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #F0F4FF 0%, #E0E7FF 50%, #F5F3FF 100%);
}
.aesthetic-card {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(16px);
    border-radius: 22px;
    padding: 22px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 12px 32px rgba(99, 102, 241, 0.09);
    margin-bottom: 20px;
}
.step-badge {
    background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
    color: #FFFFFF;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    display: inline-block;
    margin-bottom: 10px;
}
.vip-badge {
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
    color: #000;
    padding: 5px 14px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 12px;
}
.stButton>button {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    color: #FFFFFF !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 11px 22px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25) !important;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4) !important;
}
h1, h2, h3 { color: #1E1B4B !important; font-weight: 800 !important; }
</style>""", unsafe_allow_html=True)

# Top Bar Header
col_main_h, col_vip_btn, col_lang = st.columns([4, 1.8, 1.2])
with col_vip_btn:
    if st.session_state.is_vip:
        st.markdown("<span class='vip-badge'>👑 VIP UNLOCKED</span>", unsafe_allow_html=True)
    else:
        if st.button("👑 VIP Pass (₹49)", use_container_width=True):
            st.session_state.page = "Monetize"
            st.rerun()

with col_lang:
    language = st.selectbox("🌐 Language", ["Hindi", "English"], label_visibility="collapsed")

# --- HOME PAGE ---
if st.session_state.page == "Home":
    display_logo()
    st.markdown("<p style='text-align: center; color: #475569; font-weight: 600; font-size: 16px; margin-top: -8px; margin-bottom: 20px;'>Your Smart AI Learning Companion 🌸</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown(f"### 👋 Welcome back, Topper **{st.session_state.user_name}** ✨")
    col_prof1, col_prof2 = st.columns([3, 1])
    with col_prof1:
        st.write(f"Current Level: **{get_user_rank(st.session_state.total_time)}** | Focus Time: **{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m**")
    with col_prof2:
        if st.button("👤 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
    
    if st.button("☕ Quick Dose of Motivation"):
        st.toast(random.choice(FUNNY_MOTIVATIONS), icon="💡")
    st.markdown("</div>", unsafe_allow_html=True)

    # Grid Features
    st.markdown("<h3 style='text-align: center; margin-top: 15px;'>🚀 Interactive AI Studio</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎨 3D AI Visual Class", use_container_width=True):
            st.session_state.page = "Video"
            st.rerun()
        if st.button("🎭 BrainRot Explainer 🔥", use_container_width=True):
            st.session_state.page = "BrainRot"
            st.rerun()
        if st.button("📝 AI Test Series", use_container_width=True):
            st.session_state.page = "Test"
            st.rerun()

    with col2:
        if st.button("⚡ Exam Survival Kit 📄", use_container_width=True):
            st.session_state.page = "Survival"
            st.rerun()
        if st.button("📝 Magic Notes Generator", use_container_width=True):
            st.session_state.page = "Notes"
            st.rerun()
        if st.button("⏰ Study Focus Timer", use_container_width=True):
            st.session_state.page = "Timer"
            st.rerun()

    with col3:
        if st.button("📱 Shorts Script AI 🎬", use_container_width=True):
            st.session_state.page = "Shorts"
            st.rerun()
        if st.button("❓ AI Doubt Solver ⚡", use_container_width=True):
            st.session_state.page = "Doubt"
            st.rerun()
        if st.button("🎴 Smart AI Flashcards", use_container_width=True):
            st.session_state.page = "Flashcards"
            st.rerun()

# --- STUDENT DASHBOARD PAGE ---
elif st.session_state.page == "Dashboard":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("👤 Student Profile & Saved Progress")
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    st.markdown("### 🎓 Profile Info")
    new_name = st.text_input("Edit Profile Name:", value=st.session_state.user_name)
    if st.button("💾 Save Profile Name"):
        if new_name.strip():
            st.session_state.user_name = new_name.strip()
            save_user_data()
            st.success("Profile Saved Permanently!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Total Study Time", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d2:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Completed Sessions", f"🔥 {st.session_state.study_sessions}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d3:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Current Rank", get_user_rank(st.session_state.total_time))
        st.markdown("</div>", unsafe_allow_html=True)

# --- 🎨 3D AI VISUAL CLASS PAGE ---
elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎨 3D AI Visual Class Studio")
    topic = st.text_input("Enter Topic (e.g., Photosynthesis, Human Brain, Newton's Laws):")
    
    if st.button("Generate 3D Visual Class ✨"):
        if topic:
            with st.spinner("EduGenie is generating 3D HD artwork & class script..."):
                prompt = f"Explain {topic} in 2 precise step-by-step visual concepts for a student in {language}. Step 1: Core Concept. Step 2: Key Function."
                script = get_ai_answer(prompt, language)
                
                raw_lines = [p.strip('- 1234567890.').strip() for p in script.split('\n') if len(p.strip()) > 8]
                points = raw_lines[:2] if len(raw_lines) >= 2 else [f"Core structure of {topic}", f"Working process of {topic}"]
                
                img1 = generate_3d_hd_image(topic, points[0])
                img2 = generate_3d_hd_image(topic, points[1])
                
                st.session_state.v_topic = topic
                st.session_state.v_script = script
                st.session_state.v_points = points
                st.session_state.v_imgs = [img1, img2]
        else:
            st.error("Please enter a topic!")

    if 'v_script' in st.session_state:
        st.markdown(f"### ✨ Visual Topic: {st.session_state.v_topic}")
        render_voice_controls(st.session_state.v_script, key_prefix="visual_class", language=language)

        for i, pt_text in enumerate(st.session_state.v_points):
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 2])
            with col1:
                st.image(st.session_state.v_imgs[i], use_container_width=True, caption=f"3D Visual Step {i+1}")
            with col2:
                st.markdown(f"<span class='step-badge'>STEP {i+1}</span>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 17px; font-weight: 600; color: #1E293B;'>{pt_text}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown("### 📢 Full Teacher Script:")
        st.write(st.session_state.v_script)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 🎭 BRAINROT / GEN-Z EXPLAINER PAGE ---
elif st.session_state.page == "BrainRot":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 BrainRot to BrainGain (Gen-Z & Meme Explainer)")
    topic = st.text_input("Enter Concept (e.g., Organic Chemistry, Trigonometry, Photosynthesis):")
    vibe = st.selectbox("Select Vibe:", ["Gen-Z Slang & Memes 💀", "Anime / Superhero Analogy ⚡", "K-Pop & BTS Army Analogy 🎵", "Funny Hindi Webseries Style 🍿"])
    
    if st.button("Explain in Meme Style 🔥"):
        if topic:
            with st.spinner("Cooking up viral meme breakdown..."):
                prompt = f"Explain the academic concept '{topic}' in style of {vibe}. Use funny analogies, easy breakdown so a student never forgets it. Language: Hinglish."
                res = get_ai_answer(prompt, language)
                st.session_state.br_res = res
                st.balloons()
        else: st.error("Enter a topic!")

    if 'br_res' in st.session_state:
        render_voice_controls(st.session_state.br_res, key_prefix="brainrot", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.br_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- ⚡ NIGHT-BEFORE EXAM SURVIVAL KIT PAGE ---
elif st.session_state.page == "Survival":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⚡ Emergency Exam Survival Kit")
    subject = st.text_input("Enter Chapter / Subject (e.g., Electrostatics, Calculus):")
    
    if st.button("Generate Survival Sheet 📄"):
        if subject:
            with st.spinner("Creating high-yield exam sheet..."):
                prompt = f"Create a 1-page emergency exam sheet for {subject}. Include: 1) Top 5 Guaranteed Exam Questions with Answers. 2) Key Formula / Concept Cheat Sheet. 3) Common Mistakes to Avoid. Language: Hinglish."
                res = get_ai_answer(prompt, language)
                st.session_state.surv_res = res
                st.session_state.surv_topic = subject
        else: st.error("Enter chapter name!")

    if 'surv_res' in st.session_state:
        render_voice_controls(st.session_state.surv_res, key_prefix="survival", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.surv_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        pdf_file = create_pdf(st.session_state.surv_res, st.session_state.surv_topic)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF Survival Sheet", f, file_name=pdf_file, use_container_width=True)

# --- 📱 YOUTUBE SHORTS SCRIPT GENERATOR PAGE ---
elif st.session_state.page == "Shorts":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎬 Viral 30-Sec Shorts Script AI")
    topic = st.text_input("Enter Topic for Video Short:")
    
    if st.button("Generate Script & Hook 🔥"):
        if topic:
            with st.spinner("Writing catchy script..."):
                prompt = f"Write a catchy 30-second YouTube Short / Reel script on {topic}. Include: 1) Viral Hook (First 3 seconds). 2) Mindblowing Explanation. 3) Call to Action (Subscribe to Anu ot7). Language: Hinglish."
                res = get_ai_answer(prompt, language)
                st.session_state.shorts_res = res
        else: st.error("Enter topic!")

    if 'shorts_res' in st.session_state:
        render_voice_controls(st.session_state.shorts_res, key_prefix="shorts", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.shorts_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- 📝 MAGIC NOTES PAGE ---
elif st.session_state.page == "Notes":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("📝 Magic Notes Generator")
    all_subjects = ["Science", "Math", "Physics", "Chemistry", "Biology", "History", "Geography", "English", "Hindi", "Computer"]
    
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    subject = st.selectbox("Choose Subject:", all_subjects)
    topic = st.text_input("Enter Topic Name:")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Create Magic Notes ✨"):
        if topic:
            with st.spinner("EduGenie is crafting aesthetic notes..."):
                notes = get_ai_answer(f"Make 1 page concise study notes on {topic} for {subject}. Include Headings, 3 Key Points, 1 Real Example, 1 Memory Trick. Language: {language}", language)
                diag_img = generate_3d_hd_image(topic, "diagram model overview")
                st.session_state.notes_res = notes
                st.session_state.notes_topic = topic
                st.session_state.notes_img = diag_img
        else: st.error("Enter topic name!")

    if 'notes_res' in st.session_state:
        render_voice_controls(st.session_state.notes_res, key_prefix="notes", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.notes_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        st.image(st.session_state.notes_img, caption=f"3D Concept Diagram: {st.session_state.notes_topic}", use_container_width=True)
        
        pdf_file = create_pdf(st.session_state.notes_res, st.session_state.notes_topic)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF Notes", f, file_name=pdf_file, use_container_width=True)

# --- ❓ AI DOUBT SOLVER PAGE ---
elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("❓ AI Doubt Solver ⚡")
    doubt = st.text_area("Ask any doubt or question:", height=120)
    
    if st.button("Solve Doubt Now ⚡"):
        if doubt:
            with st.spinner("EduGenie is solving..."):
                answer = get_ai_answer(f"Solve this student doubt clearly step-by-step: {doubt}. Language: {language}", language)
                st.session_state.doubt_res = answer
        else: st.error("Please enter your doubt!")

    if 'doubt_res' in st.session_state:
        render_voice_controls(st.session_state.doubt_res, key_prefix="doubt", language=language)
        st.markdown(f"<div class='aesthetic-card'><b>💡 Solution:</b><br><br>{st.session_state.doubt_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- 📝 AI TEST SERIES PAGE ---
elif st.session_state.page == "Test":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("📝 AI Practice Test")
    topic = st.text_input("Enter Topic for Test:")
    
    if st.button("Generate Practice Quiz 🎯"):
        if topic:
            with st.spinner("Generating Quiz..."):
                test = get_ai_answer(f"Create 5 practice MCQs on {topic} for students in {language}. Provide Question, Options A/B/C/D, and Answers at bottom.", language)
                st.session_state.test_res = test
        else: st.error("Please enter a topic!")

    if 'test_res' in st.session_state:
        render_voice_controls(st.session_state.test_res, key_prefix="test", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.test_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- 🎴 FLASHCARDS PAGE ---
elif st.session_state.page == "Flashcards":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎴 AI Flashcards")
    fc_topic = st.text_input("Enter Topic for Flashcards:")
    
    if st.button("Generate Flashcards ✨"):
        if fc_topic:
            with st.spinner("Creating Revision Flashcards..."):
                prompt = f"Create 4 short flashcards for {fc_topic} in {language}. Format each card as Question: ... | Answer: ..."
                res = get_ai_answer(prompt, language)
                st.session_state.flashcards_data = [card for card in res.split('\n') if card.strip()]
        else: st.error("Please enter a topic!")
    
    if st.session_state.flashcards_data:
        st.markdown("### 🎴 Tap Card to Reveal Answer:")
        for idx, fc in enumerate(st.session_state.flashcards_data):
            if "|" in fc or ":" in fc:
                with st.expander(f"📌 Flashcard {idx+1}"):
                    st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>{fc}</div>", unsafe_allow_html=True)
                    render_voice_controls(fc, key_prefix=f"fc_{idx}", language=language)

# --- ⏰ FOCUS TIMER PAGE ---
elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⏰ Focus Study Timer")
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    study_timer()
    st.markdown("</div>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Total Study Duration", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Completed Sessions", f"🔥 {st.session_state.study_sessions}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 💰 MONETIZATION PAGE ---
elif st.session_state.page == "Monetize":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("👑 Unlock BrainBloom VIP Pass")
    
    st.markdown(f"""
    <div class='aesthetic-card' style='text-align: center;'>
        <h2>✨ VIP Topper Pass Benefits:</h2>
        <p>✅ Unlimited 3D AI Visual Classes & Diagrams</p>
        <p>✅ Download PDF Notes & Survival Sheets</p>
        <p>✅ 24/7 Unlimited AI Voice Assistant</p>
        <hr>
        <h3>Special Price: <b>₹49 / month</b></h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"Send ₹49 via UPI to: **{MY_UPI_ID}**")
    utr = st.text_input("Enter Transaction ID / UTR Number:")
    if st.button("Activate VIP Access 🚀"):
        if len(utr) >= 6:
            st.session_state.is_vip = True
            save_user_data()
            st.success("🎉 VIP Pass Activated!")
            st.balloons()
            time.sleep(2)
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid Transaction UTR Number.")

st.markdown("---")
st.caption("Made with ❤️ by Anugya | BrainBloom EduGenie v3.5 🌸")
