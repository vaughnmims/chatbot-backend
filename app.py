from flask import Flask, request, jsonify
import openai
import os
import requests
import xml.etree.ElementTree as ET  # For parsing XML (RSS feed)
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Fetch blog posts from RSS feed
def fetch_blog_posts():
    url = "https://www.mimsstrategicmanagementsolutions.com/blog-feed.xml"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the XML content of the RSS feed
        root = ET.fromstring(response.text)
        items = root.findall(".//item")
        
        # Extract the titles and links of the blog posts
        posts = [{"title": item.find("title").text, "link": item.find("link").text} for item in items]
        return posts
    else:
        return []

# Fetch relevant blog content (first 5 posts as an example)
def get_relevant_blog_content():
    blog_posts = fetch_blog_posts()
    if blog_posts:
        return "\n".join([f"{post['title']}: {post['link']}" for post in blog_posts[:5]])  # Titles with links
    else:
        return "No blog content available."

MAX_TOKENS = 4096  # GPT-4 token limit for input+output

def trim_messages(messages, max_tokens=MAX_TOKENS):
    total_tokens = sum(len(msg['content'].split()) for msg in messages)
    while total_tokens > max_tokens:
        messages.pop(1)  # Remove the oldest user message
        total_tokens = sum(len(msg['content'].split()) for msg in messages)
    return messages

@app.route("/", methods=["POST"])
def chat():
    try:
        # Get user input from the request
        user_input = request.json.get("user_input", "")
        
        # Get relevant blog content
        relevant_blog_content = get_relevant_blog_content()

        # Define conversation messages, including dynamic blog content
        messages = [
            {"role": "system", "content": f"You are a helpful assistant. Here is some helpful blog content: {relevant_blog_content}"}
        ]
        
        # Append the user input to the messages
        messages.append({"role": "user", "content": user_input})
        
        # Trim messages to fit within token limits
        messages = trim_messages(messages)
        
        # Request the response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the correct model here
            messages=messages
        )
        
        # Extract and append assistant's response
        assistant_reply = response['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": assistant_reply})
        
        # Return the assistant's response
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
