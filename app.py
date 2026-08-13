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
# Aap yahan apna UPI ID change kar sakti hain:
# ==========================================
MY_UPI_ID = st.secrets.get("UPI_ID", "anugya@upi")  # E.g. 9876543210@paytm ya yourname@okaxis

# --- DATA PERSISTENCE SYSTEM (Fixes Data Loss Issue) ---
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

# Initialize Session State with Saved Data
saved_data = load_user_data()
if 'user_name' not in st.session_state: st.session_state.user_name = saved_data.get("user_name", "Future Topper")
if 'total_time' not in st.session_state: st.session_state.total_time = saved_data.get("total_time", 0)
if 'study_sessions' not in st.session_state: st.session_state.study_sessions = saved_data.get("study_sessions", 0)
if 'streak' not in st.session_state: st.session_state.streak = saved_data.get("streak", 1)
if 'is_vip' not in st.session_state: st.session_state.is_vip = saved_data.get("is_vip", False)
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'video_topic' not in st.session_state: st.session_state.video_topic = ""
if 'video_ready' not in st.session_state: st.session_state.video_ready = False
if 'script' not in st.session_state: st.session_state.script = ""
if 'points' not in st.session_state: st.session_state.points = []
if 'image_urls' not in st.session_state: st.session_state.image_urls = []
if 'yt_links' not in st.session_state: st.session_state.yt_links = []
if 'speak' not in st.session_state: st.session_state.speak = True
if 'flashcards_data' not in st.session_state: st.session_state.flashcards_data = []

# --- DIRECT LOGO LINK WITH CSS SHARPNESS FIX ---
LOGO_URL = "https://i.postimg.cc/WD8XXFXD/image.png"

