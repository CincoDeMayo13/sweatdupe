"""
Web server wrapper for Render.com free tier deployment
Keeps the bot alive by exposing a health check endpoint
"""
import asyncio
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Sweat Dupe Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Run the Telegram bot in a separate thread"""
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Import here to avoid issues
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        from telegram import Update
        from config import TELEGRAM_BOT_TOKEN
        from data_manager import DataManager
        from handlers import BotHandlers
        
        # Create bot components
        data_manager = DataManager()
        handlers = BotHandlers(data_manager)
        
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_token_here":
            print("⚠️  Please add your bot token to the environment variables!")
            return
        
        # Build application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("myid", handlers.myid))
        application.add_handler(CommandHandler("start", handlers.start))
        application.add_handler(CommandHandler("setgoal", handlers.setgoal))
        application.add_handler(CommandHandler("setstakes", handlers.setstakes))
        application.add_handler(CommandHandler("progress", handlers.progress))
        application.add_handler(CommandHandler("test_reset", handlers.test_reset))
        application.add_handler(MessageHandler(filters.VIDEO_NOTE, handlers.handle_video_note))
        application.add_handler(MessageHandler(filters.COMMAND, handlers.unknown_command))
        
        print("🤖 Sweat Dupe Bot is running...")
        
        # Run the bot with asyncio
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except ValueError as e:
        print(f"⚠️  Configuration Error: {e}")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("🤖 Telegram bot started in background thread")
    
    # Give bot a moment to start
    import time
    time.sleep(2)
    
    # Run Flask web server on port 10000 (Render's default)
    import os
    port = int(os.getenv("PORT", 10000))
    print(f"🌐 Starting web server on port {port}")
    app.run(host="0.0.0.0", port=port)
