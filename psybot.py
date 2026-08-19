import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from a local .env file (for local development)
load_dotenv()

# Retrieve API key securely from the environment
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not found.", file=sys.stderr)
    print("Please set it in your environment or in a .env file.", file=sys.stderr)
    sys.exit(1)

# Configure the Gemini API client
genai.configure(api_key=API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

def chat_with_psybot(user_prompt: str) -> str:
    """Send a prompt to the model and return the generated response."""
    try:
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    print("PsyBot is running. Type 'quit' or 'exit' to stop.\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                print("Exiting PsyBot. Goodbye!")
                break
            if not user_input:
                continue

            bot_response = chat_with_psybot(user_input)
            print(f"\nPsyBot: {bot_response}\n")
        except KeyboardInterrupt:
            print("\nSession ended.")
            break
