# Developer's Guide - Extending the Application

## Architecture Overview

The application follows a **modular, layered architecture**:

```
Frontend (HTML/CSS/JS)
        ↓↑
API Layer (REST endpoints)
        ↓↑
Business Logic (Auth, DB operations)
        ↓↑
Database Layer (MongoDB)
```

---

## Adding a New Module (Feature)

### Example: Adding an "Expenses" Module

#### Step 1: Create Database Schema (models.py)

Add to `app/models.py`:
```python
EXPENSE_SCHEMA = {
    'expense_id': str,
    'description': str,
    'amount': float,
    'category': str,
    'expense_date': 'datetime',
    'user_id': str,
    'created_at': 'datetime',
    'updated_at': 'datetime'
}
```

#### Step 2: Create API Routes (routes.py)

Add to `app/routes.py`:
```python
from datetime import datetime
import uuid

expenses_bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')

@expenses_bp.route('', methods=['GET'])
@token_required
def get_expenses():
    user_id = request.current_user['user_id']
    expenses = list(mongo.db.expenses.find({'user_id': user_id}))
    for expense in expenses:
        expense['_id'] = str(expense['_id'])
    return jsonify({'success': True, 'expenses': expenses}), 200

@expenses_bp.route('', methods=['POST'])
@token_required
def create_expense():
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    expense = {
        'expense_id': str(uuid.uuid4())[:8],
        'description': data.get('description'),
        'amount': float(data.get('amount', 0)),
        'category': data.get('category'),
        'expense_date': datetime.utcnow(),
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    result = mongo.db.expenses.insert_one(expense)
    expense['_id'] = str(result.inserted_id)
    return jsonify({'success': True, 'expense': expense}), 201

# ... more CRUD routes
```

#### Step 3: Register Blueprint in __init__.py

Edit `app/__init__.py`:
```python
from app.routes import auth_bp, inventory_bp, ..., expenses_bp

app.register_blueprint(expenses_bp)
```

#### Step 4: Create Frontend Page

Add to `app/templates/dashboard.html`:
```html
<!-- Add to sidebar nav -->
<a href="#expenses" class="nav-item" onclick="navigateTo('expenses')">
    <i class="fas fa-coins"></i> Expenses
</a>

<!-- Add expenses content -->
<div id="expensesContent" class="page-content">
    <div class="page-header">
        <h2>Expenses</h2>
        <button class="btn btn-primary" onclick="openExpenseModal()">
            <i class="fas fa-plus"></i> Add Expense
        </button>
    </div>
    <div class="table-container">
        <table class="table" id="expensesTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
</div>
```

#### Step 5: Add JavaScript Functions

Add to `app/static/js/app.js`:
```javascript
async function loadExpenses() {
    const result = await apiCall('/expenses');
    if (result && result.success) {
        const tbody = document.querySelector('#expensesTable tbody');
        tbody.innerHTML = '';
        result.expenses.forEach(expense => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${expense.expense_id}</td>
                <td>${expense.description}</td>
                <td>$${expense.amount.toFixed(2)}</td>
                <td>${expense.category}</td>
                <td>${new Date(expense.expense_date).toLocaleDateString()}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editExpense('${expense.expense_id}')">
                            Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deleteExpense('${expense.expense_id}')">
                            Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

function openExpenseModal() { alert('Add expense'); }
function deleteExpense(id) { if(confirm('Delete?')) { apiCall(`/expenses/${id}`, 'DELETE'); loadExpenses(); } }
```

---

## Code Organization Best Practices

### Do's ✅

```python
# DO: Use descriptive function names
def get_user_by_email(email):
    pass

# DO: Add docstrings
def create_purchase_order(po_data):
    """Create a new purchase order and update inventory"""
    pass

# DO: Use constants
DEFAULT_PAGE_SIZE = 20
STATUS_ACTIVE = 'active'

# DO: Validate input
if not isinstance(amount, (int, float)):
    return jsonify({'error': 'Amount must be a number'}), 400

# DO: Handle errors
try:
    result = mongo.db.items.insert_one(data)
except Exception as e:
    logger.error(f"Insert failed: {e}")
    return jsonify({'error': 'Database error'}), 500
```

### Don'ts ❌

```python
# DON'T: Use single-letter variables (except loop indices)
d = request.get_json()  # Bad

# DON'T: Mix business logic with route handlers
@app.route('/api/items')
def get():  # Too short, not descriptive
    # Complex 50-line calculation here
    pass

# DON'T: Hardcode values
MONGO_URI = 'mongodb://localhost:27017/inventory'  # Should be in .env

# DON'T: Ignore errors
result = mongo.db.items.find_one({'id': item_id})  # What if it fails?

# DON'T: Trust user input directly
user_input = request.form['data']
query = f"SELECT * FROM items WHERE name='{user_input}'"  # SQL injection!
```

---

## Testing Your Changes

