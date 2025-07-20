
from decimal import Decimal

class Wallet:
    def __init__(self, id, userId, name, description=None, balance=0.00, 
                 isActive=True, createdAt=None, updatedAt=None):
        self.id = id
        self.userId = userId
        self.name = name
        self.description = description
        self.balance = Decimal(str(balance))
        self.isActive = isActive
        self.createdAt = createdAt
        self.updatedAt = updatedAt
