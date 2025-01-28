from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Use environment variable for OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from the request
        user_input = request.json.get("user_input", "")
        
        # Define conversation messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
        
        # Request the response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model
            messages=messages
        )
        
        # Extract the assistant's reply
        assistant_reply = response['choices'][0]['message']['content']
        
        # Return the assistant's response
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
