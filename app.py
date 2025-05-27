from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from werkzeug.utils import secure_filename
import os
import smtplib
from email.message import EmailMessage
import time

app = Flask(__name__)
CORS(app)

# Limit upload size to 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"

# Check if uploads folder exists and is directory; otherwise handle
if os.path.exists(UPLOAD_FOLDER):
    if not os.path.isdir(UPLOAD_FOLDER):
        raise RuntimeError(f"'{UPLOAD_FOLDER}' exists but is not a directory. Please delete or rename it before running.")
else:
    os.makedirs(UPLOAD_FOLDER)

# Serve the chat form
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Handle form/JSON submission
@app.route("/", methods=["POST"])
def chat():
    try:
        if request.is_json:
            data = request.get_json()
            user_input = data.get("user_input", "")
            thread_id = data.get("thread_id")
            uploaded_file = None  # No files expected in JSON requests
        else:
            user_input = request.form.get("user_input", "")
            thread_id = request.form.get("thread_id")
            uploaded_file = request.files.get("file")

        # Validate user input
        if not user_input or user_input.strip() == "":
            return jsonify({"error": "user_input cannot be empty"}), 400

        # Save uploaded file if present
        file_path = None
        if uploaded_file:
            safe_filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
            uploaded_file.save(file_path)

        # Create thread if not provided
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Send user message to assistant thread
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

        # Poll until run is complete or failed (wait up to ~10 seconds)
        max_polls = 20
        polls = 0
        while run.status not in ["completed", "failed"]:
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            polls += 1
            if polls >= max_polls:
                return jsonify({"error": "Assistant response timeout"}), 504

        if run.status == "failed":
            return jsonify({"error": "Assistant run failed"}), 500

        # Fetch all messages for the thread
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_messages = [m for m in messages.data if m.role == "assistant"]

        if not assistant_messages:
            return jsonify({"error": "No assistant response found"}), 500

        # Take the last assistant message's text value
        assistant_reply = assistant_messages[-1].content[0].text.value

        # Email the conversation + attachment if present
        send_email_to_vaughn(user_input, assistant_reply, file_path)

        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Email sending helper
def send_email_to_vaughn(user_msg, assistant_reply, attachment_path=None):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")      # Your sending email
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")     # App password
    RECEIVER = "Vaughn@insurems.com"

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not set. Skipping email.")
        return

    msg = EmailMessage()
    msg["Subject"] = "New Chat Submission"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECEIVER
    msg.set_content(f"User message:\n{user_msg}\n\nAssistant replied:\n{assistant_reply}")

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                data = f.read()
                name = os.path.basename(attachment_path)
                msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=name)
        except Exception as e:
            print(f"Error attaching file: {e}")

    # Connect using SMTP_SSL on port 465 (Office365 sometimes uses 587 STARTTLS, adjust if needed)
    try:
        with smtplib.SMTP_SSL("smtp.office365.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
