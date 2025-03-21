

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import base64
import os
from flask import Flask, request, render_template, session
from google import genai

import google.generativeai as genai 

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize GenAI client
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)

def initialize_conversation():
    """Initialize the conversation history"""
    return [
        {"role": "user", "text": "HELLO"},
        {"role": "model", "text": "Hello there! How can I help you today?"},
        {"role": "user", "text": "hello"},
        {"role": "model", "text": "Hi! Are you seeking medical advice or workout/fitness tips today?"},
    ]

def generate_response(user_input):
    """Generate response using Gemini API"""
    contents = []
    for msg in session['conversation']:
        contents.append(types.Content(
            role="user" if msg['role'] == "user" else "model",
            parts=[types.Part.from_text(text=msg['text'])],
        ))
    
    # Add new user input
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_input)],
    ))

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""(Your existing system instruction here)"""),
        ],
    )

    full_response = ""
    for chunk in client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=contents,
        config=generate_content_config,
    ):
        full_response += chunk.text

    return full_response

@app.route('/', methods=['GET', 'POST'])
def chat():
    if 'conversation' not in session:
        session['conversation'] = initialize_conversation()
    
    if request.method == 'POST':
        user_input = request.form['message']
        bot_response = generate_response(user_input)
        
        # Update conversation
        session['conversation'].append({"role": "user", "text": user_input})
        session['conversation'].append({"role": "model", "text": bot_response})
        session.modified = True
    
    return render_template('chat.html', conversation=session['conversation'])

if __name__ == '__main__':
    app.run(debug=True)