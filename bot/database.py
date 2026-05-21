import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import time

from .config import DATA_FILE, ADMIN_ID, REQUIRED_CHANNEL, CHANNEL_ID


class Database:
    def __init__(self):
        self.data_file = DATA_FILE
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Create data file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            initial_data = self._default_data()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)

    def _default_data(self) -> Dict[str, Any]:
        """Return the default database structure"""
        return {
            "apps": [],
            "users": [],
            "admins": [],
            "required_channels": [],
            "admin_session": {},
            "state": {}
        }

    def _normalize_data(self, data: Dict[str, Any]) -> tuple:
        """Backfill newly added keys for older data files"""
        changed = False
        default_data = self._default_data()

        for key, value in default_data.items():
            if key not in data:
                data[key] = value
                changed = True

        if ADMIN_ID and str(ADMIN_ID) not in data["admins"]:
            data["admins"].append(str(ADMIN_ID))
            changed = True

        if CHANNEL_ID and not data["required_channels"]:
            data["required_channels"].append({
                "id": str(CHANNEL_ID),
                "username": REQUIRED_CHANNEL,
                "title": REQUIRED_CHANNEL
            })
            changed = True

        return data, changed

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data, changed = self._normalize_data(data)
                if changed:
                    self.save_data(data)
                return data
        except Exception as e:
            print(f"Error loading data: {e}")
            data, _ = self._normalize_data(self._default_data())
            return data

    def save_data(self, data: Dict[str, Any]):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    # ==================== APP MANAGEMENT ====================
    def add_app(self, name: str, file_id: str, file_name: str, image_id: str) -> str:
        """Add new app and return its code"""
        data = self.load_data()
        
        # Generate app code
        if data["apps"]:
            last_code = int(data["apps"][-1]["code"])
            app_code = str(last_code + 1)
        else:
            app_code = "1"
        
        app = {
            "code": app_code,
            "name": name,
            "file_id": file_id,
            "file_name": file_name,
            "image": image_id,
            "downloads": 0,
            "active": True,
            "added_at": datetime.now().isoformat() + "Z"
        }
        
        data["apps"].append(app)
        self.save_data(data)
        return app_code

    def get_app_by_code(self, code: str) -> Optional[Dict]:
        """Get app by code"""
        data = self.load_data()
        for app in data["apps"]:
            if app["code"] == code:
                return app
        return None

    def get_app_by_name(self, name: str) -> List[Dict]:
        """Search apps by name"""
        data = self.load_data()
        return [app for app in data["apps"] if name.lower() in app["name"].lower() and app["active"]]

    def get_all_apps(self) -> List[Dict]:
        """Get all active apps"""
        data = self.load_data()
        return [app for app in data["apps"] if app["active"]]

    def get_apps_paginated(self, page: int, per_page: int = 10) -> tuple:
        """Get apps with pagination"""
        apps = self.get_all_apps()
        total = len(apps)
        start = (page - 1) * per_page
        end = start + per_page
        return apps[start:end], (total + per_page - 1) // per_page

    def get_top_apps(self, limit: int = 5) -> List[Dict]:
        """Get top downloaded apps"""
        data = self.load_data()
        apps = [app for app in data["apps"] if app["active"]]
        return sorted(apps, key=lambda x: x["downloads"], reverse=True)[:limit]

    def increment_download(self, code: str, user_id: int):
        """Increment download count and record in user"""
        data = self.load_data()
        
        # Update app download count
        for app in data["apps"]:
            if app["code"] == code:
                app["downloads"] += 1
                break
        
        # Add to user downloads
        user = self.get_user(user_id)
        if user:
            if code not in user["downloads"]:
                user["downloads"].append(code)
            # Update user in database
            for u in data["users"]:
                if u["id"] == str(user_id):
                    u["downloads"] = user["downloads"]
                    break
        
        self.save_data(data)

    def delete_app(self, code: str) -> bool:
        """Delete app by marking as inactive"""
        data = self.load_data()
        for app in data["apps"]:
            if app["code"] == code:
                app["active"] = False
                self.save_data(data)
                return True
        return False

    # ==================== USER MANAGEMENT ====================
    def add_user(self, user_id: int, username: str = None, first_name: str = None) -> Dict:
        """Add new user or return existing"""
        data = self.load_data()
        
        # Check if user exists
        for user in data["users"]:
            if user["id"] == str(user_id):
                user["last_active"] = datetime.now().isoformat() + "Z"
                self.save_data(data)
                return user
        
        # Create new user
        user = {
            "id": str(user_id),
            "username": username,
            "first_name": first_name,
            "joined_at": datetime.now().isoformat() + "Z",
            "last_active": datetime.now().isoformat() + "Z",
            "downloads": [],
            "referred_by": None
        }
        
        data["users"].append(user)
        self.save_data(data)
        return user

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        data = self.load_data()
        for user in data["users"]:
            if user["id"] == str(user_id):
                return user
        return None

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        data = self.load_data()
        return data["users"]

    def set_referrer(self, user_id: int, referrer_id: int) -> bool:
        """Set referrer for a user"""
        data = self.load_data()
        for user in data["users"]:
            if user["id"] == str(user_id):
                user["referred_by"] = str(referrer_id)
                self.save_data(data)
                return True
        return False

    def get_referrals(self, user_id: int) -> List[Dict]:
        """Get all users referred by this user"""
        data = self.load_data()
        return [user for user in data["users"] if user.get("referred_by") == str(user_id)]

    # ==================== ADMIN SESSION ====================
    def set_admin_session(self, admin_id: int, timeout: int = 3600):
        """Set admin session"""
        data = self.load_data()
        expires = int(time.time()) + timeout
        data["admin_session"][str(admin_id)] = {"expires": expires}
        self.save_data(data)

    def is_admin_authenticated(self, admin_id: int) -> bool:
        """Check if admin session is valid"""
        data = self.load_data()
        session = data["admin_session"].get(str(admin_id))
        if session and session["expires"] > int(time.time()):
            return True
        return False

    def clear_admin_session(self, admin_id: int):
        """Clear admin session"""
        data = self.load_data()
        if str(admin_id) in data["admin_session"]:
            del data["admin_session"][str(admin_id)]
            self.save_data(data)

    def is_admin(self, user_id: int) -> bool:
        """Check if user is a configured admin"""
        data = self.load_data()
        return str(user_id) in data["admins"]

    def get_admins(self) -> List[str]:
        """Get all admin IDs"""
        data = self.load_data()
        return data["admins"]

    def add_admin(self, admin_id: int) -> bool:
        """Add admin by Telegram user ID"""
        data = self.load_data()
        admin_id = str(admin_id)
        if admin_id in data["admins"]:
            return False
        data["admins"].append(admin_id)
        self.save_data(data)
        return True

    def remove_admin(self, admin_id: int) -> bool:
        """Remove admin by Telegram user ID. The owner from .env cannot be removed."""
        data = self.load_data()
        admin_id = str(admin_id)
        if ADMIN_ID and admin_id == str(ADMIN_ID):
            return False
        if admin_id not in data["admins"]:
            return False
        data["admins"].remove(admin_id)
        data["admin_session"].pop(admin_id, None)
        self.save_data(data)
        return True

    # ==================== REQUIRED CHANNELS ====================
    def get_required_channels(self) -> List[Dict[str, str]]:
        """Get all channels users must join"""
        data = self.load_data()
        return data["required_channels"]

    def add_required_channel(self, chat_id: str, username: str = None, title: str = None) -> bool:
        """Add required channel"""
        data = self.load_data()
        chat_id = str(chat_id).strip()
        username = self._normalize_username(username)

        for channel in data["required_channels"]:
            if channel["id"] == chat_id or (username and channel.get("username") == username):
                return False

        data["required_channels"].append({
            "id": chat_id,
            "username": username,
            "title": title or username or chat_id
        })
        self.save_data(data)
        return True

    def remove_required_channel(self, identifier: str) -> bool:
        """Remove required channel by ID or username"""
        data = self.load_data()
        identifier = identifier.strip()
        normalized_username = self._normalize_username(identifier)

        for channel in data["required_channels"]:
            if channel["id"] == identifier or channel.get("username") == normalized_username:
                data["required_channels"].remove(channel)
                self.save_data(data)
                return True
        return False

    @staticmethod
    def _normalize_username(username: str = None) -> str:
        if not username:
            return None
        username = username.strip()
        if not username:
            return None
        if username.startswith("https://t.me/"):
            username = username.replace("https://t.me/", "", 1)
        if username.startswith("t.me/"):
            username = username.replace("t.me/", "", 1)
        return username if username.startswith("@") else f"@{username}"

    # ==================== USER STATE ====================
    def set_user_state(self, user_id: int, state: Dict[str, Any]):
        """Set user state"""
        data = self.load_data()
        data["state"][str(user_id)] = state
        self.save_data(data)

    def get_user_state(self, user_id: int) -> Optional[Dict]:
        """Get user state"""
        data = self.load_data()
        return data["state"].get(str(user_id))

    def clear_user_state(self, user_id: int):
        """Clear user state"""
        data = self.load_data()
        if str(user_id) in data["state"]:
            del data["state"][str(user_id)]
            self.save_data(data)

    # ==================== STATISTICS ====================
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        data = self.load_data()
        
        total_downloads = sum(app["downloads"] for app in data["apps"])
        
        return {
            "total_apps": len([app for app in data["apps"] if app["active"]]),
            "total_users": len(data["users"]),
            "total_downloads": total_downloads,
            "total_admins": len(data["admins"]),
            "total_required_channels": len(data["required_channels"])
        }
