import openai
import os
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['POST'])
def api_endpoint():
    """
    Default route for simple text processing.
    """
    try:
        # Get data from the POST request
        data = request.get_json()  # expects JSON input
        input_text = data.get("input", "")  # Expects 'input' key
        
        # Ensure that input is provided
        if not input_text:
            return jsonify({"error": "Input text is required"}), 400

        # Logic to process the input text (can be customized further)
        response_text = f"You asked: {input_text}"

        return jsonify({"response": response_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate", methods=["POST"])
def generate_text():
    """
    Route for generating text using OpenAI's chat-based API.
    """
    try:
        # Get data from the request
        data = request.get_json()  # expects JSON input
        prompt = data.get("prompt", "")  # Expects 'prompt' key
        
        # Ensure that the prompt is provided
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Call OpenAI API (using the new Chat API)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Can change to gpt-4 if needed
            messages=[{"role": "user", "content": prompt}],
        )

        # Return the OpenAI response
        return jsonify({"response": response.choices[0].message['content']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure the app runs on the correct host and port
    app.run(host="0.0.0.0", port=5000)
