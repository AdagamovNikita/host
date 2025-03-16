import sqlite3
from datetime import datetime, timedelta
import random
import time
random.seed(time.time()) #I need it to set different colors for items in my database.

#these are all the tables I created while looking at my database schema from phase 1.
def init_db():
    try:
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS ProductCategory (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Product (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                category_P_id INTEGER,
                brand_name TEXT,
                FOREIGN KEY (category_P_id) REFERENCES ProductCategory(category_id)
            );
            CREATE TABLE IF NOT EXISTS ProductOption (
                product_PO_id INTEGER,
                barcode_id TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL,
                wholesale_price INTEGER NOT NULL, 
                sale_price INTEGER NOT NULL,
                FOREIGN KEY (product_PO_id) REFERENCES Product(product_id)
            );
            CREATE TABLE IF NOT EXISTS ProductAttribute (
                barcode_PA_id TEXT,
                attribute_id INTEGER,
                attribute_name TEXT NOT NULL,
                attribute_value TEXT NOT NULL,
                PRIMARY KEY (barcode_PA_id, attribute_id),
                FOREIGN KEY (barcode_PA_id) REFERENCES ProductOption(barcode_id)
            );
            CREATE TABLE IF NOT EXISTS PriceHistory (
                barcode_PH_id TEXT,
                price_id INTEGER PRIMARY KEY AUTOINCREMENT,
                old_price INTEGER NOT NULL,
                new_price INTEGER NOT NULL,
                change_date DATETIME NOT NULL,
                FOREIGN KEY (barcode_PH_id) REFERENCES ProductOption(barcode_id)
            );
            CREATE TABLE IF NOT EXISTS Supplier (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL,
                phone_number TEXT,
                address TEXT
            );
            CREATE TABLE IF NOT EXISTS ProductSupplier (
                product_PS_id INTEGER,
                supplier_PS_id INTEGER,
                PRIMARY KEY (product_PS_id, supplier_PS_id),
                FOREIGN KEY (product_PS_id) REFERENCES Product(product_id),
                FOREIGN KEY (supplier_PS_id) REFERENCES Supplier(supplier_id)
            );
            CREATE TABLE IF NOT EXISTS PromoCode (
                code_id TEXT PRIMARY KEY,
                discount_percentage INTEGER NOT NULL,
                valid_from DATE NOT NULL,
                valid_to DATE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS Sale (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date DATETIME NOT NULL,
                source_name TEXT,
                code_S_id TEXT,
                tax_rate INTEGER,
                total_price_without_vat INTEGER NOT NULL,
                vat_paid INTEGER NOT NULL,
                total_price_with_vat INTEGER NOT NULL,
                FOREIGN KEY (code_S_id) REFERENCES PromoCode(code_id)
            );
            CREATE TABLE IF NOT EXISTS SaleItem (
                sale_SI_id INTEGER,
                sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode_SI_id TEXT NOT NULL,
                quantity_sold INTEGER NOT NULL,
                price_sold_without_vat INTEGER NOT NULL,
                FOREIGN KEY (sale_SI_id) REFERENCES Sale(sale_id),
                FOREIGN KEY (barcode_SI_id) REFERENCES ProductOption(barcode_id)
            );
        ''')


#now I am just inserting some artificial data to store something in my DB.
        categories = [
            ('Smartphones',),
            ('Laptops',),
            ('Tablets',),
            ('Smartwatches',),
            ('Accessories',)
        ]
        cursor.executemany('INSERT INTO ProductCategory (category_name) VALUES (?)', categories)



        suppliers = [
            ('TechGlobal Inc.', '+1-555-0123', '123 Tech Street, Silicon Valley, CA'),
            ('Global Electronics', '+1-555-0124', '456 Electronics Ave, New York, NY'),
            ('Digital Solutions', '+1-555-0125', '789 Digital Road, Seattle, WA'),
            ('Smart Devices Co.', '+1-555-0126', '321 Smart Blvd, Austin, TX'),
            ('Future Tech Ltd.', '+1-555-0127', '654 Future Lane, Boston, MA')
        ]
        cursor.executemany('INSERT INTO Supplier (supplier_name, phone_number, address) VALUES (?, ?, ?)', suppliers)



        promo_codes = [
            ('WELCOME10', 10, '2024-01-01', '2024-12-31')
        ]
        cursor.executemany('INSERT INTO PromoCode (code_id, discount_percentage, valid_from, valid_to) VALUES (?, ?, ?, ?)', promo_codes)



        products_data = [
            ('iPhone 15 Pro', 1, 'Apple', 'APP15P-256', 50, 80000, 99900),
            ('iPhone 15', 1, 'Apple', 'APP15-128', 75, 60000, 79900),
            ('MacBook Pro 16', 2, 'Apple', 'APP-MBP16', 30, 150000, 199900),
            ('iPad Pro 12.9', 3, 'Apple', 'APP-IPAD12', 40, 80000, 99900),
            ('Apple Watch Series 9', 4, 'Apple', 'APP-WATCH9', 60, 30000, 39900),
            ('Galaxy S24 Ultra', 1, 'Samsung', 'SAM-S24U', 45, 70000, 89900),
            ('Galaxy Book 4', 2, 'Samsung', 'SAM-BOOK4', 35, 120000, 149900),
            ('Galaxy Tab S9', 3, 'Samsung', 'SAM-TABS9', 50, 60000, 79900),
            ('Galaxy Watch 6', 4, 'Samsung', 'SAM-WATCH6', 55, 25000, 29900),
            ('Galaxy Buds Pro', 5, 'Samsung', 'SAM-BUDSP', 80, 15000, 19900),
            ('Xperia 1 V', 1, 'Sony', 'SON-XP1V', 40, 75000, 94900),
            ('VAIO SX14', 2, 'Sony', 'SON-VAIO14', 25, 130000, 169900),
            ('Xperia Tablet Z4', 3, 'Sony', 'SON-TABZ4', 30, 70000, 89900),
            ('WH-1000XM5', 5, 'Sony', 'SON-WH1000', 65, 20000, 29900),
            ('WF-1000XM5', 5, 'Sony', 'SON-WF1000', 70, 15000, 19900),
            ('XPS 15', 2, 'Dell', 'DEL-XPS15', 40, 140000, 179900),
            ('Alienware m18', 2, 'Dell', 'DEL-ALIEN18', 25, 180000, 229900),
            ('Latitude 7440', 2, 'Dell', 'DEL-LAT7440', 35, 110000, 139900),
            ('Dell XPS 13', 2, 'Dell', 'DEL-XPS13', 45, 90000, 119900),
            ('Dell Inspiron 16', 2, 'Dell', 'DEL-INS16', 50, 70000, 89900),
            ('ThinkPad X1 Carbon', 2, 'Lenovo', 'LEN-X1C', 40, 120000, 149900),
            ('Yoga 9i', 2, 'Lenovo', 'LEN-YOGA9', 35, 100000, 129900),
            ('Tab P12 Pro', 3, 'Lenovo', 'LEN-TABP12', 45, 65000, 84900),
            ('ThinkPad X13', 2, 'Lenovo', 'LEN-X13', 55, 85000, 109900),
            ('IdeaPad 5', 2, 'Lenovo', 'LEN-IDEA5', 60, 60000, 79900)
        ]


#I also did not know about it before as well. lastrowid gives the ID of the last inserted row.
        colors = ['Black', 'White', 'Silver', 'Blue', 'Red', 'Green']
        for product in products_data:
            cursor.execute('''
                INSERT INTO Product (model, category_P_id, brand_name)
                VALUES (?, ?, ?)
            ''', (product[0], product[1], product[2]))
            product_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO ProductOption (product_PO_id, barcode_id, quantity, wholesale_price, sale_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_id, product[3], product[4], product[5], product[6]))
            random_color = random.choice(colors)
            cursor.execute('''
                INSERT INTO ProductAttribute (barcode_PA_id, attribute_id, attribute_name, attribute_value)
                VALUES (?, ?, ?, ?)
            ''', (product[3], 1, 'Color', random_color))
            cursor.execute('''
                INSERT INTO PriceHistory (barcode_PH_id, old_price, new_price, change_date)
                VALUES (?, ?, ?, datetime('now'))
            ''', (product[3], product[5], product[6]))
            cursor.execute(''' 
                INSERT INTO ProductSupplier (product_PS_id, supplier_PS_id)
                VALUES (?, ?)
            ''', (product_id, random.randint(1, 5)))



        sales = []
        current_date = datetime.now()
        start_date = current_date - timedelta(days=365)
        
        # Generate more varied sales data
        for i in range(500):  # Increased number of sales
            random_days = random.randint(0, 365)
            sale_date = start_date + timedelta(days=random_days)
            sale_source = random.choice(['Online', 'Store'])
            promo_code = random.choice(['WELCOME10', None])
            sale_tax_rate = 20
            
            # More realistic price ranges based on product categories
            total_price_without_vat = random.randint(15000, 200000)
            vat_paid = total_price_without_vat * sale_tax_rate // 100
            total_price_with_vat = total_price_without_vat + vat_paid
            sales.append((sale_date, sale_source, promo_code, sale_tax_rate, total_price_without_vat, vat_paid, total_price_with_vat))



        # Store product information in a more readable format
        # Each product has: (barcode, min_quantity, max_quantity, price in cents)
        sale_items_data = [
            # Smartphones
            ('APP15P-256', 1, 10, 99900),
            ('APP15-128', 1, 12, 79900),
            ('SAM-S24U', 1, 8, 89900),
            ('SON-XP1V', 1, 6, 94900),
            
            # Laptops
            ('APP-MBP16', 1, 5, 199900),
            ('DEL-XPS15', 1, 7, 179900),
            ('LEN-X1C', 1, 6, 149900),
            ('SAM-BOOK4', 1, 4, 149900),
            
            # Tablets
            ('APP-IPAD12', 1, 8, 99900),
            ('SAM-TABS9', 1, 10, 79900),
            ('LEN-TABP12', 1, 7, 84900),
            
            # Smartwatches
            ('APP-WATCH9', 1, 15, 39900),
            ('SAM-WATCH6', 1, 12, 29900),
            
            # Accessories
            ('SAM-BUDSP', 1, 20, 19900),
            ('SON-WH1000', 1, 18, 29900),
            ('SON-WF1000', 1, 25, 19900)
        ]

        # For each sale in our sales list
        for sale in sales:
            # First, add the main sale information to the database
            cursor.execute('''
                INSERT INTO Sale (sale_date, source_name, code_S_id, tax_rate,
                                total_price_without_vat, vat_paid, total_price_with_vat)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sale)
            
            # Get the ID of the sale we just created
            sale_id = cursor.lastrowid
            
            # Choose a random number of items (between 1 and 4) for this sale
            num_items = random.randint(1, 4)
            
            # Randomly select that many different products
            items_for_this_sale = random.sample(sale_items_data, num_items)
            
            # Add each selected item to the sale
            for item in items_for_this_sale:
                # Unpack the item information
                barcode = item[0]
                min_quantity = item[1]
                max_quantity = item[2]
                price = item[3]
                
                # Generate random quantity based on the min and max values
                quantity = random.randint(min_quantity, max_quantity)
                
                # Add this item to the SaleItem table
                cursor.execute('''
                    INSERT INTO SaleItem (sale_SI_id, barcode_SI_id, quantity_sold, price_sold_without_vat)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, barcode, quantity, price))

        # Save all changes to the database
        conn.commit()


        
    except sqlite3.Error as e:
        print(f"SQLite error happened: {e}")
    except Exception as e:
        print(f"An error happened: {e}")
    finally:
        if conn:
            conn.close()



if __name__ == '__main__':
    init_db()
