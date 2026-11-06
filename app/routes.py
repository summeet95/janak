from flask import Blueprint, request, jsonify, render_template
from app import mongo
from app.auth import token_required, register_user, login_user
from datetime import datetime
import uuid
import math

# Blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')
suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')
customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')
purchases_bp = Blueprint('purchases', __name__, url_prefix='/api/purchases')
sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')
receipts_bp = Blueprint('receipts', __name__, url_prefix='/api/receipts')
payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


def order_numbers(data, quantity_default=None, price_default=None):
    try:
        quantity = float(data.get('quantity', quantity_default))
        unit_price = float(data.get('unit_price', price_default))
    except (TypeError, ValueError):
        raise ValueError('Quantity and unit price must be numbers')
    if not math.isfinite(quantity) or not math.isfinite(unit_price) or quantity <= 0 or unit_price < 0:
        raise ValueError('Quantity must be positive and unit price must be non-negative')
    return quantity, unit_price

# ==================== AUTH ROUTES ====================
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    result = register_user(data['username'], data['email'], data['password'])
    status_code = 201 if result['success'] else 400
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
    result = login_user(data['username'], data['password'])
    status_code = 200 if result['success'] else 401
    return jsonify(result), status_code

# ==================== INVENTORY ROUTES ====================
@inventory_bp.route('', methods=['GET'])
@token_required
def get_inventory():
    """Get all inventory items for user"""
    user_id = request.current_user['user_id']
    items = list(mongo.db.inventory_items.find({'user_id': user_id}))
    
    # Convert ObjectId to string
    for item in items:
        item['_id'] = str(item['_id'])
    
    return jsonify({'success': True, 'items': items}), 200

@inventory_bp.route('', methods=['POST'])
@token_required
def create_inventory_item():
    """Create new inventory item"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    required_fields = ['item_name', 'item_type', 'item_category']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Auto-categorize locally if needed
    if 'item_category' not in data or not data['item_category']:
        data['item_category'] = 'General'
        data['item_type'] = data.get('item_type', 'Product')
        data['item_subcategory'] = data.get('item_subcategory', '')
    
    item = {
        'item_id': str(uuid.uuid4())[:8],
        'item_name': data.get('item_name'),
        'item_type': data.get('item_type'),
        'item_category': data.get('item_category'),
        'item_subcategory': data.get('item_subcategory', ''),
        'qty_purchased': float(data.get('qty_purchased', 0)),
        'qty_sold': float(data.get('qty_sold', 0)),
        'remaining_qty': float(data.get('remaining_qty',
                                        float(data.get('qty_purchased', 0)) - float(data.get('qty_sold', 0)))),
        'reorder_level': float(data.get('reorder_level', 0)),
        'reorder_required': False,
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Local validation
    if item['qty_purchased'] < 0 or item['qty_sold'] < 0 or item['remaining_qty'] < 0 or item['reorder_level'] < 0:
        return jsonify({'success': False, 'message': 'Numeric values must be non-negative'}), 400
    item['reorder_required'] = item['remaining_qty'] <= item['reorder_level']
    
    result = mongo.db.inventory_items.insert_one(item)
    item['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'message': 'Item created', 'item': item}), 201

@inventory_bp.route('/<item_id>', methods=['PUT'])
@token_required
def update_inventory_item(item_id):
    """Update inventory item"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    item = mongo.db.inventory_items.find_one({'item_id': item_id, 'user_id': user_id})
    if not item:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    update_data = {
        'item_name': data.get('item_name', item.get('item_name')),
        'item_type': data.get('item_type', item.get('item_type')),
        'item_category': data.get('item_category', item.get('item_category')),
        'item_subcategory': data.get('item_subcategory', item.get('item_subcategory')),
        'qty_purchased': float(data.get('qty_purchased', item.get('qty_purchased', 0))),
        'qty_sold': float(data.get('qty_sold', item.get('qty_sold', 0))),
        'remaining_qty': float(data.get('remaining_qty', item.get('remaining_qty', 0))),
        'reorder_level': float(data.get('reorder_level', item.get('reorder_level', 0))),
        'reorder_required': float(data.get('remaining_qty', item.get('remaining_qty', 0))) <= float(data.get('reorder_level', item.get('reorder_level', 0))),
        'updated_at': datetime.utcnow()
    }
    
    # Local validation
    if update_data['qty_purchased'] < 0 or update_data['qty_sold'] < 0 or update_data['remaining_qty'] < 0 or update_data['reorder_level'] < 0:
        return jsonify({'success': False, 'message': 'Numeric values must be non-negative'}), 400
    
    mongo.db.inventory_items.update_one({'item_id': item_id, 'user_id': user_id}, {'$set': update_data})
    return jsonify({'success': True, 'message': 'Item updated'}), 200

