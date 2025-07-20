CREATE TABLE users (
    id CHAR(24) NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT,
    username TEXT,
    email TEXT,
    phone TEXT,
    telegramId BIGINT UNIQUE NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,
    isActive BOOLEAN DEFAULT TRUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lastLogin TIMESTAMP NULL,
    
    -- Index untuk optimasi query isActive
    INDEX idx_isActive (isActive),
    
    -- Index untuk kolom yang sering digunakan untuk pencarian
    INDEX idx_username (username(100)),
    INDEX idx_email (email(100)),
    INDEX idx_telegramId (telegramId)
);

CREATE TABLE cashflow (
    id CHAR(24) PRIMARY KEY,
    userId CHAR(24) NOT NULL,
    walletId CHAR(24) NOT NULL,
    transactionDate TIMESTAMP NOT NULL,
    activityName VARCHAR(255) NOT NULL,
    description TEXT,
    categoryId INT,
    quantity DECIMAL(15,4) DEFAULT 1.00,
    unit VARCHAR(50) DEFAULT 'unit',
    flowType ENUM('income', 'expense', 'transfer') NOT NULL,
    isActive BOOLEAN DEFAULT TRUE,
    price DECIMAL(15,2) DEFAULT 0.00,
    total DECIMAL(15,2) DEFAULT 0.00,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_user (userId),
    INDEX idx_wallet (walletId)
);

CREATE TABLE wallets (
    id CHAR(24) PRIMARY KEY,
    userId CHAR(24) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    balance DECIMAL(15,2) DEFAULT 0.00,
    isActive BOOLEAN DEFAULT TRUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_user (userId),
    INDEX idx_name (name)
);
