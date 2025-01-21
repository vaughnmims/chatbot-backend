import openai
import os  # To access environment variables
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Get the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the conversation history
@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Retrieve user input from the POST request (you can customize this based on your use case)
        user_input = request.json.get("user_input", "")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
        
        # Make the API request using the correct endpoint for newer versions
        response = openai.chat_completions.create(  # Use chat_completions.create for chat models
            model="gpt-3.5-turbo",  # Specify the model
            messages=messages  # Pass the conversation history in the messages field
        )

        # Return the assistant's reply
        return jsonify({"response": response['choices'][0]['message']['content']})

    except Exception as e:  # General exception handling for all possible errors
        return jsonify({"error": str(e)})

# Define the port (render uses port 10000 by default)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
