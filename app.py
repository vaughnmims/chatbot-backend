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
    Route for handling prompt and generating text using OpenAI's API.
    """
    try:
        # Get data from the POST request
        data = request.get_json()  # expects JSON input
        prompt = data.get("prompt", "")  # Expects 'prompt' key
        
        # Ensure that the prompt is provided
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Call OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Can change the engine if needed
            prompt=prompt,
            max_tokens=100
        )

        # Return the OpenAI response
        return jsonify({"response": response.choices[0].text.strip()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure the app runs on the correct host and port
    app.run(host="0.0.0.0", port=5000)
