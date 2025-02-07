from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import openai  # Import OpenAI client correctly

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Your Assistant ID
ASSISTANT_ID = "asst_0pDoVhgyEs3gNDvKgr0QzoAI"

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from request
        user_input = request.json.get("user_input", "")

        # Create a new thread
        thread = openai.Thread.create()  # Using correct method for creating a thread
        thread_id = thread.id

        # Send user message to the assistant (use the correct API endpoint)
        openai.ThreadMessage.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Run the assistant (correcting the method name to match OpenAI's API)
        run = openai.ThreadRun.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Polling: Wait until the assistant completes processing
        while run["status"] not in ["completed", "failed"]:
            run = openai.ThreadRun.retrieve(thread_id=thread_id, run_id=run["id"])

        # Retrieve assistant's response
        messages = openai.ThreadMessage.list(thread_id=thread_id)
        assistant_reply = messages["data"][0]["content"]  # Extract assistant's response text

        # Return assistant's response as JSON
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
