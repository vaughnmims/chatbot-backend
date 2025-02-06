from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Your Assistant ID
ASSISTANT_ID = "asst_0pDoVhgyEs3gNDvKgr0QzoAI"

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from request
        user_input = request.json.get("user_input", "")

        # Create a thread (if needed) - You may want to persist thread IDs for conversations
        thread = openai.beta.threads.create()
        thread_id = thread.id

        # Send user input as a message to the assistant
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Run the assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for completion (polling method)
        while run.status not in ["completed", "failed"]:
            run = openai.beta.threads.runs.retrieve(run.id)

        # Get the assistant's response
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        assistant_reply = messages.data[0].content[0].text.value  # Extract text from response

        # Return assistant's response as JSON
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
