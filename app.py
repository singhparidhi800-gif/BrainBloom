import streamlit as st
import random
from datetime import datetime
from groq import Groq
import time
from PIL import Image
from fpdf import FPDF
import streamlit.components.v1 as components # VOICE KE LIYE

st.set_page_config(page_title="BrainBloom - EduGenie", page_icon="✨", layout="wide")

# --- SESSION STATE ---
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'total_time' not in st.session_state: st.session_state.total_time = 0
if 'video_topic' not in st.session_state: st.session_state.video_topic = ""

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- AI + PDF + IMAGE FUNCTIONS ---
def get_ai_answer(prompt, language):
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
    return chat_completion.choices[0].message.content

def get_ai_image(prompt):
    return f"https://image.pollinations.ai/prompt/{prompt}, educational, colorful diagram, cartoon style, for students, clear labels"

def create_pdf(notes, topic):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"BrainBloom Notes: {topic}", ln=True, align='C'); pdf.multi_cell(0, 10, txt=notes)
    pdf.output(f"{topic}.pdf"); return f"{topic}.pdf"

def study_timer():
    if st.session_state.start_time is None:
        if st.button("▶️ Start Studying"): st.session_state.start_time = time.time(); st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        st.success(f"⏰ Studying for: {int(elapsed//60)} min {int(elapsed%60)} sec")
        if st.button("⏹️ Stop & Save Time"):
            st.session_state.total_time += elapsed; st.session_state.start_time = None; st.rerun()

# --- LANGUAGE ---
LANG = {
    "English": {
        "title": "✨ BrainBloom", "caption": "Powered by EduGenie - Learn Anything",
        "menu": ["🏠 Home", "🎥 AI Video Class", "📝 Magic Notes", "❓ AI Doubt 24*7", "📝 AI Test", "⏰ Study Timer"],
        "welcome": "Hello Future Topper! 🌸", "name": "What's your name?", "start": "Let's Start Learning", "logout": "Change Name",
        "video_title": "🎥 AI Video Class", "video_placeholder": "Which topic? Ex: Quantum Physics, GST", "video_btn": "Generate AI Video", "motivation": "💪 You got this! One topic at a time.", "notes_btn_video": "📝 Get Notes for this Video",
        "notes_title": "📝 Magic Notes - 1 Page = Full Chapter", "subject": "Choose Subject/Exam", "topic": "Enter Topic or Upload Photo", "notes_btn": "Create Magic Notes ✨", "important_btn": "🔥 Show Important Only", "pdf_btn": "📥 Download PDF", "upload": "Upload Notes Photo", "download": "📥 Download TXT",
        "doubt_title": "❓ AI Doubt Solver - EduGenie Online 24*7", "doubt_placeholder": "Ask any doubt... from 6th to UPSC 😴", "doubt_btn": "Get Answer Now",
        "test_title": "📝 AI Test Series", "test_btn": "Generate 5 Questions",
        "timer_title": "⏰ Study Timer"
    },
    "Hindi": {
        "title": "✨ BrainBloom", "caption": "EduGenie ke saath - Kuch bhi Seekho",
        "menu": ["🏠 Home", "🎥 AI Video Class", "📝 Notes ka Jadu", "❓ AI Doubt 24*7", "📝 AI Test", "⏰ Study Timer"],
        "welcome": "Namaste Future Topper! 🌸", "name": "Apna naam batao", "start": "Shuru Karein", "logout": "Naam Badlo",
        "video_title": "🎥 AI Video Class", "video_placeholder": "Kaunsa topic? Ex: Quantum Physics, GST", "video_btn": "AI Video Banao", "motivation": "💪 Tum kar sakte ho! Ek din, ek topic.", "notes_btn_video": "📝 Is Video ke Notes Lo",
        "notes_title": "📝 Notes ka Jadu - 1 Page = Pura Chapter", "subject": "Subject/Exam chuno", "topic": "Topic likho ya Photo upload karo", "notes_btn": "Jadu se Notes Banao ✨", "important_btn": "🔥 Sirf Important Dikhao", "pdf_btn": "📥 PDF Download karo", "upload": "Notes ki Photo Upload karo", "download": "📥 TXT Download karo",
        "doubt_title": "❓ AI Doubt Solver - EduGenie 24 Ghante Online", "doubt_placeholder": "Koi bhi doubt... 6th se UPSC tak 😴", "doubt_btn": "Abhi Jawab Do",
        "test_title": "📝 AI Test Series", "test_btn": "5 Sawaal Banao",
        "timer_title": "⏰ Study Timer"
    }
}

# --- SUNDAR CSS ADD KIYA ---
st.markdown("""<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.stButton>button {background: linear-gradient(90deg, #FF6B9D, #C44569); color: white; border-radius: 15px; font-weight: bold; border: none; padding: 12px 25px; font-size: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s;}
.stButton>button:hover {transform: scale(1.05);}
h1 {color: white; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);}
.stTextInput>div>div>input {border-radius: 10px;}
</style>""", unsafe_allow_html=True)

col1, col2 = st.columns([4,1])
with col2: language = st.selectbox("🌐", ["English", "Hindi"], label_visibility="collapsed")
txt = LANG[language]

