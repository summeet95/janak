# AIC Inventory Management System - Local Database Version

A modern, full-featured inventory management application built with Flask and MongoDB. This application includes authentication, role-based access, and comprehensive business management features.

## Features

✅ **User Authentication** - Secure login and registration system with password hashing
✅ **Inventory Management** - Track items, quantities, and reorder levels
✅ **Supplier Management** - Manage suppliers and their transactions
✅ **Customer Management** - Track customers and their purchases
✅ **Purchase Orders** - Create and manage supplier purchase orders
✅ **Sales Orders** - Manage customer sales transactions
✅ **Receipts** - Track customer payment receipts
✅ **Payments** - Record payments to suppliers
✅ **Dashboard** - Real-time business metrics and KPIs
✅ **Database** - All data stored locally in MongoDB

## Technology Stack

- **Backend**: Python + Flask
- **Database**: MongoDB
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Authentication**: JWT (JSON Web Tokens)

## Prerequisites

Before you begin, ensure you have installed:

1. **Python** (3.8 or higher)
   - Download from: https://www.python.org/downloads/

2. **MongoDB Community Edition**
   - Download from: https://www.mongodb.com/try/download/community
   - For Windows: Download the MSI installer and follow the installation wizard
   - After installation, MongoDB will run as a service on `localhost:27017`

3. **Git** (optional, for cloning the repository)
   - Download from: https://git-scm.com/download/win

## Installation & Setup

### Step 1: Navigate to Project Directory

```bash
cd c:\Users\summe\Music\sulav\janak\Inventory_App_Local
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify MongoDB Installation

```bash
# Check if MongoDB service is running
# On Windows, open Services (services.msc) and look for "MongoDB Server"
# Or open command prompt and try:
mongo --version
```

If MongoDB is not running, start it:

**On Windows:**
- Press `Win + R`, type `services.msc`
- Find "MongoDB Server" and click "Start"
- Or run: `net start MongoDB` (as Administrator)

### Step 5: Update Configuration (if needed)

Edit `.env` file with your settings:

```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
MONGO_URI=mongodb://localhost:27017/inventory_app
JWT_SECRET=your_jwt_secret_here
```

## Running the Application

### Start the Flask Server

```bash
# Make sure virtual environment is activated
python run.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## First-Time Setup

1. **Create an Account**
   - Click "Register" on the login page
   - Enter username, email, and password
   - Click "Register" button

2. **Login**
   - Enter your credentials
   - Click "Login" button

3. **Start Using the App**
   - Go to Dashboard to see overview
   - Add inventory items
   - Create suppliers and customers
   - Generate purchase and sales orders

## Database Schema

The application uses the following MongoDB collections:

### Users
- `username` - Unique username
- `email` - User email
- `password` - Hashed password
- `created_at` - Account creation date
- `active` - Account status

### Inventory Items
- `item_id` - Unique item identifier
- `item_name` - Name of the item
- `item_type` - Type/category
- `qty_purchased` - Quantity purchased
- `qty_sold` - Quantity sold
- `remaining_qty` - Current stock
- `reorder_level` - Reorder threshold

### Suppliers
- `supplier_id` - Unique supplier ID
- `supplier_name` - Name
- `supplier_contact` - Contact number
- `supplier_email` - Email address
- `city` - City location
- `state` - State location
- `balance_payable` - Amount owed

### Customers
- `customer_id` - Unique customer ID
- `customer_name` - Name
- `customer_contact` - Contact number
- `customer_email` - Email address
- `balance_receivable` - Amount to be received

### Purchase Orders
- `po_id` - Purchase Order ID
- `supplier_id` - Supplier reference
- `item_id` - Item reference
- `quantity` - Order quantity
- `unit_price` - Price per unit
- `total_amount` - Total price
- `pmt_status` - Payment status
- `shipping_status` - Shipping status

### Sales Orders
- `so_id` - Sales Order ID
- `customer_id` - Customer reference
- `item_id` - Item reference
- `quantity` - Order quantity
- `unit_price` - Price per unit
- `total_amount` - Total price
- `so_status` - Order status

