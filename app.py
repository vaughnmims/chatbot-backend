from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

@app.route("/", methods=["POST"])
def chat():
    try:
        # Support both JSON and multipart
        if request.content_type.startswith('multipart/form-data'):
            user_input = request.form.get("user_input", "")
            uploaded_file = request.files.get("file")
        else:
            user_input = request.json.get("user_input", "")
            uploaded_file = None

        thread_id = request.form.get("thread_id") or request.json.get("thread_id")

        # Create new thread if not provided
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Upload file if it exists
        if uploaded_file:
            file_response = client.files.create(
                file=uploaded_file,
                purpose="assistants"
            )
            file_id = file_response.id

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input,
                file_ids=[file_id]
            )
        else:
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Poll until complete
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Retrieve response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_reply = messages.data[0].content[0].text.value

        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
