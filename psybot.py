import os
import sys
import logging

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

logger.info("Initializing bot script...")

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
    from google import genai
    from google.genai import types
except ImportError as e:
    logger.error(f"Missing required package during import: {e}. Check your requirements.txt!")
    sys.exit(1)

# Fetch environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

# Detailed validation check
if not TELEGRAM_BOT_TOKEN:
    logger.error("FATAL ERROR: TELEGRAM_BOT_TOKEN is missing in environment variables.")
if not GEMINI_API_KEY:
    logger.error("FATAL ERROR: GEMINI_API_KEY is missing in environment variables.")

if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    sys.exit(1)

# Initialize Gemini Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Gemini client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {e}")
    sys.exit(1)

SYSTEM_INSTRUCTION = (
    "You are PsyBot, an empathetic, supportive, and knowledgeable psychology assistant. "
    "Provide clear, grounded, and concise insights without unnecessary filler. "
    "If a user expresses acute distress or self-harm, immediately and gently encourage professional help."
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Namaste! 🙏 I am PsyBot, your psychology assistant.\n\n"
        "How can I help you today?"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=350,
            ),
        )
        reply_text = response.text or "I could not generate a response. Please try again."
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        reply_text = "⚠️ Temporary connection issue with AI services. Please send your message again."

    await update.message.reply_text(reply_text)

def main():
    try:
        logger.info("Starting optimized PsyBot on Telegram...")
        application = (
            ApplicationBuilder()
            .token(TELEGRAM_BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("Bot polling started successfully.")
        application.run_polling()
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
