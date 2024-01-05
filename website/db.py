import sqlite3

connection = sqlite3.connect("C:\\Users\\corey\\OneDrive\\Desktop\\Database_Working\\website\\exchange.db")

cursor = connection.cursor()

users_table = """ CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL,
    first_name TEXT NOT NULL,
    hashed_password TEXT NOT NULL
)"""

assets_table = """ CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY NOT NULL,
    symbol text NOT NULL
)"""

portfolio_table = """ CREATE TABLE IF NOT EXISTS portfolio (
    user_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    quantity DECIMAL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id)
)"""

symbols = [
    (0, 'GBP'),
    (1, 'BTC'),
    (2, 'ETH'),
    (3, 'BNB'),
    (4, 'ADA'),
    (5, 'SOL'),
    (6, 'XRP'),
    (7, 'DOT'),
    (8, 'DOGE'),
    (9, 'MATIC'),
    (10, 'LINK'),
    (11, 'LTC'),
    (12, 'VET'),
    (13, 'CAKE'),
    (14, 'ENJ'),
    (15, 'RUNE'),
    (16, 'LUNA')
    ]

insert_assets = """ INSERT INTO assets (asset_id, symbol)
VALUES (?, ?)
"""

cursor.executemany(insert_assets, symbols)


cursor.execute(users_table)
cursor.execute(assets_table)
cursor.execute(portfolio_table)

#resetting the db while testing
delete1 = """ DELETE FROM users"""
delete2 = """ DELETE FROM portfolio"""
cursor.execute(delete1)
cursor.execute(delete2)


connection.commit()
connection.close()