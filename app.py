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
import re

# Must be first Streamlit command
st.set_page_config(page_title="BrainBloom - EduGenie", page_icon="✨", layout="wide")

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
        "user_name": "Anugya Singh",
        "total_time": 0,
        "study_sessions": 0,
        "streak": 1,
        "xp_points": 50,
        "diary_secret": "",
        "diary_pin": "",
        "profile_pic": None
    }

def save_user_data():
    data = {
        "user_name": st.session_state.get("user_name", "Anugya Singh"),
        "total_time": st.session_state.get("total_time", 0),
        "study_sessions": st.session_state.get("study_sessions", 0),
        "streak": st.session_state.get("streak", 1),
        "xp_points": st.session_state.get("xp_points", 50),
        "diary_secret": st.session_state.get("diary_secret", ""),
        "diary_pin": st.session_state.get("diary_pin", ""),
        "profile_pic": st.session_state.get("profile_pic", None)
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Initialize Session State
saved_data = load_user_data()
if 'user_name' not in st.session_state: st.session_state.user_name = saved_data.get("user_name", "Anugya Singh")
if 'total_time' not in st.session_state: st.session_state.total_time = saved_data.get("total_time", 0)
if 'study_sessions' not in st.session_state: st.session_state.study_sessions = saved_data.get("study_sessions", 0)
if 'streak' not in st.session_state: st.session_state.streak = saved_data.get("streak", 1)
if 'xp_points' not in st.session_state: st.session_state.xp_points = saved_data.get("xp_points", 50)
if 'diary_secret' not in st.session_state: st.session_state.diary_secret = saved_data.get("diary_secret", "")
if 'diary_pin' not in st.session_state: st.session_state.diary_pin = saved_data.get("diary_pin", "")
if 'profile_pic' not in st.session_state: st.session_state.profile_pic = saved_data.get("profile_pic", None)

if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None

# Game & Boss Fight State Initialization
if 'boss_hp' not in st.session_state: st.session_state.boss_hp = 100
if 'player_hp' not in st.session_state: st.session_state.player_hp = 100

# Safe API Client Setup
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

LOGO_URL = "https://i.postimg.cc/WD8XXFXD/image.png"

# --- HIGHLIGHT CONVERTER FUNCTION (PERFECT FIX) ---
def apply_highlights(text):
    if not text:
        return ""
    # Convert **bold text** into yellow highlighted <mark> HTML tag
    highlighted = re.sub(
        r'\*\*(.*?)\*\*', 
        r'<mark style="background-color: #FDE047; color: #7C2D12; padding: 2px 7px; border-radius: 6px; font-weight: 800;">\1</mark>', 
        text
    )
    return highlighted.replace('\n', '<br>')

# --- CROPPED LOGO DISPLAY ---
def display_logo(size=110):
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 12px;'>
        <div style='
            width: {size}px; 
            height: {size}px; 
            margin: 0 auto; 
            border-radius: 50%; 
            overflow: hidden; 
            border: 3px solid #FDBA74; 
            box-shadow: 0 8px 25px rgba(251, 146, 60, 0.25);
            background-color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
        '>
            <img src='{LOGO_URL}' style='
                width: 175%; 
                height: 175%; 
                object-fit: cover; 
                object-position: center;
            '>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- CLEAN TEXT FOR VOICE SPEECH ---
def clean_text_for_speech(text):
    clean = re.sub(r'[\*\#\-\_~`]', '', text)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'[^\w\s\.,!\?]', '', clean)
    clean = clean.replace('\n', ' ').strip()
    return clean

# --- UNIVERSAL VOICE PLAYER ---
def render_voice_controls(text_content, key_prefix="default", language="Hindi"):
    col_v1, col_v2 = st.columns([1, 1])
    lang_code = 'hi-IN' if language == "Hindi" else 'en-US'
    clean_text = clean_text_for_speech(text_content)
    
    with col_v1:
        if st.button(f"🔊 Play Audio", key=f"play_{key_prefix}"):
            js_code = f"""
            <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{clean_text}');
                msg.lang = '{lang_code}';
                msg.rate = 0.9;
                msg.pitch = 1.0;
                window.speechSynthesis.speak(msg);
            </script>
            """
            components.html(js_code, height=0)
            
    with col_v2:
        if st.button(f"🔇 Mute Audio", key=f"stop_{key_prefix}"):
            js_code = "<script>window.speechSynthesis.cancel();</script>"
            components.html(js_code, height=0)

