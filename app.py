import streamlit as st
import random
from datetime import datetime
from groq import Groq
import time
from PIL import Image
from fpdf import FPDF
import streamlit.components.v1 as components
import webbrowser # NAYA

st.set_page_config(page_title="BrainBloom - EduGenie", page_icon="✨", layout="wide")

# --- SESSION STATE ---
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'total_time' not in st.session_state: st.session_state.total_time = 0
if 'video_topic' not in st.session_state: st.session_state.video_topic = ""
if 'video_ready' not in st.session_state: st.session_state.video_ready = False
if 'script' not in st.session_state: st.session_state.script = ""
if 'points' not in st.session_state: st.session_state.points = []
if 'slide_index' not in st.session_state: st.session_state.slide_index = 0
if 'yt_links' not in st.session_state: st.session_state.yt_links = [] # NAYA

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- AI + PDF + IMAGE FUNCTIONS ---
def get_ai_answer(prompt, language):
    chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.1-8b-instant")
    return chat_completion.choices[0].message.content

def get_ai_image(prompt):
    return f"https://image.pollinations.ai/prompt/ultra detailed {prompt}, educational diagram, clean white background, bold black text labels, arrows, vibrant colors, hd, 8k, vector illustration, for students"

def create_pdf(notes, topic):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"BrainBloom Notes: {topic}", ln=True, align='C'); pdf.multi_cell(0, 10, txt=notes)
    pdf.output(f"{topic}.pdf"); return f"{topic}.pdf"

# NAYA FUNCTION - YOUTUBE SEARCH
def get_youtube_videos(topic):
    return [
        f"https://www.youtube.com/results?search_query={topic}+explained+in+hindi",
        f"https://www.youtube.com/results?search_query={topic}+animated+video",
        f"https://www.youtube.com/results?search_query={topic}+class+10"
    ]

def study_timer():
    placeholder = st.empty()
    if st.session_state.start_time is None:
        if placeholder.button("▶️ Start Studying"):
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        placeholder.success(f"⏰ Studying for: {int(elapsed//60)} min {int(elapsed%60)} sec")
        if st.button("⏹️ Stop & Save Time"):
            st.session_state.total_time += elapsed
            st.session_state.start_time = None
            st.rerun()
    time.sleep(1)
    if st.session_state.start_time is not None:
        st.rerun()

# --- LANGUAGE ---
LANG = {
    "English": {
        "title": "✨ BrainBloom", "caption": "Powered by EduGenie - Learn Anything",
        "welcome": "Hello Future Topper! 🌸", "name": "What's your name?", "start": "Let's Start Learning", "logout": "Change Name",
        "video_title": "🎥 AI Video Class", "video_placeholder": "Which topic? Ex: Quantum Physics, GST", "video_btn": "Generate AI Video", "motivation": "💪 You got this! One topic at a time.", "notes_btn_video": "📝 Get Notes for this Video", "yt_title": "📺 Learn More from YouTube Top Teachers:",
        "notes_title": "📝 Magic Notes - 1 Page = Full Chapter", "subject": "Choose Subject/Exam", "topic": "Enter Topic", "notes_btn": "Create Magic Notes ✨", "important_btn": "🔥 Show Important Only", "pdf_btn": "📥 Download PDF", "download": "📥 Download TXT",
        "doubt_title": "❓ AI Doubt Solver", "doubt_placeholder": "Ask any doubt...", "doubt_btn": "Get Answer Now",
        "test_title": "📝 AI Test Series", "test_btn": "Generate 5 Questions",
        "timer_title": "⏰ Study Timer"
    },
    "Hindi": {
        "title": "✨ BrainBloom", "caption": "EduGenie ke saath - Kuch bhi Seekho",
        "welcome": "Namaste Future Topper! 🌸", "name": "Apna naam batao", "start": "Shuru Karein", "logout": "Naam Badlo",
        "video_title": "🎥 AI Video Class", "video_placeholder": "Kaunsa topic? Ex: Quantum Physics, GST", "video_btn": "AI Video Banao", "motivation": "💪 Tum kar sakte ho! Ek din, ek topic.", "notes_btn_video": "📝 Is Video ke Notes Lo", "yt_title": "📺 Ab YouTube ke Top Teachers se bhi seekho:",
        "notes_title": "📝 Notes ka Jadu - 1 Page = Pura Chapter", "subject": "Subject/Exam chuno", "topic": "Topic likho", "notes_btn": "Jadu se Notes Banao ✨", "important_btn": "🔥 Sirf Important Dikhao", "pdf_btn": "📥 PDF Download karo", "download": "📥 TXT Download karo",
        "doubt_title": "❓ AI Doubt Solver", "doubt_placeholder": "Koi bhi doubt...", "doubt_btn": "Abhi Jawab Do",
        "test_title": "📝 AI Test Series", "test_btn": "5 Sawaal Banao",
        "timer_title": "⏰ Study Timer"
    }
}

