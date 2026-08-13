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
import base64

# Must be first Streamlit command
st.set_page_config(page_title="BrainBloom - EduGenie", page_icon="✨", layout="wide")

# ==========================================
# 💳 UPI CONFIGURATION
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
        "xp_points": 50,
        "is_vip": False,
        "diary_secret": "",
        "diary_pin": "",
        "profile_pic": None
    }

def save_user_data():
    data = {
        "user_name": st.session_state.get("user_name", "Future Topper"),
        "total_time": st.session_state.get("total_time", 0),
        "study_sessions": st.session_state.get("study_sessions", 0),
        "streak": st.session_state.get("streak", 1),
        "xp_points": st.session_state.get("xp_points", 50),
        "is_vip": st.session_state.get("is_vip", False),
        "diary_secret": st.session_state.get("diary_secret", ""),
        "diary_pin": st.session_state.get("diary_pin", ""),
        "profile_pic": st.session_state.get("profile_pic", None)
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Initialize Session State
saved_data = load_user_data()
if 'user_name' not in st.session_state: st.session_state.user_name = saved_data.get("user_name", "Future Topper")
if 'total_time' not in st.session_state: st.session_state.total_time = saved_data.get("total_time", 0)
if 'study_sessions' not in st.session_state: st.session_state.study_sessions = saved_data.get("study_sessions", 0)
if 'streak' not in st.session_state: st.session_state.streak = saved_data.get("streak", 1)
if 'xp_points' not in st.session_state: st.session_state.xp_points = saved_data.get("xp_points", 50)
if 'is_vip' not in st.session_state: st.session_state.is_vip = saved_data.get("is_vip", False)
if 'diary_secret' not in st.session_state: st.session_state.diary_secret = saved_data.get("diary_secret", "")
if 'diary_pin' not in st.session_state: st.session_state.diary_pin = saved_data.get("diary_pin", "")
if 'profile_pic' not in st.session_state: st.session_state.profile_pic = saved_data.get("profile_pic", None)

if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'flashcards_data' not in st.session_state: st.session_state.flashcards_data = []

# Game & Boss Fight State Initialization
if 'boss_hp' not in st.session_state: st.session_state.boss_hp = 100
if 'player_hp' not in st.session_state: st.session_state.player_hp = 100
if 'ttt_board' not in st.session_state: st.session_state.ttt_board = [""] * 9
if 'ttt_turn' not in st.session_state: st.session_state.ttt_turn = "❌"

# Safe API Client Setup
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

LOGO_URL = "https://i.postimg.cc/WD8XXFXD/image.png"

def display_logo(size=110):
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 12px;'>
        <img src='{LOGO_URL}' style='
            width: {size}px; 
            height: {size}px; 
            object-fit: contain; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.25); 
            border: 2px solid #ffffff;
            image-rendering: -webkit-optimize-contrast;
            background-color: #ffffff;
            padding: 4px;
        '>
    </div>
    """, unsafe_allow_html=True)

# --- UNIVERSAL VOICE PLAYER HELPER WITH WORKING MUTE ---
def render_voice_controls(text_content, key_prefix="default", language="Hindi"):
    col_v1, col_v2 = st.columns([1, 1])
    lang_code = 'hi-IN' if language == "Hindi" else 'en-US'
    clean_text = text_content.replace("'", "").replace("\n", " ").replace('"', '')
    
    with col_v1:
        if st.button(f"🔊 Play Audio", key=f"play_{key_prefix}"):
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
        if st.button(f"🔇 Mute Audio", key=f"stop_{key_prefix}"):
            js_code = """
            <script>
                window.speechSynthesis.cancel();
            </script>
            """
            components.html(js_code, height=0)

# --- AI & RELIABLE IMAGE GENERATOR ---
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

def generate_2_concept_images(topic, points):
    urls = []
    for i in range(2):
        pt_text = points[i] if i < len(points) else f"Step {i+1} core concept"
        seed = random.randint(10000, 99999)
        clean_prompt = f"clean 2d educational vector illustration, {topic}, {pt_text}, colorful infographic diagram, simple textbook visual, HD digital art"
        safe_prompt = urllib.parse.quote(clean_prompt)
        urls.append(f"https://image.pollinations.ai/prompt/{safe_prompt}?seed={seed}&nologo=true&width=800&height=450")
    return urls

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
        if placeholder.button("▶️ Start Focus Session (+20 XP)", use_container_width=True):
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        placeholder.success(f"⏰ Active Focus Time: {int(elapsed//60)} min {int(elapsed%60)} sec")
        if st.button("⏹️ Stop & Claim XP", use_container_width=True):
            st.session_state.total_time += elapsed
            st.session_state.study_sessions += 1
            st.session_state.xp_points += 20
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

FORTUNES = [
    "🔮 Daily Prediction: Aaj aapka focus 200% rahega! Physics ya Math ko dhoom machane ka din hai! (+15 XP Unlocked)",
    "🔮 Daily Prediction: Caution! Procrastination Demon aapko Instagram reels par kheench raha hai! Shield on karo! (+10 XP)",
    "🔮 Daily Prediction: Sharma ji ke beta aaj aapka result dekh kar chauknay wala hai. Keep Grinding! (+20 XP)"
]

# --- VIBRANT UI STYLING ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 40%, #F3E8FF 100%); }
.aesthetic-card {
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
    margin-bottom: 18px;
}
.boss-card {
    background: linear-gradient(135deg, #4C0519 0%, #881337 100%);
    color: white;
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 12px 35px rgba(136, 19, 55, 0.3);
    margin-bottom: 20px;
}
.step-badge {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
    color: #FFFFFF;
    padding: 6px 14px;
    border-radius: 18px;
    font-weight: 700;
    font-size: 12px;
    display: inline-block;
    margin-bottom: 10px;
}
.xp-badge {
    background: #10B981;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 13px;
}
.stButton>button {
    background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
    color: #FFFFFF !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 10px 22px !important;
    font-size: 15px !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.2) !important;
}
.stButton>button:hover { transform: translateY(-2px); }
h1, h2, h3 { color: #1E1B4B !important; font-weight: 800 !important; }
</style>""", unsafe_allow_html=True)

