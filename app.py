from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set up Flask app
app = Flask(__name__)

# Initialize OpenAI client (✅ correct way for v1+)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Email config from .env
YOUR_EMAIL = os.getenv("YOUR_EMAIL")
YOUR_EMAIL_PASSWORD = os.getenv("YOUR_EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Handle incoming call
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = Gather(input='speech', action='/process', method='POST', language='en-GB', timeout=5)
    gather.say("Hello! Please tell me your full name and the reason you are calling.")
    response.append(gather)
    response.say("Sorry, I didn't catch that. Goodbye.")
    return str(response), 200

# Handle gathered speech
@app.route("/process", methods=["POST"])
def process():
    speech_result = request.form.get("SpeechResult", "")
    print(f"🗣️ User said: {speech_result}")

    prompt = f"""Extract the caller's full name and reason for calling from this input:
\"{speech_result}\".
Return:
Name: [caller name]
Reason: [caller reason]
"""

    try:
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = chat_response.choices[0].message.content.strip()
    except Exception as e:
        summary = "Sorry, there was an issue processing the input."
        print("OpenAI error:", e)

    send_email("New Voice Bot Call", f"Speech Text:\n{speech_result}\n\nExtracted Info:\n{summary}")

    response = VoiceResponse()
    response.say(f"Thank you. I have recorded: {summary}")
    response.hangup()
    return str(response), 200

# Send email using Office 365
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = YOUR_EMAIL
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(YOUR_EMAIL, YOUR_EMAIL_PASSWORD)
            server.send_message(msg)
            print("✅ Email sent")
    except Exception as e:
        print("❌ Email failed:", e)

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5001)