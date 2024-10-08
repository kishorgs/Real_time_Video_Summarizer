import moviepy.editor
from pydub import AudioSegment
import os
import speech_recognition as sr
import re
import google.generativeai as genai
from rich import print
from rich.console import Console
from rich.text import Text


# Configure Generative AI API
genai.configure(api_key="Your_Gemini_API_Key")

def format_text(text):
    console = Console()

    # Process each line to interpret the text formatting
    formatted_lines = []
    for line in text.splitlines():
        if line.startswith("* **"):  # Bold with bullet
            line = line.replace("* **", "- [bold]").replace(":**", "[/bold]:")
        elif line.startswith("*"):  # Bullet
            line = line.replace("*", "-")
        formatted_lines.append(line)

    # Join the lines back into a formatted text
    formatted_text = "\n".join(formatted_lines)

    return formatted_text

# Function to extract and summarize video
def summarize_video(video_file):
    # Step 1: Extract audio from video
    video = moviepy.editor.VideoFileClip(video_file)
    audio = video.audio
    audio_file_path = 'extracted_audio.wav'
    audio.write_audiofile(audio_file_path)

    # Step 2: Split audio into 1-minute segments
    audio = AudioSegment.from_file(audio_file_path)
    segment_length = 60 * 1000
    audio_duration = len(audio)

    # Create directory for audio segments
    output_dir = 'audio_segments'
    os.makedirs(output_dir, exist_ok=True)

    segment_counter = 0
    for start in range(0, audio_duration, segment_length):
        end = min(start + segment_length, audio_duration)
        segment = audio[start:end]
        segment_file_path = os.path.join(output_dir, f'segment_{segment_counter}.wav')
        segment.export(segment_file_path, format='wav')
        segment_counter += 1

    # Step 3: Transcribe audio segments
    recognizer = sr.Recognizer()
    final_transcription = ""
    sorted_files = sorted(os.listdir(output_dir), key=lambda x: int(re.search(r'(\d+)', x).group(1)))
    
    for filename in sorted_files:
        file_path = os.path.join(output_dir, filename)
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio_data)
                final_transcription += transcription + " "
            except sr.UnknownValueError:
                pass

    # Step 4: Summarize transcription using Generative AI
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    })
    chat_session = model.start_chat(history=[])
    prompt_message = final_transcription + "\n\nSummarize this text into points without adding any additional information or changing context. Use bullet points."
    response = chat_session.send_message(prompt_message)

    return format_text(response.text) 
