import sqlite3
import random
from datetime import datetime, timedelta

# Create database connection
conn = sqlite3.connect('data/sample.db')
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute('DROP TABLE IF EXISTS order_items')
cursor.execute('DROP TABLE IF EXISTS orders')
cursor.execute('DROP TABLE IF EXISTS products')
cursor.execute('DROP TABLE IF EXISTS customers')

# Create customers table
cursor.execute('''
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT,
    country TEXT,
    signup_date DATE
)
''')

# Create products table
cursor.execute('''
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER
)
''')

# Create orders table
cursor.execute('''
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    total_amount REAL,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')

# Create order_items table
cursor.execute('''
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

# Sample data
cities = ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon', 'Gwangju', 'Ulsan']
countries = ['South Korea', 'USA', 'Japan', 'China', 'Canada']
categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys']
product_names = {
    'Electronics': ['Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Camera', 'Smart Watch'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Dress', 'Sweater'],
    'Books': ['Fiction Novel', 'Programming Book', 'Cookbook', 'Biography', 'Science Book', 'History Book'],
    'Home & Garden': ['Table Lamp', 'Garden Tools', 'Bed Sheets', 'Cooking Set', 'Plant Pot', 'Wall Clock'],
    'Sports': ['Basketball', 'Tennis Racket', 'Yoga Mat', 'Dumbbells', 'Running Shoes', 'Bicycle'],
    'Toys': ['Action Figure', 'Board Game', 'Puzzle', 'Doll', 'Building Blocks', 'RC Car']
}
statuses = ['Completed', 'Processing', 'Shipped', 'Cancelled']

# Insert customers
customers = []
for i in range(1, 101):
    name = f"Customer {i}"
    email = f"customer{i}@email.com"
    city = random.choice(cities)
    country = random.choice(countries)
    signup_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    customers.append((i, name, email, city, country, signup_date))

cursor.executemany('INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)', customers)

# Insert products
products = []
product_id = 1
for category in categories:
    for product_name in product_names[category]:
        price = round(random.uniform(10, 500), 2)
        stock_quantity = random.randint(0, 100)
        products.append((product_id, product_name, category, price, stock_quantity))
        product_id += 1

cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)', products)

# Insert orders and order items
order_id = 1
order_item_id = 1

for customer_id in range(1, 101):
    num_orders = random.randint(0, 5)

    for _ in range(num_orders):
        order_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
        status = random.choice(statuses)

        # Create order items first to calculate total
        num_items = random.randint(1, 5)
        order_items = []
        total_amount = 0

        for _ in range(num_items):
            product = random.choice(products)
            product_id_selected = product[0]
            price = product[3]
            quantity = random.randint(1, 3)
            item_total = price * quantity
            total_amount += item_total

            order_items.append((order_item_id, order_id, product_id_selected, quantity, price))
            order_item_id += 1

        # Insert order
        cursor.execute('INSERT INTO orders VALUES (?, ?, ?, ?, ?)',
                       (order_id, customer_id, order_date, round(total_amount, 2), status))

        # Insert order items
        cursor.executemany('INSERT INTO order_items VALUES (?, ?, ?, ?, ?)', order_items)

        order_id += 1

# Commit and close
conn.commit()

# Print statistics
cursor.execute('SELECT COUNT(*) FROM customers')
print(f"Created {cursor.fetchone()[0]} customers")

cursor.execute('SELECT COUNT(*) FROM products')
print(f"Created {cursor.fetchone()[0]} products")

cursor.execute('SELECT COUNT(*) FROM orders')
print(f"Created {cursor.fetchone()[0]} orders")

cursor.execute('SELECT COUNT(*) FROM order_items')
print(f"Created {cursor.fetchone()[0]} order items")

conn.close()
print("\nSample database created successfully at data/sample.db")
