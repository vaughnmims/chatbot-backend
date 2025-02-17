from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from openai import OpenAI  # Correctly import OpenAI client

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your Assistant ID
ASSISTANT_ID = "asst_0pDoVhgyEs3gNDvKgr0QzoAI"

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input and thread_id from request
        user_input = request.json.get("user_input", "")
        thread_id = request.json.get("thread_id")

        # If no thread_id is provided, create a new thread
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Send user message to the assistant
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Polling: Wait until the assistant completes processing
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Retrieve assistant's response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_reply = messages.data[0].content[0].text.value  # Extract text from response

        # Return assistant's response and thread_id
        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