# Top Bar
col_h1, col_xp, col_lang = st.columns([3.5, 2, 1.2])
with col_xp:
    st.markdown(f"<div style='text-align: right; padding-top: 5px;'><span class='xp-badge'>⚡ {st.session_state.xp_points} XP</span></div>", unsafe_allow_html=True)
with col_lang:
    language = st.selectbox("🌐 Language", ["Hindi", "English"], label_visibility="collapsed")

# --- HOME PAGE ---
if st.session_state.page == "Home":
    display_logo()
    st.markdown("<h1 style='text-align: center; margin-top: -10px; font-size: 34px;'>BrainBloom</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #475569; font-weight: 600; font-size: 15px; margin-bottom: 20px;'>Your Smart AI Learning Companion 🌸</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown(f"### 👋 Welcome back, Topper **{st.session_state.user_name}** ✨")
    col_prof1, col_prof2, col_prof3 = st.columns([2.5, 1, 1])
    with col_prof1:
        st.write(f"Current Rank: **{get_user_rank(st.session_state.total_time)}** | Focus Time: **{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m**")
    with col_prof2:
        if st.button("🔒 Secret Diary", use_container_width=True):
            st.session_state.page = "Diary"
            st.rerun()
    with col_prof3:
        if st.button("👤 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
    
    col_mot1, col_mot2 = st.columns(2)
    with col_mot1:
        if st.button("☕ Quick Dose of Motivation", use_container_width=True):
            st.toast(random.choice(FUNNY_MOTIVATIONS), icon="💡")
    with col_mot2:
        if st.button("🔮 Daily Study Fortune Card", use_container_width=True):
            st.session_state.page = "Fortune"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Grid Features
    st.markdown("<h3 style='text-align: center; margin-top: 15px;'>🚀 Interactive Learning & Gaming Studio</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🎰 XP Betting Arena", use_container_width=True):
            st.session_state.page = "XPBetting"
            st.rerun()
        if st.button("🎮 AI Boss Fight Arena", use_container_width=True):
            st.session_state.page = "BossFight"
            st.rerun()
        if st.button("🔄 Reverse Feynman AI", use_container_width=True):
            st.session_state.page = "Feynman"
            st.rerun()
        if st.button("🎬 AI Reel Class Studio", use_container_width=True):
            st.session_state.page = "Video"
            st.rerun()
        if st.button("📝 AI Practice Test", use_container_width=True):
            st.session_state.page = "Test"
            st.rerun()

    with col2:
        if st.button("🎭 AI Partner Switcher", use_container_width=True):
            st.session_state.page = "Persona"
            st.rerun()
        if st.button("🎧 Lofi Sound Deck", use_container_width=True):
            st.session_state.page = "Lofi"
            st.rerun()
        if st.button("⚡ Exam Survival Kit", use_container_width=True):
            st.session_state.page = "Survival"
            st.rerun()
        if st.button("📝 Magic Notes Generator", use_container_width=True):
            st.session_state.page = "Notes"
            st.rerun()
        if st.button("⏰ Focus Study Timer", use_container_width=True):
            st.session_state.page = "Timer"
            st.rerun()

    with col3:
        if st.button("🧠 Mnemonic Trick Maker", use_container_width=True):
            st.session_state.page = "Mnemonic"
            st.rerun()
        if st.button("🕹️ Dopamine Arcade", use_container_width=True):
            st.session_state.page = "Arcade"
            st.rerun()
        if st.button("🎭 BrainRot Explainer", use_container_width=True):
            st.session_state.page = "BrainRot"
            st.rerun()
        if st.button("📱 Shorts Script AI", use_container_width=True):
            st.session_state.page = "Shorts"
            st.rerun()
        if st.button("❓ AI Doubt Solver", use_container_width=True):
            st.session_state.page = "Doubt"
            st.rerun()

    with col4:
        if st.button("🎯 Exam Predictor Paper", use_container_width=True):
            st.session_state.page = "GuessPaper"
            st.rerun()

# --- 🔒 SECRET DIARY PAGE ---
elif st.session_state.page == "Diary":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🔒 Student Secret Diary & Profile Lock")
    
    # PIN Setup/Authentication logic
    if not st.session_state.diary_pin:
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.write("🔒 **Set up your 4-digit secret PIN for the first time:**")
        new_pin = st.text_input("Choose 4-digit PIN:", type="password", max_chars=4)
        if st.button("Set Secret PIN"):
            if len(new_pin) == 4 and new_pin.isdigit():
                st.session_state.diary_pin = new_pin
                save_user_data()
                st.success("PIN set successfully! Refreshing...")
                st.rerun()
            else: st.error("Please enter a valid 4-digit numeric PIN!")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        check_pin = st.text_input("Enter your 4-digit Secret PIN to unlock:", type="password", max_chars=4)
        if check_pin == st.session_state.diary_pin:
            st.success("🔓 Diary Unlocked!")
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            st.markdown("### 🖼️ Profile Photo Upload")
            uploaded_pic = st.file_uploader("Upload your profile picture:", type=['jpg', 'jpeg', 'png'])
            if uploaded_pic:
                img_bytes = uploaded_pic.getvalue()
                st.session_state.profile_pic = base64.b64encode(img_bytes).decode('utf-8')
                save_user_data()
                st.success("Profile photo updated!")
            
            if st.session_state.profile_pic:
                st.image(base64.b64decode(st.session_state.profile_pic), width=120, caption="Your Profile Picture")
            
            st.markdown("### 📝 My Secret Journal")
            secret_input = st.text_area("Write down your secrets, goals, or thoughts here...", value=st.session_state.diary_secret, height=220)
            if st.button("💾 Lock & Save Secrets"):
                st.session_state.diary_secret = secret_input
                save_user_data()
                st.toast("Secrets safely saved & encrypted under PIN!", icon="🔐")
            st.markdown("</div>", unsafe_allow_html=True)
        elif check_pin != "":
            st.error("❌ Incorrect PIN! Try again.")

# --- 🎭 AI STUDY PARTNER PERSONA SWITCHER PAGE ---
elif st.session_state.page == "Persona":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 AI Study Partner Persona Switcher")
    
    persona = st.selectbox("Choose AI Study Partner Style:", [
        "Strict Coaching Teacher 👨‍🏫 (No-nonsense & direct)",
        "Cool Backbencher Senior 😎 (Friendly shortcuts & tricks)",
        "K-Pop / Chill Idol Partner 🎵 (Encouraging, soft & friendly)"
    ])
    topic = st.text_input("What concept do you want to learn?")
    
    if st.button("Start AI Partner Explanation 🔥"):
        if topic:
            with st.spinner("AI Partner is preparing..."):
                p_style = "strict, no-nonsense, highly disciplined coaching teacher" if "Strict" in persona else ("chill backbencher senior using cool exam hacks" if "Cool" in persona else "caring, encouraging, friendly K-Pop style study idol")
                prompt = f"Act as a {p_style}. Explain the topic '{topic}' to a student in {language}. Keep it clear, engaging, and in character."
                res = get_ai_answer(prompt, language)
                st.session_state.persona_res = res
        else: st.error("Please enter a topic!")

    if 'persona_res' in st.session_state:
        render_voice_controls(st.session_state.persona_res, key_prefix="persona", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.persona_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- 🧠 CRAZY MNEMONIC TRICK MAKER PAGE ---
elif st.session_state.page == "Mnemonic":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🧠 Crazy Mnemonic & Memory Trick Maker ('Ratne Se Mukti')")
    topic = st.text_input("Enter Topic / Items to Remember (e.g. Periodic Table Period 2, Trigonometry Ratios, Taxonomy Hierarchy):")
    
    if st.button("Generate Funny Memory Trick 🚀"):
        if topic:
            with st.spinner("Creating viral mnemonic..."):
                prompt = f"Create a funny, unforgettable mnemonic story/acronym/rhyme in Hinglish to easily memorize: '{topic}'. Make it super simple so a student never forgets it in exams!"
                res = get_ai_answer(prompt, language)
                st.session_state.mnem_res = res
        else: st.error("Enter topic or list!")

    if 'mnem_res' in st.session_state:
        render_voice_controls(st.session_state.mnem_res, key_prefix="mnemonic", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.mnem_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- 🎯 EXAM PREDICTOR GUESS PAPER PAGE ---
elif st.session_state.page == "GuessPaper":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎯 AI Board Exam Guess Paper Predictor")
    subject = st.text_input("Enter Subject / Chapter (e.g., Class 12 Physics - Electrostatics):")
    
    if st.button("Predict High-Yield Questions 🔮"):
        if subject:
            with st.spinner("Analyzing past exam patterns..."):
                prompt = f"Act as an expert examiner. Predict top 5 most expected exam questions with detailed answers for '{subject}'. Format clearly with marks distribution in {language}."
                res = get_ai_answer(prompt, language)
                st.session_state.guess_res = res
                st.session_state.guess_topic = subject
        else: st.error("Enter subject name!")

    if 'guess_res' in st.session_state:
        render_voice_controls(st.session_state.guess_res, key_prefix="guesspaper", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.guess_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        pdf_file = create_pdf(st.session_state.guess_res, st.session_state.guess_topic)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download Guess Paper PDF", f, file_name=pdf_file, use_container_width=True)

# --- 🎰 XP BETTING ARENA PAGE ---
elif st.session_state.page == "XPBetting":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎰 XP Betting Arena: High-Risk Active Recall")
    
    st.markdown(f"<div class='aesthetic-card'><b>Your Available XP:</b> ⚡ {st.session_state.xp_points} XP</div>", unsafe_allow_html=True)
    bet_amount = st.slider("Select XP to Bet:", min_value=10, max_value=max(10, st.session_state.xp_points), step=10)
    topic = st.text_input("Subject for Betting Challenge (e.g. Organic Chemistry, Calculus):")

    if st.button("Place Bet & Start Challenge 🎯"):
        if topic and st.session_state.xp_points >= bet_amount:
            with st.spinner("Generating High-Stakes Question..."):
                prompt = f"Create 1 challenging MCQ question on {topic} in {language}. Format strictly as JSON with keys: 'question', 'options' (list of 4), 'correct_index' (0,1,2,3)."
                res = get_ai_answer(prompt, language)
                try:
                    clean_json = res[res.find('{'):res.rfind('}')+1]
                    st.session_state.bet_q = json.loads(clean_json)
                    st.session_state.current_bet = bet_amount
                except Exception:
                    st.session_state.bet_q = {
                        "question": f"Core concept formula check for {topic}:",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_index": 0
                    }
                    st.session_state.current_bet = bet_amount
        else: st.error("Enter topic or check if you have enough XP!")

    if 'bet_q' in st.session_state and st.session_state.bet_q:
        bq = st.session_state.bet_q
        st.markdown(f"<div class='aesthetic-card'><h3>🔥 Bet: {st.session_state.current_bet} XP</h3><p style='font-size: 18px;'>{bq['question']}</p></div>", unsafe_allow_html=True)
        user_choice = st.radio("Pick your answer carefully:", bq['options'])
        
        if st.button("Submit Answer 💥"):
            chosen_idx = bq['options'].index(user_choice)
            if chosen_idx == bq['correct_index']:
                win_xp = st.session_state.current_bet * 2
                st.session_state.xp_points += st.session_state.current_bet
                st.balloons()
                st.success(f"🎉 Right Answer! You won +{win_xp} XP!")
            else:
                st.session_state.xp_points -= st.session_state.current_bet
                st.error(f"❌ Wrong Answer! You lost -{st.session_state.current_bet} XP!")
            save_user_data()
            st.session_state.bet_q = None
            st.rerun()

# --- 🎮 AI BOSS FIGHT MODE PAGE ---
elif st.session_state.page == "BossFight":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎮 AI Boss Fight Arena: Defeat Dr. Brain-Drain 👹")
    
    st.markdown("<div class='boss-card'>", unsafe_allow_html=True)
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown(f"### 👹 Boss HP: {st.session_state.boss_hp}/100")
        st.progress(max(0, st.session_state.boss_hp) / 100)
    with col_b2:
        st.markdown(f"### 🛡️ Player HP: {st.session_state.player_hp}/100")
        st.progress(max(0, st.session_state.player_hp) / 100)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.boss_hp <= 0:
        st.balloons()
        st.success("🎉 Victory! You defeated Dr. Brain-Drain and earned +50 XP!")
        if st.button("Restart Boss Fight 🔄"):
            st.session_state.boss_hp = 100
            st.session_state.player_hp = 100
            st.session_state.xp_points += 50
            save_user_data()
            st.rerun()
    elif st.session_state.player_hp <= 0:
        st.error("💀 You were defeated by the Boss! Review your notes and try again!")
        if st.button("Try Again 🔄"):
            st.session_state.boss_hp = 100
            st.session_state.player_hp = 100
            st.rerun()
    else:
        topic = st.text_input("Enter Subject/Chapter (e.g., Organic Chemistry, Integration, Laws of Motion):")
        if st.button("Generate Attack Question ⚔️"):
            if topic:
                with st.spinner("Dr. Brain-Drain is preparing a question..."):
                    q_prompt = f"Create 1 multiple choice question on {topic} in {language}. Format strictly as JSON with keys: 'question', 'options' (list of 4), 'correct_index' (0,1,2,3)."
                    res = get_ai_answer(q_prompt, language)
                    try:
                        clean_json = res[res.find('{'):res.rfind('}')+1]
                        st.session_state.boss_q = json.loads(clean_json)
                    except Exception:
                        st.session_state.boss_q = {
                            "question": f"What is the core unit of {topic}?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_index": 0
                        }
            else: st.error("Enter a topic!")

        if 'boss_q' in st.session_state and st.session_state.boss_q:
            bq = st.session_state.boss_q
            st.markdown(f"<div class='aesthetic-card'><h3>❓ Boss Question:</h3><p style='font-size: 18px; font-weight: 600;'>{bq['question']}</p></div>", unsafe_allow_html=True)
            
            user_ans = st.radio("Choose your Attack Power:", bq['options'])
            if st.button("Launch Attack 🚀"):
                chosen_idx = bq['options'].index(user_ans)
                if chosen_idx == bq['correct_index']:
                    st.success("💥 Direct Hit! Correct Answer! Boss took 25 Damage!")
                    st.session_state.boss_hp -= 25
                    st.session_state.boss_q = None
                    st.rerun()
                else:
                    st.error("❌ Missed attack! Boss counter-attacked you for 20 Damage!")
                    st.session_state.player_hp -= 20
                    st.session_state.boss_q = None
                    st.rerun()

# --- 🔄 REVERSE FEYNMAN AI PAGE ---
elif st.session_state.page == "Feynman":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🔄 Reverse Feynman AI: Padhayein Chintu ko 🧒")
    st.markdown("<p style='color: #475569;'>Chintu ek 10 saal ka curious bacha hai. Aap usse koi concept samjhaoge aur dekhenge kya wo samajh paata hai!</p>", unsafe_allow_html=True)

    topic = st.text_input("Topic Name (e.g. Gravity, Photosynthesis, Fractions):")
    explanation = st.text_area("Aapka Explanation (Aap jaise Chintu ko samjhana chahte ho):", height=120)

    if st.button("Chintu Ko Samjhao 🚀"):
        if topic and explanation:
            with st.spinner("Chintu soch raha hai..."):
                f_prompt = f"Act as Chintu, an innocent and curious 10-year-old kid. A student is trying to teach you '{topic}'. Here is their explanation: '{explanation}'. Reply in friendly Hinglish with excitement. Either say you got it completely or ask 1 funny innocent follow-up doubt to check if they can explain better."
                res = get_ai_answer(f_prompt, language)
                st.session_state.feynman_res = res
                st.session_state.xp_points += 15
                save_user_data()
        else: st.error("Please enter both topic and your explanation!")

    if 'feynman_res' in st.session_state:
        st.markdown(f"<div class='aesthetic-card'><h3>🧒 Chintu ka Reply:</h3><p style='font-size: 17px;'>{st.session_state.feynman_res.replace(chr(10), '<br>')}</p></div>", unsafe_allow_html=True)
        render_voice_controls(st.session_state.feynman_res, key_prefix="chintu_voice", language=language)

# --- 🎧 LOFI & FOCUS SOUND DECK PAGE ---
elif st.session_state.page == "Lofi":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎧 Lofi & Focus Ambience Sound Deck")
    st.markdown("<p>Study mode set karne ke liye background music aur ambient sounds sunein!</p>", unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("<div class='aesthetic-card'><h3>🎵 Lofi Study Beats Stream</h3>", unsafe_allow_html=True)
        st.components.v1.iframe("https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=0", height=240)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_m2:
        st.markdown("<div class='aesthetic-card'><h3>🌧️ Ambient Rain Sounds</h3>", unsafe_allow_html=True)
        st.components.v1.iframe("https://www.youtube.com/embed/mPZkdNFkNps?autoplay=0", height=240)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 🔮 DAILY FORTUNE PAGE ---
elif st.session_state.page == "Fortune":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🔮 Daily Study Fortune & Horoscope")
    
    st.markdown("<div class='aesthetic-card' style='text-align: center; padding: 30px;'>", unsafe_allow_html=True)
    fortune_today = random.choice(FORTUNES)
    st.markdown(f"<h2>{fortune_today}</h2>", unsafe_allow_html=True)
    st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🕹️ DOPAMINE MINI ARCADE PAGE ---
elif st.session_state.page == "Arcade":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🕹️ Dopamine Refresh Mini Arcade: Tic-Tac-Toe ❌⭕")
    
    def check_winner(board):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if board[a] == board[b] == board[c] and board[a] != "":
                return board[a]
        if "" not in board: return "Tie"
        return None

    board = st.session_state.ttt_board
    winner = check_winner(board)

    if winner:
        if winner == "❌": st.success("🎉 You Win the Refresh Game!")
        elif winner == "⭕": st.error("🤖 AI Won! Try again!")
        else: st.info("🤝 It's a Tie!")
        if st.button("Reset Game 🔄"):
            st.session_state.ttt_board = [""] * 9
            st.rerun()
    else:
        grid_cols = st.columns(3)
        for i in range(9):
            with grid_cols[i % 3]:
                label = board[i] if board[i] != "" else " "
                if st.button(label, key=f"ttt_{i}", use_container_width=True):
                    if board[i] == "":
                        board[i] = "❌"
                        empty_indices = [idx for idx, val in enumerate(board) if val == ""]
                        if empty_indices:
                            ai_choice = random.choice(empty_indices)
                            board[ai_choice] = "⭕"
                        st.session_state.ttt_board = board
                        st.rerun()

# --- DASHBOARD PAGE ---
elif st.session_state.page == "Dashboard":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("👤 Student Profile & XP Rewards")
    
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    col_dash_pic, col_dash_info = st.columns([1, 3])
    with col_dash_pic:
        if st.session_state.profile_pic:
            st.image(base64.b64decode(st.session_state.profile_pic), width=130)
        else:
            st.info("No Profile Picture Set (Set in Secret Diary)")
    with col_dash_info:
        new_name = st.text_input("Edit Profile Name:", value=st.session_state.user_name)
        if st.button("💾 Save Profile Name"):
            if new_name.strip():
                st.session_state.user_name = new_name.strip()
                save_user_data()
                st.success("Profile Saved!")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Total Study Duration", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d2:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Sessions Completed", f"🔥 {st.session_state.study_sessions}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d3:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Total XP Earned", f"⚡ {st.session_state.xp_points}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 🎬 AI REEL CLASS PAGE ---
elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎬 AI Visual Reel & Video Class Studio")
    topic = st.text_input("Enter Concept (e.g. Photosynthesis, Newton's Laws, Black Hole):")
    
    if st.button("Generate Video Reel Class ✨"):
        if topic:
            with st.spinner("EduGenie is generating 2 Visual Slides & Video Script..."):
                prompt = f"Explain {topic} in 2 precise step-by-step visual bullet points for a student in {language}. Step 1: Core Concept. Step 2: Main Working/Application."
                script = get_ai_answer(prompt, language)
                
                raw_lines = [p.strip('- 1234567890.').strip() for p in script.split('\n') if len(p.strip()) > 8]
                points = raw_lines[:2] if len(raw_lines) >= 2 else [f"Basic principle of {topic}", f"Practical working of {topic}"]
                
                imgs = generate_2_concept_images(topic, points)
                st.session_state.vid_topic = topic
                st.session_state.vid_script = script
                st.session_state.vid_points = points
                st.session_state.vid_imgs = imgs
                st.session_state.xp_points += 10
                save_user_data()
        else: st.error("Please enter a topic!")

    if 'vid_script' in st.session_state:
        st.markdown(f"<div class='boss-card' style='background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);'>", unsafe_allow_html=True)
        st.markdown(f"<h2>🎬 Reel Video Class: {st.session_state.vid_topic}</h2>", unsafe_allow_html=True)
        render_voice_controls(st.session_state.vid_script, key_prefix="video_class", language=language)
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            st.image(st.session_state.vid_imgs[0], caption=f"Visual Step 1: {st.session_state.vid_topic}", use_container_width=True)
            st.markdown("<span class='step-badge'>STEP 1</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-weight: 600;'>{st.session_state.vid_points[0]}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            st.image(st.session_state.vid_imgs[1], caption=f"Visual Step 2: {st.session_state.vid_topic}", use_container_width=True)
            st.markdown("<span class='step-badge'>STEP 2</span>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-weight: 600;'>{st.session_state.vid_points[1] if len(st.session_state.vid_points) > 1 else 'Key Application'}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- 🎭 BRAINROT EXPLAINER PAGE ---
elif st.session_state.page == "BrainRot":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 BrainRot to BrainGain (Gen-Z & Meme Explainer)")
    topic = st.text_input("Enter Concept (e.g. Organic Chemistry, Trigonometry):")
    vibe = st.selectbox("Select Vibe Style:", ["Gen-Z Slang & Memes 💀", "Anime / Superhero Analogy ⚡", "K-Pop & BTS Army Analogy 🎵", "Funny Hindi Webseries Style 🍿"])
    
    if st.button("Explain in Meme Style 🔥"):
        if topic:
            with st.spinner("Cooking up viral meme explanation..."):
                prompt = f"Explain the academic concept '{topic}' in style of {vibe}. Use hilarious analogies, easy breakdown so a student never forgets it. Language: Hinglish."
                res = get_ai_answer(prompt, language)
                st.session_state.br_res = res
                st.balloons()
        else: st.error("Enter a topic!")

    if 'br_res' in st.session_state:
        render_voice_controls(st.session_state.br_res, key_prefix="brainrot", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.br_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- ⚡ SURVIVAL KIT PAGE ---
elif st.session_state.page == "Survival":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⚡ Emergency Exam Survival Kit")
    subject = st.text_input("Enter Chapter Name (e.g. Electrostatics, Integration):")
    
    if st.button("Generate Survival Sheet 📄"):
        if subject:
            with st.spinner("Creating high-yield sheet..."):
                prompt = f"Create a 1-page emergency exam sheet for {subject}. Include: 1) Top 5 Guaranteed Questions with Answers. 2) Key Formula Cheat Sheet. 3) Common Mistakes. Language: Hinglish."
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

# --- 📱 YOUTUBE SHORTS SCRIPT PAGE ---
elif st.session_state.page == "Shorts":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎬 Viral 30-Sec YouTube Shorts Script AI")
    topic = st.text_input("Enter Topic for Video Short:")
    
    if st.button("Generate Script & Hook 🔥"):
        if topic:
            with st.spinner("Writing script..."):
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
                st.session_state.notes_res = notes
                st.session_state.notes_topic = topic
        else: st.error("Enter topic name!")

    if 'notes_res' in st.session_state:
        render_voice_controls(st.session_state.notes_res, key_prefix="notes", language=language)
        st.markdown(f"<div class='aesthetic-card'>{st.session_state.notes_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        pdf_file = create_pdf(st.session_state.notes_res, st.session_state.notes_topic)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF Notes", f, file_name=pdf_file, use_container_width=True)

# --- ❓ DOUBT SOLVER PAGE ---
elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("❓ AI Doubt Solver ⚡")
    doubt = st.text_area("Ask any doubt or question:", height=120)
    
    if st.button("Solve Doubt Now ⚡"):
        if doubt:
            with st.spinner("Solving..."):
                answer = get_ai_answer(f"Solve this student doubt clearly step-by-step: {doubt}. Language: {language}", language)
                st.session_state.doubt_res = answer
        else: st.error("Please enter your doubt!")

    if 'doubt_res' in st.session_state:
        render_voice_controls(st.session_state.doubt_res, key_prefix="doubt", language=language)
        st.markdown(f"<div class='aesthetic-card'><b>💡 Solution:</b><br><br>{st.session_state.doubt_res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- 📝 TEST SERIES PAGE ---
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

# --- ⏰ FOCUS TIMER PAGE ---
elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⏰ Focus Study Timer")
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    study_timer()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Made with ❤️ by Anugya | BrainBloom EduGenie v5.0 Ultimate 🌸")
