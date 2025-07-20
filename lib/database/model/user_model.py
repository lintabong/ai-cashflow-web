

from decimal import Decimal

class User:
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
