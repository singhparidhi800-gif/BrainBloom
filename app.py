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

# Page Config (Must be first)
st.set_page_config(page_title="BrainBloom - AI Study Companion", page_icon="🌸", layout="wide")

# --- BROWSER LOCAL STORAGE PERSISTENCE (Fixes Streamlit Cloud Data Loss) ---
def init_storage():
    components.html("""
    <script>
    if (!localStorage.getItem('brainbloom_data')) {
        const initialData = { user_name: 'Future Topper', total_time: 0, sessions: 0, coins: 50, is_vip: false };
        localStorage.setItem('brainbloom_data', JSON.stringify(initialData));
    }
    </script>
    """, height=0)

init_storage()

# Session State Initialization
if 'user_name' not in st.session_state: st.session_state.user_name = "Future Topper"
if 'total_time' not in st.session_state: st.session_state.total_time = 0
if 'study_sessions' not in st.session_state: st.session_state.study_sessions = 0
if 'is_vip' not in st.session_state: st.session_state.is_vip = False
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'video_ready' not in st.session_state: st.session_state.video_ready = False
if 'script' not in st.session_state: st.session_state.script = ""
if 'points' not in st.session_state: st.session_state.points = []
if 'image_urls' not in st.session_state: st.session_state.image_urls = []

# Safe API Client
groq_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=groq_key) if groq_key else None

def get_ai_answer(prompt):
    if not client:
        return "⚠️ GROQ_API_KEY Missing! Please add it in Streamlit Secrets."
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"AI Connection Error: {str(e)}"

# Fixed Robust Image Generator with High Visual Prompting
def generate_hd_images(topic, points):
    urls = []
    styles = ["3d vibrant colorful digital artwork, educational infographic, detailed", 
              "ultra high quality modern vector illustration, concept explanation, vibrant clean background"]
    for i in range(2):
        pt_text = points[i] if i < len(points) else f"Step {i+1} summary of {topic}"
        clean_prompt = f"{topic}, {pt_text}, {styles[i]}"
        safe_encoded = urllib.parse.quote(clean_prompt)
        seed = random.randint(1000, 99999)
        img_url = f"https://image.pollinations.ai/prompt/{safe_encoded}?seed={seed}&width=800&height=450&nologo=true"
        urls.append(img_url)
    return urls

