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

# --- DIRECT LOGO LINK WITH CSS CROP FIX ---
# Direct PostImg URL with fallback
LOGO_URL = "https://i.postimg.cc/WD8XXFXD/image.png"

def display_logo():
    # CSS Object-fit ensures status bar / time gets cropped automatically
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 10px;'>
            <img src='{LOGO_URL}' style='width: 90px; height: 90px; object-fit: cover; border-radius: 22px; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.25); border: 3px solid #000000;'>
        </div>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'total_time' not in st.session_state: st.session_state.total_time = 0
if 'video_topic' not in st.session_state: st.session_state.video_topic = ""
if 'video_ready' not in st.session_state: st.session_state.video_ready = False
if 'script' not in st.session_state: st.session_state.script = ""
if 'points' not in st.session_state: st.session_state.points = []
if 'image_urls' not in st.session_state: st.session_state.image_urls = [] # FIX: Permanent storage for 5 images
if 'yt_links' not in st.session_state: st.session_state.yt_links = []
if 'speak' not in st.session_state: st.session_state.speak = True
if 'study_sessions' not in st.session_state: st.session_state.study_sessions = 0
if 'flashcards_data' not in st.session_state: st.session_state.flashcards_data = []

# Safe API Client Setup
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

# --- AI + PDF + IMAGE FUNCTIONS ---
def get_ai_answer(prompt, language):
    if not client:
        return "GROQ API Key missing in Streamlit Secrets!"
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
    return chat_completion.choices[0].message.content

def generate_5_images(topic, points):
    """ Generates and locks 5 distinct aesthetic image URLs """
    urls = []
    for i, pt in enumerate(points):
        seed = random.randint(1000, 9999)
        safe_prompt = urllib.parse.quote(f"educational illustration of {topic}, {pt}, clean digital art, high quality")
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
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"BrainBloom Notes: {topic}", ln=True, align='C'); pdf.multi_cell(0, 10, txt=notes)
    pdf.output(f"{topic}.pdf"); return f"{topic}.pdf"

def study_timer():
    placeholder = st.empty()
    if st.session_state.start_time is None:
        if placeholder.button("▶️ Start Studying Session", use_container_width=True):
            st.session_state.start_time = time.time(); st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        placeholder.success(f"⏰ Active Focus Time: {int(elapsed//60)} min {int(elapsed%60)} sec")
        if st.button("⏹️ Stop & Save Time", use_container_width=True):
            st.session_state.total_time += elapsed
            st.session_state.study_sessions += 1
            st.session_state.start_time = None; st.rerun()
    time.sleep(1)
    if st.session_state.start_time is not None: st.rerun()

# --- LANGUAGE DICTIONARY ---
LANG = {
    "English": {
        "title": "BrainBloom", "caption": "Powered by EduGenie • Visual & Intelligent Learning",
        "welcome": "Hello Future Topper! 🌸", "name": "Enter your name to begin...", "start": "Start Learning", "logout": "Change Profile",
        "video_title": "🎨 AI Visual Class", "video_placeholder": "Enter topic (e.g., Photosynthesis, Black Hole, GST)", "video_btn": "Generate 5-Step Visual Class ✨", "notes_btn_video": "📝 Generate Notes for this Video", "yt_title": "📺 Recommended YouTube Masterclasses:", "stop_voice": "🔇 Stop AI Voice",
        "notes_title": "📝 Magic Notes Generator", "subject": "Choose Subject/Exam", "topic": "Enter Topic", "notes_btn": "Create Magic Notes ✨", "pdf_btn": "📥 Download PDF", "download": "📥 Download TXT",
        "doubt_title": "❓ AI Doubt Solver", "doubt_placeholder": "Ask any concept, question or doubt...", "doubt_btn": "Solve Doubt Now ⚡",
        "test_title": "📝 AI Test Series", "test_btn": "Generate 5 Practice Questions 🎯",
        "timer_title": "⏰ Study Timer & Focus Analytics",
        "flashcard_title": "🎴 AI Flashcards - Quick Smart Revision", "flashcard_btn": "Generate Flashcards ✨"
    },
    "Hindi": {
        "title": "BrainBloom", "caption": "EduGenie ke saath • Visual aur Smart Padhai",
        "welcome": "Namaste Future Topper! 🌸", "name": "Apna naam likhein...", "start": "Shuru Karein", "logout": "Naam Badlein",
        "video_title": "🎨 AI Visual Class", "video_placeholder": "Kaunsa topic seekhna hai? (Ex: Quantum Physics, GST)", "video_btn": "5-Step AI Visual Class Banao ✨", "notes_btn_video": "📝 Is Class ke Notes Lo", "yt_title": "📺 Top YouTube Teachers ke Videos:", "stop_voice": "🔇 Awaaz Band Karo",
        "notes_title": "📝 Magic Notes - 1 Page Full Chapter", "subject": "Subject / Exam Chuno", "topic": "Topic Ka Naam", "notes_btn": "Magic Notes Banao ✨", "pdf_btn": "📥 PDF Download Karo", "download": "📥 TXT Download Karo",
        "doubt_title": "❓ AI Doubt Solver", "doubt_placeholder": "Koi bhi sawaal ya doubt pucho...", "doubt_btn": "Abhi Jawab Paayein ⚡",
        "test_title": "📝 AI Test Series", "test_btn": "5 Sawaal Banao 🎯",
        "timer_title": "⏰ Study Timer & Analytics",
        "flashcard_title": "🎴 AI Flashcards - Quick Revision", "flashcard_btn": "Flashcards Banao ✨"
    }
}

# --- AESTHETIC STYLING (PASTEL GRADIENT + GLASS CARDS) ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 50%, #7DD3FC 100%);
}

