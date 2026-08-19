import os
import asyncio
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# API Keys from Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client Setup
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "You are PsyBot, an empathetic, supportive, and knowledgeable psychology assistant. "
    "Provide clear, grounded, and insightful responses with care and professionalism. "
    "If a user mentions severe distress or self-harm, gently urge them to seek professional help."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Hello! Main PsyBot hoon. Aapki mental health aur emotional well-being se judi baaton me help karne ke liye taiyaar hoon. Aap kaise hain aaj?"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Typing status indicator
    await update.message.chat.send_action(action="typing")

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        reply_text = response.text if response.text else "Sorry, I couldn't process that."
    except Exception as e:
        reply_text = f"Error: {str(e)}"

    await update.message.reply_text(reply_text)

def main():
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        print("Error: TELEGRAM_BOT_TOKEN or GEMINI_API_KEY missing in environment variables.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("PsyBot Telegram Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
