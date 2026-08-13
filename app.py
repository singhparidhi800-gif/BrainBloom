import streamlit as st
import random
from datetime import datetime
from groq import Groq
import time
from PIL import Image
from fpdf import FPDF
import streamlit.components.v1 as components
import urllib.parse
import os

st.set_page_config(page_title="BrainBloom - EduGenie", page_icon="✨", layout="wide")

# --- DIRECT LOGO LINK WITH CSS CROP FIX & LARGER SIZE --- #
LOGO_URL = "https://i.postimg.cc/WD8XXFXD/image.png"

def display_logo(size=140):
    # CSS Object-fit ensures status bar / time gets cropped automatically, size enlarged to 140px
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 15px;'>
        <img src='{LOGO_URL}' style='width: {size}px; height: {size}px; object-fit: cover; border-radius: 28px; box-shadow: 0 12px 30px rgba(99, 102, 241, 0.22); border: 3px solid #ffffff;'>
    </div>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'user_name' not in st.session_state or not st.session_state.user_name:
    st.session_state.user_name = "Future Topper"
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'total_time' not in st.session_state:
    st.session_state.total_time = 0
if 'video_topic' not in st.session_state:
    st.session_state.video_topic = ""
if 'video_ready' not in st.session_state:
    st.session_state.video_ready = False
if 'script' not in st.session_state:
    st.session_state.script = ""
if 'points' not in st.session_state:
    st.session_state.points = []
if 'image_urls' not in st.session_state:
    st.session_state.image_urls = [] # Permanent storage for 2 visual images
if 'yt_links' not in st.session_state:
    st.session_state.yt_links = []
if 'speak' not in st.session_state:
    st.session_state.speak = True
if 'study_sessions' not in st.session_state:
    st.session_state.study_sessions = 0
if 'flashcards_data' not in st.session_state:
    st.session_state.flashcards_data = []

# Safe API Client Setup
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

# --- AI + PDF + IMAGE FUNCTIONS ---
def get_ai_answer(prompt, language):
    if not client:
        return "GROQ API Key missing in Streamlit Secrets!"
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant"
    )
    return chat_completion.choices[0].message.content

def generate_2_images(topic, points):
    """ Generates and locks exactly 2 distinct aesthetic image URLs """
    urls = []
    for i, pt in enumerate(points[:2]):
        seed = random.randint(1000, 9999)
        safe_prompt = urllib.parse.quote(f"educational illustration of {topic}, {pt}, clean modern digital vector art, high resolution")
        urls.append(f"https://image.pollinations.ai/prompt/{safe_prompt}?seed={seed}&nologo=true&width=800&height=450")
    return urls

def get_youtube_videos(topic):
    q = urllib.parse.quote(topic)
    return [
        f"https://www.youtube.com/results?search_query={q}+in+hindi+class",
        f"https://www.youtube.com/results?search_query={q}+animated+explanation",
        f"https://www.youtube.com/results?search_query={q}+crash+course"
    ]

def create_pdf(notes, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"BrainBloom Notes: {topic}", ln=True, align='C')
    pdf.multi_cell(0, 10, txt=notes)
    pdf.output(f"{topic}.pdf")
    return f"{topic}.pdf"

def study_timer():
    placeholder = st.empty()
    if st.session_state.start_time is None:
        if placeholder.button("▶️ Start Studying Session", use_container_width=True):
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        placeholder.success(f"⏰ Active Focus Time: {int(elapsed//60)} min {int(elapsed%60)} sec")
        if st.button("⏹️ Stop & Save Time", use_container_width=True):
            st.session_state.total_time += elapsed
            st.session_state.study_sessions += 1
            st.session_state.start_time = None
            st.rerun()
        time.sleep(1)
        if st.session_state.start_time is not None:
            st.rerun()

# --- LANGUAGE DICTIONARY ---
LANG = {
    "English": {
        "title": "BrainBloom",
        "welcome": "Welcome back, Topper! 🌸",
        "profile_title": "👤 Student Profile & Dashboard",
        "video_title": "🎨 AI Visual Class (2-Step Visuals)",
        "video_placeholder": "Enter topic (e.g., Photosynthesis, Black Hole, GST)",
        "video_btn": "Generate 2-Step Visual Class ✨",
        "notes_btn_video": "📝 Generate Notes for this Video",
        "yt_title": "📺 Recommended Masterclasses:",
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
        "welcome": "Namaste Future Topper! 🌸",
        "profile_title": "👤 Student Profile & Dashboard",
        "video_title": "🎨 AI Visual Class (2-Step Visuals)",
        "video_placeholder": "Kaunsa topic seekhna hai? (Ex: Quantum Physics, GST)",
        "video_btn": "2-Step AI Visual Class Banao ✨",
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

# --- ULTRA-AESTHETIC STYLING (GLASSMORPHISM, NO BLACK BORDERS) ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background Soft Pastel Gradient */
.stApp {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 40%, #F3E8FF 100%);
}

/* Glassmorphic Aesthetic Cards - Clean No Harsh Black Outlines */
.aesthetic-card {
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.7);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08), 0 2px 6px rgba(0, 0, 0, 0.02);
    margin-bottom: 22px;
}

