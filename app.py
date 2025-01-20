from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = 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

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}]
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

