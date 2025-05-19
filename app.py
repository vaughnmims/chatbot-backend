from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status == "failed":
            return jsonify({"error": "Assistant run failed"}), 500

        # Get assistant response (take last message from assistant)
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_messages = [m for m in messages.data if m.role == "assistant"]

        if not assistant_messages:
            return jsonify({"error": "No assistant response found"}), 500

        assistant_reply = assistant_messages[-1].content[0].text.value

        # Email the conversation + attachment
        send_email_to_vaughn(user_input, assistant_reply, file_path)

        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Email function
def send_email_to_vaughn(user_msg, assistant_reply, attachment_path=None):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")      # Your sending email
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")     # App password
    RECEIVER = "Vaughn@insurems.com"

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not set")
        return

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
