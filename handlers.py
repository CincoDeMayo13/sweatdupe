"""
Telegram bot handlers for Sweat Dupe
Contains all command and message handlers
"""
from datetime import timedelta
from telegram import Update
from telegram.ext import ContextTypes
from data_manager import DataManager
from config import MAX_USERS, MIN_WEEKLY_GOAL, MAX_WEEKLY_GOAL, WHITELIST


class BotHandlers:
    """Collection of all bot command and message handlers"""
    
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
    
    def _is_whitelisted(self, user_id: int) -> bool:
        """Check if user is whitelisted (if whitelist is enabled)"""
        if not WHITELIST:  # Empty list means everyone allowed
            return True
        # Note: This requires checking the update object for username
        # Will be checked in each handler
        return True  # Placeholder, actual check in handlers
    
    def _check_username_whitelist(self, update: Update) -> bool:
        """Check if user's username is whitelisted"""
        if not WHITELIST:  # Empty list means everyone allowed
            return True
        
        username = update.effective_user.username
        if not username:
            # User has no username set
            return False
        
        # Check if username (without @) is in whitelist
        return username.lower() in [w.lower() for w in WHITELIST]
    
    async def _send_new_week_notification(self, context: ContextTypes.DEFAULT_TYPE):
        """Send notification to all users about new week"""
        if not self.dm.should_send_week_notification():
            return
        
        user_ids = self.dm.get_user_ids()
        week_start = self.dm.get_week_start()
        
        for user_id in user_ids:
            try:
                user_data = self.dm.get_user_data(user_id)
                current_goal = user_data.get("weekly_goal", 0) if user_data else 0
                
                message = (
                    f"🗓️ NEW WEEK STARTED! 🗓️\n\n"
                    f"Week of {week_start.strftime('%B %d, %Y')}\n\n"
                    f"Your workouts have been reset to 0.\n"
                )
                
                if current_goal > 0:
                    message += (
                        f"\n💪 Your goal: {current_goal} workouts\n\n"
                        f"Want to change it? Use /setgoal\n"
                        f"Time to crush it! 🔥"
                    )
                else:
                    message += (
                        f"\n⚠️ You haven't set a goal yet!\n\n"
                        f"Use /setgoal [number] to set your weekly target\n"
                        f"Example: /setgoal 4"
                    )
                
                await context.bot.send_message(chat_id=user_id, text=message)
                print(f"✅ Sent new week notification to user {user_id}")
            except Exception as e:
                print(f"❌ Failed to send notification to user {user_id}: {e}")
        
        self.dm.mark_week_notification_sent()
    
    async def myid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user their Telegram info for whitelist setup"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name or "Unknown"
        
        if username:
            await update.message.reply_text(
                f"ℹ️ YOUR TELEGRAM INFO\n\n"
                f"Username: @{username}\n"
                f"Name: {first_name}\n"
                f"User ID: {user_id}\n\n"
                f"💡 To whitelist, add this to .env file:\n"
                f'WHITELIST={username}\n\n'
                f"Or for multiple users:\n"
                f'WHITELIST={username},otheruser'
            )
        else:
            await update.message.reply_text(
                f"⚠️ YOU DON'T HAVE A USERNAME!\n\n"
                f"Name: {first_name}\n"
                f"User ID: {user_id}\n\n"
                f"To use username whitelist, you need to:\n"
                f"1. Go to Telegram Settings\n"
                f"2. Edit Profile\n"
                f"3. Set a Username\n\n"
                f"Or use numeric ID: {user_id}"
            )
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.first_name or "Champion"
        
        # Check whitelist by username
        if not self._check_username_whitelist(update):
            tg_username = update.effective_user.username or "[No username]"
            await update.message.reply_text(
                "🚫 ACCESS DENIED 🚫\n\n"
                "This is a private gym.\n"
                "Members only! 💪🔒\n\n"
                f"Your username: @{tg_username}" if tg_username != "[No username]" else ""
            )
            print(f"⚠️ Unauthorized access attempt by {username} (@{tg_username}, ID: {user_id})")
            return
        
        was_reset = self.dm.check_and_reset_week()
        
        # Send week notification if needed
        if was_reset or self.dm.should_send_week_notification():
            await self._send_new_week_notification(context)
        
        if self.dm.user_exists(user_id):
            await update.message.reply_text(
                f"Welcome back, {username}! 💪\n\n"
                f"Use /setgoal to set your weekly workout target\n"
                f"Use /setstakes to set what's on the line!\n"
                f"Check your progress with /progress"
            )
        elif self.dm.get_user_count() < MAX_USERS:
            self.dm.add_user(user_id, username)
            
            if self.dm.get_user_count() == 1:
                await update.message.reply_text(
                    f"🔥 Hey {username}! You're in!\n"
                    f"Waiting for your workout partner to join...\n\n"
                    f"Once they /start, you can both set your weekly goals!"
                )
            else:
                await update.message.reply_text(
                    f"🎯 Perfect! {username}, you're paired up!\n\n"
                    f"Here's how it works:\n"
                    f"1️⃣ Both set weekly goals: /setgoal 4\n"
                    f"2️⃣ Set stakes: /setstakes loser buys dinner\n"
                    f"3️⃣ After each workout, send a video bubble (Sweatcam)!\n"
                    f"4️⃣ End of week: Did you both hit your goals? 👀\n\n"
                    f"Let's get it! 💪"
                )
        else:
            await update.message.reply_text(
                f"Sorry {username}, this bot is for a 1-on-1 partnership and it's already full! 🤝"
            )
    
    async def setgoal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setgoal command - set weekly workout goal"""
        user_id = update.effective_user.id
        
        if not self._check_username_whitelist(update):
            return
        
        self.dm.check_and_reset_week()
        
        username = update.effective_user.first_name or "Champion"
        
        # Check if user is registered
        if not self.dm.user_exists(user_id):
            await update.message.reply_text("⚠️ You need to /start first!")
            return
        
        # Get the goal number
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text(
                "💡 Set your weekly workout goal like this:\n"
                "/setgoal 3  (workout 3 times this week)\n"
                "/setgoal 5  (workout 5 times this week)"
            )
            return
        
        goal = int(context.args[0])
        
        if goal < MIN_WEEKLY_GOAL or goal > MAX_WEEKLY_GOAL:
            await update.message.reply_text(
                f"⚠️ Goal must be between {MIN_WEEKLY_GOAL} and {MAX_WEEKLY_GOAL} workouts per week!"
            )
            return
        
        self.dm.update_user_goal(user_id, goal)
        user_data = self.dm.get_user_data(user_id)
        
        await update.message.reply_text(
            f"🎯 GOAL SET: {goal} workouts this week!\n\n"
            f"Current progress: {user_data['workouts_this_week']}/{goal}\n\n"
            f"Send a video bubble after each workout to log it! 💪"
        )
        
        # Notify partner
        partner_id = self.dm.get_partner_id(user_id)
        if partner_id:
            try:
                partner_data = self.dm.get_user_data(partner_id)
                partner_goal = partner_data.get("weekly_goal", 0) if partner_data else 0
                await context.bot.send_message(
                    chat_id=partner_id,
                    text=f"🔔 {username} set their goal: {goal} workouts!\n"
                         f"Your goal: {partner_goal if partner_goal > 0 else 'Not set yet'}\n\n"
                         f"Time to step up! 🔥"
                )
            except Exception as e:
                print(f"Could not notify partner: {e}")
    
    async def setstakes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setstakes command - set what happens if someone fails"""
        user_id = update.effective_user.id
        
        if not self._check_username_whitelist(update):
            return
        
        # Check if user is registered
        if not self.dm.user_exists(user_id):
            await update.message.reply_text("⚠️ You need to /start first!")
            return
        
        # Check if both partners are registered (TESTING: Commented out)
        # if self.dm.get_user_count() < 2:
        #     await update.message.reply_text(
        #         "⏳ Hold on! You need your partner to join first."
        #     )
        #     return
        
        # Get the stakes
        if not context.args:
            await update.message.reply_text(
                "💡 Set the stakes like this:\n"
                "/setstakes loser buys dinner\n"
                "/setstakes loser does the dishes\n"
                "/setstakes loser buys ice cream\n\n"
                "Keep it fun and motivating! 😄"
            )
            return
        
        stakes = " ".join(context.args)
        self.dm.set_stakes(stakes)
        
        await update.message.reply_text(
            f"💰 STAKES SET!\n\n"
            f"📜 {stakes}\n\n"
            f"If you both hit your goals: Nothing happens! 🎉\n"
            f"If someone misses: Time to pay up! 😅\n\n"
            f"Let the games begin! 🔥"
        )
        
        # Notify partner (if exists)
        partner_id = self.dm.get_partner_id(user_id)
        if partner_id:
            try:
                await context.bot.send_message(
                    chat_id=partner_id,
                    text=f"💰 Stakes have been set:\n\n"
                         f"📜 {stakes}\n\n"
                         f"Game on! 🔥"
                )
            except Exception as e:
                print(f"Could not notify partner: {e}")
        else:
            print("[TEST MODE] No partner to notify")
    
    async def handle_video_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video note (bubble video) submissions - the Sweatcam!"""
        user_id = update.effective_user.id
        
        if not self._check_username_whitelist(update):
            return
        
        self.dm.check_and_reset_week()
        
        username = update.effective_user.first_name or "Your Partner"
        
        # Check if user is registered
        if not self.dm.user_exists(user_id):
            await update.message.reply_text("⚠️ You need to /start first!")
            return
        
        user_data = self.dm.get_user_data(user_id)
        
        # Check if goal is set
        if user_data["weekly_goal"] == 0:
            await update.message.reply_text(
                "⚠️ Set your weekly goal first using /setgoal\n\n"
                "Example: /setgoal 4"
            )
            return
        
        # Get partner
        partner_id = self.dm.get_partner_id(user_id)
        # TESTING: Allow without partner
        # if not partner_id:
        #     await update.message.reply_text(
        #         "⚠️ Your partner hasn't joined yet! They need to /start first."
        #     )
        #     return
        
        # Log the workout
        self.dm.increment_workout_count(user_id)
        user_data = self.dm.get_user_data(user_id)
        
        workouts_done = user_data["workouts_this_week"]
        goal = user_data["weekly_goal"]
        
        # Check if goal reached
        goal_reached = workouts_done >= goal
        
        # Forward the video note to partner (if exists)
        if partner_id:
            try:
                partner_data = self.dm.get_user_data(partner_id)
                partner_name = partner_data["name"] if partner_data else "Partner"
                
                await context.bot.send_message(
                    chat_id=partner_id,
                    text=f"📸 SWEATCAM from {username}!\n\n"
                         f"💪 Their progress: {workouts_done}/{goal} workouts\n"
                         f"{'🎉 GOAL REACHED!' if goal_reached else '⏳ Still grinding...'}\n\n"
                         f"Check out their proof! 👀"
                )
                
                # Forward the actual video note
                await update.message.forward(chat_id=partner_id)
                
            except Exception as e:
                print(f"Error forwarding video note: {e}")
        else:
            print("[TEST MODE] No partner to forward to")
        
        # Confirm to sender
        congrats = ""
        if goal_reached and workouts_done == goal:
            congrats = "\n\n🎉 YOU HIT YOUR WEEKLY GOAL! 🎉\nKeep the streak going!"
        elif goal_reached:
            congrats = f"\n\n🔥 CRUSHING IT! That's {workouts_done} workouts!"
        
        partner_msg = "Partner notified! 🔔" if partner_id else "[TEST MODE - No partner]"
        
        await update.message.reply_text(
            f"✅ WORKOUT LOGGED! 💪\n\n"
            f"This week: {workouts_done}/{goal} workouts\n"
            f"{partner_msg}{congrats}"
        )
    
    async def progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current week's progress"""
        user_id = update.effective_user.id
        
        if not self._check_username_whitelist(update):
            return
        
        self.dm.check_and_reset_week()
        
        if not self.dm.user_exists(user_id):
            await update.message.reply_text("You need to /start first!")
            return
        
        partner_id = self.dm.get_partner_id(user_id)
        
        # Get week info
        week_start = self.dm.get_week_start()
        week_end = week_start + timedelta(days=6)
        
        # User stats
        user_data = self.dm.get_user_data(user_id)
        user_workouts = user_data["workouts_this_week"]
        user_goal = user_data["weekly_goal"]
        user_status = "✅ Goal reached!" if user_workouts >= user_goal and user_goal > 0 else "⏳ Keep going!"
        
        # Partner stats
        partner_data = self.dm.get_user_data(partner_id) if partner_id else {}
        partner_workouts = partner_data.get("workouts_this_week", 0)
        partner_goal = partner_data.get("weekly_goal", 0)
        partner_name = partner_data.get("name", "Partner")
        partner_status = "✅ Goal reached!" if partner_workouts >= partner_goal and partner_goal > 0 else "⏳ Keep going!"
        
        stakes = self.dm.get_stakes()
        
        progress_msg = (
            f"📊 THIS WEEK'S PROGRESS\n"
            f"📅 {week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}\n\n"
            f"YOU:\n"
            f"💪 {user_workouts}/{user_goal if user_goal > 0 else '?'} workouts\n"
            f"{user_status}\n\n"
        )
        
        if partner_id:
            progress_msg += (
                f"{partner_name.upper()}:\n"
                f"💪 {partner_workouts}/{partner_goal if partner_goal > 0 else '?'} workouts\n"
                f"{partner_status}\n\n"
            )
        
        progress_msg += (
            f"💰 Stakes: {stakes}\n\n"
            f"Commands:\n"
            f"/setgoal [number] - Set weekly goal\n"
            f"/setstakes [text] - Set stakes\n"
            f"Send bubble video - Log workout!"
        )
        
        await update.message.reply_text(progress_msg)
    
    async def test_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """[TEST COMMAND] Show reset info and manually trigger reset"""
        user_id = update.effective_user.id
        
        if not self._check_username_whitelist(update):
            return
        
        if not self.dm.user_exists(user_id):
            await update.message.reply_text("You need to /start first!")
            return
        
        from datetime import datetime
        
        # Get current week info
        current_week_start = self.dm.get_week_start()
        stored_week_start = self.dm.data.get("week_start")
        
        if stored_week_start:
            stored_date = datetime.fromisoformat(stored_week_start)
            days_until_reset = 7 - (datetime.now() - stored_date).days
        else:
            days_until_reset = "Unknown"
        
        info_msg = (
            f"🧪 WEEKLY RESET TEST INFO\n\n"
            f"📅 Current week starts: {current_week_start.strftime('%A, %B %d')}\n"
            f"📅 Stored week start: {stored_date.strftime('%A, %B %d') if stored_week_start else 'Not set'}\n"
            f"⏰ Days until Monday reset: {days_until_reset}\n\n"
            f"💡 To test reset:\n"
            f"/test_reset force - Force a reset now\n"
            f"/test_reset info - Show this info"
        )
        
        # Check if user wants to force reset
        if context.args and context.args[0] == "force":
            # Save current data
            user_data = self.dm.get_user_data(update.effective_user.id)
            old_count = user_data["workouts_this_week"]
            
            # Manually trigger reset
            self.dm._reset_weekly_data()
            
            user_data = self.dm.get_user_data(update.effective_user.id)
            new_count = user_data["workouts_this_week"]
            
            await update.message.reply_text(
                f"✅ RESET FORCED!\n\n"
                f"Before: {old_count} workouts\n"
                f"After: {new_count} workouts\n\n"
                f"Week start updated to: {self.dm.data['week_start']}\n\n"
                f"Use /progress to see reset data"
            )
        else:
            await update.message.reply_text(info_msg)
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands - show available commands"""
        user_id = update.effective_user.id
        
        if not self._check_username_whitelist(update):
            return
        
        await update.message.reply_text(
            "❓ Unknown command!\n\n"
            "📋 Available Commands:\n\n"
            "/start - Register and join\n"
            "/setgoal [number] - Set weekly workout goal\n"
            "  Example: /setgoal 4\n\n"
            "/setstakes [text] - Set what's at stake\n"
            "  Example: /setstakes loser buys dinner\n\n"
            "/progress - Check this week's progress\n\n"
            "/myid - Get your Telegram ID\n\n"
            "📸 Send a video bubble after each workout to log it!"
        )
