import openai
import os  # To access environment variables

# Get the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the conversation history
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who are you?"}
]

# Make the API request using the correct endpoint for newer versions
try:
    response = openai.completions.create(  # Use completions.create for newer OpenAI API
        model="gpt-3.5-turbo",  # Use the correct model; can also be "gpt-4" if you have access
        messages=messages  # Pass the conversation history in the messages field
    )

    # Print the assistant's reply
    print("Assistant's reply:", response['choices'][0]['message']['content'])

except Exception as e:  # General exception handling for all possible errors
    print(f"An error occurred: {str(e)}")