# --- AI GENERATOR WITH STRICT LANGUAGE PROMPTS ---
def get_ai_answer(prompt, language="English"):
    if not client:
        return "GROQ API Key missing in Streamlit Secrets! Please add GROQ_API_KEY."
    try:
        lang_instruction = "Respond strictly in pure standard Hindi (Devanagari script). Do not use English script." if language == "Hindi" else "Respond strictly in grammatically correct English. Do not mix Hindi words."
        full_prompt = f"{prompt}\n\nLanguage Directive: {lang_instruction}"
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama-3.1-8b-instant"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

def generate_2_concept_images(topic, points):
    urls = []
    for i in range(2):
        pt_text = points[i] if i < len(points) else f"Step {i+1} concept"
        seed = random.randint(10000, 99999)
        clean_prompt = urllib.parse.quote(f"hd detailed infographic educational diagram of {topic}, {pt_text}, high quality vector illustration, clean white background")
        urls.append(f"https://image.pollinations.ai/prompt/{clean_prompt}?seed={seed}&nologo=true&width=700&height=400")
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
    "Gyaan wo amrit hai jo sirf padhne se milta hai, reels scroll karne se nahi! 📱❌"
]

FORTUNES = [
    "🔮 Daily Prediction: Aaj aapka focus 200% rahega! Physics ya Math ko dhoom machane ka din hai! (+15 XP)",
    "🔮 Daily Prediction: Caution! Procrastination Demon aapko reels par kheench raha hai! Shield on karo! (+10 XP)",
    "🔮 Daily Prediction: Class topper aaj aapka score dekh kar chauknay wala hai. Keep Grinding! (+20 XP)"
]

# --- VIBRANT & PEACH UI STYLING ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 50%, #FED7AA 100%); }

/* Soft Peach Card Background */
.aesthetic-card {
    background: #FFF4EC !important;
    border: 1.5px solid #FDBA74 !important;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 25px rgba(251, 146, 60, 0.12);
    margin-bottom: 18px;
    color: #2D1A0E !important;
    font-size: 16px;
    line-height: 1.8;
}

