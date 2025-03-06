from flask import Flask, render_template, request, jsonify
import requests
import pyttsx3

app = Flask(__name__)

# Ollama server configuration
OLLAMA_SERVER = "http://192.168.1.50:11434"  # Change this to your actual local IP
MODEL_NAME = "llama3:latest"

# Initialize text-to-speech engine
engine = pyttsx3.init()
selected_voice_index = 0  # Change if needed
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[selected_voice_index].id)

# Conversation history
conversation_history = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "Empty input"}), 400
    
    conversation_history += f"\nUser: {user_input}\n"
    
    response = requests.post(
        f"{OLLAMA_SERVER}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": conversation_history,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        try:
            result = response.json()
            bot_reply = result.get("response", "No response").strip()
            conversation_history += f"Llama3: {bot_reply}\n"
            return jsonify({"response": bot_reply})
        except requests.exceptions.JSONDecodeError:
            return jsonify({"error": "Failed to decode JSON"}), 500
    else:
        return jsonify({"error": response.text}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
