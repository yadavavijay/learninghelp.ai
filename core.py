import google.generativeai as genai
from dotenv import load_dotenv
import os
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
import re


# Load environment variables from .env file
load_dotenv()

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))



def get_video_id(youtube_video_url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_video_url)
    return match.group(1) if match else None




# getting the transcript details from the youtube video
def extract_transcript_details(youtube_url):
    try:
        video_id = get_video_id(youtube_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([i['text'] for i in transcript])
        return transcript_text
    except Exception as e:
        print(f"[Transcript Error] {e}")
        return None

    

# helper function - send prompt to gemini
def generate_with_gemini(prompt, content):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt + content)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "Sorry, I couldn't generate the output due to an error."
    

# 🔸 Difficulty-specific descriptions
def get_difficulty_description(level):
    level = level.lower()
    if level == "beginner":
        return "super simple language like you're teaching someone new to the topic"
    elif level == "intermediate":
        return "clear language suitable for college students who know the basics"
    elif level == "advanced":
        return "technical and detailed language suitable for professionals or advanced learners"
    else:
        return "clear language for general learners"
    


# generate summary
def generate_summary(transcript_text, level="Intermediate"):
    style = get_difficulty_description(level)
    prompt = (
        f"You're a helpful study coach. Summarize the following video transcript into clear, bullet-point notes "
        f"within 300 words, using {style}. Transcript:\n"
    )
    return generate_with_gemini(prompt, transcript_text)


# generate flashcards
def generate_flashcards(transcript_text, level="Intermediate"):
    style = get_difficulty_description(level)
    prompt = (
        f"You're an AI tutor creating flashcards. From the transcript, generate 5–10 flashcards in Q&A format "
        f"using {style}. Make the answers short and factual. Transcript:\n"
    )
    return generate_with_gemini(prompt, transcript_text)


# generate the revision plan
def generate_revision_plan(transcript_text, level="Intermediate"):
    style = get_difficulty_description(level)
    prompt = (
        f"Create a 5-day revision plan based on the transcript, using {style}. "
        f"For each day, include:\n"
        f"1. Topics to revise\n2. One quiz-style question\n3. Time estimate (in minutes). Transcript:\n"
    )
    return generate_with_gemini(prompt, transcript_text)


# generate extra resources for study
def generate_resources(transcript_text):
    prompt = (
        "From this transcript, suggest 2 to 3 YouTube videos or resources that help learners go deeper. "
        "Include a short reason for each recommendation. Transcript:\n"
    )
    return generate_with_gemini(prompt, transcript_text)



