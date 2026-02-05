from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import requests
import textwrap




# Configuration for Hugging Face API
API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-large"

HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/json"
}

def to_telugu(text):
    """
    Translates the given text to Telugu.

    Args:
        text (str): The text to translate.

    Returns:
        str: The translated text in Telugu.
    """
    try:
        return GoogleTranslator(source='auto', target='te').translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def speak_telugu(text):
    """
    Generates an audio file for the given Telugu text using gTTS.

    Args:
        text (str): The text to convert to speech.

    Returns:
        str: The filename of the generated audio file.
    """
    filename = "telugu_audio.mp3"
    try:
        tts = gTTS(text=text, lang='te')
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Audio generation error: {e}")
        return None

def ask_llm(prompt):
    """
    Queries the Hugging Face LLM with the given prompt.

    Args:
        prompt (str): The prompt to send to the LLM.

    Returns:
        str: The response from the LLM or an error message.
    """
    payload = {"inputs": prompt}
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes

        try:
            result = response.json()
        except ValueError:
            return "AI service did not return valid JSON data. Try again."

        if isinstance(result, dict) and "error" in result:
            return f"API Error: {result['error']}"

        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            return result[0]["generated_text"]

        return "Unexpected AI response format."

    except requests.exceptions.RequestException as e:
        return f"Connection issue with AI service: {e}"

def summarize_doc(chunks):
    """
    Summarizes the document by extracting main topics and generating a Telugu summary with audio.

    Args:
        chunks (list): List of text chunks from the document.

    Returns:
        tuple: (English summary, Telugu summary, audio file path)
    """
    if not chunks:
        return "No content to summarize.", "", None

    text = chunks[0]
    lines = text.split("\n")
    topics = []

    for line in lines:
        line = line.strip()
        if len(line) > 5 and line.isupper():
            topics.append(line)

    if not topics:
        important = [line for line in lines if len(line) > 40]
        summary = "This document contains key formulas and concepts related to: " + ", ".join(important[:5])
    else:
        summary = "This document covers important topics in Electromagnetics such as: " + ", ".join(topics[:6])

    telugu_summary = to_telugu(summary)
    audio_file = speak_telugu(telugu_summary)

    return summary, telugu_summary, audio_file

def extract_key_points(chunks):
    """
    Extracts key points from the document and generates a Telugu version with audio.

    Args:
        chunks (list): List of text chunks from the document.

    Returns:
        tuple: (English key points, Telugu key points, audio file path)
    """
    if not chunks:
        return "No content to extract key points from.", "", None

    text = chunks[0]
    lines = text.split(".")
    points = [line.strip() for line in lines if len(line.strip()) > 40]
    key_points = "\n• " + "\n• ".join(points[:5])

    telugu = to_telugu(key_points)
    audio_file = speak_telugu(telugu)

    return key_points, telugu, audio_file

def find_best_chunk(question, chunks):
    """
    Finds the best matching chunk for the given question.

    Args:
        question (str): The question to match.
        chunks (list): List of text chunks.

    Returns:
        str: The best matching chunk or the first chunk if no match.
    """
    for chunk in chunks:
        if question.lower() in chunk.lower():
            return chunk
    return chunks[0] if chunks else ""

def answer_question(question, chunks):
    """
    Answers a question based on the document chunks.

    Args:
        question (str): The question to answer.
        chunks (list): List of text chunks.

    Returns:
        str: The answer or a default message.
    """
    context = find_best_chunk(question, chunks)
    sentences = context.split(".")
    for s in sentences:
        if question.lower().split()[0] in s.lower():
            return s.strip()
    return "The document discusses this topic, but no exact sentence match was found."





from gtts import gTTS

def speak_english(text):
    filename = "english_audio.mp3"
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename
def speak_telugu_voice(text):
    return speak_telugu(text)
