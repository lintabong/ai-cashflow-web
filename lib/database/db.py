
from mysql.connector import pooling
from constants import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER, 
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)

class DatabaseConnection:
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