def display_logo(size=110):
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 10px;'>
        <img src='{LOGO_URL}' style='
            width: {size}px; 
            height: {size}px; 
            object-fit: contain; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2); 
            border: 2px solid #ffffff;
            image-rendering: -webkit-optimize-contrast;
            background-color: #ffffff;
            padding: 4px;
        '>
    </div>
    """, unsafe_allow_html=True)

# Safe API Client Setup
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

# --- AI + PDF + IMAGE FUNCTIONS ---
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

# Fixed High-Quality Visual Image Generator
def generate_step_images(topic, points):
    urls = []
    for i, pt_text in enumerate(points):
        seed = random.randint(10000, 99999)
        # Clear, educational prompt to prevent weird abstract sketches
        clean_prompt = f"high quality 2D educational infographic illustration of {topic}, step: {pt_text}, colorful vector art, simple textbook diagram, bright colors, clear visual"
        safe_prompt = urllib.parse.quote(clean_prompt)
        urls.append(f"https://image.pollinations.ai/prompt/{safe_prompt}?seed={seed}&nologo=true&width=800&height=450")
    return urls

def get_youtube_videos(topic):
    q = urllib.parse.quote(topic)
    return [
        f"https://www.youtube.com/results?search_query={q}+in+hindi+class",
        f"https://www.youtube.com/results?search_query={q}+animated+explanation",
        f"https://www.youtube.com/results?search_query={q}+one+shot+revision"
    ]

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
    if hours < 1:
        return "🐣 Novice Learner"
    elif hours < 5:
        return "⚡ Backbencher Se Topper"
    elif hours < 15:
        return "🔥 Study Machine"
    else:
        return "🧠 Einstein Pro Max"

# --- FUNNY DIALOGUE GENERATOR ---
FUNNY_MOTIVATIONS = [
    "Padhle bhai, crush bhi topper ke sath hi baithti hai! 😉",
    "Dimaag overheat ho raha hai? Thoda paani piyo aur phir dhoom machao! ☕🔥",
    "Mummy ko bol do: 'Sharma ji ke beta ko bolna ab competition tough hai!' 😎",
    "Gyaan wo amrit hai jo sirf padhne se milta hai, reels scroll karne se nahi! 📱❌",
    "Aapka dimaag 100% active hai, bas isko thoda Instagram se door rakho! 🚀"
]

# --- LANGUAGE DICTIONARY ---
LANG = {
    "English": {
        "title": "BrainBloom",
        "caption": "Your Smart AI Learning Companion 🌸",
        "welcome": "Welcome back, Topper! 🌸",
        "profile_title": "👤 Student Profile & Saved Progress",
        "video_title": "🎨 AI Visual Class",
        "video_placeholder": "Enter topic (e.g., Photosynthesis, Black Hole, GST)",
        "video_btn": "Generate Visual Class ✨",
        "notes_btn_video": "📝 Generate Notes for this Video",
        "yt_title": "📺 Recommended Video Classes:",
        "stop_voice": "🔇 Stop AI Voice",
        "notes_title": "📝 Magic Notes Generator",
        "subject": "Choose Subject/Exam",
        "topic": "Enter Topic",
        "notes_btn": "Create Magic Notes ✨",
        "pdf_btn": "📥 Download PDF",
        "download": "📥 Download TXT",
        "doubt_title": "❓ AI Doubt Solver",
        "doubt_placeholder": "Ask any concept, question or doubt...",
        "doubt_btn": "Solve Doubt Now ⚡",
        "test_title": "📝 AI Test Series",
        "test_btn": "Generate Practice Quiz 🎯",
        "timer_title": "⏰ Study Timer & Focus Analytics",
        "flashcard_title": "🎴 AI Flashcards - Quick Revision",
        "flashcard_btn": "Generate Flashcards ✨"
    },
    "Hindi": {
        "title": "BrainBloom",
        "caption": "Aapka Smart AI Learning Saathi 🌸",
        "welcome": "Namaste Future Topper! 🌸",
        "profile_title": "👤 Student Profile & Saved Progress",
        "video_title": "🎨 AI Visual Class",
        "video_placeholder": "Kaunsa topic seekhna hai? (Ex: Quantum Physics, GST)",
        "video_btn": "AI Visual Class Banao ✨",
        "notes_btn_video": "📝 Is Class ke Notes Lo",
        "yt_title": "📺 Top YouTube Teachers ke Videos:",
        "stop_voice": "🔇 Awaaz Band Karo",
        "notes_title": "📝 Magic Notes - 1 Page Full Chapter",
        "subject": "Subject / Exam Chuno",
        "topic": "Topic Ka Naam",
        "notes_btn": "Magic Notes Banao ✨",
        "pdf_btn": "📥 PDF Download Karo",
        "download": "📥 TXT Download Karo",
        "doubt_title": "❓ AI Doubt Solver",
        "doubt_placeholder": "Koi bhi sawaal ya doubt pucho...",
        "doubt_btn": "Abhi Jawab Paayein ⚡",
        "test_title": "📝 AI Test Series",
        "test_btn": "Practice Quiz Banao 🎯",
        "timer_title": "⏰ Study Timer & Analytics",
        "flashcard_title": "🎴 AI Flashcards - Quick Revision",
        "flashcard_btn": "Flashcards Banao ✨"
    }
}

# --- ULTRA-AESTHETIC STYLING ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 40%, #F3E8FF 100%);
}
.aesthetic-card {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 22px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
    margin-bottom: 18px;
}
.step-badge {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
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
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 12px;
}
.viral-badge {
    background: #EC4899;
    color: white;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 700;
}
.stButton>button {
    background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
    color: #FFFFFF !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 10px 22px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.2) !important;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.35) !important;
}
h1, h2, h3 { color: #1E1B4B !important; font-weight: 800 !important; }
</style>""", unsafe_allow_html=True)

# Top Bar Header
col_main_h, col_vip_btn, col_lang = st.columns([4, 1.8, 1.2])
with col_vip_btn:
    if st.session_state.is_vip:
        st.markdown("<span class='vip-badge'>👑 VIP UNLOCKED</span>", unsafe_allow_html=True)
    else:
        if st.button("👑 Unlock VIP (₹49)", use_container_width=True):
            st.session_state.page = "Monetize"
            st.rerun()

with col_lang:
    language = st.selectbox("🌐 Language", ["Hindi", "English"], label_visibility="collapsed")
