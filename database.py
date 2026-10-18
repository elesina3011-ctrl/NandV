import sqlite3
DATABASE = "database.db"

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    connection.close()
    seed_initial_data()

def add_category(name):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    connection.commit()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    category_id = cursor.fetchone()[0]
    connection.close()
    return category_id

def add_menu_item(title, category_name, price, description="", image="default.jpg"):
    category_id = add_category(category_name)
    connection = get_connection()
    connection.execute("""
        INSERT INTO menu_items (title, price, description, image, category_id)
        VALUES (?, ?, ?, ?, ?)
    """, (title, price, description, image, category_id))
    connection.commit()
    connection.close()

def seed_initial_data():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    count = cursor.fetchone()[0]
    connection.close()
    if count == 0:
        initial_items = [
            {"title": "Карамельний Лате", "category": "Напої", "price": 95,
             "description": "Ніжний еспресо зі збитим шовковистим молоком.", "image": "latte.jpg"},
            {"title": "Матча Лате", "category": "Напої", "price": 105,
             "description": "Традиційний японський зелений чай матча.", "image": "matcha.jpg"},
            {"title": "Мигдалевий Круасан", "category": "Випічка", "price": 65,
             "description": "Хрусткий французький круасан із мигдалевим кремом.", "image": "croissant.jpg"},
            {"title": "Чізкейк Нью-Йорк", "category": "Десерти", "price": 110,
             "description": "Класичний сирний десерт на пісочній основі.", "image": "cheesecake.jpg"}
        ]
        for item in initial_items:
            add_menu_item(item["title"], item["category"], item["price"], item["description"], item["image"])

def get_all_items():
    connection = get_connection()
    items = connection.execute("""
        SELECT m.id, m.title, c.name as category_name, m.price, m.description, m.image
        FROM menu_items m
        LEFT JOIN categories c ON m.category_id = c.id
        ORDER BY m.id DESC
    """).fetchall()
    connection.close()
    return items

def get_item_by_id(item_id):
    connection = get_connection()
    item = connection.execute("""
        SELECT m.id, m.title, c.name as category_name, m.price, m.description, m.image
        FROM menu_items m
        LEFT JOIN categories c ON m.category_id = c.id
        WHERE m.id = ?
    """, (item_id,)).fetchone()
    connection.close()
    return item

def search_items(keyword):
    connection = get_connection()
    items = connection.execute("""
        SELECT m.id, m.title, c.name as category_name, m.price, m.description, m.image
        FROM menu_items m
        LEFT JOIN categories c ON m.category_id = c.id
        WHERE m.title LIKE ?
    """, (f"%{keyword}%",)).fetchall()
    connection.close()
    return items

def update_item(item_id, title, category_name, price, description):
    category_id = add_category(category_name)
    connection = get_connection()
    connection.execute("""
        UPDATE menu_items 
        SET title = ?, category_id = ?, price = ?, description = ?
        WHERE id = ?
    """, (title, category_id, price, description, item_id))
    connection.commit()
    connection.close()

def delete_item(item_id):
    connection = get_connection()
    connection.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    connection.commit()
    connection.close()

def add_search_history(query):
    if query:
        connection = get_connection()
        connection.execute("INSERT INTO search_history (query) VALUES (?)", (query,))
        connection.commit()
        connection.close()

def get_search_history():
    connection = get_connection()
    history = connection.execute("SELECT * FROM search_history ORDER BY id DESC LIMIT 10").fetchall()
    connection.close()
    return history