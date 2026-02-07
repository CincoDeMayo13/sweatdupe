"""
Web server wrapper for Render.com free tier deployment
Keeps the bot alive by exposing a health check endpoint
"""
from flask import Flask
from threading import Thread
from bot import SweatDupeBot

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Sweat Dupe Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Run the Telegram bot in a separate thread"""
    try:
        bot = SweatDupeBot()
        bot.run()
    except ValueError as e:
        print(f"⚠️  Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("🤖 Telegram bot started in background thread")
    
    # Run Flask web server on port 10000 (Render's default)
    import os
    port = int(os.getenv("PORT", 10000))
    print(f"🌐 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port)