@inventory_bp.route('/<item_id>', methods=['DELETE'])
@token_required
def delete_inventory_item(item_id):
    """Delete inventory item"""
    user_id = request.current_user['user_id']
    if mongo.db.has_tracked_orders(user_id, item_id):
        return jsonify({'success': False, 'message': 'Delete related orders before deleting this item'}), 400
    result = mongo.db.inventory_items.delete_one({'item_id': item_id, 'user_id': user_id})
    
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Item not found'}), 404
    
    return jsonify({'success': True, 'message': 'Item deleted'}), 200

# ==================== INVENTORY MANAGEMENT ROUTES ====================
@inventory_bp.route('/manage', methods=['GET'])
@token_required
def manage_inventory():
    """Render inventory management page"""
    return render_template('inventory.html')

@inventory_bp.route('/<item_id>', methods=['POST'])
@token_required
def delete_inventory_item_form(item_id):
    """Delete inventory item via form"""
    user_id = request.current_user['user_id']
    if mongo.db.has_tracked_orders(user_id, item_id):
        return jsonify({'success': False, 'message': 'Delete related orders before deleting this item'}), 400
    result = mongo.db.inventory_items.delete_one({'item_id': item_id, 'user_id': user_id})

    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Item not found'}), 404

    return jsonify({'success': True, 'message': 'Item deleted'}), 200

# ==================== SUPPLIERS ROUTES ====================
@suppliers_bp.route('', methods=['GET'])
@token_required
def get_suppliers():
    """Get all suppliers for user"""
    user_id = request.current_user['user_id']
    suppliers = list(mongo.db.suppliers.find({'user_id': user_id}))
    
    for supplier in suppliers:
        supplier['_id'] = str(supplier['_id'])
    
    return jsonify({'success': True, 'suppliers': suppliers}), 200

@suppliers_bp.route('', methods=['POST'])
@token_required
def create_supplier():
    """Create new supplier"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    required_fields = ['supplier_name', 'supplier_contact']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    supplier = {
        'supplier_id': str(uuid.uuid4())[:8],
        'supplier_name': data.get('supplier_name'),
        'supplier_contact': data.get('supplier_contact'),
        'supplier_email': data.get('supplier_email', ''),
        'state': data.get('state', ''),
        'city': data.get('city', ''),
        'supplier_address': data.get('supplier_address', ''),
        'total_purchases': float(data.get('total_purchases', 0)),
        'total_payments': float(data.get('total_payments', 0)),
        'balance_payable': float(data.get('balance_payable', 0)),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = mongo.db.suppliers.insert_one(supplier)
    supplier['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'message': 'Supplier created', 'supplier': supplier}), 201

@suppliers_bp.route('/<supplier_id>', methods=['PUT'])
@token_required
def update_supplier(supplier_id):
    """Update supplier"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    supplier = mongo.db.suppliers.find_one({'supplier_id': supplier_id, 'user_id': user_id})
    if not supplier:
        return jsonify({'success': False, 'message': 'Supplier not found'}), 404
    
    update_data = {
        'supplier_name': data.get('supplier_name', supplier.get('supplier_name')),
        'supplier_contact': data.get('supplier_contact', supplier.get('supplier_contact')),
        'supplier_email': data.get('supplier_email', supplier.get('supplier_email')),
        'state': data.get('state', supplier.get('state')),
        'city': data.get('city', supplier.get('city')),
        'supplier_address': data.get('supplier_address', supplier.get('supplier_address')),
        'updated_at': datetime.utcnow()
    }
    
    mongo.db.suppliers.update_one({'supplier_id': supplier_id, 'user_id': user_id}, {'$set': update_data})
    return jsonify({'success': True, 'message': 'Supplier updated'}), 200

