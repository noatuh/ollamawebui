from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import pyttsx3
import os
import sys
import keyboard

app = Flask(__name__)

# Default Ollama server configuration (can be overridden per request)
DEFAULT_OLLAMA_SERVER = "http://192.168.1.50:11434"
DEFAULT_MODEL_NAME = "llama3:latest"

# Initialize text-to-speech engine (not currently used in the chat flow)
engine = pyttsx3.init()
selected_voice_index = 0  # Change if needed
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[selected_voice_index].id)

# Global conversation history (note: this is shared among all sessions/models in this simple example)
conversation_history = ""

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history

    data = request.json
    if not data:
        return jsonify({"error": "Empty request data"}), 400

    user_input = data.get("message", "").strip()
    model_name = data.get("model", DEFAULT_MODEL_NAME).strip()
    ollama_server = data.get("server_url", DEFAULT_OLLAMA_SERVER).strip()
    base64_image = data.get("image")  # This might be None

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    conversation_history += f"\nUser: {user_input}\n"

    payload = {
        "model": model_name,
        "prompt": conversation_history,
        "stream": False
    }

    if base64_image:
        payload["images"] = [base64_image]

    try:
        response = requests.post(
            f"{ollama_server}/api/generate",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

    try:
        result = response.json()
        bot_reply = result.get("response", "No response").strip()
    except ValueError:
        return jsonify({"error": "Failed to parse JSON from Ollama"}), 500

    conversation_history += f"Bot: {bot_reply}\n"
    return jsonify({"response": bot_reply})

@app.route('/restart', methods=['POST'])
def restart():
    restart_script()
    return jsonify({"status": "restarting"}), 200

def restart_script():
    os.execv(sys.executable, [sys.executable] + sys.argv)

keyboard.add_hotkey('ctrl+r', restart_script)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
