
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
import os
from flask import Flask, request, render_template, session
import google.generativeai as genai  # Correct import

# Initialize Flask app first
app = Flask(__name__)
# Use environment variable for secret key with fallback
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# Configure Gemini API
if "GEMINI_API_KEY" not in os.environ:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')  # Correct model initialization

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
    try:
        # Prepare conversation history
        conversation = session.get('conversation', [])
        history = [{'role': msg['role'], 'parts': [msg['text']]} for msg in conversation]
        
        # Add new user input
        history.append({'role': 'user', 'parts': [user_input]})
        
        # Generate response
        response = model.generate_content(
            contents=history,
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192
            }
        )
        
        return response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def chat():
    if 'conversation' not in session:
        session['conversation'] = initialize_conversation()
    
    if request.method == 'POST':
        if 'message' not in request.form:
            return "Invalid request", 400
            
        user_input = request.form['message']
        if not user_input.strip():
            return "Message cannot be empty", 400
        
        try:
            bot_response = generate_response(user_input)
            
            # Update conversation
            session['conversation'].extend([
                {"role": "user", "text": user_input},
                {"role": "model", "text": bot_response}
            ])
            session.modified = True
            
        except Exception as e:
            return f"Error processing request: {str(e)}", 500
    
    return render_template('chat.html', conversation=session['conversation'])

if __name__ == '__main__':
    app.run(debug=True)