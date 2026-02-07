"""
Bot initialization and setup
"""
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from config import TELEGRAM_BOT_TOKEN
from data_manager import DataManager
from handlers import BotHandlers


class SweatDupeBot:
    """Main bot class that sets up and runs the Telegram bot"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.handlers = BotHandlers(self.data_manager)
        self.application = None
    
    def setup(self):
        """Setup the bot with handlers"""
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_token_here":
            raise ValueError(
                "Please add your bot token to the .env file!\n"
                "1. Open .env file\n"
                "2. Replace 'your_token_here' with your actual token from @BotFather"
            )
        
        # Create application
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("myid", self.handlers.myid))
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("setgoal", self.handlers.setgoal))
        self.application.add_handler(CommandHandler("setstakes", self.handlers.setstakes))
        self.application.add_handler(CommandHandler("progress", self.handlers.progress))
        self.application.add_handler(CommandHandler("test_reset", self.handlers.test_reset))
        self.application.add_handler(MessageHandler(filters.VIDEO_NOTE, self.handlers.handle_video_note))
        
        # Unknown command handler (must be last)
        self.application.add_handler(MessageHandler(filters.COMMAND, self.handlers.unknown_command))
    
    def run(self):
        """Start the bot"""
        self.setup()
        print("🤖 Sweat Dupe Bot is running...")
        print("Press Ctrl+C to stop")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