### Unit Testing Example

Create `test_auth.py`:
```python
import unittest
from app import create_app, mongo
from app.auth import hash_password, verify_password

class TestAuth(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
    
    def test_password_hashing(self):
        password = "test123"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        
    def test_wrong_password(self):
        password = "test123"
        hashed = hash_password(password)
        self.assertFalse(verify_password("wrong", hashed))

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python -m pytest test_auth.py
```

---

## Adding Authentication Levels

### Role-Based Access Control

Add to `auth.py`:
```python
def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.current_user
        user = mongo.db.users.find_one({'_id': token['user_id']})
        
        if user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated
```

Usage:
```python
@app.route('/admin/users', methods=['GET'])
@token_required
@require_admin
def get_all_users():
    users = list(mongo.db.users.find({}))
    return jsonify(users), 200
```

---

## Adding Logging

```python
import logging

# In run.py
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# In routes
logger.info(f"User {user_id} created new item")
logger.error(f"Database connection failed: {error}")
logger.warning(f"Suspicious login attempt from {ip}")
```

---

## Optimization Techniques

### Database Query Optimization

```python
# SLOW - N+1 problem
for po in mongo.db.purchase_orders.find():
    supplier = mongo.db.suppliers.find_one({'supplier_id': po['supplier_id']})
    # Process data

# FAST - Use single query  
pos = mongo.db.purchase_orders.aggregate([
    {
        '$lookup': {
            'from': 'suppliers',
            'localField': 'supplier_id',
            'foreignField': 'supplier_id',
            'as': 'supplier'
        }
    }
])
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_statuses():
    """Cache status values"""
    statuses = mongo.db.dimensions.find_one({})
    return statuses.get('pmt_status', [])
```

---

## API Documentation

When adding endpoints, document them:

```python
@app.route('/api/items', methods=['GET'])
@token_required
def get_items():
    """
    Get all items for the current user
    
    Returns:
        200: List of items with {id, name, quantity, ...}
        401: Unauthorized
        500: Server error
    
    Example:
        GET /api/items
        Response: {
            "success": true,
            "items": [
                {"item_id": "123", "item_name": "Widget", ...}
            ]
        }
    """
    pass
```

---

## Database Migration

If you need to modify collection structure:

```python
# migration_v2.py
from pymongo import MongoClient

def migrate():
    client = MongoClient('mongodb://localhost:27017')
    db = client['inventory_app']
    
    # Add a new field to all documents
    db.items.update_many(
        {},
        {'$set': {'status': 'active'}}
    )
    
    # Migrate existing data
    for item in db.items.find():
        if not item.get('reorder_level'):
            db.items.update_one(
                {'_id': item['_id']},
                {'$set': {'reorder_level': 10}}
            )

if __name__ == '__main__':
    migrate()
    print("Migration complete!")
```

---

## Environment-Specific Configurations

### Development
- Debug mode ON
- Detailed error messages
- Hot reloading

### Production
- Debug mode OFF
- Error tracking (Sentry)
- Performance monitoring
- Database backup enabled

### Testing
- Separate test database
- Fixtures and mocks
- Automated tests

```python
# In config.py
if os.getenv('FLASK_ENV') == 'production':
    # Production settings
    DEBUG = False
    MONGO_URI = os.getenv('PROD_MONGO_URI')  # Different DB
elif os.getenv('FLASK_ENV') == 'testing':
    # Testing settings
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/inventory_app_test'
```

---

## Version Control

### .gitignore Example
```
# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local

# Cache
__pycache__/
*.pyc
*.pyo

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log

# Database
/data/
*.sqlite
```

---

## Deployment Checklist

- [ ] Change SECRET_KEY
- [ ] Change JWT_SECRET
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=False
- [ ] Use production database
- [ ] Setup HTTPS/SSL
- [ ] Enable logging
- [ ] Setup monitoring
- [ ] Enable backups
- [ ] Test all APIs
- [ ] Load test the app
- [ ] Document changes

---

## Performance Profiling

```python
# Add to run.py
from werkzeug.middleware.profiler import ProfilerMiddleware

app = ProfilerMiddleware(app, restrictions=[30])
app.run()

# Generates profile.txt with performance data
```

---

## Common Pitfalls

1. **Not using @token_required**
   - Always protect sensitive endpoints
   
2. **Mixing user data**
   - Always filter by user_id
   
3. **Not validating input**
   - Always check data types
   
4. **Hardcoding values**
   - Use environment variables
   
5. **Ignoring errors**
   - Always handle exceptions

---

## Resources for Learning

- Flask Official Docs: https://flask.palletsprojects.com/
- MongoDB Documentation: https://docs.mongodb.com/
- REST API Best Practices: https://restfulapi.net/
- Python Best Practices: https://peps.python.org/

---

Happy developing! 🚀

For questions, refer to the main README.md or modify this guide.
