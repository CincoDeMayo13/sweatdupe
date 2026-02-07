# Sweat Dupe Bot 💪

A competitive workout accountability Telegram bot for 1-on-1 partnerships.

## Features

- **User Pairing**: Supports exactly 2 users in a workout partnership
- **Wager System**: Set workout challenges using `/wager`
- **Video Note Proof**: Send circular bubble videos as proof
- **Auto-Forwarding**: Instantly forwards proof to your partner
- **Session Persistence**: Saves data to JSON file across restarts
- **Competitive & Encouraging**: Messages designed to motivate and challenge

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Your Bot Token**:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the token you receive

3. **Set Your Token**:
   
   Option A - Environment Variable (Recommended):
   ```bash
   # Windows PowerShell
   $env:TELEGRAM_BOT_TOKEN="your_token_here"
   
   # Linux/Mac
   export TELEGRAM_BOT_TOKEN="your_token_here"
   ```
   
   Option B - Edit the code:
   - Open `sweat_dupe_bot.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual token

4. **Run the Bot**:
   ```bash
   python main.py
   ```

## Usage

### Commands

- `/start` - Register as a user (both partners need to do this)
- `/wager [goal]` - Set a workout challenge
  - Example: `/wager 50 pushups`
  - Example: `/wager 5km run`
- `/status` - Check current partnership and wager status

### Sending Proof

1. Set a wager first using `/wager`
2. Complete your workout
3. Record a **Video Note** (bubble video):
   - In Telegram, tap and hold the microphone icon
   - Switch to video mode (camera icon)
   - Record your proof
4. Bot automatically forwards it to your partner with a notification

## Data Persistence

The bot saves data to `bot_data.json` including:
- Registered user IDs
- Current active wager

This ensures the bot remembers your partnership even after restarts.

## Example Flow

```
User 1: /start
Bot: "🔥 Hey Champion! You're the first one in!"

User 2: /start
Bot: "🎯 Perfect! You're paired up!"

User 1: /wager 50 pushups
Bot: "🎯 WAGER SET: 50 pushups"
[User 2 gets notified]

User 1: [Sends video note]
Bot: "✅ PROOF SENT! 🔥"
[User 2 receives video note]
```

## Error Handling

- Prevents video notes before wager is set
- Checks if both users are registered
- Validates commands before execution
- Graceful error messages

## Notes

- Bot is designed for exactly 2 users
- Video Notes are the circular "bubble" videos in Telegram
- All data persists across bot restarts
- Uses latest async/await syntax for python-telegram-bot v20+

---

Built with competitive spirit and accountability in mind! 🔥💪
