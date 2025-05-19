from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve the chat frontend
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Handle chat messages sent as JSON
@app.route("/", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("user_input", "")
        thread_id = data.get("thread_id")

        if not user_input:
            return jsonify({"error": "No user input provided"}), 400

        # Create thread if none exists
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Send user message
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

        # Poll until completion
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Get assistant reply
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_reply = messages.data[0].content[0].text.value

        # Email conversation (no attachment here)
        send_email_to_vaughn(user_input, assistant_reply)

        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle file uploads separately
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        uploaded_file = request.files.get("file")
        thread_id = request.form.get("thread_id")

        if not uploaded_file:
            return jsonify({"error": "No file uploaded"}), 400

        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(file_path)

        # Create thread if none exists
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Notify assistant about file upload
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"File uploaded: {uploaded_file.filename}"
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Poll until completion
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Get assistant reply
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_reply = messages.data[0].content[0].text.value

        # Email chat + attachment
        send_email_to_vaughn(f"File uploaded: {uploaded_file.filename}", assistant_reply, file_path)

        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Email function
def send_email_to_vaughn(user_msg, assistant_reply, attachment_path=None):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")      # Your email (e.g., noreply@yourdomain.com)
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")     # App password or actual password
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

with smtplib.SMTP("smtp.office365.com", 587) as smtp:
    smtp.starttls()  # Use TLS for encryption
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