@suppliers_bp.route('/<supplier_id>', methods=['DELETE'])
@token_required
def delete_supplier(supplier_id):
    """Delete supplier"""
    user_id = request.current_user['user_id']
    result = mongo.db.suppliers.delete_one({'supplier_id': supplier_id, 'user_id': user_id})
    
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Supplier not found'}), 404
    
    return jsonify({'success': True, 'message': 'Supplier deleted'}), 200

# ==================== CUSTOMERS ROUTES ====================
@customers_bp.route('', methods=['GET'])
@token_required
def get_customers():
    """Get all customers for user"""
    user_id = request.current_user['user_id']
    customers = list(mongo.db.customers.find({'user_id': user_id}))
    
    for customer in customers:
        customer['_id'] = str(customer['_id'])
    
    return jsonify({'success': True, 'customers': customers}), 200

@customers_bp.route('', methods=['POST'])
@token_required
def create_customer():
    """Create new customer"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    required_fields = ['customer_name', 'customer_contact']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    customer = {
        'customer_id': str(uuid.uuid4())[:8],
        'customer_name': data.get('customer_name'),
        'customer_contact': data.get('customer_contact'),
        'customer_email': data.get('customer_email', ''),
        'state': data.get('state', ''),
        'city': data.get('city', ''),
        'customer_address': data.get('customer_address', ''),
        'total_sales': float(data.get('total_sales', 0)),
        'total_received': float(data.get('total_received', 0)),
        'balance_receivable': float(data.get('balance_receivable', 0)),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = mongo.db.customers.insert_one(customer)
    customer['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'message': 'Customer created', 'customer': customer}), 201

@customers_bp.route('/<customer_id>', methods=['PUT'])
@token_required
def update_customer(customer_id):
    """Update customer"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    customer = mongo.db.customers.find_one({'customer_id': customer_id, 'user_id': user_id})
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    
    update_data = {
        'customer_name': data.get('customer_name', customer.get('customer_name')),
        'customer_contact': data.get('customer_contact', customer.get('customer_contact')),
        'customer_email': data.get('customer_email', customer.get('customer_email')),
        'state': data.get('state', customer.get('state')),
        'city': data.get('city', customer.get('city')),
        'customer_address': data.get('customer_address', customer.get('customer_address')),
        'updated_at': datetime.utcnow()
    }
    
    mongo.db.customers.update_one({'customer_id': customer_id, 'user_id': user_id}, {'$set': update_data})
    return jsonify({'success': True, 'message': 'Customer updated'}), 200

