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

# Pre-execution validation
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    logger.error("Error: TELEGRAM_BOT_TOKEN or GEMINI_API_KEY missing in environment variables.")
    sys.exit(1)

# Initialize Gemini Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {e}")
    sys.exit(1)

# Compact, direct system instruction for faster token processing
SYSTEM_INSTRUCTION = (
    "You are PsyBot, an empathetic, supportive, and knowledgeable psychology assistant. "
    "Provide clear, grounded, and concise insights without unnecessary filler. "
    "If a user expresses acute distress or self-harm, immediately and gently encourage professional help."
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = (
        "Namaste! 🙏 I am PsyBot, your psychology assistant.\n\n"
        "How can I help you today?"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asynchronously handle incoming messages for maximum speed."""
    user_text = update.message.text
    if not user_text:
        return

    # Trigger Telegram typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Non-blocking async API call
        response = await client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=350,  # Limits token generation time
            ),
        )
        reply_text = response.text or "I could not generate a response. Please try again."
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        reply_text = "⚠️ Temporary connection issue with AI services. Please send your message again."

    await update.message.reply_text(reply_text)

def main():
    """Start polling."""
    logger.info("Starting optimized PsyBot on Telegram...")
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .concurrent_updates(True)  # Process multiple users simultaneously
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
