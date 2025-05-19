from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage
import time

app = Flask(__name__)
CORS(app)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve the chat form
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Handle form submission
@app.route("/", methods=["POST"])
def chat():
    try:
        user_input = request.form.get("user_input", "")
        thread_id = request.form.get("thread_id")
        uploaded_file = request.files.get("file")

        # Save uploaded file
        file_path = None
        if uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)

        # Create thread if not provided
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Send message to assistant
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
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status == "failed":
            return jsonify({"error": "Assistant run failed"}), 500

        # Get assistant response (last message)
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if not messages.data:
            return jsonify({"error": "No messages found in thread"}), 500

        # Extract last assistant message content safely
        try:
            assistant_message = None
            for msg in reversed(messages.data):
                if msg.role == "assistant":
                    # Assuming the message content format
                    assistant_message = msg.content[0].text.value
                    break
            if assistant_message is None:
                return jsonify({"error": "No assistant response found"}), 500
        except Exception as e:
            return jsonify({"error": f"Failed to parse assistant message: {str(e)}"}), 500

        # Email the conversation + attachment
        send_email_to_vaughn(user_input, assistant_message, file_path)

        return jsonify({"response": assistant_message, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Email function
def send_email_to_vaughn(user_msg, assistant_reply, attachment_path=None):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
    RECEIVER = "Vaughn@insurems.com"

    msg = EmailMessage()
    msg["Subject"] = "New Chat Submission"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECEIVER
    msg.set_content(f"User message:\n{user_msg}\n\nAssistant replied:\n{assistant_reply}")

    if attachment_path:
        with open(attachment_path, "rb") as f:
            data = f.read()
            name = os.path.basename(attachment_path)
            msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=name)

    with smtplib.SMTP_SSL("smtp.office365.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
