from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'maxika13572461'  # Add a secret key

# Use persistent storage path on Render, fallback to local path
if os.environ.get('RENDER'):
    DATABASE = '/opt/render/project/src/data/store.db'
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    DATABASE = os.path.join(APP_ROOT, 'store.db')

TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

#so, for the backend I used our lectures about the Flask as a reference. I also used try-except-finally, so the code style should be almost the same. 

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        brands = conn.execute('SELECT DISTINCT brand_name FROM Product ORDER BY brand_name').fetchall()
        conn.close()
        return render_template(os.path.join(TEMPLATE_FOLDER, 'index.html'), brands=brands)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    #except Exception  as e:
    #    print(f"Error: {e}")
    #    return jsonify({"Sorry, there is a server problem :("}) #I also did not know about it before but we need jsonify to convert data into json format for my website.
    #finally:
    #    if conn:
    #        conn.close()



@app.route('/search_brand', methods=['POST'])
def search_brand():
    try:
        brand =  request.form.get('brand')
        if not brand:
            return redirect(url_for('index')) #I know nothing about websites, so it was also new for me. It will redirect the user to the main page if the brand is empty.
        conn = get_db_connection()
        if not conn:
            return jsonify({"Sorry, there is a server problem :("})
        results = conn.execute('''
            SELECT
                p.brand_name AS Brand,
                p.model AS Model,
                pa.attribute_name AS AttributeName,
                pa.attribute_value AS AttributeValue,
                po.quantity AS Quantity,
                po.wholesale_price AS WholesalePrice,
                po.sale_price AS SalePrice,
                '-' AS NewPrice,
                '-' AS ChangeDate,
                MAX(pc.code_id) AS PromoCode
            FROM 
                Product p
            JOIN 
                ProductOption po ON p.product_id = po.product_PO_id
            LEFT JOIN 
                ProductAttribute pa ON po.barcode_id = pa.barcode_PA_id
            LEFT JOIN
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            LEFT JOIN 
                Sale s ON si.sale_SI_id = s.sale_id
            LEFT JOIN 
                PromoCode pc ON s.code_S_id =pc.code_id
            WHERE p.brand_name = ?
            GROUP BY 
                p.brand_name, p.model, pa.attribute_name, pa.attribute_value, po.quantity, 
                po.wholesale_price, po.sale_price
            ORDER BY 
                p.brand_name, p.model
        ''', (brand,)).fetchall()
        return  render_template(os.path.join(TEMPLATE_FOLDER, 'search_results.html'), results=results, brand=brand)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@app.route('/api/top_products')
