import os
import sys
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

# Validate API keys before running
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    logger.error("Error: TELEGRAM_BOT_TOKEN or GEMINI_API_KEY missing in environment variables.")
    sys.exit(1)

# Initialize Gemini Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {e}")
    sys.exit(1)

# System instruction for PsyBot
SYSTEM_INSTRUCTION = (
    "You are PsyBot, a warm, empathetic, and supportive psychology assistant. "
    "Listen carefully, provide structured and thoughtful advice, and maintain a comforting tone. "
    "If a user expresses severe crisis or self-harm, gently advise them to connect with real-world professional help."
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = (
        "Namaste! 🙏 I am PsyBot, your psychology assistant.\n\n"
        "Feel free to share what's on your mind, ask questions about psychology, "
        "or talk through anything causing you stress."
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from Telegram and generate Gemini response."""
    user_text = update.message.text
    if not user_text:
        return

    # Show typing status in Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        reply_text = response.text or "I could not generate a response. Please try again."
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        reply_text = "Sorry, I ran into an issue connecting to AI services. Please try again in a moment."

    await update.message.reply_text(reply_text)

def main():
    """Start the Telegram bot."""
    logger.info("Starting PsyBot on Telegram...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run polling
    application.run_polling()

if __name__ == "__main__":
    main()
