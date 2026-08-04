import streamlit as st
import random
from datetime import datetime
import google.generativeai as genai # 1. YE NAYA ADD KIYA

st.set_page_config(page_title="BrainBloom - AI Didi", page_icon="✨", layout="centered")

# 2. SECRETS SE KEY UTHAO
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. AI DIDID KA FUNCTION BANAYA
def get_ai_answer(doubt, language):
    if language == "Hindi":
        prompt = f"""
        Tum "AI Doubt Didi" ho. Ek friendly teacher ho jo 6th se 12th tak ke bachchon ko padhati ho.
        Jawab Hindi me do, simple words me, example ke saath. 4-5 line me khatam karo.
        Student ka sawaal: {doubt}
        """
    else:
        prompt = f"""
        You are "AI Doubt Didi". A friendly teacher for 6th to 12th students.
        Answer in simple English, with an example. Keep it short, 4-5 lines.
        Student's question: {doubt}
        """
    response = model.generate_content(prompt)
    return response.text

# Language Dictionary
LANG = {
    "English": {
        "title": "✨ BrainBloom - Your AI Didi",
        "caption": "Magic of Notes + AI Video + 24*7 Doubt Solver",
        "menu": ["🏠 Home", "🎥 AI Video Class", "📝 Magic Notes", "❓ AI Doubt 24*7"],
        "welcome": "Hello Future Topper! 🌸",
        "name": "Enter your name",
        "start": "Let's Start Learning",
        "video_title": "🎥 AI Video Class",
        "video_placeholder": "Which topic do you want to understand? Ex: Photosynthesis, Pythagoras",
        "video_btn": "Explain like a Video",
        "notes_title": "📝 Magic Notes - Everything in 1 Page",
        "subject": "Choose Subject",
        "topic": "Enter Topic: Ex: Cell, Algebra, Mughal Empire",
        "notes_btn": "Create Magic Notes ✨",
        "doubt_title": "❓ AI Doubt Solver - Didi Online 24*7",
        "doubt_placeholder": "Ask your doubt here... even at 2 AM 😴",
        "doubt_btn": "Get Answer Now",
        "download": "Download Notes"
    },
    "Hindi": {
        "title": "✨ BrainBloom - Tumhari AI Didi",
        "caption": "Notes ka Jadu + AI Video + 24*7 Doubt Solver",
        "menu": ["🏠 Home", "🎥 AI Video Class", "📝 Notes ka Jadu", "❓ AI Doubt 24*7"],
        "welcome": "Namaste Future Topper! 🌸",
        "name": "Apna naam likho",
        "start": "Shuru Karein",
        "video_title": "🎥 AI Video Class",
        "video_placeholder": "Kaunsa topic samjhna hai? Ex: Photosynthesis, Pythagoras",
        "video_btn": "Video Jaisa Samjhao",
        "notes_title": "📝 Notes ka Jadu - 1 Page me sab",
        "subject": "Subject chuno",
        "topic": "Topic likho: Ex: Cell, Algebra, Mughal Empire",
        "notes_btn": "Jadu se Notes Banao ✨",
        "doubt_title": "❓ AI Doubt Solver - Didi 24 Ghante Online",
        "doubt_placeholder": "Apna doubt yaha likho... raat 2 baje bhi 😴",
        "doubt_btn": "Abhi Jawab Do",
        "download": "Notes Download karo"
    }
}

# Styling
st.markdown("""
<style>
.stButton>button {background: linear-gradient(90deg, #FF69B4, #FF1493); color: white; border-radius: 15px; font-weight: bold;}
h1 {color: #FF1493;}
</style>
""", unsafe_allow_html=True)

# LANGUAGE SWITCHER - Top Right
col1, col2 = st.columns([4,1])
with col2:
    language = st.selectbox("🌐 Language", ["English", "Hindi"], index=0) # Default English

txt = LANG[language]

st.title(txt["title"])
st.caption(txt["caption"])

