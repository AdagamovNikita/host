from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'maxika13572461'

# Use persistent storage path on Render, fallback to local path
if os.environ.get('RENDER'):
    DATA_DIR = '/opt/render/project/src/data'
    os.makedirs(DATA_DIR, exist_ok=True)
    DATABASE = os.path.join(DATA_DIR, 'store.db')
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    DATABASE = os.path.join(APP_ROOT, 'store.db')

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Database connection error: {str(e)}")
        raise

@app.route('/')
def index():
    conn = None
    try:
        conn = get_db_connection()
        if not os.path.exists(DATABASE):
            raise Exception(f"Database file not found at {DATABASE}")
        brands = conn.execute('SELECT DISTINCT brand_name FROM Product ORDER BY brand_name').fetchall()
        return render_template('index.html', brands=brands)
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/search_brand', methods=['POST'])
def search_brand():
    conn = None
    try:
        brand = request.form.get('brand')
        if not brand:
            return redirect(url_for('index'))
        
        conn = get_db_connection()
        results = conn.execute('''
            SELECT 
                p.brand_name,
                p.model,
                po.barcode_id,
                po.quantity,
                po.sale_price,
                s.supplier_name,
                s.phone_number,
                pc.category_name
            FROM Product p
            LEFT JOIN ProductOption po ON p.product_id = po.product_PO_id
            LEFT JOIN ProductSupplier ps ON p.product_id = ps.product_PS_id
            LEFT JOIN Supplier s ON ps.supplier_PS_id = s.supplier_id
            LEFT JOIN ProductCategory pc ON p.category_P_id = pc.category_id
            WHERE p.brand_name = ?
            ORDER BY p.model
        ''', (brand,)).fetchall()
        
        return render_template('search_results.html', results=results, brand=brand)
    except Exception as e:
        app.logger.error(f"Error in search_brand route: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/top_products')
def get_top_products():
    conn = None
    try:
        conn = get_db_connection()
        products = conn.execute('''
            SELECT 
                p.brand_name || ' ' || p.model as product_name,
                SUM(si.quantity_sold) as total_quantity,
                SUM(si.quantity_sold * si.price_sold_without_vat) as total_revenue,
                SUM(si.quantity_sold * (si.price_sold_without_vat - po.wholesale_price)) as profit
            FROM Product p
            JOIN ProductOption po ON p.product_id = po.product_PO_id
            JOIN SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY p.product_id
            ORDER BY total_quantity DESC
            LIMIT 5
        ''').fetchall()

        total_profit = conn.execute('''
            SELECT SUM(si.quantity_sold * (si.price_sold_without_vat - po.wholesale_price)) as total_profit
            FROM SaleItem si
            JOIN ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()

        return jsonify({
            'products': [dict(row) for row in products],
            'total_profit': total_profit['total_profit'] if total_profit['total_profit'] else 0
        })
    except Exception as e:
        app.logger.error(f"Error in top_products route: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/top_categories')
def get_top_categories():
    conn = None
    try:
        conn = get_db_connection()
        categories = conn.execute('''
            SELECT 
                pc.category_name,
                COUNT(DISTINCT si.sale_SI_id) as total_sales,
                SUM(si.quantity_sold) as total_quantity,
                SUM(si.quantity_sold * si.price_sold_without_vat) as revenue
            FROM ProductCategory pc
            JOIN Product p ON p.category_P_id = pc.category_id
            JOIN ProductOption po ON p.product_id = po.product_PO_id
            JOIN SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY pc.category_id
            ORDER BY total_quantity DESC
            LIMIT 5
        ''').fetchall()

        total_revenue = conn.execute('''
            SELECT SUM(quantity_sold * price_sold_without_vat) as total_revenue
            FROM SaleItem
        ''').fetchone()

        return jsonify({
            'categories': [dict(row) for row in categories],
            'total_revenue': total_revenue['total_revenue'] if total_revenue['total_revenue'] else 0
        })
    except Exception as e:
        app.logger.error(f"Error in top_categories route: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/product_details')
def get_product_details():
    conn = None
    try:
        conn = get_db_connection()
        products = conn.execute('''
            SELECT 
                p.brand_name,
                p.model,
                pc.category_name,
                po.quantity as stock,
                po.sale_price,
                s.supplier_name,
                s.phone_number,
                COUNT(DISTINCT si.sale_SI_id) as total_sales,
                SUM(si.quantity_sold) as total_quantity_sold
            FROM Product p
            LEFT JOIN ProductCategory pc ON p.category_P_id = pc.category_id
            LEFT JOIN ProductOption po ON p.product_id = po.product_PO_id
            LEFT JOIN ProductSupplier ps ON p.product_id = ps.product_PS_id
            LEFT JOIN Supplier s ON ps.supplier_PS_id = s.supplier_id
            LEFT JOIN SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY p.product_id
            ORDER BY total_quantity_sold DESC
        ''').fetchall()
        return jsonify([dict(row) for row in products])
    except Exception as e:
        app.logger.error(f"Error in product_details route: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=False)