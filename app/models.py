"""
Collection schemas and models
"""

USER_SCHEMA = {
    'username': str,
    'email': str,
    'password': str,  # hashed
    'created_at': 'datetime',
    'active': bool
}

SUPPLIER_SCHEMA = {
    'supplier_id': str,
    'supplier_name': str,
    'supplier_contact': str,
    'supplier_email': str,
    'state': str,
    'city': str,
    'supplier_address': str,
    'total_purchases': float,
    'total_payments': float,
    'balance_payable': float,
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

CUSTOMER_SCHEMA = {
    'customer_id': str,
    'customer_name': str,
    'customer_contact': str,
    'customer_email': str,
    'state': str,
    'city': str,
    'customer_address': str,
    'total_sales': float,
    'total_received': float,
    'balance_receivable': float,
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

INVENTORY_SCHEMA = {
    'item_id': str,
    'item_type': str,
    'item_category': str,
    'item_subcategory': str,
    'item_name': str,
    'qty_purchased': float,
    'qty_sold': float,
    'remaining_qty': float,
    'reorder_level': float,
    'reorder_required': bool,
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

PURCHASE_ORDER_SCHEMA = {
    'po_id': str,
    'po_date': 'datetime',
    'supplier_id': str,
    'supplier_name': str,
    'item_id': str,
    'item_name': str,
    'quantity': float,
    'unit_price': float,
    'total_amount': float,
    'pmt_status': str,  # Pending, Paid, Partial
    'shipping_status': str,  # Not Shipped, In Transit, Delivered
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

SALES_ORDER_SCHEMA = {
    'so_id': str,
    'so_date': 'datetime',
    'customer_id': str,
    'customer_name': str,
    'item_id': str,
    'item_name': str,
    'quantity': float,
    'unit_price': float,
    'total_amount': float,
    'so_status': str,  # Open, Shipped, Received
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

RECEIPT_SCHEMA = {
    'trx_id': str,
    'trx_date': 'datetime',
    'customer_id': str,
    'customer_name': str,
    'state': str,
    'city': str,
    'so_id': str,
    'invoice_num': str,
    'pmt_mode': str,  # Cash, Check, Online, Credit Card
    'amount_received': float,
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

PAYMENT_SCHEMA = {
    'payment_id': str,
    'payment_date': 'datetime',
    'supplier_id': str,
    'supplier_name': str,
    'po_id': str,
    'amount_paid': float,
    'pmt_mode': str,  # Cash, Check, Online, Credit Card
    'reference_num': str,
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

DIMENSION_SCHEMA = {
    'item_type': [str],
    'item_category': [str],
    'item_subcategory': [str],
    'state': [str],
    'city': [str],
    'pmt_status': [str],
    'shipping_status': [str],
    'so_status': [str],
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}

def get_collection_names():
    """Return list of collection names"""
    return [
        'users',
        'suppliers',
        'customers',
        'inventory_items',
        'purchase_orders',
        'sales_orders',
        'receipts',
        'payments',
        'dimensions'
    ]
