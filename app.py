from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import openai

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Store active conversation context in memory (for development, can be stored in DB for production)
active_conversations = {}

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from request
        user_input = request.json.get("user_input", "")
        thread_id = str(request.json.get("thread_id", ""))  # Ensure thread_id is treated as a string

        if not user_input:
            return jsonify({"error": "No user input provided"}), 400

        # If thread_id doesn't exist, create a new conversation history
        if not thread_id:
            thread_id = str(len(active_conversations) + 1)  # Unique thread ID for this conversation
            active_conversations[thread_id] = []  # Initialize message history for the new thread

        # Add user message to the thread history
        active_conversations[thread_id].append({"role": "user", "content": user_input})

        # Send the conversation history (messages) to OpenAI API
        response = openai.chat.completions.create(  # Update: Using `chat.completions.create` for new SDK
            model="gpt-3.5-turbo",  # You can use gpt-4 as needed
            messages=active_conversations[thread_id]  # This sends the conversation history
        )

        # Get assistant's response
        assistant_reply = response['choices'][0]['message']['content']

        # Add assistant's response to the thread history
        active_conversations[thread_id].append({"role": "assistant", "content": assistant_reply})

        # Return assistant's response as JSON along with thread_id for future use
        return jsonify({
            "response": assistant_reply,
            "thread_id": thread_id
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
