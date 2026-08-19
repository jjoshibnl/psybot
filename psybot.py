import os
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# Initialize the Gemini API client
# Ensure GEMINI_API_KEY is set in Render's Environment Variables
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# System prompt for PsyBot's personality and role
SYSTEM_INSTRUCTION = (
    "You are PsyBot, an empathetic, supportive, and knowledgeable psychology assistant. "
    "Provide clear, grounded, and insightful responses with care and professionalism. "
    "If a user mentions severe distress or self-harm, gently urge them to seek professional help."
)

# Simple HTML Chat Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PsyBot</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 15px; }
        .chat-card { width: 100%; max-width: 600px; height: 80vh; background: #ffffff; border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); display: flex; flex-direction: column; overflow: hidden; }
        .chat-header { background: #4f46e5; color: white; padding: 18px 24px; font-weight: 600; font-size: 1.2rem; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 80%; padding: 12px 16px; border-radius: 14px; font-size: 0.95rem; line-height: 1.5; word-wrap: break-word; }
        .msg.bot { background: #f3f4f6; color: #1f2937; align-self: flex-start; border-bottom-left-radius: 4px; }
        .msg.user { background: #4f46e5; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        .chat-input-area { display: flex; padding: 16px; border-top: 1px solid #e5e7eb; gap: 10px; background: #fafafa; }
        input[type="text"] { flex: 1; padding: 12px 16px; border: 1px solid #d1d5db; border-radius: 8px; outline: none; font-size: 0.95rem; }
        input[type="text"]:focus { border-color: #4f46e5; }
        button { background: #4f46e5; color: white; border: none; padding: 0 20px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 0.95rem; }
        button:hover { background: #4338ca; }
    </style>
</head>
<body>
    <div class="chat-card">
        <div class="chat-header">PsyBot AI</div>
        <div class="chat-box" id="chatBox">
            <div class="msg bot">Hello! I am PsyBot. How can I support you today?</div>
        </div>
        <form class="chat-input-area" id="chatForm">
            <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off" required />
            <button type="submit">Send</button>
        </form>
    </div>

    <script>
        const chatForm = document.getElementById('chatForm');
        const userInput = document.getElementById('userInput');
        const chatBox = document.getElementById('chatBox');

        function appendMessage(text, sender) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `msg ${sender}`;
            msgDiv.innerText = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = userInput.value.trim();
            if (!message) return;

            appendMessage(message, 'user');
            userInput.value = '';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await res.json();
                if (data.reply) {
                    appendMessage(data.reply, 'bot');
                } else {
                    appendMessage('Error: ' + (data.error || 'Unable to get response'), 'bot');
                }
            } catch (err) {
                appendMessage('Server connection error.', 'bot');
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    """Renders the web chat UI."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    """API endpoint to interact with Gemini."""
    if not client:
        return jsonify({"error": "GEMINI_API_KEY environment variable is not configured."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
