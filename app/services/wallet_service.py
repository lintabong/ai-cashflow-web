from typing import Optional
from bson import ObjectId

from lib.database.model.wallet_model import Wallet
from lib.database.manager.wallet_manager import WalletManager

class WalletService:
    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager
    
    def create_wallet(self, user_id: str, name: str, balance: float) -> tuple[bool, str]:
        """Create new wallet. Returns (success, message)."""
        try:
            wallet = Wallet(
                id=str(ObjectId()),
                userId=user_id,
                name=name,
                description='',
                balance=balance,
            )
            
            self.wallet_manager.insert_wallet(wallet)
            return True, "✅ Wallet berhasil ditambahkan!"
            
        except Exception as e:
            return False, f"❌ Gagal membuat wallet: {str(e)}"
    
    def get_wallet_by_name(self, user_id: str, wallet_name: str) -> Optional[Wallet]:
        """Get wallet by name for specific user."""
        return self.wallet_manager.get_wallet_by_name(user_id, wallet_name)
    
    def update_balance(self, wallet_id: str, new_balance: float) -> bool:
        """Update wallet balance."""
        try:
            self.wallet_manager.update_balance(wallet_id, new_balance)
            return True
        except Exception:
            return False