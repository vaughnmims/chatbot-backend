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

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
client = OpenAI(api_key=OPENAI_API_KEY)
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

# Upload folder config
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
elif not os.path.isdir(UPLOAD_FOLDER):
    raise RuntimeError(f"'{UPLOAD_FOLDER}' exists but is not a directory.")

# Render index.html (optional route for browser interface)
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Main chat route
@app.route("/", methods=["POST"])
def chat():
    try:
        if request.is_json:
            data = request.get_json()
            user_input = data.get("user_input", "").strip()
            thread_id = data.get("thread_id")
            uploaded_file = None
        else:
            user_input = request.form.get("user_input", "").strip()
            thread_id = request.form.get("thread_id")
            uploaded_file = request.files.get("file")

        if not user_input:
            return jsonify({"error": "user_input cannot be empty"}), 400

        # Save file if provided
        file_path = None
        if uploaded_file and uploaded_file.filename:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(file_path)

        # Create thread if not provided
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id

        # Post message
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

        # Poll for assistant reply
        for _ in range(20):
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run.status in ["completed", "failed"]:
                break

        if run.status != "completed":
            return jsonify({"error": "Assistant run did not complete in time."}), 504

        # Get messages and response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_msgs = [m for m in messages.data if m.role == "assistant"]

        if not assistant_msgs:
            return jsonify({"error": "No assistant response found."}), 500

        reply = assistant_msgs[-1].content[0].text.value

        # Send email (optional)
        send_email_to_vaughn(user_input, reply, file_path)

        return jsonify({"response": reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_email_to_vaughn(user_msg, assistant_reply, attachment_path=None):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    RECEIVER = "Vaughn@insurems.com"

    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials not set, skipping email.")
        return

    msg = EmailMessage()
    msg["Subject"] = "New Chat Submission"
    msg["From"] = EMAIL_USER
    msg["To"] = RECEIVER
    msg.set_content(f"User message:\n{user_msg}\n\nAssistant reply:\n{assistant_reply}")

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
        except Exception as e:
            print(f"Failed to attach file: {e}")

    try:
        with smtplib.SMTP_SSL("smtp.office365.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
