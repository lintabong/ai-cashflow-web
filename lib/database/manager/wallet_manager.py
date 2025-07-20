
from mysql.connector import Error
from typing import Optional, List
import logging
from decimal import Decimal
from datetime import datetime

from lib.database.model.wallet_model import Wallet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalletManager:
    """Class utama untuk mengelola wallet"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def insert_wallet(self, wallet: Wallet) -> bool:
        """Insert wallet ke database"""
        query = """
        INSERT INTO wallets 
        (id, userId, name, description, balance, isActive)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (
                wallet.id, wallet.userId, wallet.name, wallet.description,
                wallet.balance, wallet.isActive
            ))
            conn.commit()
            conn.close()
            logger.info(f"Wallet '{wallet.name}' berhasil diinsert")
            return True
            
        except Error as e:
            logger.error(f"Error insert wallet: {e}")
            return False
    
    def get_wallet_by_id(self, wallet_id: str) -> Optional[Wallet]:
        """Ambil wallet berdasarkan ID"""
        query = "SELECT * FROM wallets WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (wallet_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return Wallet(
                    id=result['id'],
                    userId=result['userId'],
                    name=result['name'],
                    description=result['description'],
                    balance=result['balance'],
                    isActive=result['isActive'],
                    createdAt=result['createdAt'],
                    updatedAt=result['updatedAt']
                )
            return None
            
        except Error as e:
            logger.error(f"Error get wallet: {e}")
            return None
    
    def get_wallets_by_user(self, user_id: str) -> List[Wallet]:
        """Ambil semua wallet berdasarkan user ID"""
        query = "SELECT * FROM wallets WHERE userId = %s AND isActive = TRUE ORDER BY name"
        
        wallets = []
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            conn.close()
            
            for result in results:
                wallets.append(Wallet(
                    id=result['id'],
                    userId=result['userId'],
                    name=result['name'],
                    description=result['description'],
                    balance=result['balance'],
                    isActive=result['isActive'],
                    createdAt=result['createdAt'],
                    updatedAt=result['updatedAt']
                ))
                
        except Error as e:
            logger.error(f"Error get wallets by user: {e}")
        
        return wallets
    
    def get_wallet_by_name(self, user_id: str, wallet_name: str) -> Optional[Wallet]:
        """Ambil wallet berdasarkan user ID dan nama wallet"""
        query = "SELECT * FROM wallets WHERE userId = %s AND name = %s AND isActive = TRUE"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id, wallet_name))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return Wallet(
                    id=result['id'],
                    userId=result['userId'],
                    name=result['name'],
                    description=result['description'],
                    balance=result['balance'],
                    isActive=result['isActive'],
                    createdAt=result['createdAt'],
                    updatedAt=result['updatedAt']
                )
            return None
            
        except Error as e:
            logger.error(f"Error get wallet by name: {e}")
            return None
    
    def update_wallet(self, wallet: Wallet) -> bool:
        """Update wallet information"""
        query = """
        UPDATE wallets 
        SET name = %s, description = %s, balance = %s, isActive = %s
        WHERE id = %s
        """
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (
                wallet.name, wallet.description, wallet.balance, 
                wallet.isActive, wallet.id
            ))
            conn.commit()
            conn.close()
            logger.info(f"Wallet '{wallet.name}' berhasil diupdate")
            return True
            
        except Error as e:
            logger.error(f"Error update wallet: {e}")
            return False
    
    def update_balance(self, wallet_id: str, new_balance: Decimal) -> bool:
        """Update balance wallet"""
        query = "UPDATE wallets SET balance = %s WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (new_balance, wallet_id))
            conn.commit()
            conn.close()
            logger.info(f"Balance wallet ID '{wallet_id}' berhasil diupdate ke {new_balance}")
            return True
            
        except Error as e:
            logger.error(f"Error update balance: {e}")
            return False
    
    def add_balance(self, wallet_id: str, amount: Decimal) -> bool:
        """Tambah balance wallet"""
        query = "UPDATE wallets SET balance = balance + %s WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (amount, wallet_id))
            conn.commit()
            conn.close()
            logger.info(f"Balance wallet ID '{wallet_id}' ditambah sebesar {amount}")
            return True
            
        except Error as e:
            logger.error(f"Error add balance: {e}")
            return False
    
    def subtract_balance(self, wallet_id: str, amount: Decimal) -> bool:
        """Kurangi balance wallet"""
        # Cek apakah balance mencukupi
        wallet = self.get_wallet_by_id(wallet_id)
        if not wallet:
            logger.info(f"Wallet ID '{wallet_id}' tidak ditemukan")
            return False
        
        if wallet.balance < amount:
            logger.error(f"Balance tidak mencukupi. Current: {wallet.balance}, Required: {amount}")
            return False
        
        query = "UPDATE wallets SET balance = balance - %s WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (amount, wallet_id))
            conn.commit()
            conn.close()
            logger.info(f"Balance wallet ID '{wallet_id}' dikurangi sebesar {amount}")
            return True
            
        except Error as e:
            logger.error(f"Error subtract balance: {e}")
            return False
    
    def transfer_balance(self, from_wallet_id: str, to_wallet_id: str, amount: Decimal) -> bool:
        """Transfer balance antar wallet"""
        from_wallet = self.get_wallet_by_id(from_wallet_id)
        to_wallet = self.get_wallet_by_id(to_wallet_id)
        
        if not from_wallet or not to_wallet:
            print("Salah satu wallet tidak ditemukan")
            return False
        
        if from_wallet.balance < amount:
            print(f"Balance wallet '{from_wallet.name}' tidak mencukupi")
            return False
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Kurangi balance wallet sumber
            cursor.execute("UPDATE wallets SET balance = balance - %s WHERE id = %s", 
                         (amount, from_wallet_id))
            
            # Tambah balance wallet tujuan
            cursor.execute("UPDATE wallets SET balance = balance + %s WHERE id = %s", 
                         (amount, to_wallet_id))
            
            conn.commit()
            conn.close()
            print(f"Transfer {amount} dari '{from_wallet.name}' ke '{to_wallet.name}' berhasil")
            return True
            
        except Error as e:
            print(f"Error transfer balance: {e}")
            conn.rollback()
            return False
    
    def delete_wallet(self, wallet_id: str) -> bool:
        """Soft delete wallet (set isActive = FALSE)"""
        query = "UPDATE wallets SET isActive = FALSE WHERE id = %s"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (wallet_id,))
            conn.commit()
            conn.close()
            print(f"Wallet dengan ID '{wallet_id}' berhasil dihapus")
            return True
            
        except Error as e:
            print(f"Error delete wallet: {e}")
            return False
    
    def get_total_balance_by_user(self, user_id: str) -> Decimal:
        """Hitung total balance semua wallet user"""
        query = "SELECT COALESCE(SUM(balance), 0) as total FROM wallets WHERE userId = %s AND isActive = TRUE"
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return Decimal(str(result[0])) if result[0] else Decimal('0')
            
        except Error as e:
            print(f"Error get total balance: {e}")
            return Decimal('0')
    
    def get_wallet_summary_by_user(self, user_id: str) -> dict:
        """Dapatkan ringkasan wallet user"""
        wallets = self.get_wallets_by_user(user_id)
        total_balance = self.get_total_balance_by_user(user_id)
        
        wallet_list = []
        for wallet in wallets:
            wallet_list.append({
                'id': wallet.id,
                'name': wallet.name,
                'balance': wallet.balance,
                'description': wallet.description
            })
        
        return {
            'total_wallets': len(wallets),
            'total_balance': total_balance,
            'wallets': wallet_list
        }
    
    def is_wallet_name_exists(self, user_id: str, wallet_name: str, exclude_id: str = None) -> bool:
        """Cek apakah nama wallet sudah digunakan user"""
        if exclude_id:
            query = "SELECT COUNT(*) FROM wallets WHERE userId = %s AND name = %s AND id != %s AND isActive = TRUE"
            params = (user_id, wallet_name, exclude_id)
        else:
            query = "SELECT COUNT(*) FROM wallets WHERE userId = %s AND name = %s AND isActive = TRUE"
            params = (user_id, wallet_name)
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            return result[0] > 0
            
        except Error as e:
            print(f"Error check wallet name exists: {e}")
            return True  # Return True untuk safety
    
    def create_default_wallet(self, user_id: str) -> Optional[Wallet]:
        """Buat wallet default untuk user baru"""
        wallet_id = f"wallet_{user_id}_{int(datetime.now().timestamp())}"
        
        default_wallet = Wallet(
            id=wallet_id,
            userId=user_id,
            name="Kas Utama",
            description="Wallet default untuk kas utama",
            balance=Decimal('0.00'),
            isActive=True
        )
        
        if self.insert_wallet(default_wallet):
            return default_wallet
        return None