/* Modern Gradient Step Badges */
.step-badge {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
    color: #FFFFFF;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
    display: inline-block;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

/* Premium Aesthetic Buttons */
.stButton>button {
    background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
    color: #FFFFFF !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 12px 26px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.25) !important;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.38) !important;
    background: linear-gradient(135deg, #4338CA 0%, #312E81 100%) !important;
}

/* Header Aesthetics */
h1, h2, h3 {
    color: #1E1B4B !important;
    font-weight: 800 !important;
}

/* Input Fields Soft Border */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
    border-radius: 16px !important;
    border: 1px solid #CBD5E1 !important;
    background: rgba(255, 255, 255, 0.95) !important;
    color: #0F172A !important;
    font-size: 15px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
}

.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

a {
    color: #4F46E5 !important;
    font-weight: 700;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
</style>""", unsafe_allow_html=True)

# Language Selector
col_main, col_lang = st.columns([5,1])
with col_lang:
    language = st.selectbox("🌐 Language", ["English", "Hindi"], label_visibility="collapsed")
txt = LANG[language]

# --- HOME PAGE ---
if st.session_state.page == "Home":
    display_logo(size=140)
    st.markdown(f"<h1 style='text-align: center; margin-top: -5px; font-size: 38px;'>{txt['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #475569; font-weight: 600; font-size: 16px; margin-bottom: 25px;'>{txt['caption']}</p>", unsafe_allow_html=True)
    
    # Welcome Card & Student Quick Dashboard Button
    st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown(f"### 👋 {txt['welcome']} **{st.session_state.user_name}**")
    
    col_prof1, col_prof2 = st.columns([3, 1])
    with col_prof1:
        st.write("Ready to bloom your brain today with AI visuals & interactive notes?")
    with col_prof2:
        if st.button("👤 Open Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; margin-top: 20px; margin-bottom: 15px;'>✨ Choose Learning Mode</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎨 AI Visual Class", use_container_width=True):
            st.session_state.page = "Video"
            st.session_state.video_ready = False
            st.rerun()
        if st.button("📝 AI Test Series", use_container_width=True):
            st.session_state.page = "Test"
            st.rerun()
            
    with col2:
        if st.button("📝 Magic Notes", use_container_width=True):
            st.session_state.page = "Notes"
            st.rerun()
        if st.button("⏰ Study Timer", use_container_width=True):
            st.session_state.page = "Timer"
            st.rerun()
            
    with col3:
        if st.button("❓ AI Doubt Solver", use_container_width=True):
            st.session_state.page = "Doubt"
            st.rerun()
        if st.button("🎴 AI Flashcards", use_container_width=True):
            st.session_state.page = "Flashcards"
            st.rerun()

# --- STUDENT DASHBOARD PAGE ---
elif st.session_state.page == "Dashboard":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
        
    st.subheader(txt["profile_title"])
    
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    st.markdown("### 🎓 Student Info")
    new_name = st.text_input("Edit Profile Name:", value=st.session_state.user_name)
    if st.button("💾 Save Profile Name"):
        if new_name.strip():
            st.session_state.user_name = new_name.strip()
            st.success("Profile Name Updated Successfully!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Total Active Study Hours", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d2:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Completed Sessions", f"🔥 {st.session_state.study_sessions}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_d3:
        st.markdown("<div class='aesthetic-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.metric("Current Learning Level", "🌟 Topper Rank")
        st.markdown("</div>", unsafe_allow_html=True)

# --- AI VISUAL CLASS PAGE (UPDATED TO 2 IMAGES ONLY) ---
elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.session_state.video_ready = False
        st.rerun()
        
    st.subheader(txt["video_title"])
    topic = st.text_input(txt["video_placeholder"])
    
    if st.button(txt["video_btn"]):
        if topic:
            with st.spinner("EduGenie is generating 2 HD visual illustrations..."):
                script = get_ai_answer(f"Explain {topic} in 2 simple, clear sequential points for students in {language}. Each point exactly 1-2 lines.", language)
                points = [p.strip('- ').strip() for p in script.split('\n') if p.strip()][:2]
                
                # FIX: Lock exactly 2 image URLs permanently into session state
                image_urls = generate_2_images(topic, points)
                st.session_state.script = script
                st.session_state.points = points
                st.session_state.image_urls = image_urls
                st.session_state.yt_links = get_youtube_videos(topic)
                st.session_state.video_ready = True
                st.session_state.speak = True
                st.rerun()
        else:
            st.error("Please enter a topic first")
            
    if st.session_state.video_ready:
        st.markdown(f"<h3 style='color: #1E1B4B;'>✨ Visual Class: {topic}</h3>", unsafe_allow_html=True)
        
        if st.button(txt["stop_voice"]):
            st.session_state.speak = False
            components.html("""<script>window.speechSynthesis.cancel();</script>""", height=0)
            st.rerun()
            
        st.markdown("### 🖼️ 2-Step Visual Concept Explanation")
        
        # Displaying 2 images side-by-side or stacked cleanly
        for i, point in enumerate(st.session_state.points[:2]):
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 2])
            with col1:
                img_src = st.session_state.image_urls[i] if i < len(st.session_state.image_urls) else "https://picsum.photos/800/450"
                st.image(img_src, use_container_width=True, caption=f"Visual {i+1}")
            with col2:
                st.markdown(f"<span class='step-badge'>STEP {i+1}</span>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 18px; font-weight: 600; color: #1E293B; line-height: 1.6;'>{point}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown("### 📢 AI Teacher Complete Script:")
        st.write(st.session_state.script)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.speak:
            lang_code = 'hi-IN' if language=="Hindi" else 'en-US'
            js_code = f"""<script>var msg = new SpeechSynthesisUtterance(`{st.session_state.script}`); msg.lang = '{lang_code}'; msg.rate = 0.9; window.speechSynthesis.speak(msg);</script>"""
            components.html(js_code, height=0)
            
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.markdown(f"### {txt['yt_title']}")
        st.markdown(f"1. 🔗 [🔥 Detailed Class Explanation]({st.session_state.yt_links[0]})")
        st.markdown(f"2. 🔗 [🎨 Animated Video Version]({st.session_state.yt_links[1]})")
        st.markdown(f"3. 🔗 [⚡ Quick Exam Revision]({st.session_state.yt_links[2]})")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button(txt["notes_btn_video"]):
            st.session_state.video_topic = topic
            st.session_state.video_ready = False
            st.session_state.page = "Notes"
            st.rerun()

# --- NOTES PAGE ---
elif st.session_state.page == "Notes":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
        
    st.subheader(txt["notes_title"])
    all_subjects = ["Science", "Math", "History", "Geography", "Polity", "Economics", "English", "Hindi", "Computer", "Physics", "Chemistry", "Biology", "JEE", "NEET", "UPSC", "SSC", "Banking", "CA"]
    default_topic = st.session_state.get('video_topic', '')
    
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    subject = st.selectbox(txt["subject"], all_subjects)
    topic = st.text_input(txt["topic"], value=default_topic)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(txt["notes_btn"]):
        if topic:
            with st.spinner("EduGenie is crafting aesthetic notes..."):
                notes = get_ai_answer(f"Make 1 page concise study notes on {topic} for {subject}. Include Headings, 3 Key Points, 1 Real Example, 1 Memory Trick. Language: {language}", language)
                diagram_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(topic + ' diagram concept')}&seed=999&nologo=true&width=800&height=400"
                
                st.markdown(f"<div class='aesthetic-card' style='font-size: 16px; line-height: 1.8;'>{notes.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.image(diagram_url, caption=f"Visual Diagram: {topic}", use_container_width=True)
                
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(txt["download"], notes, file_name=f"{topic}_Notes.txt", use_container_width=True)
                with col_d2:
                    pdf_file = create_pdf(notes, topic)
                    with open(pdf_file, "rb") as f:
                        st.download_button(txt["pdf_btn"], f, file_name=pdf_file, use_container_width=True)
                st.session_state.video_topic = ""
        else:
            st.error("Enter topic name")

# --- DOUBT PAGE ---
elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
        
    st.subheader(txt["doubt_title"])
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    doubt = st.text_area(txt["doubt_placeholder"], height=120)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(txt["doubt_btn"]):
        if doubt:
            st.info(f"**Your Doubt:** {doubt}")
            with st.spinner("EduGenie is solving..."):
                answer = get_ai_answer(f"You are EduGenie expert tutor. Solve this student doubt clearly: {doubt}. Language: {language}", language)
                st.markdown(f"<div class='aesthetic-card'><b>💡 Solution:</b><br><br>{answer.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

# --- TEST PAGE ---
elif st.session_state.page == "Test":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
        
    st.subheader(txt["test_title"])
    st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
    topic = st.text_input("Enter Topic for Test:")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(txt["test_btn"]):
        if topic:
            with st.spinner("Generating Quiz..."):
                test = get_ai_answer(f"Create 5 practice MCQs on {topic} for students in {language}. Provide Question, Options A/B/C/D, and Answers at the bottom.", language)
                st.markdown(f"<div class='aesthetic-card'>{test.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        else:
            st.error("Please enter a topic!")

# --- FLASHCARDS PAGE ---
elif st.session_state.page == "Flashcards":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
        
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
        else:
            st.error("Please enter a topic!")
            
    if st.session_state.flashcards_data:
        st.markdown("### 🎴 Tap Card to Reveal Answer:")
        for idx, fc in enumerate(st.session_state.flashcards_data):
            if "|" in fc or ":" in fc:
                with st.expander(f"📌 Flashcard {idx+1}"):
                    st.markdown(f"<div style='font-size: 16px; font-weight: 600;'>{fc}</div>", unsafe_allow_html=True)

# --- TIMER PAGE ---
elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()
        
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
st.caption("Made with ❤️ by Anugya ")