/* Aesthetic Cards */
.aesthetic-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 22px;
    border: 2px solid #000000;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.step-badge {
    background: #000000;
    color: #7DD3FC;
    padding: 6px 14px;
    border-radius: 12px;
    font-weight: 800;
    font-size: 14px;
    display: inline-block;
    margin-bottom: 8px;
}

/* Custom Buttons */
.stButton>button {
    background: #000000 !important;
    color: #7DD3FC !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    border: 2px solid #000000 !important;
    padding: 12px 28px !important;
    font-size: 15px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15) !important;
}

.stButton>button:hover {
    background: #7DD3FC !important;
    color: #000000 !important;
    transform: translateY(-2px);
}

h1, h2, h3 {
    color: #0f172a !important;
    font-weight: 800 !important;
}

.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    border-radius: 14px !important;
    border: 2px solid #000000 !important;
    background: #FFFFFF !important;
    color: #000000 !important;
    font-size: 15px !important;
}

a { color: #0284C7 !important; font-weight: 700; text-decoration: none; }
a:hover { text-decoration: underline; }
</style>""", unsafe_allow_html=True)

# Language Selector
col_main, col_lang = st.columns([5,1])
with col_lang: language = st.selectbox("🌐", ["English", "Hindi"], label_visibility="collapsed")
txt = LANG[language]

# --- HOME PAGE ---
if st.session_state.page == "Home":
    display_logo()
    st.markdown(f"<h1 style='text-align: center; margin-top: -10px;'>{txt['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #334155; font-weight: 600; font-size: 16px; margin-bottom: 25px;'>{txt['caption']}</p>", unsafe_allow_html=True)

    if st.session_state.user_name == "":
        st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
        st.subheader(txt["welcome"])
        name = st.text_input(txt["name"])
        if st.button(txt["start"], use_container_width=True):
            if name: st.session_state.user_name = name; st.rerun()
            else: st.warning("Please enter your name" if language=="English" else "Kripya naam likhein")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success(f"{txt['welcome']} **{st.session_state.user_name}**!")
        if st.button(txt["logout"]): st.session_state.user_name = ""; st.rerun()
        
        st.markdown("<h3 style='text-align: center; margin-top: 20px;'>✨ Choose Learning Mode</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎨 AI Visual Class", use_container_width=True): st.session_state.page = "Video"; st.session_state.video_ready = False; st.rerun()
            if st.button("📝 AI Test Series", use_container_width=True): st.session_state.page = "Test"; st.rerun()
        with col2:
            if st.button("📝 Magic Notes", use_container_width=True): st.session_state.page = "Notes"; st.rerun()
            if st.button("⏰ Study Timer", use_container_width=True): st.session_state.page = "Timer"; st.rerun()
        with col3:
            if st.button("❓ AI Doubt Solver", use_container_width=True): st.session_state.page = "Doubt"; st.rerun()
            if st.button("🎴 AI Flashcards", use_container_width=True): st.session_state.page = "Flashcards"; st.rerun()

# --- AI VISUAL CLASS PAGE ---
elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"; st.session_state.video_ready = False; st.rerun()
    
    st.subheader(txt["video_title"])
    topic = st.text_input(txt["video_placeholder"])

    if st.button(txt["video_btn"]):
        if topic:
            with st.spinner("EduGenie is generating 5 HD visual illustrations..."):
                script = get_ai_answer(f"Explain {topic} in 5 simple, clear sequential points for students in {language}. Each point exactly 1 line.", language)
                points = [p.strip('- ').strip() for p in script.split('\n') if p.strip()][:5]
                
                # FIX: Lock all 5 image URLs permanently into session state
                image_urls = generate_5_images(topic, points)
                
                st.session_state.script = script
                st.session_state.points = points
                st.session_state.image_urls = image_urls
                st.session_state.yt_links = get_youtube_videos(topic)
                st.session_state.video_ready = True
                st.session_state.speak = True
            st.rerun()
        else: st.error("Please enter a topic first")

    if st.session_state.video_ready:
        st.markdown(f"<h3 style='color: #0f172a;'>✨ Visual Class: {topic}</h3>", unsafe_allow_html=True)

        if st.button(txt["stop_voice"]):
            st.session_state.speak = False
            components.html("""<script>window.speechSynthesis.cancel();</script>""", height=0)
            st.rerun()

        st.markdown("### 🖼️ Step-by-Step Visual Explanation")
        
        # Displaying all 5 images with full stability
        for i, point in enumerate(st.session_state.points):
            st.markdown("<div class='aesthetic-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1.2, 2])
            with col1:
                img_src = st.session_state.image_urls[i] if i < len(st.session_state.image_urls) else "https://picsum.photos/800/450"
                st.image(img_src, use_container_width=True, caption=f"Visual {i+1}")
            with col2:
                st.markdown(f"<span class='step-badge'>STEP {i+1}</span>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 18px; font-weight: 600; color: #0f172a; line-height: 1.6;'>{point}</p>", unsafe_allow_html=True)
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
            st.session_state.video_topic = topic;
            st.session_state.video_ready = False;
            st.session_state.page = "Notes";
            st.rerun()

# --- NOTES PAGE ---
elif st.session_state.page == "Notes":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
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
            st.info(f"**Your Doubt:** {doubt}")
            with st.spinner("EduGenie is solving..."):
                answer = get_ai_answer(f"You are EduGenie expert tutor. Solve this student doubt clearly: {doubt}. Language: {language}", language)
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
                test = get_ai_answer(f"Create 5 practice MCQs on {topic} for students in {language}. Provide Question, Options A/B/C/D, and Answers at the bottom.", language)
            st.markdown(f"<div class='aesthetic-card'>{test.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        else:
            st.error("Please enter a topic!")

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
st.caption("Made with ❤️ by Anugya | BrainBloom")
