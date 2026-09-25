"""
app.py

Flask backend for the solar-system-only chatbot.
It receives a user message from the front end, sends it to the Gemini API
along with the system prompt from chatbot_config.py, and returns the reply.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Please add it to your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Create the model once with the system prompt baked in
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question about the solar system."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text.strip() if response.text else "Sorry, I couldn't generate a reply."
    except Exception as exc:
        reply_text = f"Something went wrong while contacting the AI service: {exc}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
