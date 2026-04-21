"""
Simple user management (in-memory for now, should use database in production)
"""
import json
from typing import Optional, Dict, Any
from pathlib import Path
from auth.security import get_password_hash, verify_password
from auth.models import User, UserCreate
from config import Config
import logging

logger = logging.getLogger(__name__)

# Simple file-based user storage (replace with database in production)
USERS_FILE = Path("data/users.json")


class UserManager:
    """Simple user management"""
    
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self._load_users()
        self._create_default_users()
    
    def _load_users(self):
        """Load users from file"""
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE, 'r') as f:
                    self.users = json.load(f)
                logger.info(f"Loaded {len(self.users)} users from file")
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                self.users = {}
        else:
            self.users = {}
            # Create directory if it doesn't exist
            USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def _save_users(self):
        """Save users to file"""
        try:
            with open(USERS_FILE, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def _create_default_users(self):
        """Create default users if none exist"""
        if not self.users:
            default_users = [
                {
                    "username": "admin",
                    "password": get_password_hash("admin123"),  # Change in production!
                    "role": "admin",
                    "email": "admin@hospital.local"
                },
                {
                    "username": "nurse",
                    "password": get_password_hash("nurse123"),  # Change in production!
                    "role": "user",
                    "email": "nurse@hospital.local"
                }
            ]
            
            for user in default_users:
                username = user.pop("username")
                self.users[username] = user
            
            self._save_users()
            logger.warning("Created default users. CHANGE PASSWORDS IN PRODUCTION!")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user_data = self.users.get(username)
        if not user_data:
            return None
        
        if not verify_password(password, user_data["password"]):
            return None
        
        if user_data.get("disabled", False):
            return None
        
        return User(
            username=username,
            email=user_data.get("email"),
            role=user_data.get("role", "user"),
            disabled=user_data.get("disabled", False)
        )
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_data = self.users.get(username)
        if not user_data:
            return None
        
        return User(
            username=username,
            email=user_data.get("email"),
            role=user_data.get("role", "user"),
            disabled=user_data.get("disabled", False)
        )
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        if self.users.get(user_create.username):
            raise ValueError(f"User {user_create.username} already exists")
        
        self.users[user_create.username] = {
            "password": get_password_hash(user_create.password),
            "email": user_create.email,
            "role": user_create.role,
            "disabled": False
        }
        
        self._save_users()
        
        return User(
            username=user_create.username,
            email=user_create.email,
            role=user_create.role,
            disabled=False
        )


# Global user manager instance
user_manager = UserManager()

