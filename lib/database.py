import mysql.connector
from mysql.connector import pooling, Error
from decimal import Decimal
from typing import Optional, List
from constants import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER, 
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)

class DatabaseConnection:
    """Mengelola koneksi database dengan pooling"""
    
    def __init__(self):
        self.pool = pooling.MySQLConnectionPool(
            pool_name='inventory_pool',
            pool_size=5,
            pool_reset_session=True,
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            database=MYSQL_DATABASE,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            autocommit=False
        )
    
    def get_connection(self):
        return self.pool.get_connection()

class User:
    """Model untuk user"""
    
    def __init__(self, id, name, telegramId, password=None, username=None, 
                 email=None, phone=None, balance=0.00, isActive=True):
        self.id = id
        self.name = name
        self.password = password
        self.username = username
        self.email = email
        self.phone = phone
        self.telegramId = telegramId
        self.balance = Decimal(str(balance))
        self.isActive = isActive

class InventoryItem:
    """Model untuk inventory item"""
    
    def __init__(self, id, userId, itemName, itemType, sellingPrice, 
                 costPrice=0.00, unit='pcs', stock=0.00, isActive=True):
        self.id = id
        self.userId = userId
        self.itemName = itemName
        self.itemType = itemType
        self.sellingPrice = Decimal(str(sellingPrice))
        self.costPrice = Decimal(str(costPrice))
        self.unit = unit
        self.stock = Decimal(str(stock))
        self.isActive = isActive

class UserManager:
    """Class utama untuk mengelola users"""
    
    def __init__(self, db_connection: DatabaseConnection):
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
            print(f"User '{user.name}' berhasil diinsert")
            return True
            
        except Error as e:
            print(f"Error insert user: {e}")
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
            print(f"Error get user: {e}")
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
            print(f"Error get user by telegram: {e}")
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
            print(f"Error get user by username: {e}")
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
            print(f"Error get all users: {e}")
        
        return users

class InventoryManager:
    """Class utama untuk mengelola inventory"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def insert_item(self, item: InventoryItem) -> bool:
        """Insert item ke database"""
        query = """
        INSERT INTO inventories 
        (id, userId, itemName, itemType, sellingPrice, costPrice, unit, stock, isActive)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (
                item.id, item.userId, item.itemName, item.itemType,
                item.sellingPrice, item.costPrice, item.unit, item.stock, item.isActive
            ))
            conn.commit()
            conn.close()
            print(f"Item '{item.itemName}' berhasil diinsert")
            return True
            
        except Error as e:
            print(f"Error insert: {e}")
            return False
    
    def get_item_by_id(self, item_id: str) -> Optional[InventoryItem]:
        """Ambil item berdasarkan ID"""
        query = "SELECT * FROM inventories WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return InventoryItem(
                    id=result['id'],
                    userId=result['userId'],
                    itemName=result['itemName'],
                    itemType=result['itemType'],
                    sellingPrice=result['sellingPrice'],
                    costPrice=result['costPrice'],
                    unit=result['unit'],
                    stock=result['stock'],
                    isActive=result['isActive']
                )
            return None
            
        except Error as e:
            print(f"Error get item: {e}")
            return None
    
    def get_items_by_user(self, user_id: str) -> List[InventoryItem]:
        """Ambil semua items berdasarkan user ID"""
        query = "SELECT * FROM inventories WHERE userId = %s AND isActive = TRUE"
        
        items = []
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            conn.close()
            
            for result in results:
                items.append(InventoryItem(
                    id=result['id'],
                    userId=result['userId'],
                    itemName=result['itemName'],
                    itemType=result['itemType'],
                    sellingPrice=result['sellingPrice'],
                    costPrice=result['costPrice'],
                    unit=result['unit'],
                    stock=result['stock'],
                    isActive=result['isActive']
                ))
                
        except Error as e:
            print(f"Error get items: {e}")
        
        return items