# --- LIGHT BLUE + BLACK THEME ---
st.markdown("""<style>
.stApp {background: linear-gradient(135deg, #87CEEB 0%, #ADD8E6 100%);}
.stButton>button {background: #000; color: #87CEEB; border-radius: 15px; font-weight: bold; border: 2px solid #87CEEB; padding: 12px 25px; font-size: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);}
.stButton>button:hover {background: #87CEEB; color: #000;}
h1, h2, h3 {color: #000; text-align: center;}
.stTextInput>div>div>input {border-radius: 10px; border: 2px solid #000;}
a {color: #0000EE; font-weight: bold;}
</style>""", unsafe_allow_html=True)

col1, col2 = st.columns([4,1])
with col2: language = st.selectbox("🌐", ["English", "Hindi"], label_visibility="collapsed")
txt = LANG[language]

# --- HOME PAGE ---
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
            if st.button("🎥 AI Video Class", use_container_width=True): st.session_state.page = "Video"; st.session_state.video_ready = False; st.rerun()
            if st.button("📝 AI Test", use_container_width=True): st.session_state.page = "Test"; st.rerun()
        with col2:
            if st.button("📝 Magic Notes", use_container_width=True): st.session_state.page = "Notes"; st.rerun()
            if st.button("⏰ Study Timer", use_container_width=True): st.session_state.page = "Timer"; st.rerun()
        with col3:
            if st.button("❓ AI Doubt", use_container_width=True): st.session_state.page = "Doubt"; st.rerun()

# --- VIDEO PAGE - 5 SLIDES + YOUTUBE ---
elif st.session_state.page == "Video":
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home";
        st.session_state.video_ready = False;
        st.session_state.slide_index = 0;
        st.rerun()
    st.subheader(txt["video_title"]); topic = st.text_input(txt["video_placeholder"])

    if st.button(txt["video_btn"]) and not st.session_state.video_ready:
        if topic:
            with st.spinner("EduGenie is creating video... 20 sec"):
                script = get_ai_answer(f"Explain {topic} in 5 simple points for students in {language}. Each point 1 line only.", language)
                points = [p.strip('- ').strip() for p in script.split('\n') if p.strip()][:5]
                st.session_state.script = script
                st.session_state.points = points
                st.session_state.yt_links = get_youtube_videos(topic) # YT LINK SAVE
                st.session_state.video_ready = True
                st.session_state.slide_index = 0
            st.rerun()
        else: st.error("Enter topic first")

    if st.session_state.video_ready:
        st.success(f"✨ BrainBloom Video Playing: {topic}")

        total = len(st.session_state.points)
        progress = st.progress(0)
        video_container = st.container()

        current = st.session_state.slide_index
        point = st.session_state.points[current]

        with video_container:
            st.image(get_ai_image(f"detailed illustration of {topic} - {point}"), use_container_width=True)
            st.markdown(f"<div style='background:white; padding:25px; border-radius:15px; border:3px solid black; font-size:22px; text-align:center; color:black; min-height:100px;'><b>Step {current+1}: {point}</b></div>", unsafe_allow_html=True)

            lang_code = 'hi-IN' if language=="Hindi" else 'en-US'
            js_code = f"""
            <script>
            var msg = new SpeechSynthesisUtterance(`Step {current+1}. {point}`);
            msg.lang = '{lang_code}'; msg.rate = 0.85;
            window.speechSynthesis.speak(msg);
            </script>
            """
            components.html(js_code, height=0)

        for i in range(6):
            progress.progress(((current * 6) + i) / (total * 6))
            time.sleep(1)

        st.session_state.slide_index += 1

        if st.session_state.slide_index >= total:
            progress.progress(1.0)
            st.session_state.video_ready = False
            st.session_state.slide_index = 0
            st.balloons()
            st.success("🎉 BrainBloom Video Khatam!")

            # YOUTUBE SUGGESTION
            st.markdown("---")
            st.markdown(f"### {txt['yt_title']}")
            st.markdown(f"1. [🔥 Best Explanation]({st.session_state.yt_links[0]})")
            st.markdown(f"2. [🎨 Animated Video]({st.session_state.yt_links[1]})")
            st.markdown(f"3. [⚡ Quick Revision]({st.session_state.yt_links[2]})")
            st.info("Link par click karke YouTube me khul jayega")

            if st.button(txt["notes_btn_video"]):
                st.session_state.video_topic = topic;
                st.session_state.page = "Notes";
                st.rerun()
        else:
            st.rerun()

