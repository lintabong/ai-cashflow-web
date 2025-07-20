

from mysql.connector import Error
from typing import Optional, List
import logging

from lib.database.model.user_model import User

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserManager:
    """Class utama untuk mengelola users"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def insert_user(self, user: User) -> bool:
        """Insert user ke database"""
        query = """
        INSERT INTO users 
        (id, name, password, username, email, phone, telegramId, balance, isActive)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (
                user.id, user.name, user.password, user.username, user.email,
                user.phone, user.telegramId, user.balance, user.isActive
            ))
            conn.commit()
            conn.close()
            logger.info(f"User '{user.name}' berhasil diinsert")
            return True
            
        except Error as e:
            logger.info(f"Error insert user: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Ambil user berdasarkan ID"""
        query = "SELECT * FROM users WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    id=result['id'],
                    name=result['name'],
                    password=result['password'],
                    username=result['username'],
                    email=result['email'],
                    phone=result['phone'],
                    telegramId=result['telegramId'],
                    balance=result['balance'],
                    isActive=result['isActive']
                )
            return None
            
        except Error as e:
            logger.info(f"Error get user: {e}")
            return None
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Ambil user berdasarkan Telegram ID"""
        query = "SELECT * FROM users WHERE telegramId = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (telegram_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    id=result['id'],
                    name=result['name'],
                    password=result['password'],
                    username=result['username'],
                    email=result['email'],
                    phone=result['phone'],
                    telegramId=result['telegramId'],
                    balance=result['balance'],
                    isActive=result['isActive']
                )
            return None
            
        except Error as e:
            logger.info(f"Error get user by telegram: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Ambil user berdasarkan username"""
        query = "SELECT * FROM users WHERE username = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return User(
                    id=result['id'],
                    name=result['name'],
                    password=result['password'],
                    username=result['username'],
                    email=result['email'],
                    phone=result['phone'],
                    telegramId=result['telegramId'],
                    balance=result['balance'],
                    isActive=result['isActive']
                )
            return None
            
        except Error as e:
            logger.info(f"Error get user by username: {e}")
            return None
    
    def get_all_active_users(self) -> List[User]:
        """Ambil semua user yang aktif"""
        query = "SELECT * FROM users WHERE isActive = TRUE ORDER BY createdAt DESC"
        
        users = []
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            for result in results:
                users.append(User(
                    id=result['id'],
                    name=result['name'],
                    password=result['password'],
                    username=result['username'],
                    email=result['email'],
                    phone=result['phone'],
                    telegramId=result['telegramId'],
                    balance=result['balance'],
                    isActive=result['isActive']
                ))
                
        except Error as e:
            logger.info(f"Error get all users: {e}")
        
        return users
