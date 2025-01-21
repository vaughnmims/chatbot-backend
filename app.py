from flask import Flask, request, jsonify
import openai
import os

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['POST'])
def api_endpoint():
    try:
        # Get data from the POST request
        data = request.get_json()  # expects JSON input
        input_text = data.get("input", "")
        
        # Ensure that input is provided
        if not input_text:
            return jsonify({"error": "Input text is required"}), 400

        # Logic to process the input text (can be customized further)
        response_text = f"You asked: {input_text}"

        return jsonify({"response": response_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["POST"])
def generate_text():
    try:
        # Get data from the request
        data = request.json
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Call OpenAI API (using your preferred model/engine)
        response = openai.Completion.create(
            engine="text-davinci-003",  # Can change engine if needed
            prompt=prompt,
            max_tokens=100
        )

        # Return the OpenAI response
        return jsonify({"response": response.choices[0].text.strip()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
