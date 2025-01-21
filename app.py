from flask import Flask, request, jsonify
import openai
import os

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route('/', methods=['POST'])
def api_endpoint():
    """
    Route for handling prompt and generating text using OpenAI's new API.
    """
    try:
        # Get data from the POST request
        data = request.get_json()  # expects JSON input
        prompt = data.get("prompt", "")  # Expects 'prompt' key
        
        # Ensure that the prompt is provided
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Call OpenAI API with the new method
        response = openai.chat_completions.create(
            model="gpt-3.5-turbo",  # Using the GPT-3.5 model, change to a newer model if needed
            messages=[{"role": "user", "content": prompt}],
        )

        # Return the OpenAI response
        return jsonify({"response": response['choices'][0]['message']['content']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure the app runs on the correct host and port
    app.run(host="0.0.0.0", port=5000)

