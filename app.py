import openai
import os  # Import the os module to access environment variables

# Get the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the conversation history as an array of messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who are you?"}
]

# Make the API request to the correct endpoint for chat completions
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the correct model; can also be "gpt-4" if you have access
        messages=messages  # Pass the conversation history in the messages field
    )

    # Print the assistant's reply
    print("Assistant's reply:", response['choices'][0]['message']['content'])

except openai.error.OpenAIError as e:
    # Handle any errors that may occur
    print(f"An error occurred: {e}")