### Receipts
- `trx_id` - Transaction ID
- `customer_id` - Customer reference
- `amount_received` - Payment amount
- `pmt_mode` - Payment method
- `so_id` - Related sales order

### Payments
- `payment_id` - Payment ID
- `supplier_id` - Supplier reference
- `amount_paid` - Payment amount
- `pmt_mode` - Payment method
- `po_id` - Related purchase order

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### Inventory
- `GET /api/inventory` - Get all items
- `POST /api/inventory` - Create new item
- `PUT /api/inventory/<item_id>` - Update item
- `DELETE /api/inventory/<item_id>` - Delete item

### Suppliers
- `GET /api/suppliers` - Get all suppliers
- `POST /api/suppliers` - Create supplier
- `PUT /api/suppliers/<supplier_id>` - Update supplier
- `DELETE /api/suppliers/<supplier_id>` - Delete supplier

### Customers
- `GET /api/customers` - Get all customers
- `POST /api/customers` - Create customer
- `PUT /api/customers/<customer_id>` - Update customer
- `DELETE /api/customers/<customer_id>` - Delete customer

### Purchase Orders
- `GET /api/purchases` - Get all POs
- `POST /api/purchases` - Create PO
- `PUT /api/purchases/<po_id>` - Update PO
- `DELETE /api/purchases/<po_id>` - Delete PO

### Sales Orders
- `GET /api/sales` - Get all SOs
- `POST /api/sales` - Create SO
- `PUT /api/sales/<so_id>` - Update SO
- `DELETE /api/sales/<so_id>` - Delete SO

### Receipts
- `GET /api/receipts` - Get all receipts
- `POST /api/receipts` - Create receipt
- `PUT /api/receipts/<trx_id>` - Update receipt
- `DELETE /api/receipts/<trx_id>` - Delete receipt

### Payments
- `GET /api/payments` - Get all payments
- `POST /api/payments` - Create payment
- `PUT /api/payments/<payment_id>` - Update payment
- `DELETE /api/payments/<payment_id>` - Delete payment

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## Troubleshooting

### MongoDB Connection Error
```
Error: Unable to connect to MongoDB
```
**Solution:**
1. Check if MongoDB is installed: `mongo --version`
2. Start MongoDB service (Windows): Open Services and start "MongoDB Server"
3. Verify connection: `mongo` should connect to local instance

### Port Already in Use
```
Address already in use
```
**Solution:**
- Change port in `run.py` (default: 5000)
- Or kill the process: `lsof -ti:5000 | xargs kill -9` (Mac/Linux)

### Cannot Find Module
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:**
1. Activate virtual environment: `venv\Scripts\activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### CORS Issues
```
Access to XMLHttpRequest blocked by CORS
```
**Solution:**
- This shouldn't occur if Flask-CORS is properly installed
- Run: `pip install Flask-CORS==4.0.0`

## Project Structure

```
Inventory_App_Local/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── auth.py               # Authentication logic
│   ├── models.py             # Database schemas
│   ├── routes.py             # API endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Main stylesheet
│   │   └── js/
│   │       └── app.js        # Frontend logic
│   └── templates/
│       ├── login.html        # Login page
│       └── dashboard.html    # Dashboard page
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # This file
```

## Important Security Notes

⚠️ **Production Deployment:**
- Change `SECRET_KEY` and `JWT_SECRET` in `.env`
- Set `FLASK_DEBUG=False` in production
- Use environment-specific secrets management
- Enable HTTPS/SSL
- Use a production WSGI server (Gunicorn, uWSGI)
- Database should be backed up regularly

## Default Configuration

- **Host**: localhost
- **Port**: 5000
- **Database**: inventory_app
- **Database Location**: localhost:27017

## Support & Documentation

For more information:
- Flask Documentation: https://flask.palletsprojects.com/
- MongoDB Documentation: https://docs.mongodb.com/
- PyMongo Documentation: https://pymongo.readthedocs.io/

## License

This project is provided as-is for educational and business purposes.

## Notes

- All user data is isolated per user account
- Changes are saved immediately to MongoDB
- Supports multiple concurrent users
- Can be easily extended with additional features

---

**Created**: May 2026
**Version**: 1.0