@customers_bp.route('/<customer_id>', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    """Delete customer"""
    user_id = request.current_user['user_id']
    result = mongo.db.customers.delete_one({'customer_id': customer_id, 'user_id': user_id})
    
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    
    return jsonify({'success': True, 'message': 'Customer deleted'}), 200

# ==================== PURCHASES ROUTES ====================
@purchases_bp.route('', methods=['GET'])
@token_required
def get_purchase_orders():
    """Get all purchase orders for user"""
    user_id = request.current_user['user_id']
    pos = list(mongo.db.purchase_orders.find({'user_id': user_id}))
    
    for po in pos:
        po['_id'] = str(po['_id'])
    
    return jsonify({'success': True, 'purchase_orders': pos}), 200

@purchases_bp.route('', methods=['POST'])
@token_required
def create_purchase_order():
    """Create new purchase order"""
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True) or {}
    
    required_fields = ['supplier_id', 'item_id', 'quantity', 'unit_price']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        quantity, unit_price = order_numbers(data)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    po = {
        'po_id': 'PO-' + str(uuid.uuid4())[:8].upper(),
        'po_date': datetime.utcnow(),
        'supplier_id': data.get('supplier_id'),
        'supplier_name': data.get('supplier_name', ''),
        'item_id': data.get('item_id'),
        'item_name': data.get('item_name', ''),
        'quantity': quantity,
        'unit_price': unit_price,
        'total_amount': quantity * unit_price,
        'pmt_status': data.get('pmt_status', 'Pending'),
        'shipping_status': data.get('shipping_status', 'Not Shipped'),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    try:
        po = mongo.db.save_order_with_stock('purchase_orders', user_id, po)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    return jsonify({'success': True, 'message': 'Purchase order created', 'po': po}), 201

@purchases_bp.route('/<po_id>', methods=['PUT'])
@token_required
def update_purchase_order(po_id):
    """Update purchase order"""
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True) or {}
    
    po = mongo.db.purchase_orders.find_one({'po_id': po_id, 'user_id': user_id})
    if not po:
        return jsonify({'success': False, 'message': 'Purchase order not found'}), 404
    
    try:
        quantity, unit_price = order_numbers(data, po.get('quantity'), po.get('unit_price'))
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    update_data = {
        'pmt_status': data.get('pmt_status', po.get('pmt_status')),
        'shipping_status': data.get('shipping_status', po.get('shipping_status')),
        'quantity': quantity,
        'unit_price': unit_price,
        'total_amount': quantity * unit_price,
        'updated_at': datetime.utcnow()
    }
    
    try:
        mongo.db.save_order_with_stock('purchase_orders', user_id, update_data, po_id)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    return jsonify({'success': True, 'message': 'Purchase order updated'}), 200

@purchases_bp.route('/<po_id>', methods=['DELETE'])
@token_required
def delete_purchase_order(po_id):
    """Delete purchase order"""
    user_id = request.current_user['user_id']
    try:
        mongo.db.save_order_with_stock('purchase_orders', user_id, None, po_id, delete=True)
    except LookupError:
        return jsonify({'success': False, 'message': 'Purchase order not found'}), 404
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    return jsonify({'success': True, 'message': 'Purchase order deleted'}), 200

# ==================== SALES ROUTES ====================
@sales_bp.route('', methods=['GET'])
@token_required
def get_sales_orders():
    """Get all sales orders for user"""
    user_id = request.current_user['user_id']
    sos = list(mongo.db.sales_orders.find({'user_id': user_id}))
    
    for so in sos:
        so['_id'] = str(so['_id'])
    
    return jsonify({'success': True, 'sales_orders': sos}), 200

@sales_bp.route('', methods=['POST'])
@token_required
def create_sales_order():
    """Create new sales order"""
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True) or {}
    
    required_fields = ['customer_id', 'item_id', 'quantity', 'unit_price']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        quantity, unit_price = order_numbers(data)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    so = {
        'so_id': 'SO-' + str(uuid.uuid4())[:8].upper(),
        'so_date': datetime.utcnow(),
        'customer_id': data.get('customer_id'),
        'customer_name': data.get('customer_name', ''),
        'item_id': data.get('item_id'),
        'item_name': data.get('item_name', ''),
        'quantity': quantity,
        'unit_price': unit_price,
        'total_amount': quantity * unit_price,
        'so_status': data.get('so_status', 'Open'),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    try:
        so = mongo.db.save_order_with_stock('sales_orders', user_id, so)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    return jsonify({'success': True, 'message': 'Sales order created', 'so': so}), 201

@sales_bp.route('/<so_id>', methods=['PUT'])
@token_required
def update_sales_order(so_id):
    """Update sales order"""
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True) or {}
    
    so = mongo.db.sales_orders.find_one({'so_id': so_id, 'user_id': user_id})
    if not so:
        return jsonify({'success': False, 'message': 'Sales order not found'}), 404
    
    try:
        quantity, unit_price = order_numbers(data, so.get('quantity'), so.get('unit_price'))
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    update_data = {
        'so_status': data.get('so_status', so.get('so_status')),
        'quantity': quantity,
        'unit_price': unit_price,
        'total_amount': quantity * unit_price,
        'updated_at': datetime.utcnow()
    }
    
    try:
        mongo.db.save_order_with_stock('sales_orders', user_id, update_data, so_id)
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    return jsonify({'success': True, 'message': 'Sales order updated'}), 200

