from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get the user input from the POST request
        user_input = request.json.get("user_input", "")

        # Define the chat messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]

        # Send the request to OpenAI's Chat API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Extract the assistant's reply
        assistant_reply = response["choices"][0]["message"]["content"]

        # Return the response as JSON
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
