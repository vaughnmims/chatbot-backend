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
    Handle both simple text processing and OpenAI text generation.
    """
    try:
        # Get data from the POST request
        data = request.get_json()  # expects JSON input
        
        # Check if 'input' key is provided for simple text processing
        input_text = data.get("input", "")
        
        # If 'input' is found, process it (simple text processing)
        if input_text:
            response_text = f"You asked: {input_text}"
            return jsonify({"response": response_text}), 200
        
        # Check if 'prompt' key is provided for OpenAI text generation
        prompt = data.get("prompt", "")
        
        if prompt:
            # Call OpenAI API (updated for new API)
            response = openai.Completion.create(
                model="gpt-3.5-turbo",  # Can change to gpt-4 if needed
                prompt=prompt,  # Adjusted for simple text generation
                max_tokens=100
            )

            # Return the OpenAI response
            return jsonify({"response": response['choices'][0]['text'].strip()}), 200
        
        # If neither 'input' nor 'prompt' is provided, return an error
        return jsonify({"error": "Input text or prompt is required"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure the app runs on the correct host and port
    app.run(host="0.0.0.0", port=5000)
