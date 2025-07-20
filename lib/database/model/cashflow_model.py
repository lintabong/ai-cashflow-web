
from decimal import Decimal

class CashflowItem:
    def __init__(self, id, userId, transactionDate, activityName, 
                 description=None, category=None, quantity=1.00, unit='unit',
                 flowType='income', isActive=True, price=0.00, total=0.00, 
                 profit=0.00, createdAt=None, updatedAt=None):
        self.id = id
        self.userId = userId
        self.transactionDate = transactionDate
        self.activityName = activityName
        self.description = description
        self.category = category
        self.quantity = Decimal(str(quantity))
        self.unit = unit
        self.flowType = flowType
        self.isActive = isActive
        self.price = Decimal(str(price))
        self.total = Decimal(str(total))
        self.profit = Decimal(str(profit))
        self.createdAt = createdAt
        self.updatedAt = updatedAt
