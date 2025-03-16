# Electronics Store Dashboard

A simple web application that displays an interactive dashboard for an electronics store. The dashboard shows top-selling products, categories, and allows searching by brand.

## Features

- Display top selling products with total quantity sold and profit
- Display top selling categories with number of products and revenue
- Search products by brand
- Detailed product and category information
- SQLite database for data storage

## Tech Stack

- Backend: Python + Flask
- Frontend: HTML + CSS + JavaScript
- Database: SQLite3

## Project Structure

```
electronics-store/
├── app.py              # Flask application
├── init_db.py         # Database initialization script
├── requirements.txt   # Python dependencies
├── templates/        # HTML templates
│   ├── index.html
│   └── search_results.html
└── store.db          # SQLite database (generated)
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repository-url>
cd electronics-store
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the application:
```bash
python app.py
```

5. Open your web browser and go to:
```
http://localhost:5000
```

## Database Schema

The application uses several interconnected tables:
- Product
- ProductCategory
- ProductOption
- ProductAttribute
- PriceHistory
- Supplier
- ProductSupplier
- PromoCode
- Sale
- SaleItem

## Contributing

Feel free to submit issues and enhancement requests! 