import os
import csv
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# 1. फ़ोल्डर का सटीक पाथ और .env लोड करना
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
# 1. फ़ोल्डर का सटीक पाथ और .env लोड करना
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# .env से कीज़ लें, न मिलने पर डायरेक्ट वैल्यू का उपयोग करें
TELEGRAM_BOT_TOKEN = os.getenv("PSYCHO_BOT_TOKEN") or "8855280565:AAFDOiy0a2mxEvxJgD5xFyQhv80lP3IvMCw"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AQ.Ab8RN6LTPhjMgRgxVqIaf6UrGebh84LMFFFkPusOgc7HR2TTgw"

# आपकी एडमिन टेलीग्राम आईडी
ADMIN_USER_ID = 601053093

if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Credentials missing.")
# 2. जेमिनी क्लाइंट
client = genai.Client(api_key=GEMINI_API_KEY)

# 3. नैतिक मनोवैज्ञानिक सिस्टम प्रॉम्प्ट
SYSTEM_PROMPT = """
आप एक अत्यंत संवेदनशील, विचारशील, सहानुभूतिपूर्ण और नैतिक मनोवैज्ञानिक सहायक (Psychological Self-Reflection & Guidance Companion) हैं।

दिशा-निर्देश:
1. Active Listening: यूज़र की भावनाओं को बिना किसी पूर्वग्रह के समझें और स्वीकार करें।
2. Cognitive Framing: यूज़र को विचारों के पैटर्न को समझने और पॉजिटिव दृष्टिकोण अपनाने में मदद करें।
3. Limits: आप AI साथी हैं, कोई डॉक्टर नहीं। कोई मेडिकल डायग्नोसिस या दवाई न लिखें।
4. Crisis Helpline: यदि यूज़र गंभीर तनाव या आत्म-हानि का संकेत दे, तो तुरंत किरण हेल्पलाइन (1800-599-0019) या Tele-MANAS (14416) साझा करें।
5. संरचित उत्तर: उत्तर के अंत में अनिवार्य रूप से '---INSIGHT---' लिखकर 1-2 शब्दों में मुख्य पहलू (जैसे: Workplace Stress, Anxiety, Imposter Syndrome) लिखें।
"""

def get_user_csv(user_id):
    path = os.path.join(BASE_DIR, f"journal_{user_id}.csv")
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "User_Input", "Psychological_Insight", "Bot_Response"])
    return path

# /start कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"नमस्ते {user_name}! 🌸\n\n"
        "मैं आपका व्यक्तिगत मनोवैज्ञानिक आत्म-चिंतन सहायक हूँ। आप बिना किसी संकोच के अपने मन के विचार, तनाव या अनुभव यहाँ साझा कर सकते हैं।\n\n"
        "📌 *कमांड्स:*\n"
        "• अपनी पूरी रिपोर्ट देखने के लिए: `/report`\n\n"
        "⚠️ *नोट:* यह बॉट आत्म-चिंतन और भावनात्मक अभिव्यक्ति के लिए है, किसी मेडिकल डायग्नोसिस का विकल्प नहीं है।",
        parse_mode="Markdown"
    )

# यूज़र की खुद की रिपोर्ट (/report)
async def send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_csv = get_user_csv(user_id)

    records = []
    with open(user_csv, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 4:
                records.append(row)

    if not records:
        await update.message.reply_text("ℹ️ अभी तक आपका कोई रिकॉर्ड दर्ज नहीं हुआ है।")
        return

    report_text = f"📋 *आपकी व्यक्तिगत जर्नल रिपोर्ट*\n"
    report_text += f"📊 *कुल सत्र:* {len(records)}\n\n"
    report_text += "━━━━━━━━━━━━━━━━━━━━\n"

    for row in records[-5:]:
        t_stamp, u_text, insight, _ = row[0], row[1], row[2], row[3]
        report_text += f"🗓 *समय:* `{t_stamp}`\n"
        report_text += f"💭 *आपके विचार:* {u_text[:70]}...\n"
        report_text += f"🧠 *विश्लेषण:* {insight}\n\n"

    if len(records) > 5:
        report_text += f"_(पिछले 5 रिकॉर्ड दिखाए गए हैं, पूरी फ़ाइल नीचे संलग्न है)_\n"

    await update.message.reply_text(report_text, parse_mode="Markdown")
    with open(user_csv, "rb") as f:
        await update.message.reply_document(document=f, filename="my_psychological_report.csv")

# केवल आपके लिए: सभी यूज़र्स की रिपोर्ट्स (/allreports)
async def admin_all_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⚠️ यह कमांड केवल बॉट एडमिन के लिए है।")
        return

    csv_files = [f for f in os.listdir(BASE_DIR) if f.startswith("journal_") and f.endswith(".csv")]
    if not csv_files:
        await update.message.reply_text("कोई भी यूज़र डेटा उपलब्ध नहीं है।")
        return

    await update.message.reply_text(f"📊 कुल {len(csv_files)} यूज़र्स का डेटा मिला। फ़ाइलें भेजी जा रही हैं...")
    for file_name in csv_files:
        file_path = os.path.join(BASE_DIR, file_name)
        with open(file_path, "rb") as f:
            await update.message.reply_document(document=f, filename=file_name)

# मैसेज हैंडलर
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    user_csv = get_user_csv(user_id)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"उपयोगकर्ता का संदेश: '{user_text}'\n\n"
        "कृपया दो भागों में उत्तर दें:\n"
        "1. मुख्य उत्तर (सहानुभूतिपूर्ण, मनोवैज्ञानिक रूप से सटीक)\n"
        "2. अंत में '---INSIGHT---' लिखकर 1-2 शब्दों में मुख्य मनोवैज्ञानिक पहलू लिखें।"
    )

    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            if response and response.text:
                break
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                await asyncio.sleep(2)
                continue
            else:
                await update.message.reply_text("सर्वर व्यस्त है। कृपया कुछ पलों बाद पुनः प्रयास करें।")
                return

    full_reply = response.text.strip()

    if "---INSIGHT---" in full_reply:
        reply_part, insight_part = full_reply.split("---INSIGHT---", 1)
        clean_reply = reply_part.strip()
        clean_insight = insight_part.strip()
    else:
        clean_reply = full_reply
        clean_insight = "General Reflection"

    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CSV में डेटा सुरक्षित करना
    with open(user_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp_now, user_text, clean_insight, clean_reply])
        f.flush()
        os.fsync(f.fileno())

    await update.message.reply_text(clean_reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", send_report))
    app.add_handler(CommandHandler("allreports", admin_all_reports))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("PsyBot is running successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()