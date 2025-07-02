from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action='/process',
        method='POST',
        language='en-GB',
        timeout=5
    )
    gather.say("Hello! Please tell me your full name and the reason you are calling.")
    response.append(gather)
    response.say("Sorry, I didn’t catch that. Goodbye.")
    return str(response), 200

@app.route("/process", methods=["POST"])
def process():
    speech_result = request.form.get("SpeechResult", "")
    print(f"🗣️ User said: {speech_result}")

    # Ask OpenAI to extract name and reason
    prompt = f"""Extract the caller's full name and reason for calling from this input:
\"{speech_result}\".
Return:
Name: [caller name]
Reason: [caller reason]"""

    try:
        chat_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = chat_response.choices[0].message.content.strip()
    except Exception as e:
        summary = "Sorry, I couldn't process what you said."
        print("❌ OpenAI error:", e)

    # Read back to caller
    response = VoiceResponse()
    response.say(f"Thank you. I have recorded: {summary}")
    response.hangup()
    return str(response), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