txt = LANG[language]

# --- HOME PAGE ---
if st.session_state.page == "Home":
    display_logo(size=110)
    st.markdown(f"<h1 style='text-align: center; margin-top: -5px; font-size: 36px;'>{txt['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #475569; font-weight: 600; font-size: 15px; margin-bottom: 20px;'>{txt['caption']}</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown(f"### 👋 {txt['welcome']} **{st.session_state.user_name}**")
    col_prof1, col_prof2 = st.columns([3, 1])
    with col_prof1:
        st.write(f"Current Level: **{get_user_rank(st.session_state.total_time)}** | Focus Time: **{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m**")
    with col_prof2:
        if st.button("👤 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
    
    if st.button("☕ Quick Dose of Funny Motivation"):
        st.toast(random.choice(FUNNY_MOTIVATIONS), icon="💡")
    st.markdown("</div>", unsafe_allow_html=True)

    # Feature Buttons Grid
    st.markdown("<h3 style='text-align: center; margin-top: 15px;'>✨ Choose Learning Mode</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎨 AI Visual Class", use_container_width=True):
            st.session_state.page = "Video"
            st.session_state.video_ready = False
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
        if st.button("📝 Magic Notes", use_container_width=True):
            st.session_state.page = "Notes"
            st.rerun()
        if st.button("⏰ Study Timer", use_container_width=True):
            st.session_state.page = "Timer"
            st.rerun()

    with col3:
        if st.button("📱 Shorts Script Generator 🎬", use_container_width=True):
            st.session_state.page = "Shorts"
            st.rerun()
        if st.button("❓ AI Doubt Solver", use_container_width=True):
            st.session_state.page = "Doubt"
            st.rerun()
        if st.button("🎴 AI Flashcards", use_container_width=True):
            st.session_state.page = "Flashcards"
            st.rerun()

# --- STUDENT DASHBOARD PAGE ---
elif st.session_state.page == "Dashboard":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["profile_title"])
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    st.markdown("### 🎓 Student Profile")
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
        st.metric("Total Study Time", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d2:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Sessions Completed", f"🔥 {st.session_state.study_sessions}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d3:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Current Rank", get_user_rank(st.session_state.total_time))
        st.markdown("</div>", unsafe_allow_html=True)

# --- AI VISUAL CLASS PAGE ---
elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.session_state.video_ready = False; st.rerun()
    st.subheader(txt["video_title"])
    topic = st.text_input(txt["video_placeholder"])
    
    if st.button(txt["video_btn"]):
        if topic:
            with st.spinner("EduGenie is generating step-by-step visual concepts..."):
                prompt = f"Explain {topic} in 2 precise step-by-step points for a student in {language}. Step 1: Core Concept. Step 2: Working or Application."
                script = get_ai_answer(prompt, language)
                
                # Extract clean sentence points
                raw_lines = [p.strip('- 1234567890.').strip() for p in script.split('\n') if len(p.strip()) > 8]
                if len(raw_lines) >= 2:
                    points = raw_lines[:2]
                else:
                    sentences = [s.strip() for s in script.split('.') if len(s.strip()) > 8]
                    points = sentences[:2] if len(sentences) >= 2 else [f"Core principle of {topic}", f"Practical working of {topic}"]
                
                image_urls = generate_step_images(topic, points)
                st.session_state.script = script
                st.session_state.points = points
                st.session_state.image_urls = image_urls
                st.session_state.yt_links = get_youtube_videos(topic)
                st.session_state.video_ready = True
                st.session_state.speak = True
                st.rerun()
        else:
            st.error("Please enter a topic first!")

    if st.session_state.video_ready:
        st.markdown(f"### ✨ Visual Class: {topic}")
        if st.button(txt["stop_voice"]):
            st.session_state.speak = False
            components.html("""<script>window.speechSynthesis.cancel();</script>""", height=0)
            st.rerun()

        # Step Pictures Render
        for i in range(len(st.session_state.points)):
            pt_text = st.session_state.points[i]
            img_src = st.session_state.image_urls[i] if i < len(st.session_state.image_urls) else "https://picsum.photos/800/450"
            
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 2])
            with col1:
                st.image(img_src, use_container_width=True, caption=f"Visual Diagram Step {i+1}")
            with col2:
                st.markdown(f"<span class='step-badge'>STEP {i+1}</span>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 17px; font-weight: 600; color: #1E293B;'>{pt_text}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown("### 📢 AI Complete Explanation:")
        st.write(st.session_state.script)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.speak:
            lang_code = 'hi-IN' if language == "Hindi" else 'en-US'
            clean_speech = st.session_state.script.replace("'", "").replace("\n", " ")
            js_code = f"""<script>var msg = new SpeechSynthesisUtterance('{clean_speech}'); msg.lang = '{lang_code}'; msg.rate = 0.9; window.speechSynthesis.speak(msg);</script>"""
            components.html(js_code, height=0)

        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown(f"### {txt['yt_title']}")
        st.markdown(f"1. 🔗 [🔥 Detailed Explanation Video]({st.session_state.yt_links[0]})")
        st.markdown(f"2. 🔗 [🎨 Animated Video Class]({st.session_state.yt_links[1]})")
        st.markdown(f"3. 🔗 [⚡ Quick Revision Video]({st.session_state.yt_links[2]})")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 🎭 BRAINROT / GEN-Z EXPLAINER PAGE ---
elif st.session_state.page == "BrainRot":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 BrainRot to BrainGain (Gen-Z & Meme Explainer)")
    topic = st.text_input("Enter Concept (e.g. Newton's 3rd Law, Integration, Organic Chemistry):")
    vibe = st.selectbox("Select Meme Style Vibe:", ["Gen-Z Slang & Memes 💀", "Anime / Superhero Analogy ⚡", "K-Pop & BTS Army Analogy 🎵", "Funny Hindi Webseries Style 🍿"])
    
    if st.button("Explain in Meme Style 🔥"):
        if topic:
            with st.spinner("Cooking up viral meme explanation..."):
                prompt = f"Explain the academic concept '{topic}' in style of {vibe}. Use hilarious analogies, clear bullet points, easy simple breakdown so a student never forgets it. Language: Hinglish."
                res = get_ai_answer(prompt, language)
                st.markdown(f"<div class='aesthetic-card'>{res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.balloons()
        else: st.error("Enter a topic!")

# --- ⚡ NIGHT-BEFORE EXAM SURVIVAL KIT PAGE ---
elif st.session_state.page == "Survival":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⚡ 1-Hour Night-Before Exam Survival Kit")
    subject = st.text_input("Enter Chapter / Subject Name (e.g., Electrostatics, Calculus):")
    
    if st.button("Generate Survival Sheet 📄"):
        if subject:
            with st.spinner("Creating high-yield exam sheet..."):
                prompt = f"Create a 1-page emergency exam sheet for {subject}. Include: 1) Top 5 Guaranteed Exam Questions with Answers. 2) Key Formula / Concept Cheat Sheet. 3) Common Mistakes to Avoid. Language: Hinglish."
                res = get_ai_answer(prompt, language)
                st.markdown(f"<div class='aesthetic-card'>{res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                pdf_file = create_pdf(res, subject)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF Survival Sheet", f, file_name=pdf_file, use_container_width=True)
        else: st.error("Enter chapter name!")

# --- 📱 YOUTUBE SHORTS SCRIPT GENERATOR PAGE ---
elif st.session_state.page == "Shorts":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎬 Viral 30-Sec YouTube Shorts Script AI")
    topic = st.text_input("Enter Topic for Video Short:")
    
    if st.button("Generate Script & Hook 🔥"):
        if topic:
            with st.spinner("Writing catchy script..."):
                prompt = f"Write a catchy 30-second YouTube Short / Reel script on {topic}. Include: 1) Viral Hook (First 3 seconds). 2) Mindblowing Fact/Explanation. 3) Call to Action (Subscribe to Anu ot7). Hinglish language."
                res = get_ai_answer(prompt, language)
                st.markdown(f"<div class='aesthetic-card'>{res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        else: st.error("Enter topic!")

# --- 💰 MONETIZATION / VIP PASS PAGE ---
elif st.session_state.page == "Monetize":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader("👑 Unlock BrainBloom VIP Pass")
    
    st.markdown(f"""
    <div class='aesthetic-card' style='text-align: center;'>
        <h2>✨ VIP Topper Pass Benefits:</h2>
        <p>✅ Unlimited HD AI Visual Classes & Diagrams</p>
        <p>✅ Instant Download of PDF Survival Kits & Formula Cheat Sheets</p>
        <p>✅ 24/7 Priority AI Doubt Solver Access</p>
        <hr>
        <h3>Special Offer: <b>₹49 / month</b></h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💳 Pay via Any UPI App (Paytm / PhonePe / Google Pay):")
    st.info(f"Send ₹49 to UPI ID: **{MY_UPI_ID}**")
    
    utr = st.text_input("Enter Payment Transaction ID / UTR Number:")
    if st.button("Verify Payment & Activate VIP 🚀"):
        if len(utr) >= 6:
            st.session_state.is_vip = True
            save_user_data()
            st.success("🎉 VIP Access Activated Successfully!")
            st.balloons()
            time.sleep(2)
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid 12-digit UTR/Transaction ID.")

# --- NOTES PAGE ---
elif st.session_state.page == "Notes":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["notes_title"])
    all_subjects = ["Science", "Math", "Physics", "Chemistry", "Biology", "History", "Geography", "English", "Hindi", "Computer"]
    default_topic = st.session_state.get('video_topic', '')
    
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    subject = st.selectbox(txt["subject"], all_subjects)
    topic = st.text_input(txt["topic"], value=default_topic)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(txt["notes_btn"]):
        if topic:
            with st.spinner("EduGenie is crafting aesthetic notes..."):
                notes = get_ai_answer(f"Make 1 page concise study notes on {topic} for {subject}. Include Headings, 3 Key Points, 1 Real Example, 1 Memory Trick. Language: {language}", language)
                diagram_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(topic + ' educational diagram concept')}&seed=999&nologo=true&width=800&height=400"
                
                st.markdown(f"<div class='aesthetic-card'>{notes.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.image(diagram_url, caption=f"Visual Diagram: {topic}", use_container_width=True)
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(txt["download"], notes, file_name=f"{topic}_Notes.txt", use_container_width=True)
                with col_d2:
                    pdf_file = create_pdf(notes, topic)
                    with open(pdf_file, "rb") as f:
                        st.download_button(txt["pdf_btn"], f, file_name=pdf_file, use_container_width=True)
        else: st.error("Enter topic name")

# --- DOUBT PAGE ---
elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["doubt_title"])
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    doubt = st.text_area(txt["doubt_placeholder"], height=120)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button(txt["doubt_btn"]):
        if doubt:
            with st.spinner("EduGenie is solving..."):
                answer = get_ai_answer(f"Solve this student doubt clearly step-by-step: {doubt}. Language: {language}", language)
                st.markdown(f"<div class='aesthetic-card'><b>💡 Solution:</b><br><br>{answer.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- TEST PAGE ---
elif st.session_state.page == "Test":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["test_title"])
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    topic = st.text_input("Enter Topic for Test:")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button(txt["test_btn"]):
        if topic:
            with st.spinner("Generating Quiz..."):
                test = get_ai_answer(f"Create 5 practice MCQs on {topic} for students in {language}. Provide Question, Options A/B/C/D, and Answers at bottom.", language)
                st.markdown(f"<div class='aesthetic-card'>{test.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        else: st.error("Please enter a topic!")

# --- FLASHCARDS PAGE ---
elif st.session_state.page == "Flashcards":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["flashcard_title"])
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    fc_topic = st.text_input("Enter Topic for Revision Flashcards:")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button(txt["flashcard_btn"]):
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

# --- TIMER PAGE ---
elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["timer_title"])
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
        st.metric("Completed Study Sessions", f"🔥 {st.session_state.study_sessions}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Made with ❤️ by Anugya | BrainBloom EduGenie v3.0 🌸")