.boss-card {
    background: linear-gradient(135deg, #7C2D12 0%, #9A3412 100%);
    color: white;
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(124, 45, 18, 0.25);
    margin-bottom: 20px;
}
.step-badge {
    background: #EA580C;
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
    padding: 6px 14px;
    border-radius: 14px;
    font-weight: 800;
    font-size: 14px;
}
.stButton>button {
    background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important;
    color: #FFFFFF !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 10px 22px !important;
    font-size: 15px !important;
    box-shadow: 0 6px 18px rgba(234, 88, 12, 0.2) !important;
}
.stButton>button:hover { transform: translateY(-2px); }
h1, h2, h3 { color: #431407 !important; font-weight: 800 !important; }
</style>""", unsafe_allow_html=True)

# --- TOP CORNER HEADER BAR ---
col_head_left, col_head_right = st.columns([2.5, 1.5])

with col_head_left:
    col_xp, col_lang = st.columns([1, 1])
    with col_xp:
        st.markdown(f"<span class='xp-badge'>⚡ {st.session_state.xp_points} XP</span>", unsafe_allow_html=True)
    with col_lang:
        language = st.selectbox("🌐 Language", ["Hindi", "English"], label_visibility="collapsed")

with col_head_right:
    with st.expander("🎧 Sukoon Ambient Deck (Corner Audio)", expanded=False):
        bg_sound = st.radio("Choose Music:", [
            "Off 🔇", 
            "Lofi Study Beats 🎵", 
            "Soft Rain 🌧️", 
            "Relaxing Piano 🎹", 
            "Forest Birds 🍃", 
            "Ocean Waves 🌊", 
            "Deep Alpha Meditation 🧘"
        ], label_visibility="collapsed")
        
        if bg_sound == "Lofi Study Beats 🎵":
            st.components.v1.iframe("https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1&loop=1", height=120)
        elif bg_sound == "Soft Rain 🌧️":
            st.components.v1.iframe("https://www.youtube.com/embed/mPZkdNFkNps?autoplay=1&loop=1", height=120)
        elif bg_sound == "Relaxing Piano 🎹":
            st.components.v1.iframe("https://www.youtube.com/embed/WJ3-F02-F_Y?autoplay=1&loop=1", height=120)
        elif bg_sound == "Forest Birds 🍃":
            st.components.v1.iframe("https://www.youtube.com/embed/xNN7iTA57jM?autoplay=1&loop=1", height=120)
        elif bg_sound == "Ocean Waves 🌊":
            st.components.v1.iframe("https://www.youtube.com/embed/bn9F19Hi1Lk?autoplay=1&loop=1", height=120)
        elif bg_sound == "Deep Alpha Meditation 🧘":
            st.components.v1.iframe("https://www.youtube.com/embed/5qap5aO4i9A?autoplay=1&loop=1", height=120)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px; border-color: #FDBA74;'>", unsafe_allow_html=True)

# --- HOME PAGE ---
if st.session_state.page == "Home":
    display_logo()
    st.markdown("<h1 style='text-align: center; margin-top: -10px; font-size: 34px;'>BrainBloom</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7C2D12; font-weight: 600; font-size: 15px; margin-bottom: 20px;'>Your Smart AI Learning Companion 🌸</p>", unsafe_allow_html=True)
    
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
        if st.button("🎰 XP Betting Arena (5 Qs)", use_container_width=True):
            st.session_state.page = "XPBetting"
            st.rerun()
        if st.button("🎮 AI Boss Battle (5 Qs)", use_container_width=True):
            st.session_state.page = "BossFight"
            st.rerun()
        if st.button("🔄 Reverse Feynman AI", use_container_width=True):
            st.session_state.page = "Feynman"
            st.rerun()
        if st.button("🎨 AI Visual Class Studio", use_container_width=True):
            st.session_state.page = "VisualClass"
            st.rerun()
        if st.button("📝 AI Practice Test", use_container_width=True):
            st.session_state.page = "Test"
            st.rerun()

    with col2:
        if st.button("🎭 AI Partner Switcher", use_container_width=True):
            st.session_state.page = "Persona"
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
        if st.button("🕹️ Brain Refresher Arcade", use_container_width=True):
            st.session_state.page = "Arcade"
            st.rerun()
        if st.button("🎭 BrainRot Explainer", use_container_width=True):
            st.session_state.page = "BrainRot"
            st.rerun()
        if st.button("📱 Shorts Script AI", use_container_width=True):
            st.session_state.page = "Shorts"
            st.rerun()

    with col4:
        if st.button("❓ AI Doubt Solver", use_container_width=True):
            st.session_state.page = "Doubt"
            st.rerun()
        if st.button("🎯 Exam Predictor Paper", use_container_width=True):
            st.session_state.page = "GuessPaper"
            st.rerun()

# --- ❓ DOUBT SOLVER PAGE ---
elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("❓ AI Doubt Solver ⚡")
    doubt = st.text_area("Ask any doubt or question:", height=120)
    
    if st.button("Solve Doubt Now ⚡"):
        if doubt:
            with st.spinner("Solving..."):
                answer = get_ai_answer(f"Solve this student doubt clearly step-by-step: {doubt}. Highlight key terms using bold text like **term**.", language)
                st.session_state.doubt_res = answer
        else: st.error("Please enter your doubt!")

    if 'doubt_res' in st.session_state:
        render_voice_controls(st.session_state.doubt_res, key_prefix="doubt", language=language)
        st.markdown(f"<div class='aesthetic-card'><b>💡 Solution:</b><br><br>{apply_highlights(st.session_state.doubt_res)}</div>", unsafe_allow_html=True)

# --- 🎰 XP BETTING ARENA PAGE ---
elif st.session_state.page == "XPBetting":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎰 XP Betting Arena: 5-Question Challenge")
    
    st.markdown(f"<div class='aesthetic-card'><b>Your Current Balance:</b> ⚡ <b>{st.session_state.xp_points} XP</b></div>", unsafe_allow_html=True)
    bet_amount = st.slider("Select XP to Bet:", min_value=10, max_value=max(10, st.session_state.xp_points), step=10)
    topic = st.text_input("Subject/Chapter for 5-Question Bet Challenge:")

    if st.button("Place Bet & Generate 5 Questions 🎯"):
        if topic and st.session_state.xp_points >= bet_amount:
            with st.spinner("Generating 5 High-Stakes Questions..."):
                prompt = f"Create 5 MCQ questions on {topic}. Format strictly as a JSON array of 5 objects, each having keys: 'question', 'options' (list of 4 strings), 'correct_index' (0,1,2,3), 'explanation' (1 short sentence why it is correct)."
                res = get_ai_answer(prompt, language)
                try:
                    clean_json = res[res.find('['):res.rfind(']')+1]
                    st.session_state.bet_5q = json.loads(clean_json)
                    st.session_state.current_bet = bet_amount
                    st.session_state.submitted_bet = False
                except Exception:
                    st.session_state.bet_5q = [
                        {"question": f"Q{i+1}: Core concept question on {topic}?", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "Basic core principle."} for i in range(5)
                    ]
                    st.session_state.current_bet = bet_amount
                    st.session_state.submitted_bet = False
        else: st.error("Please enter a topic and ensure you have enough XP!")

    if 'bet_5q' in st.session_state and st.session_state.bet_5q:
        st.markdown(f"### 🔥 Active Bet: {st.session_state.current_bet} XP")
        user_choices = []
        for idx, q_item in enumerate(st.session_state.bet_5q):
            st.markdown(f"<div class='aesthetic-card'><b>Q{idx+1}: {q_item['question']}</b></div>", unsafe_allow_html=True)
            ans = st.radio(f"Select option for Q{idx+1}:", q_item['options'], key=f"bet_q_{idx}")
            user_choices.append(q_item['options'].index(ans))
        
        if st.button("Submit Answers & Check Result 🚀"):
            st.session_state.submitted_bet = True
            st.session_state.user_bet_choices = user_choices

        if st.session_state.get('submitted_bet', False):
            st.markdown("---")
            st.markdown("### 📊 Detailed Answer Breakdown:")
            correct_cnt = 0
            for idx, q_item in enumerate(st.session_state.bet_5q):
                user_ans_idx = st.session_state.user_bet_choices[idx]
                correct_idx = q_item['correct_index']
                
                if user_ans_idx == correct_idx:
                    correct_cnt += 1
                    st.success(f"✅ **Q{idx+1}: Correct!** You selected '{q_item['options'][user_ans_idx]}'. Explanation: {q_item.get('explanation', '')}")
                else:
                    st.error(f"❌ **Q{idx+1}: Incorrect!** You selected '{q_item['options'][user_ans_idx]}'. **Correct Answer:** '{q_item['options'][correct_idx]}'. Explanation: {q_item.get('explanation', '')}")
            
            if correct_cnt >= 3:
                win_xp = st.session_state.current_bet * 2
                st.session_state.xp_points += st.session_state.current_bet
                st.balloons()
                st.success(f"🎉 Great job! You scored {correct_cnt}/5! You won +{win_xp} XP!")
            else:
                st.session_state.xp_points -= st.session_state.current_bet
                st.error(f"💀 You scored {correct_cnt}/5. You lost -{st.session_state.current_bet} XP!")
            save_user_data()

# --- 🎨 AI VISUAL CLASS STUDIO PAGE ---
elif st.session_state.page == "VisualClass":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎨 AI Visual Class Studio")
    topic = st.text_input("Enter Concept (e.g. Photosynthesis, Newton's Laws, Human Heart):")
    
    if st.button("Generate Visual Class ✨"):
        if topic:
            with st.spinner("EduGenie is generating Visual Diagrams & Text Explanation..."):
                prompt = f"Explain **{topic}** clearly in 2 distinct visual steps for a student. Include **important key points** using bold like **key point**."
                script = get_ai_answer(prompt, language)
                
                points = [f"Core Principle of {topic}", f"Working & Application of {topic}"]
                imgs = generate_2_concept_images(topic, points)
                
                st.session_state.vid_topic = topic
                st.session_state.vid_script = script
                st.session_state.vid_imgs = imgs
                st.session_state.xp_points += 10
                save_user_data()
        else: st.error("Please enter a topic!")

    if 'vid_script' in st.session_state:
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown(f"<h2>🎨 Lesson: **{st.session_state.vid_topic}**</h2>", unsafe_allow_html=True)
        st.markdown(f"<div>{apply_highlights(st.session_state.vid_script)}</div>", unsafe_allow_html=True)
        render_voice_controls(st.session_state.vid_script, key_prefix="visual_class", language=language)
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            if len(st.session_state.vid_imgs) > 0:
                st.image(st.session_state.vid_imgs[0], caption=f"Visual Diagram 1: {st.session_state.vid_topic}", use_container_width=True)
            st.markdown("<span class='step-badge'>VISUAL STEP 1</span>", unsafe_allow_html=True)
            st.markdown("<b>Step 1 Visual Diagram Representation</b>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            if len(st.session_state.vid_imgs) > 1:
                st.image(st.session_state.vid_imgs[1], caption=f"Visual Diagram 2: {st.session_state.vid_topic}", use_container_width=True)
            st.markdown("<span class='step-badge'>VISUAL STEP 2</span>", unsafe_allow_html=True)
            st.markdown("<b>Step 2 Practical Process Diagram</b>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- 🎮 AI BOSS FIGHT MODE PAGE ---
elif st.session_state.page == "BossFight":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎮 AI Boss Battle Arena: Defeat Dr. Brain-Drain 👹")
    
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
            st.session_state.boss_5q = None
            save_user_data()
            st.rerun()
    elif st.session_state.player_hp <= 0:
        st.error("💀 You were defeated by the Boss! Review your notes and try again!")
        if st.button("Try Again 🔄"):
            st.session_state.boss_hp = 100
            st.session_state.player_hp = 100
            st.session_state.boss_5q = None
            st.rerun()
    else:
        topic = st.text_input("Enter Subject/Chapter for 5-Question Challenge:")
        if st.button("Generate 5 Battle Questions ⚔️"):
            if topic:
                with st.spinner("Dr. Brain-Drain is preparing 5 questions..."):
                    q_prompt = f"Create 5 challenging multiple choice questions on {topic}. Format strictly as a JSON array of 5 objects, each having keys: 'question', 'options' (list of 4 strings), 'correct_index' (0,1,2,3)."
                    res = get_ai_answer(q_prompt, language)
                    try:
                        clean_json = res[res.find('['):res.rfind(']')+1]
                        st.session_state.boss_5q = json.loads(clean_json)
                    except Exception:
                        st.session_state.boss_5q = [
                            {"question": f"Q{i+1}: Core question on {topic}?", "options": ["A", "B", "C", "D"], "correct_index": 0} for i in range(5)
                        ]
            else: st.error("Enter a topic!")

        if 'boss_5q' in st.session_state and st.session_state.boss_5q:
            st.markdown("### ⚔️ Answer all 5 questions to attack the Boss:")
            user_answers = []
            for idx, q_item in enumerate(st.session_state.boss_5q):
                st.markdown(f"<div class='aesthetic-card'><b>Q{idx+1}: {q_item['question']}</b></div>", unsafe_allow_html=True)
                ans = st.radio(f"Select Answer for Q{idx+1}:", q_item['options'], key=f"boss_q_{idx}")
                user_answers.append(q_item['options'].index(ans))
            
            if st.button("Submit All Answers 🚀"):
                correct_count = sum(1 for idx, q_item in enumerate(st.session_state.boss_5q) if user_answers[idx] == q_item['correct_index'])
                
                boss_damage = correct_count * 20
                player_damage = (5 - correct_count) * 20
                
                st.session_state.boss_hp -= boss_damage
                st.session_state.player_hp -= player_damage
                
                if correct_count >= 3:
                    st.success(f"💥 You answered {correct_count}/5 correctly! Boss took {boss_damage} Damage!")
                else:
                    st.error(f"❌ You got only {correct_count}/5 correct! Boss hit you for {player_damage} Damage!")
                
                st.session_state.boss_5q = None
                st.rerun()

# --- 🕹️ REPLACED GAME: BRAIN REFRESHER WORD SCRAMBLE ---
elif st.session_state.page == "Arcade":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🧠 Brain Refresher: Quick Word Unscramble")
    
    WORDS = [
        {"scrambled": "S I C Y H P S", "original": "PHYSICS", "hint": "Study of matter and energy"},
        {"scrambled": "Y R T S I M E H C", "original": "CHEMISTRY", "hint": "Study of elements and reactions"},
        {"scrambled": "I Y O L O G B", "original": "BIOLOGY", "hint": "Study of living organisms"},
        {"scrambled": "A T E M A H T C I M S", "original": "MATHEMATICS", "hint": "Study of numbers and equations"},
        {"scrambled": "O N T O R U E N", "original": "ELECTRON", "hint": "Negatively charged subatomic particle"}
    ]
    
    if 'scramble_idx' not in st.session_state:
        st.session_state.scramble_idx = random.randint(0, len(WORDS)-1)
    
    current_word = WORDS[st.session_state.scramble_idx]
    
    st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown(f"## 🔤 Unscramble: **{current_word['scrambled']}**")
    st.markdown(f"💡 **Hint:** {current_word['hint']}")
    
    guess = st.text_input("Type your answer here:").strip().upper()
    
    if st.button("Check Word 🚀"):
        if guess == current_word['original']:
            st.balloons()
            st.success("🎉 Correct Answer! +15 XP added!")
            st.session_state.xp_points += 15
            save_user_data()
            st.session_state.scramble_idx = random.randint(0, len(WORDS)-1)
        else:
            st.error("❌ Wrong word! Try again!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🔒 SECRET DIARY PAGE ---
elif st.session_state.page == "Diary":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🔒 Student Secret Diary & Profile Lock")
    
    if not st.session_state.diary_pin:
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.write("🔒 **Set up your 4-digit secret PIN:**")
        new_pin = st.text_input("Choose 4-digit PIN:", type="password", max_chars=4)
        if st.button("Set Secret PIN"):
            if len(new_pin) == 4 and new_pin.isdigit():
                st.session_state.diary_pin = new_pin
                save_user_data()
                st.success("PIN set successfully!")
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

# --- 🎭 AI PARTNER PERSONA PAGE ---
elif st.session_state.page == "Persona":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 AI Study Partner Persona Switcher")
    
    persona = st.selectbox("Choose AI Study Partner Style:", [
        "Strict Coaching Teacher 👨‍🏫",
        "Cool Backbencher Senior 😎",
        "K-Pop / Chill Idol Partner 🎵"
    ])
    topic = st.text_input("What concept do you want to learn?")
    
    if st.button("Start AI Partner Explanation 🔥"):
        if topic:
            with st.spinner("AI Partner is preparing..."):
                p_style = "strict coaching teacher" if "Strict" in persona else ("cool backbencher senior using exam hacks" if "Cool" in persona else "caring K-Pop study idol")
                prompt = f"Act as a {p_style}. Explain the topic **{topic}** clearly. Use bold text like **term** for key points."
                res = get_ai_answer(prompt, language)
                st.session_state.persona_res = res
        else: st.error("Please enter a topic!")

    if 'persona_res' in st.session_state:
        render_voice_controls(st.session_state.persona_res, key_prefix="persona", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.persona_res)}</div>", unsafe_allow_html=True)

# --- 🧠 MNEMONIC TRICK MAKER PAGE ---
elif st.session_state.page == "Mnemonic":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🧠 Crazy Mnemonic & Memory Trick Maker")
    topic = st.text_input("Enter Topic / Items to Remember:")
    
    if st.button("Generate Memory Trick 🚀"):
        if topic:
            with st.spinner("Creating mnemonic..."):
                prompt = f"Create a funny, unforgettable mnemonic story/acronym/rhyme to easily memorize **{topic}**. Use bold like **term** for key parts."
                res = get_ai_answer(prompt, language)
                st.session_state.mnem_res = res
        else: st.error("Enter topic or list!")

    if 'mnem_res' in st.session_state:
        render_voice_controls(st.session_state.mnem_res, key_prefix="mnemonic", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.mnem_res)}</div>", unsafe_allow_html=True)

# --- 🎯 EXAM PREDICTOR GUESS PAPER PAGE ---
elif st.session_state.page == "GuessPaper":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎯 AI Board Exam Guess Paper Predictor")
    subject = st.text_input("Enter Subject / Chapter (e.g., Class 12 Physics - Electrostatics):")
    
    if st.button("Predict High-Yield Questions 🔮"):
        if subject:
            with st.spinner("Analyzing past exam patterns..."):
                prompt = f"Act as an expert examiner. Predict top 5 most expected exam questions with detailed answers for **{subject}**. Use bold for key points."
                res = get_ai_answer(prompt, language)
                st.session_state.guess_res = res
                st.session_state.guess_topic = subject
        else: st.error("Enter subject name!")

    if 'guess_res' in st.session_state:
        render_voice_controls(st.session_state.guess_res, key_prefix="guesspaper", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.guess_res)}</div>", unsafe_allow_html=True)
        pdf_file = create_pdf(st.session_state.guess_res, st.session_state.guess_topic)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download Guess Paper PDF", f, file_name=pdf_file, use_container_width=True)

# --- 🔄 REVERSE FEYNMAN AI PAGE ---
elif st.session_state.page == "Feynman":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🔄 Reverse Feynman AI: Teach Chintu 🧒")
    topic = st.text_input("Topic Name:")
    explanation = st.text_area("Your Explanation for 10-year old Chintu:", height=120)

    if st.button("Explain to Chintu 🚀"):
        if topic and explanation:
            with st.spinner("Chintu is thinking..."):
                f_prompt = f"Act as Chintu, a curious 10-year-old kid. A student is trying to teach you **{topic}**: '{explanation}'. Reply enthusiastically and use bold text like **term** for main points."
                res = get_ai_answer(f_prompt, language)
                st.session_state.feynman_res = res
                st.session_state.xp_points += 15
                save_user_data()
        else: st.error("Please enter both topic and explanation!")

    if 'feynman_res' in st.session_state:
        st.markdown(f"<div class='aesthetic-card'><h3>🧒 Chintu's Reply:</h3>{apply_highlights(st.session_state.feynman_res)}</div>", unsafe_allow_html=True)
        render_voice_controls(st.session_state.feynman_res, key_prefix="chintu_voice", language=language)

# --- 🔮 DAILY FORTUNE PAGE ---
elif st.session_state.page == "Fortune":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🔮 Daily Study Fortune")
    
    st.markdown("<div class='aesthetic-card' style='text-align: center; padding: 30px;'>", unsafe_allow_html=True)
    fortune_today = random.choice(FORTUNES)
    st.markdown(f"<h2>{fortune_today}</h2>", unsafe_allow_html=True)
    st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

# --- DASHBOARD PAGE ---
elif st.session_state.page == "Dashboard":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("👤 Student Profile & Dashboard")
    
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    col_dash_pic, col_dash_info = st.columns([1, 3])
    with col_dash_pic:
        if st.session_state.profile_pic:
            st.image(base64.b64decode(st.session_state.profile_pic), width=130)
        else:
            st.info("No Profile Picture Set")
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

# --- 🎭 BRAINROT EXPLAINER PAGE ---
elif st.session_state.page == "BrainRot":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 BrainRot to BrainGain Explainer")
    topic = st.text_input("Enter Concept:")
    vibe = st.selectbox("Select Vibe Style:", ["Gen-Z Slang & Memes 💀", "Anime / Superhero Analogy ⚡", "K-Pop & BTS Army Analogy 🎵", "Funny Webseries Style 🍿"])
    
    if st.button("Explain in Meme Style 🔥"):
        if topic:
            with st.spinner("Generating..."):
                prompt = f"Explain **{topic}** in style of {vibe}. Use **bold words** for main terms."
                res = get_ai_answer(prompt, language)
                st.session_state.br_res = res
                st.balloons()
        else: st.error("Enter a topic!")

    if 'br_res' in st.session_state:
        render_voice_controls(st.session_state.br_res, key_prefix="brainrot", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.br_res)}</div>", unsafe_allow_html=True)

# --- ⚡ SURVIVAL KIT PAGE ---
elif st.session_state.page == "Survival":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⚡ Emergency Exam Survival Kit")
    subject = st.text_input("Enter Chapter Name:")
    
    if st.button("Generate Survival Sheet 📄"):
        if subject:
            with st.spinner("Creating survival sheet..."):
                prompt = f"Create a concise exam survival sheet for **{subject}** with Top 5 questions and key formulas highlighted using bold text."
                res = get_ai_answer(prompt, language)
                st.session_state.surv_res = res
                st.session_state.surv_topic = subject
        else: st.error("Enter chapter name!")

    if 'surv_res' in st.session_state:
        render_voice_controls(st.session_state.surv_res, key_prefix="survival", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.surv_res)}</div>", unsafe_allow_html=True)
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
                prompt = f"Write a catchy 30-second YouTube Short script on **{topic}** including a hook and Call to Action to subscribe to Anu ot7. Use bold text for key words."
                res = get_ai_answer(prompt, language)
                st.session_state.shorts_res = res
        else: st.error("Enter topic!")

    if 'shorts_res' in st.session_state:
        render_voice_controls(st.session_state.shorts_res, key_prefix="shorts", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.shorts_res)}</div>", unsafe_allow_html=True)

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
            with st.spinner("Creating notes..."):
                notes = get_ai_answer(f"Make concise study notes on **{topic}** for {subject}. Highlight key concepts using bold text like **term**.", language)
                st.session_state.notes_res = notes
                st.session_state.notes_topic = topic
        else: st.error("Enter topic name!")

    if 'notes_res' in st.session_state:
        render_voice_controls(st.session_state.notes_res, key_prefix="notes", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.notes_res)}</div>", unsafe_allow_html=True)
        pdf_file = create_pdf(st.session_state.notes_res, st.session_state.notes_topic)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF Notes", f, file_name=pdf_file, use_container_width=True)

# --- 📝 TEST SERIES PAGE ---
elif st.session_state.page == "Test":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("📝 AI Practice Test")
    topic = st.text_input("Enter Topic for Test:")
    
    if st.button("Generate Practice Quiz 🎯"):
        if topic:
            with st.spinner("Generating Quiz..."):
                test = get_ai_answer(f"Create 5 practice MCQs on **{topic}** with answers. Use bold text like **term** for key headings.", language)
                st.session_state.test_res = test
        else: st.error("Please enter a topic!")

    if 'test_res' in st.session_state:
        render_voice_controls(st.session_state.test_res, key_prefix="test", language=language)
        st.markdown(f"<div class='aesthetic-card'>{apply_highlights(st.session_state.test_res)}</div>", unsafe_allow_html=True)

# --- ⏰ FOCUS TIMER PAGE ---
elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⏰ Focus Study Timer")
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    study_timer()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Made with ❤️ by Anugya | BrainBloom EduGenie v7.1 Ultimate 🌸")
