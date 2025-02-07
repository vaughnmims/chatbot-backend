from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import openai  # Import OpenAI client correctly

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Your Assistant ID (if needed for some specific purposes)
ASSISTANT_ID = "asst_0pDoVhgyEs3gNDvKgr0QzoAI"

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from request
        user_input = request.json.get("user_input", "")

        # Send user message to the assistant (use ChatCompletion for conversational threads)
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Specify GPT-4 model here
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},  # Optional system message to set context
                {"role": "user", "content": user_input}  # User's message
            ]
        )

        # Extract assistant's reply
        assistant_reply = response['choices'][0]['message']['content']

        # Return assistant's response as JSON
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
