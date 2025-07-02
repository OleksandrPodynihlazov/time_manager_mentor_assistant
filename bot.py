import os
import datetime
import tempfile
from telegram import Update, Voice
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from transcriber import transcribe_voice
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

BOT_TOKEN = os.getenv("TELEGRAM_API")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receives a voice message, transcribes it to text,
    writes it to a log file, and sends the text back."""
    
    voice: Voice = update.message.voice
    ogg_file = await voice.get_file()

    temp_ogg_path = None
    temp_wav_path = None
    try:
        # Create a temporary file for the .ogg
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as ogg_f:
            temp_ogg_path = ogg_f.name
        
        # Create a path for the future .wav file
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as wav_f:
            temp_wav_path = wav_f.name

        await ogg_file.download_to_drive(temp_ogg_path)

        text = transcribe_voice(temp_ogg_path, temp_wav_path)
        
        today = datetime.date.today().isoformat()
        log_path = os.path.join(LOG_DIR, f"{today}.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{update.message.date}] {text.strip()}\n")

        await update.message.reply_text(f"Transcribed:\n\n{text.strip()}")

    finally:
        # Reliably delete temporary files after use
        if temp_ogg_path and os.path.exists(temp_ogg_path):
            os.remove(temp_ogg_path)
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Error: TELEGRAM_API token not found. Check your .env file and the variable name.")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))
        print("Bot started.")
        app.run_polling()