with st.sidebar:
    st.header("📚 Menu")
    page = st.radio("Select", txt["menu"])

# 1. HOME
if page == txt["menu"][0]:
    st.subheader(txt["welcome"])
    name = st.text_input(txt["name"])
    if st.button(txt["start"]):
        if name:
            msg = f"Welcome {name}! Let's make learning easy 💪" if language=="English" else f"Welcome {name}! Aaj padhai ko easy banayenge 💪"
            st.success(msg)
            st.balloons()
        else:
            warn = "Please enter your name first 😊" if language=="English" else "Pehle naam likho na 😊"
            st.warning(warn)

# 2. AI VIDEO CLASS
elif page == txt["menu"][1]:
    st.subheader(txt["video_title"])
    topic = st.text_input(txt["video_placeholder"])

    if st.button(txt["video_btn"]):
        if topic:
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Demo
            step1 = "Step 1: Understand the basic concept" if language=="English" else "Step 1: Basic concept samjho"
            step2 = "Step 2: Learn with an example" if language=="English" else "Step 2: Example se samjho"
            step3 = "Step 3: Now you try it" if language=="English" else "Step 3: Khud try karo"
            st.success(step1)
            st.success(step2)
            st.success(step3)
        else:
            err = "Please enter a topic first 😅" if language=="English" else "Pehle topic likho na 😅"
            st.error(err)

# 3. NOTES KA JADU
elif page == txt["menu"][2]:
    st.subheader(txt["notes_title"])
    subject = st.selectbox(txt["subject"], ["Science", "Math", "History", "English"])
    topic = st.text_input(txt["topic"])

    if st.button(txt["notes_btn"]):
        if topic:
            st.balloons()
            head = f"### Super Short Notes: {topic}" if language=="English" else f"### {topic} ke Super Short Notes"
            st.success(head)

            if language=="English":
                st.write(f"**Definition:** {topic} is a very important topic in {subject}")
                st.write("**3 Key Points:**")
                st.write("1. Basic concept")
                st.write("2. Formula/Example")
                st.write("3. How it comes in exam")
                st.write("**Memory Trick:** Make a story from first letters 😄")
            else:
                st.write(f"**Definition:** {topic} {subject} ka bahut important topic hai")
                st.write("**3 Key Points:**")
                st.write("1. Basic concept")
                st.write("2. Formula/Example")
                st.write("3. Exam me kaise aayega")
                st.write("**Yaad rakhne ki Trick:** Pehle akshar se story banao 😄")

            content = f"{topic} Notes\n1. Basic\n2. Example\n3. Exam Tips"
            st.download_button(txt["download"], content, file_name=f"{topic}.txt")
        else:
            err = "Please enter a topic" if language=="English" else "Topic likho tabhi jadu hoga"
            st.error(err)

# 4. AI DOUBT 24*7 - AB YE ASLI AI HAI
elif page == txt["menu"][3]:
    st.subheader(txt["doubt_title"])
    doubt = st.text_area(txt["doubt_placeholder"])

    if st.button(txt["doubt_btn"]):
        if doubt:
            q = "Your Doubt:" if language=="English" else "Tumhara Doubt:"
            a = "AI Didi's Answer:" if language=="English" else "AI Didi ka Jawab:"
            st.info(f"**{q}** {doubt}")

            with st.spinner("Didi soch rahi hai... 5 sec" if language=="Hindi" else "Didi is thinking... 5 sec"):
                answer = get_ai_answer(doubt, language) # 4. YAHAN ASLI AI CALL HUA

            st.success(f"**{a}**")
            st.write(answer) # ASLI JAWAB YAHAN
            st.caption(f"Answered at: {datetime.now().strftime('%I:%M %p')}")
        else:
            warn = "Please ask your doubt Didi is waiting 💜" if language=="English" else "Doubt likho didi, main wait kar rahi hu 💜"
            st.warning(warn)

st.markdown("---")
st.caption("Made with ❤️ by Anugya | BrainBloom")