# PDF Creator
def create_pdf(notes, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"BrainBloom Master Notes: {topic}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    clean_notes = notes.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_notes)
    filename = f"{topic.replace(' ', '_')}_Notes.pdf"
    pdf.output(filename)
    return filename

# --- AESTHETIC CSS STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 50%, #F3E8FF 100%); }

/* Glassmorphism Card Fix */
.main-card {
    background: rgba(255, 255, 255, 0.92);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(226, 232, 240, 0.8);
    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.05);
    margin-bottom: 15px;
}
.vip-badge {
    background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
    color: #000; font-weight: 800; padding: 4px 12px; border-radius: 12px; font-size: 12px;
}
.viral-tag {
    background: #4F46E5; color: white; padding: 3px 10px; border-radius: 10px; font-size: 11px; font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# Top Bar Header
col_logo, col_title, col_vip = st.columns([1, 4, 2])
with col_logo:
    st.markdown("### 🌸")
with col_title:
    st.markdown("## **BrainBloom AI** 🚀")
with col_vip:
    if st.session_state.is_vip:
        st.markdown("<span class='vip-badge'>👑 VIP UNLOCKED</span>", unsafe_allow_html=True)
    else:
        if st.button("👑 Unlock VIP (₹49)", use_container_width=True):
            st.session_state.page = "Monetize"
            st.rerun()

st.divider()

# --- HOME NAVIGATION ---
if st.session_state.page == "Home":
    st.markdown(f"### 👋 Welcome, **{st.session_state.user_name}**!")
    st.caption("Transform study time into viral knowledge & top grades!")
    
    # Feature Grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("### 🎭 BrainRot to BrainGain <span class='viral-tag'>VIRAL</span>", unsafe_allow_html=True)
        st.write("Understand tough Physics/Chem/Math topics via Memes & Anime analogies!")
        if st.button("Launch Meme Explainer 🔥", use_container_width=True):
            st.session_state.page = "BrainRot"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("### ⚡ Night-Before Survival Kit", unsafe_allow_html=True)
        st.write("1-Hour Emergency Notes + Top 5 Guaranteed Exam Questions + Formulas!")
        if st.button("Generate Survival Kit ⚡", use_container_width=True):
            st.session_state.page = "Survival"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("### 🎨 2-Step HD Visual Class", unsafe_allow_html=True)
        st.write("AI generates sequential step-by-step illustrations with explanation.")
        if st.button("Open AI Visual Class ✨", use_container_width=True):
            st.session_state.page = "Video"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("### 📱 YouTube Shorts Script AI", unsafe_allow_html=True)
        st.write("Create viral educational 30s scripts for Reels/Shorts & earn!")
        if st.button("Generate Shorts Script 🎬", use_container_width=True):
            st.session_state.page = "Shorts"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 🎭 MEME / GEN-Z EXPLAINER PAGE ---
elif st.session_state.page == "BrainRot":
    if st.button("⬅️ Back"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎭 BrainRot to BrainGain (Gen-Z Explainer)")
    topic = st.text_input("Enter Topic (e.g. Thermodynamics, Integration, Photosynthesis):")
    vibe = st.selectbox("Choose Style Vibe:", ["Gen-Z Slang & Memes 💀", "Anime / Superhero Analogy ⚡", "K-Pop & Pop Culture 🎵", "Funny Hindi Webseries Style 🍿"])
    
    if st.button("Explain in Viral Style 🔥"):
        if topic:
            with st.spinner("Cooking up viral explanation..."):
                prompt = f"Explain the academic concept '{topic}' in style of {vibe}. Use hilarious analogies, clear bullet points, easy simple breakdown so a student never forgets it. Language: Hinglish."
                res = get_ai_answer(prompt)
                st.markdown(f"<div class='main-card'>{res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                st.balloons()
        else: st.error("Enter a topic!")

# --- 🎨 2-STEP HD VISUAL CLASS PAGE ---
elif st.session_state.page == "Video":
    if st.button("⬅️ Back"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎨 2-Step HD AI Visual Class")
    topic = st.text_input("Enter Concept Name (e.g., Newton's Laws of Motion):")
    
    if st.button("Generate HD Visual Class ✨"):
        if topic:
            with st.spinner("AI is generating HD visuals & explanation..."):
                script_prompt = f"Explain {topic} in 2 precise steps for class 11-12 student in Hinglish. Step 1: Core Concept. Step 2: Practical Application/Formula."
                script = get_ai_answer(script_prompt)
                
                # Clean point extraction
                lines = [l.strip() for l in script.split('\n') if len(l.strip()) > 10]
                pts = lines[:2] if len(lines) >= 2 else [f"Step 1 Core concept of {topic}", f"Step 2 Real application of {topic}"]
                
                imgs = generate_hd_images(topic, pts)
                st.session_state.script = script
                st.session_state.points = pts
                st.session_state.image_urls = imgs
                st.session_state.video_ready = True
                st.rerun()
        else: st.error("Please enter a topic!")

    if st.session_state.video_ready:
        st.markdown(f"### 📍 Concept: {topic}")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.image(st.session_state.image_urls[0], caption="Step 1: Visual Overview", use_container_width=True)
            st.info(st.session_state.points[0] if len(st.session_state.points)>0 else "Step 1")
        with col_v2:
            st.image(st.session_state.image_urls[1], caption="Step 2: Practical Mechanism", use_container_width=True)
            st.success(st.session_state.points[1] if len(st.session_state.points)>1 else "Step 2")

        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("#### 📖 Full Explanation Script:")
        st.write(st.session_state.script)
        st.markdown("</div>", unsafe_allow_html=True)

# --- ⚡ NIGHT-BEFORE SURVIVAL KIT PAGE ---
elif st.session_state.page == "Survival":
    if st.button("⬅️ Back"): st.session_state.page = "Home"; st.rerun()
    st.subheader("⚡ 1-Hour Night-Before Exam Survival Kit")
    subject = st.text_input("Subject / Chapter Name (e.g., Organic Chemistry, Calculus):")
    
    if st.button("Generate Survival Sheet 📄"):
        if subject:
            with st.spinner("Creating high-yield exam sheet..."):
                prompt = f"Create a 1-page emergency exam sheet for {subject}. Include: 1) Top 5 Guaranteed Exam Questions with Answers. 2) Formula/Key-Point Cheat Sheet. 3) Common Exam Mistakes to avoid. Language: Hinglish."
                res = get_ai_answer(prompt)
                st.markdown(f"<div class='main-card'>{res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                pdf_file = create_pdf(res, subject)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF Survival Sheet", f, file_name=pdf_file)
        else: st.error("Enter chapter name!")

# --- 📱 SHORTS SCRIPT AI ---
elif st.session_state.page == "Shorts":
    if st.button("⬅️ Back"): st.session_state.page = "Home"; st.rerun()
    st.subheader("🎬 Viral 30-Sec YouTube Shorts Script Generator")
    topic = st.text_input("Enter Topic for Short Video:")
    
    if st.button("Generate Script & Hook 🔥"):
        if topic:
            with st.spinner("Creating viral script..."):
                prompt = f"Write a catchy 30-second YouTube Short / Reel script on {topic}. Include: 1) Viral Hook (First 3 seconds). 2) Mindblowing Fact/Explanation. 3) Call to Action (Subscribe to channel). Hinglish language."
                res = get_ai_answer(prompt)
                st.markdown(f"<div class='main-card'>{res.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        else: st.error("Enter topic!")

# --- 💰 MONETIZATION / VIP PASS PAGE ---
elif st.session_state.page == "Monetize":
    if st.button("⬅️ Back"): st.session_state.page = "Home"; st.rerun()
    st.subheader("👑 Unlock BrainBloom VIP Pass")
    
    st.markdown("""
    <div class='main-card' style='text-align: center;'>
        <h2>✨ VIP Features:</h2>
        <p>✅ Unlimited HD Visual Class Generation</p>
        <p>✅ Instant Download of PDF Cheat Sheets & Survival Kits</p>
        <p>✅ 24/7 AI Doubt Solver Access</p>
        <hr>
        <h3>Special Price: <b>₹49 / month</b></h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💳 Pay via UPI:")
    st.info("Scan UPI QR or send ₹49 to UPI ID: **yourname@upi**")
    
    utr = st.text_input("Enter Payment Transaction ID / UTR Number:")
    if st.button("Verify & Activate VIP Pass 🚀"):
        if len(utr) >= 6:
            st.session_state.is_vip = True
            st.success("🎉 VIP Access Activated Successfully!")
            st.balloons()
            time.sleep(2)
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("Please enter a valid Transaction ID / UTR.")

st.markdown("---")
st.caption("BrainBloom AI v3.0 | Built with ❤️ for Future Toppers")
