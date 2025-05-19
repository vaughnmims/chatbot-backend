from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ASSISTANT_ID = "asst_evvcHxQQTnCCFqnDOxcsPjJL"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["POST"])
def chat():
    try:
        user_input = request.form.get("user_input", "")
        thread_id = request.form.get("thread_id")
        uploaded_file = request.files.get("file")

        # Save file if uploaded
        file_path = None
        if uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)

        # Create thread if needed
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

        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Get reply
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_reply = messages.data[0].content[0].text.value

        # Email details to Vaughn
        send_email_to_vaughn(user_input, assistant_reply, file_path)

        return jsonify({"response": assistant_reply, "thread_id": thread_id})

    except Exception as e:
        return jsonify({"error": str(e)})

def send_email_to_vaughn(user_msg, assistant_reply, attachment_path=None):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")      # e.g., noreply@yourdomain.com
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")     # App password or SMTP key
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

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
