from typing import Optional
from bson import ObjectId

from lib.database.model.user_model import User
from lib.database.manager.user_manager import UserManager

class UserService:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
    
    def get_or_create_user(self, telegram_user) -> Optional[User]:
        """Get existing user or return None if not registered."""
        return self.user_manager.get_user_by_telegram_id(telegram_user.id)
    
    def register_user(self, telegram_user) -> tuple[bool, str]:
        """Register new user. Returns (success, message)."""
        # Check if user already exists
        if self.get_or_create_user(telegram_user):
            return False, f'⚠️ Kamu sudah terdaftar, {telegram_user.first_name}'
        
        # Create new user
        user = User(
            id=str(ObjectId()),
            name=f'{telegram_user.first_name}'.strip(),
            telegramId=telegram_user.id,
            password='',
            username=telegram_user.username,
            email='',
            phone='',
        )
        
        self.user_manager.insert_user(user)
        return True, f'✅ Pendaftaran berhasil, {telegram_user.first_name}!'