# --- NOTES PAGE ---
elif st.session_state.page == "Notes":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["notes_title"])
    all_subjects = ["Science", "Math", "History", "Geography", "Polity", "Economics", "English", "Hindi", "Computer", "Physics", "Chemistry", "Biology", "JEE", "NEET", "UPSC", "SSC", "Banking", "CA"]
    subject = st.selectbox(txt["subject"], all_subjects); topic = st.text_input(txt["topic"], value=st.session_state.get('video_topic', ''))
    if st.button(txt["notes_btn"]):
        if topic:
            with st.spinner("Making magic notes..."):
                notes = get_ai_answer(f"Make 1 page notes on {topic} for {subject}. Heading, 3 Key Points, 1 Example, 1 Memory Trick. {language}", language)
                diagram_url = get_ai_image(f"Diagram of {topic}")
            st.markdown(f"<div style='background: #FFFFFF; padding: 25px; border-radius: 15px; border: 3px solid #000; color: #000; font-size: 16px; line-height: 1.8;'>{notes.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            st.image(diagram_url, caption=f"{topic} Diagram")
            st.download_button(txt["download"], notes, file_name=f"{topic}.txt")
            pdf_file = create_pdf(notes, topic)
            with open(pdf_file, "rb") as f: st.download_button(txt["pdf_btn"], f, file_name=pdf_file)
        else: st.error("Enter topic")

# --- DOUBT PAGE ---
elif st.session_state.page == "Doubt":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["doubt_title"]); doubt = st.text_area(txt["doubt_placeholder"])
    if st.button(txt["doubt_btn"]):
        if doubt:
            st.info(f"**Your Doubt:** {doubt}")
            with st.spinner("EduGenie thinking..."):
                answer = get_ai_answer(f"You are EduGenie. Answer: {doubt}. {language}", language)
            st.success("**EduGenie's Answer:**"); st.write(answer)

# --- TEST PAGE ---
elif st.session_state.page == "Test":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["test_title"]); topic = st.text_input("Topic for Test:")
    if st.button(txt["test_btn"]):
        with st.spinner("EduGenie making test..."):
            test = get_ai_answer(f"Make 5 MCQs on {topic}. Format: Q1. Question? A) B) C) D) Answer: B. {language}", language)
        st.write(test)

# --- TIMER PAGE ---
elif st.session_state.page == "Timer":
    if st.button("🏠 Back to Home"): st.session_state.page = "Home"; st.rerun()
    st.subheader(txt["timer_title"]); study_timer()
    st.metric("Total Study Time Today", f"{int(st.session_state.total_time//3600)}h {int((st.session_state.total_time%3600)//60)}m")

st.markdown("---"); st.caption("Made with ❤️ by Anugya | BrainBloom")
