import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId

from lib.database.model.cashflow_model import CashflowItem
from lib.database.manager.cashflow_manager import CashflowManager
from bot.services.ai_service import AIService
from bot.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, ai_service: AIService, cashflow_manager: CashflowManager, 
                 wallet_service: WalletService):
        self.ai_service = ai_service
        self.cashflow_manager = cashflow_manager
        self.wallet_service = wallet_service
    
    def process_transaction_message(self, user_id: str, message: str, history: Optional[List] = None) -> str:
        """Process transaction message and return formatted response."""
        return self.ai_service.process_transaction(message, history)
    
    def extract_wallet_from_chat_log(self, chat_log: List[Dict]) -> Optional[str]:
        """Extract wallet name from chat log."""
        for message in chat_log:
            if message["role"] == "model":
                text = message["text"]
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(text)
                    for entry in data:
                        if "activityName" in entry and "wallet" in entry:
                            return entry['wallet']
                except Exception as e:
                    logger.error(f"Failed to parse JSON from chat log: {e}")
        return None
    
    def extract_transaction_data_from_chat_log(self, chat_log: List[Dict]) -> List[Dict]:
        """Extract transaction data from chat log."""
        for message in chat_log:
            if message["role"] == "model":
                text = message["text"]
                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(text)
                except Exception as e:
                    logger.error(f"Failed to parse transaction data: {e}")
        return []
    
    def save_transactions(self, user_id: str, chat_log: List[Dict]) -> tuple[bool, str]:
        """Save confirmed transactions to database."""
        try:
            # Extract wallet information
            wallet_name = self.extract_wallet_from_chat_log(chat_log)
            if not wallet_name:
                return False, '❌ Wallet tidak ditemukan dalam data transaksi.'
            
            wallet = self.wallet_service.get_wallet_by_name(user_id, wallet_name)
            if not wallet:
                return False, '❌ Wallet tidak ditemukan di database.'
            
            # Extract and save transactions
            transaction_data = self.extract_transaction_data_from_chat_log(chat_log)
            if not transaction_data:
                return False, '❌ Data transaksi tidak valid.'
            
            total_amount = 0
            
            for transaction in transaction_data:
                cashflow_item = CashflowItem(
                    id=str(ObjectId()),
                    userId=user_id,
                    walletId=wallet.id,
                    transactionDate=datetime.strptime(transaction['date'], '%Y-%m-%d %H:%M:%S'),
                    activityName=transaction['activityName'],
                    description='',
                    categoryId=1,
                    quantity=transaction['quantity'],
                    unit=transaction['unit'],
                    flowType=transaction['flowType'],
                    price=transaction['price'],
                    total=transaction['price'] * transaction['quantity'],
                )
                
                # Calculate total amount for balance update
                if transaction['flowType'] == 'income':
                    total_amount -= transaction['price'] * transaction['quantity']
                if transaction['flowType'] == 'expense':
                    total_amount += transaction['price'] * transaction['quantity']
                
                self.cashflow_manager.insert_cashflow(cashflow_item)
            
            # Update wallet balance
            new_balance = wallet.balance - total_amount
            self.wallet_service.update_balance(wallet.id, new_balance)
            
            return True, '✅ Data telah disimpan. Terima kasih!'
            
        except Exception as e:
            logger.error(f"Error saving transactions: {e}")
            return False, '❌ Terjadi kesalahan saat menyimpan transaksi.'
