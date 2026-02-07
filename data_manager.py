"""
Data persistence manager for Sweat Dupe bot
Handles loading, saving, and managing bot data
"""
import json
import os
from typing import Optional
from datetime import datetime, timedelta
from config import DATA_FILE


class DataManager:
    """Manages persistent data storage for the bot"""
    
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self) -> dict:
        """Load data from JSON file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._get_default_data()
        return self._get_default_data()
    
    def _get_default_data(self) -> dict:
        """Get default data structure"""
        return {
            "users": {},  # user_id: {name, weekly_goal, workouts_this_week}
            "stakes": None,  # What happens if someone fails
            "week_start": None  # ISO format date string
        }
    
    def save_data(self):
        """Save data to JSON file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_partner_id(self, user_id: int) -> Optional[int]:
        """Get the partner's user_id"""
        users = self.data.get("users", {})
        user_ids = list(users.keys())
        if str(user_id) in user_ids:
            for uid in user_ids:
                if uid != str(user_id):
                    return int(uid)
        return None
    
    def get_week_start(self) -> datetime:
        """Get the start of the current week (Monday)"""
        today = datetime.now()
        # Get Monday of current week
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def check_and_reset_week(self) -> bool:
        """Check if we need to reset for a new week"""
        current_week_start = self.get_week_start()
        stored_week_start = self.data.get("week_start")
        
        if stored_week_start is None:
            # First time setup
            print(f"📅 First time setup - Setting week start to {current_week_start.strftime('%Y-%m-%d')}")
            self.data["week_start"] = current_week_start.isoformat()
            self.save_data()
            return False
        
        stored_date = datetime.fromisoformat(stored_week_start)
        
        # If current week is different, reset
        if current_week_start > stored_date:
            print(f"✅ New week detected: {stored_date.strftime('%Y-%m-%d')} → {current_week_start.strftime('%Y-%m-%d')}")
            self._reset_weekly_data()
            return True
        return False
    
    def _reset_weekly_data(self):
        """Reset workout counts for a new week"""
        users = self.data.get("users", {})
        print(f"\n🔄 WEEKLY RESET TRIGGERED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        for user_id in users:
            old_count = users[user_id]["workouts_this_week"]
            users[user_id]["workouts_this_week"] = 0
            print(f"   User {user_id}: {old_count} → 0 workouts")
        
        self.data["week_start"] = self.get_week_start().isoformat()
        self.data["needs_week_notification"] = True  # Flag to send notifications
        self.save_data()
        print(f"   New week starts: {self.data['week_start']}\n")
    
    def get_user_ids(self) -> list:
        """Get list of all user IDs"""
        return [int(uid) for uid in self.data.get("users", {}).keys()]
    
    def should_send_week_notification(self) -> bool:
        """Check if week notification needs to be sent"""
        return self.data.get("needs_week_notification", False)
    
    def mark_week_notification_sent(self):
        """Mark that week notification has been sent"""
        self.data["needs_week_notification"] = False
        self.save_data()
    
    def add_user(self, user_id: int, username: str) -> bool:
        """Add a new user. Returns True if successful, False if full"""
        users = self.data.get("users", {})
        if len(users) >= 2:
            return False
        
        users[str(user_id)] = {
            "name": username,
            "weekly_goal": 0,
            "workouts_this_week": 0
        }
        self.data["users"] = users
        self.save_data()
        return True
    
    def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        return str(user_id) in self.data.get("users", {})
    
    def get_user_data(self, user_id: int) -> Optional[dict]:
        """Get user data"""
        return self.data.get("users", {}).get(str(user_id))
    
    def update_user_goal(self, user_id: int, goal: int):
        """Update user's weekly goal"""
        users = self.data.get("users", {})
        if str(user_id) in users:
            users[str(user_id)]["weekly_goal"] = goal
            self.data["users"] = users
            self.save_data()
    
    def increment_workout_count(self, user_id: int):
        """Increment user's workout count"""
        users = self.data.get("users", {})
        if str(user_id) in users:
            users[str(user_id)]["workouts_this_week"] += 1
            self.data["users"] = users
            self.save_data()
    
    def set_stakes(self, stakes: str):
        """Set the stakes for the week"""
        self.data["stakes"] = stakes
        self.save_data()
    
    def get_stakes(self) -> str:
        """Get current stakes"""
        return self.data.get("stakes", "Not set")
    
    def get_user_count(self) -> int:
        """Get number of registered users"""
        return len(self.data.get("users", {}))
