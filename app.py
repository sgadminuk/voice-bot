from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# OpenAI Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/process", methods=["POST"])
def process():
    speech_result = request.form.get("SpeechResult", "")
    print(f"🗣️ User said: {speech_result}")

    prompt = f"""Extract the caller's full name and reason for calling from this input:
\"{speech_result}\".
Return:
Name: [caller name]
Reason: [caller reason]"""

    try:
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = chat_response.choices[0].message.content.strip()
    except Exception as e:
        summary = "Sorry, I couldn't process what you said."
        print("❌ OpenAI error:", e)

    response = VoiceResponse()
    response.say(f"Thank you. I have recorded: {summary}")
    response.hangup()
    return str(response), 200