def top_products():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"Sorry, there  is a server problem :("})
        products = conn.execute('''
            SELECT 
                p.brand_name AS Brand,
                p.model AS Model,
                SUM(si.quantity_sold) AS TotalQuantitySold
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id= po.barcode_id
            JOIN 
                Product p ON po.product_PO_id = p.product_id
            GROUP BY 
                p.product_id, p.brand_name, p.model
            ORDER BY 
                TotalQuantitySold DESC
            LIMIT 5
        ''').fetchall()
        profit = conn.execute('''
            SELECT 
                SUM((po.sale_price - po.wholesale_price) * si.quantity_sold) AS profit
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()
        return jsonify({
            'products': [dict(row) for row in products],
            'profit': profit['profit'] / 100 
        })
        #if I am not miskaten, sqlite does not have a DECIMAL datatype, so I decided to store everything related to money in cents instead of euros and then divide by 100 for display.
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@app.route('/api/top_categories')
def top_categories():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"Sorry, there is a server problem :("})
        categories = conn.execute('''
            SELECT 
                pc.category_name AS Category,
                COUNT(DISTINCT p.product_id) AS NumberOfProducts,
                SUM(si.quantity_sold) AS TotalQuantitySold
            FROM 
                ProductCategory pc
            JOIN 
                Product p ON pc.category_id = p.category_P_id
            JOIN 
                ProductOption po ON p.product_id = po.product_PO_id
            JOIN 
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY 
                pc.category_id,pc.category_name
            ORDER BY 
                TotalQuantitySold DESC
            LIMIT 5
        ''').fetchall()
        revenue = conn.execute('''
            SELECT 
                SUM(po.sale_price * si.quantity_sold) AS revenue
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()
        return jsonify({
            'categories': [dict(row) for row in categories],
            'revenue': revenue['revenue'] / 100  #same logic
        })
    except Exception  as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@app.route('/api/product_details')
def product_details():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"Sorry, there is a server problem :("})
        products= conn.execute('''
            SELECT 
                p.brand_name AS Brand,
                p.model AS Model,
                po.sale_price AS SalePrice,
                SUM(si.quantity_sold) AS TotalQuantitySold,
                ((po.sale_price - po.wholesale_price) * 100.0 / po.sale_price) AS MarginPercentage,
                s.supplier_name AS SupplierName,
                s.phone_number AS Phone,
                s.address AS Address
            FROM 
                SaleItem si
            JOIN 
                ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN 
                Product p ON po.product_PO_id = p.product_id
            JOIN 
                ProductSupplier ps ON p.product_id = ps.product_PS_id
            JOIN 
                Supplier s ON ps.supplier_PS_id = s.supplier_id
            GROUP BY 
                p.product_id
            ORDER BY 
                TotalQuantitySold DESC
        ''').fetchall()
        return jsonify([dict(row) for row in products]) 
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@app.route('/api/category_details')
def category_details():
    try:
        conn =  get_db_connection()
        if not conn:
            return jsonify({"Sorry, there is  a server problem :("})
        categories = conn.execute('''
            SELECT 
                pc.category_name AS Category,
                COUNT(DISTINCT p.product_id) AS NumberOfProducts,
                SUM(si.quantity_sold) AS TotalQuantitySold,
                AVG(po.sale_price) AS AverageProductPrice,
                MAX(po.sale_price) AS MaximumProductPrice,
                SUM(si.price_sold_without_vat) AS TotalRevenue
            FROM 
                ProductCategory pc
            JOIN 
                Product p ON pc.category_id = p.category_P_id
            JOIN 
                ProductOption po ON p.product_id = po.product_PO_id
            JOIN 
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY 
                pc.category_id, pc.category_name
            ORDER BY 
                TotalQuantitySold DESC
        ''').fetchall()
        return jsonify([dict(row) for row in categories])
    except Exception as e:
        print(f"Error: {e}")
        return  jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



@app.route('/api/chart-filters')
def get_chart_filters():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"Sorry,  there is a server problem :("})
        categories = conn.execute('''
            SELECT category_id, category_name 
            FROM ProductCategory 
            ORDER BY category_name
        ''').fetchall()
        return jsonify({
            'categories': [dict(row) for row in categories]
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if  conn:
            conn.close()




@app.route('/api/sales-data', methods=['POST'])
def get_sales_data():
    try:
        category_id= request.form.get('category_id')
        if not category_id:
            return jsonify({"Category is required"})
        conn = get_db_connection()
        if not conn:
            return jsonify({"Sorry, there is a server problem :("})
        results = conn.execute('''
            SELECT 
                s.sale_date AS SaleDate,
                SUM(si.quantity_sold) AS TotalQuantity,
                SUM(si.price_sold_without_vat) AS TotalSales
            FROM 
                SaleItem si
            JOIN Sale s ON si.sale_SI_id= s.sale_id
            JOIN ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN Product p ON po.product_PO_id = p.product_id
            JOIN ProductCategory pc ON p.category_P_id = pc.category_id

            WHERE 
                pc.category_id = ?
            GROUP BY 
                s.sale_date
            ORDER BY 
                s.sale_date
        ''', (category_id,)).fetchall()
        return jsonify([{
            'date': row['SaleDate'],
            'quantity': row['TotalQuantity'],
            'sales': row['TotalSales']
        } for row  in results])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()



if __name__ == '__main__':
    app.run(debug=False) 