@sales_bp.route('/<so_id>', methods=['DELETE'])
@token_required
def delete_sales_order(so_id):
    """Delete sales order"""
    user_id = request.current_user['user_id']
    try:
        mongo.db.save_order_with_stock('sales_orders', user_id, None, so_id, delete=True)
    except LookupError:
        return jsonify({'success': False, 'message': 'Sales order not found'}), 404
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    
    return jsonify({'success': True, 'message': 'Sales order deleted'}), 200

# ==================== RECEIPTS ROUTES ====================
@receipts_bp.route('', methods=['GET'])
@token_required
def get_receipts():
    """Get all receipts for user"""
    user_id = request.current_user['user_id']
    receipts = list(mongo.db.receipts.find({'user_id': user_id}))
    
    for receipt in receipts:
        receipt['_id'] = str(receipt['_id'])
    
    return jsonify({'success': True, 'receipts': receipts}), 200

@receipts_bp.route('', methods=['POST'])
@token_required
def create_receipt():
    """Create new receipt"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    required_fields = ['customer_id', 'amount_received']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    receipt = {
        'trx_id': 'RT-' + str(uuid.uuid4())[:8].upper(),
        'trx_date': datetime.utcnow(),
        'customer_id': data.get('customer_id'),
        'customer_name': data.get('customer_name', ''),
        'state': data.get('state', ''),
        'city': data.get('city', ''),
        'so_id': data.get('so_id', ''),
        'invoice_num': data.get('invoice_num', ''),
        'pmt_mode': data.get('pmt_mode', 'Cash'),
        'amount_received': float(data.get('amount_received', 0)),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = mongo.db.receipts.insert_one(receipt)
    receipt['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'message': 'Receipt created', 'receipt': receipt}), 201

@receipts_bp.route('/<trx_id>', methods=['PUT'])
@token_required
def update_receipt(trx_id):
    """Update receipt"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    receipt = mongo.db.receipts.find_one({'trx_id': trx_id, 'user_id': user_id})
    if not receipt:
        return jsonify({'success': False, 'message': 'Receipt not found'}), 404
    
    update_data = {
        'pmt_mode': data.get('pmt_mode', receipt.get('pmt_mode')),
        'amount_received': float(data.get('amount_received', receipt.get('amount_received', 0))),
        'updated_at': datetime.utcnow()
    }
    
    mongo.db.receipts.update_one({'trx_id': trx_id, 'user_id': user_id}, {'$set': update_data})
    return jsonify({'success': True, 'message': 'Receipt updated'}), 200

@receipts_bp.route('/<trx_id>', methods=['DELETE'])
@token_required
def delete_receipt(trx_id):
    """Delete receipt"""
    user_id = request.current_user['user_id']
    result = mongo.db.receipts.delete_one({'trx_id': trx_id, 'user_id': user_id})
    
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Receipt not found'}), 404
    
    return jsonify({'success': True, 'message': 'Receipt deleted'}), 200

# ==================== PAYMENTS ROUTES ====================
@payments_bp.route('', methods=['GET'])
@token_required
def get_payments():
    """Get all payments for user"""
    user_id = request.current_user['user_id']
    payments = list(mongo.db.payments.find({'user_id': user_id}))
    
    for payment in payments:
        payment['_id'] = str(payment['_id'])
    
    return jsonify({'success': True, 'payments': payments}), 200