# --- PAGES ---
if st.session_state.page == "Home":
    st.title(txt["title"]); st.caption(txt["caption"])
    if st.session_state.user_name == "":
        st.subheader(txt["welcome"]); name = st.text_input(txt["name"])
        if st.button(txt["start"]):
            if name: st.session_state.user_name = name; st.rerun()
            else: st.warning("Please enter name" if language=="English" else "Naam likho")
    else:
        st.success(f"{txt['welcome']} {st.session_state.user_name}!")
        if st.button(txt["logout"]): st.session_state.user_name = ""; st.rerun()
        st.markdown("---"); st.header("Choose Your Weapon ⚔️")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎥 AI Video Class", use_container_width=True): st.session_state.page = "Video"; st.rerun()
            if st.button("📝 AI Test", use_container_width=True): st.session_state.page = "Test"; st.rerun()
        with col2:
            if st.button("📝 Magic Notes", use_container_width=True): st.session_state.page = "Notes"; st.rerun()
            if st.button("⏰ Study Timer", use_container_width=True): st.session_state.page = "Timer"; st.rerun()
        with col3:
            if st.button("❓ AI Doubt 24*7", use_container_width=True): st.session_state.page = "Doubt"; st.rerun()

elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["video_title"]); topic = st.text_input(txt["video_placeholder"])
    if st.button(txt["video_btn"]):
        if topic:
            with st.spinner("EduGenie is creating video... 20 sec"):
                script = get_ai_answer(f"Explain {topic} in 3 simple points for students in {language}.", language)
                points = [p for p in script.split('\n') if p.strip()][:3]

            st.success("✨ Video Ready!")
            st.markdown(f"**📢 AI Teacher:** {script}")

            # --- NAYA VOICE CODE - BINA gTTS ---
            lang_code = 'hi-IN' if language=="Hindi" else 'en-US'
            js_code = f"""<script>var msg = new SpeechSynthesisUtterance(`{script}`); msg.lang = '{lang_code}'; msg.rate = 0.9; msg.pitch = 1.1; window.speechSynthesis.speak(msg);</script>"""
            components.html(js_code, height=0) # YE BOLEGA

            st.markdown(f"**{txt['motivation']}**")
            for i, point in enumerate(points):
                st.image(get_ai_image(f"{topic} - {point}"), caption=f"Step {i+1}")
                time.sleep(1)

            if st.button(txt["notes_btn_video"]): st.session_state.video_topic = topic; st.session_state.page = "Notes"; st.rerun()
        else: st.error("Enter topic first")

elif st.session_state.page == "Notes":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["notes_title"])
    all_subjects = ["Science", "Math", "History", "Geography", "Polity", "Economics", "English", "Hindi", "Computer", "Physics", "Chemistry", "Biology", "JEE", "NEET", "UPSC", "SSC", "Banking", "CA"]
    subject = st.selectbox(txt["subject"], all_subjects); topic = st.text_input(txt["topic"], value=st.session_state.get('video_topic', '')); uploaded_file = st.file_uploader(txt["upload"], type=['png', 'jpg', 'jpeg'])
    col1, col2 = st.columns(2)
    with col1:
        if st.button(txt["notes_btn"]):
            if topic:
                with st.spinner("Making magic notes..."):
                    notes = get_ai_answer(f"Make 1 page colorful notes on {topic} for {subject}. Heading, 3 Key Points, 1 Example, 1 Memory Trick, and 'Diagram:' description. {language}", language)
                    diagram_url = get_ai_image(f"Diagram of {topic}")
                st.markdown(f"<div style='background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%); padding: 20px; border-radius: 20px;'>{notes.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.image(diagram_url, caption=f"{topic} Diagram")
                st.download_button(txt["download"], notes, file_name=f"{topic}.txt")
                pdf_file = create_pdf(notes, topic)
                with open(pdf_file, "rb") as f: st.download_button(txt["pdf_btn"], f, file_name=pdf_file)
            else: st.error("Enter topic")
    with col2:
        if st.button(txt["important_btn"]):
            if topic: st.error(get_ai_answer(f"List only 5 most important points of {topic} from {subject} for exams. {language}", language))
            else: st.error("Enter topic")

elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["doubt_title"]); doubt = st.text_area(txt["doubt_placeholder"])
    if st.button(txt["doubt_btn"]):
        if doubt:
            st.info(f"**Your Doubt:** {doubt}")
            with st.spinner("EduGenie thinking..."):
                answer = get_ai_answer(f"You are EduGenie. Answer: {doubt}. Make **important points bold**. {language}", language)
                answer = answer.replace("**", "<span style='color: #FF1493; font-weight: bold;'>").replace("**", "</span>")
            st.success("**EduGenie's Answer:**"); st.markdown(answer, unsafe_allow_html=True)
            if "diagram" in doubt.lower(): st.image(get_ai_image(f"Diagram for: {doubt}"), caption="AI Generated Diagram")
            st.caption(f"Answered at: {datetime.now().strftime('%I:%M %p')}")
        else: st.warning("Ask your doubt")

elif st.session_state.page == "Test":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["test_title"]); topic = st.text_input("Topic for Test: Ex: Newton's Laws")
    if st.button(txt["test_btn"]):
        with st.spinner("EduGenie making test..."):
            test = get_ai_answer(f"Make 5 MCQs on {topic} for school/competitive exam. Format: Q1. Question? A) B) C) D) Answer: B. {language}", language)
        st.write(test)

elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["timer_title"]); study_timer()
    st.metric("Total Study Time Today", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")

st.markdown("---"); st.caption(f"Made with ❤️ by {st.session_state.user_name} | BrainBloom")
