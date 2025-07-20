
from mysql.connector import Error
from typing import List
from datetime import date
import logging

from lib.database.model.cashflow_model import CashflowItem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CashflowManager:
    """Class utama untuk mengelola cashflow"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def insert_cashflow(self, item: CashflowItem) -> bool:
        """Insert cashflow ke database"""
        query = """
        INSERT INTO cashflow 
        (id, userId, walletId, transactionDate, activityName, description, categoryId, 
         quantity, unit, flowType, isActive, price, total)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (
                item.id, item.userId, item.walletId, item.transactionDate, 
                item.activityName, item.description, item.categoryId, item.quantity, 
                item.unit, item.flowType, item.isActive, item.price, item.total
            ))
            conn.commit()
            conn.close()
            logger.info(f'Cashflow {item.activityName} berhasil diinsert')
            return True
            
        except Error as e:
            logger.error(f'Error insert cashflow: {e}')
            return False
        
    def get_cashflows_by_date_range(self, user_id: str, start_date: date, end_date: date) -> List[CashflowItem]:
        """Ambil cashflow berdasarkan user ID dan rentang tanggal"""
        query = """
        SELECT * FROM cashflow 
        WHERE userId = %s AND transactionDate BETWEEN %s AND %s AND isActive = TRUE 
        ORDER BY transactionDate DESC
        """
        
        cashflows = []
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id, start_date, end_date))
            results = cursor.fetchall()
            conn.close()
            
            for result in results:
                cashflows.append(CashflowItem(
                    id=result['id'],
                    userId=result['userId'],
                    walletId=result['walletId'],
                    transactionDate=result['transactionDate'],
                    activityName=result['activityName'],
                    description=result['description'],
                    categoryId=result['categoryId'],
                    quantity=result['quantity'],
                    unit=result['unit'],
                    flowType=result['flowType'],
                    isActive=result['isActive'],
                    price=result['price'],
                    total=result['total'],
                    createdAt=result['createdAt'],
                    updatedAt=result['updatedAt']
                ))
                
        except Error as e:
            logger.error(f"Error get cashflows by date range: {e}")
        
        return cashflows
    
    def get_cashflows_by_wallet(self, user_id: str, wallet_id: str, start_date: date = None, end_date: date = None) -> List[CashflowItem]:
        """Ambil cashflow berdasarkan user ID dan wallet ID dengan optional date range"""
        base_query = """
        SELECT * FROM cashflow 
        WHERE userId = %s AND walletId = %s AND isActive = TRUE 
        """
        
        params = [user_id, wallet_id]
        
        if start_date and end_date:
            base_query += "AND transactionDate BETWEEN %s AND %s "
            params.extend([start_date, end_date])
        
        base_query += "ORDER BY transactionDate DESC"
        
        cashflows = []
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            conn.close()
            
            for result in results:
                cashflows.append(CashflowItem(
                    id=result['id'],
                    userId=result['userId'],
                    walletId=result['walletId'],
                    transactionDate=result['transactionDate'],
                    activityName=result['activityName'],
                    description=result['description'],
                    categoryId=result['categoryId'],
                    quantity=result['quantity'],
                    unit=result['unit'],
                    flowType=result['flowType'],
                    isActive=result['isActive'],
                    price=result['price'],
                    total=result['total'],
                    createdAt=result['createdAt'],
                    updatedAt=result['updatedAt']
                ))
                
        except Error as e:
            logger.error(f"Error get cashflows by wallet: {e}")
        
        return cashflows
