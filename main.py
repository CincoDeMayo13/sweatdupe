"""
Main entry point for Sweat Dupe Telegram bot
"""
from bot import SweatDupeBot


def main():
    """Start the Sweat Dupe bot"""
    try:
        bot = SweatDupeBot()
        bot.run()
    except ValueError as e:
        print(f"⚠️  Configuration Error: {e}")
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