@payments_bp.route('', methods=['POST'])
@token_required
def create_payment():
    """Create new payment"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    required_fields = ['supplier_id', 'amount_paid']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    payment = {
        'payment_id': 'PAY-' + str(uuid.uuid4())[:8].upper(),
        'payment_date': datetime.utcnow(),
        'supplier_id': data.get('supplier_id'),
        'supplier_name': data.get('supplier_name', ''),
        'po_id': data.get('po_id', ''),
        'amount_paid': float(data.get('amount_paid', 0)),
        'pmt_mode': data.get('pmt_mode', 'Cash'),
        'reference_num': data.get('reference_num', ''),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = mongo.db.payments.insert_one(payment)
    payment['_id'] = str(result.inserted_id)
    
    return jsonify({'success': True, 'message': 'Payment created', 'payment': payment}), 201

@payments_bp.route('/<payment_id>', methods=['PUT'])
@token_required
def update_payment(payment_id):
    """Update payment"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    payment = mongo.db.payments.find_one({'payment_id': payment_id, 'user_id': user_id})
    if not payment:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404
    
    update_data = {
        'pmt_mode': data.get('pmt_mode', payment.get('pmt_mode')),
        'amount_paid': float(data.get('amount_paid', payment.get('amount_paid', 0))),
        'reference_num': data.get('reference_num', payment.get('reference_num')),
        'updated_at': datetime.utcnow()
    }
    
    mongo.db.payments.update_one({'payment_id': payment_id, 'user_id': user_id}, {'$set': update_data})
    return jsonify({'success': True, 'message': 'Payment updated'}), 200

@payments_bp.route('/<payment_id>', methods=['DELETE'])
@token_required
def delete_payment(payment_id):
    """Delete payment"""
    user_id = request.current_user['user_id']
    result = mongo.db.payments.delete_one({'payment_id': payment_id, 'user_id': user_id})
    
    if result.deleted_count == 0:
        return jsonify({'success': False, 'message': 'Payment not found'}), 404
    
    return jsonify({'success': True, 'message': 'Payment deleted'}), 200

# ==================== DASHBOARD ROUTES ====================
# ==================== DASHBOARD ROUTES ====================
@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    user_id = request.current_user['user_id']
    
    # Calculate statistics - fixed aggregation pipeline calls
    sales_agg = list(mongo.db.sales_orders.aggregate([
        {'$match': {'user_id': user_id}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
    ]))
    total_sales = sales_agg[0]['total'] if sales_agg else 0
    
    purchases_agg = list(mongo.db.purchase_orders.aggregate([
        {'$match': {'user_id': user_id}},
        {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
    ]))
    total_purchases = purchases_agg[0]['total'] if purchases_agg else 0
    
    receipts_agg = list(mongo.db.receipts.aggregate([
        {'$match': {'user_id': user_id}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount_received'}}}
    ]))
    total_receipts = receipts_agg[0]['total'] if receipts_agg else 0
    
    payments_agg = list(mongo.db.payments.aggregate([
        {'$match': {'user_id': user_id}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount_paid'}}}
    ]))
    total_payments = payments_agg[0]['total'] if payments_agg else 0
    
    inventory_count = mongo.db.inventory_items.count_documents({'user_id': user_id})
    suppliers_count = mongo.db.suppliers.count_documents({'user_id': user_id})
    customers_count = mongo.db.customers.count_documents({'user_id': user_id})
    
    return jsonify({
        'success': True,
        'stats': {
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'total_receipts': total_receipts,
            'total_payments': total_payments,
            'net_profit': total_sales - total_purchases,
            'inventory_count': inventory_count,
            'suppliers_count': suppliers_count,
            'customers_count': customers_count
        }
    }), 200
