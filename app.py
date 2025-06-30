import streamlit as st
import core
from datetime import datetime
import io
from fpdf import FPDF
import re

# Initialize history in session state
if "history" not in st.session_state:
    st.session_state.history = []

# streamlit app
st.set_page_config(page_title="Study Coach AI", layout="wide")
st.title("Youtube transcript to detailed notes convertor")

youtube_link = st.text_input("Paste your YouTube lecture/tutorial link below:")

video_id = core.get_video_id(youtube_link)
print("Video ID:", video_id)

# displaying thumbnail image
if youtube_link and video_id:
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", caption="Video Preview", width=320)

    difficulty = st.selectbox(
        "Select your learning level:",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button("Generate Study Material"):
        with st.spinner("Extracting transcript and analyzing..."):
            transcript_text = core.extract_transcript_details(youtube_link)

        if transcript_text:
            with st.spinner("Generating Summary..."):
                st.session_state.summary = core.generate_summary(transcript_text, difficulty)
            with st.spinner("Generating Flashcards..."):
                st.session_state.flashcards = core.generate_flashcards(transcript_text)
            with st.spinner("Generating Revision Plan..."):
                st.session_state.revision_plan = core.generate_revision_plan(transcript_text)
            with st.spinner("Finding Extra Resources..."):
                st.session_state.resources = core.generate_resources(transcript_text)
            st.session_state.transcript_text = transcript_text
            st.session_state.history.append({
                "video_url": youtube_link,
                "summary": st.session_state.summary,
                "flashcards": st.session_state.flashcards,
                "revision_plan": st.session_state.revision_plan,
                "resources": st.session_state.resources,
                "timestamp": str(datetime.now())
            })
        else:
            st.error("⚠️ Could not extract the transcript. Please check the video URL.")

# Only show tabs if content exists in session_state
if all(x in st.session_state for x in ["summary", "flashcards", "revision_plan", "resources"]):
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🃏 Flashcards", "🗓️ Revision Plan", "🔗 Resources"])

    with tab1:
        st.download_button("📥 Download Summary", st.session_state.summary, file_name="summary.txt")
        st.subheader("Video Summary")
        st.write(st.session_state.summary)

    with tab2:
        st.download_button("📥 Download Flashcards", st.session_state.flashcards, file_name="flashcards.txt")
        st.subheader("Flashcards")
        st.markdown(st.session_state.flashcards)
        st.divider()

    with tab3:
        st.subheader("5-Day Revision Plan")
        st.write(st.session_state.revision_plan)

    with tab4:
        st.subheader("Extra Learning Resources")
        st.write(st.session_state.resources)

st.markdown("## 🔁 Your History")
for entry in st.session_state.history[::-1]:
    with st.expander(f"{entry['video_url']} – {entry['timestamp']}"):
        st.write(entry["summary"][:300] + "...")

# --- Personal Dashboard Tab ---

def export_text_to_pdf(text, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    # Replace non-latin1 characters with a safe fallback (e.g., '?')
    def safe_latin1(s):
        return s.encode('latin-1', errors='replace').decode('latin-1')
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, safe_latin1(line))
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

st.markdown("---")
st.header("📊 Your Study Dashboard")
if st.session_state.history:
    for idx, entry in enumerate(st.session_state.history[::-1]):
        with st.expander(f"{entry['video_url']} – {entry['timestamp']}"):
            st.write("**Summary (first 300 chars):**", entry["summary"][:300] + "...")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("Download Summary (txt)", entry["summary"], file_name=f"summary_{idx}.txt")
                pdf_sum = export_text_to_pdf(entry["summary"], "Summary")
                st.download_button("Download Summary (PDF)", pdf_sum, file_name=f"summary_{idx}.pdf")
            with col2:
                st.download_button("Download Flashcards (txt)", entry["flashcards"], file_name=f"flashcards_{idx}.txt")
                pdf_flash = export_text_to_pdf(entry["flashcards"], "Flashcards")
                st.download_button("Download Flashcards (PDF)", pdf_flash, file_name=f"flashcards_{idx}.pdf")
            with col3:
                st.download_button("Download Revision Plan (txt)", entry["revision_plan"], file_name=f"revision_{idx}.txt")
                pdf_rev = export_text_to_pdf(entry["revision_plan"], "Revision Plan")
                st.download_button("Download Revision Plan (PDF)", pdf_rev, file_name=f"revision_{idx}.pdf")
            st.write("**Resources:**", entry["resources"])
else:
    st.info("No study history yet. Generate some study material to see your dashboard!")

# --- Feedback Sidebar ---
st.sidebar.header("💬 Feedback or Contact")
with st.sidebar.form("feedback_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Message or Feedback")
    submitted = st.form_submit_button("Send Feedback")
    if submitted:
        with open("feedback.txt", "a", encoding="utf-8") as f:
            f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n{'-'*40}\n")
        st.sidebar.success("Thank you for your feedback!")
