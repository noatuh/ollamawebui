from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import pyttsx3 # Note: pyttsx3 and keyboard are not used in the core web flow, consider removing if not needed elsewhere
import os
import sys
import keyboard # Note: keyboard hotkey works only if the *server process* has focus, not the browser.

app = Flask(__name__)

# --- Configuration ---
DEFAULT_OLLAMA_SERVER = "http://192.168.1.50:11434"
DEFAULT_MODEL_NAME = "llama3:latest"
MEMORY_FILE = "memories.txt" # File to store persistent memories

# --- Initialize TTS (Optional - Not used in chat flow) ---
try:
    engine = pyttsx3.init()
    selected_voice_index = 0
    voices = engine.getProperty('voices')
    if voices and len(voices) > selected_voice_index:
        engine.setProperty('voice', voices[selected_voice_index].id)
    else:
        print("Warning: Could not set TTS voice.")
except Exception as e:
    print(f"Warning: Failed to initialize pyttsx3 engine: {e}")
    engine = None

# --- Global State ---
# Note: Global history is shared and grows indefinitely. Consider session management for production.
conversation_history = ""

# --- Memory Functions ---
def load_memories():
    """Loads persistent memories from the memory file."""
    if not os.path.exists(MEMORY_FILE):
        return ""
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        print(f"Error reading memory file {MEMORY_FILE}: {e}")
        return ""

def save_memory(user_message, bot_response):
    """Appends a user message and bot response to the memory file."""
    try:
        with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"User: {user_message}\n")
            f.write(f"Bot: {bot_response}\n\n") # Add extra newline for readability
    except IOError as e:
        print(f"Error writing to memory file {MEMORY_FILE}: {e}")

# --- Flask Routes ---
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    # Check if memory file exists, create if not
    if not os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                f.write("# Persistent Memories for Ollama GUI\n\n")
            print(f"Created memory file: {MEMORY_FILE}")
        except IOError as e:
             print(f"Error creating memory file {MEMORY_FILE}: {e}")
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
    base64_image = data.get("image")  # Optional image
    remember_this = data.get("remember", False) # Flag to save to memory

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    # --- Construct the prompt ---
    persistent_memories = load_memories()
    current_user_prompt = f"\nUser: {user_input}\n"

    # Combine persistent memories, current session history, and the new user message
    # Note: conversation_history still grows globally in this simple example.
    full_prompt = persistent_memories + conversation_history + current_user_prompt

    payload = {
        "model": model_name,
        "prompt": full_prompt, # Send combined context
        "stream": False
    }

    if base64_image:
        payload["images"] = [base64_image]

    # --- Call Ollama API ---
    try:
        response = requests.post(
            f"{ollama_server}/api/generate",
            json=payload,
            timeout=300 # Increased timeout for potentially longer context
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
         return jsonify({"error": f"API timeout connecting to {ollama_server}"}), 500
    except requests.exceptions.ConnectionError:
         return jsonify({"error": f"API connection error to {ollama_server}"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

    # --- Process Response ---
    try:
        result = response.json()
        bot_reply = result.get("response", "No response").strip()
    except ValueError: # Catch JSON decoding errors
        return jsonify({"error": "Failed to parse JSON from Ollama"}), 500

    # --- Update History and Memory ---
    bot_response_line = f"Bot: {bot_reply}\n"
    conversation_history += current_user_prompt + bot_response_line # Update session history

    if remember_this:
        save_memory(user_input, bot_reply) # Save this interaction to persistent memory

    return jsonify({"response": bot_reply})

@app.route('/restart', methods=['POST'])
def restart():
    # Note: This restart function might not work reliably on all OS/environments,
    # especially if run via a service manager. Ctrl+R hotkey is also server-side.
    restart_script()
    return jsonify({"status": "restarting"}), 200

def restart_script():
    print("Attempting to restart server...")
    # Flush stdout to ensure message is seen before execv replaces the process
    sys.stdout.flush()
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"Error during restart: {e}")
        # Optional: exit if execv fails, otherwise the old process might continue
        sys.exit(1)

# Optional: Keyboard hotkey (runs on server, needs focus)
try:
    keyboard.add_hotkey('ctrl+r', restart_script)
    print("Ctrl+R hotkey registered for server restart (requires server console focus).")
except Exception as e:
    print(f"Warning: Could not register keyboard hotkey: {e}")


if __name__ == '__main__':
    # Ensure memory file exists on startup
    if not os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                f.write("# Persistent Memories for Ollama GUI\n\n")
            print(f"Created memory file: {MEMORY_FILE}")
        except IOError as e:
             print(f"Error creating memory file {MEMORY_FILE}: {e}")

    # Use threaded=False if using keyboard module, or remove keyboard logic
    # Use debug=False for production
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) # Use threaded=True for better performance