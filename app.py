from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# GPT-4 Turbo Token Limit (adjust if needed)
MAX_TOKENS = 4096  

def trim_messages(messages, max_tokens=MAX_TOKENS):
    """Ensure messages stay within the token limit."""
    total_tokens = sum(len(msg['content'].split()) for msg in messages)
    while total_tokens > max_tokens:
        messages.pop(1)  # Remove the oldest user message
        total_tokens = sum(len(msg['content'].split()) for msg in messages)
    return messages

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from request
        user_input = request.json.get("user_input", "")

        # Define conversation history
        messages = [
            {"role": "system", "content": "You are a helpful and knowledgeable assistant."},
            {"role": "user", "content": user_input}
        ]

        # Trim messages to fit within token limits
        messages = trim_messages(messages)

        # Request response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # Updated to GPT-4 Turbo
            messages=messages
        )

        # Extract assistant's response
        assistant_reply = response['choices'][0]['message']['content']

        # Return assistant's response as JSON
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
