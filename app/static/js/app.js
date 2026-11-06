const API_BASE_URL = 'http://localhost:5000/api';

const pageData = {
    inventory: [],
    suppliers: [],
    customers: [],
    purchases: [],
    sales: [],
    receipts: [],
    payments: []
};

let activeModal = null;

// Get token from localStorage
function getToken() {
    const token = localStorage.getItem('token');
    console.log('Retrieved token:', token ? 'exists' : 'missing');
    return token;
}

// Get user info
function getUserInfo() {
    const userStr = localStorage.getItem('user');
    console.log('Retrieved user:', userStr ? 'exists' : 'missing');
    return JSON.parse(userStr || '{}');
}

// Check authentication
function checkAuth() {
    const token = getToken();
    console.log('Checking auth, token present:', !!token);
    if (!token) {
        console.log('No token found, redirecting to login');
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

// API Call Helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok && response.status === 401) {
            logout();
            return null;
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// Navigation
function navigateTo(page) {
    // Hide all content
    document.querySelectorAll('.page-content').forEach(el => {
        el.classList.remove('active');
    });

    // Remove active from nav
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.remove('active');
    });

    // Show selected content
    const contentId = page + 'Content';
    const content = document.getElementById(contentId);
    if (content) {
        content.classList.add('active');
    }

    // Set active nav - find the nav item with correct text
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(page)) {
            item.classList.add('active');
        }
    });

    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        inventory: 'Inventory Items',
        suppliers: 'Suppliers',
        customers: 'Customers',
        purchases: 'Purchase Orders',
        sales: 'Sales Orders',
        receipts: 'Receipts',
        payments: 'Payments'
    };
    document.getElementById('pageTitle').textContent = titles[page] || page;

    // Load data
    loadPageData(page);

    // Close sidebar on mobile
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth < 768) {
        sidebar.classList.remove('active');
    }
}

// Load page data
async function loadPageData(page) {
    switch(page) {
        case 'dashboard':
            loadDashboardStats();
            break;
        case 'inventory':
            loadInventory();
            break;
        case 'suppliers':
            loadSuppliers();
            break;
        case 'customers':
            loadCustomers();
            break;
        case 'purchases':
            loadPurchases();
            break;
        case 'sales':
            loadSales();
            break;
        case 'receipts':
            loadReceipts();
            break;
        case 'payments':
            loadPayments();
            break;
    }
}

// Dashboard Stats
async function loadDashboardStats() {
    const result = await apiCall('/dashboard/stats');
    if (result && result.success) {
        const stats = result.stats;
        document.getElementById('stat-total-sales').textContent = stats.total_sales.toFixed(2);
        document.getElementById('stat-total-purchases').textContent = stats.total_purchases.toFixed(2);
        document.getElementById('stat-net-profit').textContent = stats.net_profit.toFixed(2);
        document.getElementById('stat-inventory-count').textContent = stats.inventory_count;
        document.getElementById('stat-suppliers-count').textContent = stats.suppliers_count;
        document.getElementById('stat-customers-count').textContent = stats.customers_count;
        document.getElementById('stat-total-receipts').textContent = stats.total_receipts.toFixed(2);
    }
}

// Load Inventory
async function loadInventory() {
    const result = await apiCall('/inventory');
    if (result && result.success) {
        pageData.inventory = result.items || [];
        const tbody = document.querySelector('#inventoryTable tbody');
        tbody.innerHTML = '';

        pageData.inventory.forEach(item => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${item.item_id}</td>
                <td>${item.item_name}</td>
                <td>${item.item_type}</td>
                <td>${item.item_category}</td>
                <td>${item.qty_purchased}</td>
                <td>${item.qty_sold}</td>
                <td>${item.remaining_qty}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editInventoryItem('${item.item_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deleteInventoryItem('${item.item_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

// Load Suppliers
async function loadSuppliers() {
    const result = await apiCall('/suppliers');
    if (result && result.success) {
        pageData.suppliers = result.suppliers || [];
        const tbody = document.querySelector('#suppliersTable tbody');
        tbody.innerHTML = '';

        pageData.suppliers.forEach(supplier => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${supplier.supplier_id}</td>
                <td>${supplier.supplier_name}</td>
                <td>${supplier.supplier_contact}</td>
                <td>${supplier.supplier_email}</td>
                <td>${supplier.city}</td>
                <td>${supplier.state}</td>
                <td>$${supplier.balance_payable.toFixed(2)}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editSupplier('${supplier.supplier_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deleteSupplier('${supplier.supplier_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

// Load Customers
async function loadCustomers() {
    const result = await apiCall('/customers');
    if (result && result.success) {
        pageData.customers = result.customers || [];
        const tbody = document.querySelector('#customersTable tbody');
        tbody.innerHTML = '';

        pageData.customers.forEach(customer => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${customer.customer_id}</td>
                <td>${customer.customer_name}</td>
                <td>${customer.customer_contact}</td>
                <td>${customer.customer_email}</td>
                <td>${customer.city}</td>
                <td>${customer.state}</td>
                <td>$${customer.balance_receivable.toFixed(2)}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editCustomer('${customer.customer_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deleteCustomer('${customer.customer_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

// Load Purchases
async function loadPurchases() {
    const result = await apiCall('/purchases');
    if (result && result.success) {
        pageData.purchases = result.purchase_orders || [];
        const tbody = document.querySelector('#purchasesTable tbody');
        tbody.innerHTML = '';

        pageData.purchases.forEach(po => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${po.po_id}</td>
                <td>${po.supplier_name}</td>
                <td>${po.item_name}</td>
                <td>${po.quantity}</td>
                <td>$${po.unit_price.toFixed(2)}</td>
                <td>$${po.total_amount.toFixed(2)}</td>
                <td><span class="badge">${po.pmt_status}</span></td>
                <td><span class="badge">${po.shipping_status}</span></td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editPurchase('${po.po_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deletePurchase('${po.po_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

// Load Sales
async function loadSales() {
    const result = await apiCall('/sales');
    if (result && result.success) {
        pageData.sales = result.sales_orders || [];
        const tbody = document.querySelector('#salesTable tbody');
        tbody.innerHTML = '';

        pageData.sales.forEach(so => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${so.so_id}</td>
                <td>${so.customer_name}</td>
                <td>${so.item_name}</td>
                <td>${so.quantity}</td>
                <td>$${so.unit_price.toFixed(2)}</td>
                <td>$${so.total_amount.toFixed(2)}</td>
                <td><span class="badge">${so.so_status}</span></td>
                <td>${new Date(so.so_date).toLocaleDateString()}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editSales('${so.so_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deleteSales('${so.so_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

// Load Receipts
async function loadReceipts() {
    const result = await apiCall('/receipts');
    if (result && result.success) {
        pageData.receipts = result.receipts || [];
        const tbody = document.querySelector('#receiptsTable tbody');
        tbody.innerHTML = '';

        pageData.receipts.forEach(receipt => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${receipt.trx_id}</td>
                <td>${receipt.customer_name}</td>
                <td>${receipt.so_id}</td>
                <td>$${receipt.amount_received.toFixed(2)}</td>
                <td>${receipt.pmt_mode}</td>
                <td>${new Date(receipt.trx_date).toLocaleDateString()}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editReceipt('${receipt.trx_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deleteReceipt('${receipt.trx_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

// Load Payments
async function loadPayments() {
    const result = await apiCall('/payments');
    if (result && result.success) {
        pageData.payments = result.payments || [];
        const tbody = document.querySelector('#paymentsTable tbody');
        tbody.innerHTML = '';

        pageData.payments.forEach(payment => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${payment.payment_id}</td>
                <td>${payment.supplier_name}</td>
                <td>$${payment.amount_paid.toFixed(2)}</td>
                <td>${payment.pmt_mode}</td>
                <td>${payment.reference_num}</td>
                <td>${new Date(payment.payment_date).toLocaleDateString()}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn edit-btn" onclick="editPayment('${payment.payment_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="action-btn delete-btn" onclick="deletePayment('${payment.payment_id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </td>
            `;
        });
    }
}

const formConfigs = {
    inventory: {
        title: 'Inventory Item',
        endpoint: '/inventory',
        idKey: 'item_id',
        reload: loadInventory,
        fields: [
            { name: 'item_name', label: 'Item Name', type: 'text', required: true },
            { name: 'item_type', label: 'Item Type', type: 'text', required: true },
            { name: 'item_category', label: 'Item Category', type: 'text', required: true },
            { name: 'item_subcategory', label: 'Subcategory', type: 'text' },
            { name: 'qty_purchased', label: 'Qty Purchased', type: 'number', step: '0.01' },
            { name: 'qty_sold', label: 'Qty Sold', type: 'number', step: '0.01' },
            { name: 'remaining_qty', label: 'Remaining Qty', type: 'number', step: '0.01' },
            { name: 'reorder_level', label: 'Reorder Level', type: 'number', step: '0.01' }
        ]
    },
    suppliers: {
        title: 'Supplier',
        endpoint: '/suppliers',
        idKey: 'supplier_id',
        reload: loadSuppliers,
        fields: [
            { name: 'supplier_name', label: 'Supplier Name', type: 'text', required: true },
            { name: 'supplier_contact', label: 'Contact', type: 'text', required: true },
            { name: 'supplier_email', label: 'Email', type: 'email' },
            { name: 'city', label: 'City', type: 'text' },
            { name: 'state', label: 'State', type: 'text' },
            { name: 'supplier_address', label: 'Address', type: 'textarea' }
        ]
    },
    customers: {
        title: 'Customer',
        endpoint: '/customers',
        idKey: 'customer_id',
        reload: loadCustomers,
        fields: [
            { name: 'customer_name', label: 'Customer Name', type: 'text', required: true },
            { name: 'customer_contact', label: 'Contact', type: 'text', required: true },
            { name: 'customer_email', label: 'Email', type: 'email' },
            { name: 'city', label: 'City', type: 'text' },
            { name: 'state', label: 'State', type: 'text' },
            { name: 'customer_address', label: 'Address', type: 'textarea' }
        ]
    },
    purchases: {
        title: 'Purchase Order',
        endpoint: '/purchases',
        idKey: 'po_id',
        reload: loadPurchases,
        fields: [
            { name: 'supplier_id', label: 'Supplier ID', type: 'text', required: true, createOnly: true },
            { name: 'supplier_name', label: 'Supplier Name', type: 'text', createOnly: true },
            { name: 'item_id', label: 'Item ID', type: 'text', required: true, createOnly: true },
            { name: 'item_name', label: 'Item Name', type: 'text', createOnly: true },
            { name: 'quantity', label: 'Quantity', type: 'number', step: '0.01', required: true },
            { name: 'unit_price', label: 'Unit Price', type: 'number', step: '0.01', required: true },
            { name: 'pmt_status', label: 'Payment Status', type: 'select', options: ['Pending', 'Partial', 'Paid'] },
            { name: 'shipping_status', label: 'Shipping Status', type: 'select', options: ['Not Shipped', 'In Transit', 'Delivered'] }
        ]
    },
    sales: {
        title: 'Sales Order',
        endpoint: '/sales',
        idKey: 'so_id',
        reload: loadSales,
        fields: [
            { name: 'customer_id', label: 'Customer ID', type: 'text', required: true, createOnly: true },
            { name: 'customer_name', label: 'Customer Name', type: 'text', createOnly: true },
            { name: 'item_id', label: 'Item ID', type: 'text', required: true, createOnly: true },
            { name: 'item_name', label: 'Item Name', type: 'text', createOnly: true },
            { name: 'quantity', label: 'Quantity', type: 'number', step: '0.01', required: true },
            { name: 'unit_price', label: 'Unit Price', type: 'number', step: '0.01', required: true },
            { name: 'so_status', label: 'Status', type: 'select', options: ['Open', 'Shipped', 'Received'] }
        ]
    },
    receipts: {
        title: 'Receipt',
        endpoint: '/receipts',
        idKey: 'trx_id',
        reload: loadReceipts,
        fields: [
            { name: 'customer_id', label: 'Customer ID', type: 'text', required: true, createOnly: true },
            { name: 'customer_name', label: 'Customer Name', type: 'text', createOnly: true },
            { name: 'so_id', label: 'SO ID', type: 'text', createOnly: true },
            { name: 'invoice_num', label: 'Invoice Number', type: 'text', createOnly: true },
            { name: 'amount_received', label: 'Amount Received', type: 'number', step: '0.01', required: true },
            { name: 'pmt_mode', label: 'Payment Mode', type: 'select', options: ['Cash', 'Check', 'Online', 'Credit Card'] }
        ]
    },
    payments: {
        title: 'Payment',
        endpoint: '/payments',
        idKey: 'payment_id',
        reload: loadPayments,
        fields: [
            { name: 'supplier_id', label: 'Supplier ID', type: 'text', required: true, createOnly: true },
            { name: 'supplier_name', label: 'Supplier Name', type: 'text', createOnly: true },
            { name: 'po_id', label: 'PO ID', type: 'text', createOnly: true },
            { name: 'amount_paid', label: 'Amount Paid', type: 'number', step: '0.01', required: true },
            { name: 'pmt_mode', label: 'Payment Mode', type: 'select', options: ['Cash', 'Check', 'Online', 'Credit Card'] },
            { name: 'reference_num', label: 'Reference Number', type: 'text' }
        ]
    }
};

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function findRecord(type, id) {
    const config = formConfigs[type];
    return (pageData[type] || []).find(record => record[config.idKey] === id);
}

function fieldMarkup(field, value = '') {
    const required = field.required ? 'required' : '';
    const step = field.step ? `step="${field.step}"` : '';
    const safeValue = escapeHtml(value);

    if (field.type === 'textarea') {
        return `
            <div class="form-group">
                <label for="modal-${field.name}">${field.label}</label>
                <textarea id="modal-${field.name}" name="${field.name}" ${required}>${safeValue}</textarea>
            </div>
        `;
    }

    if (field.type === 'select') {
        const options = field.options.map(option => {
            const selected = option === value ? 'selected' : '';
            return `<option value="${escapeHtml(option)}" ${selected}>${escapeHtml(option)}</option>`;
        }).join('');

        return `
            <div class="form-group">
                <label for="modal-${field.name}">${field.label}</label>
                <select id="modal-${field.name}" name="${field.name}" ${required}>${options}</select>
            </div>
        `;
    }

    return `
        <div class="form-group">
            <label for="modal-${field.name}">${field.label}</label>
            <input id="modal-${field.name}" name="${field.name}" type="${field.type}" value="${safeValue}" ${step} ${required}>
        </div>
    `;
}

function openCrudModal(type, mode, record = null) {
    const config = formConfigs[type];
    activeModal = { type, mode, id: record ? record[config.idKey] : null };

    const modal = document.getElementById('crudModal');
    const title = document.getElementById('crudModalTitle');
    const form = document.getElementById('crudForm');
    const fields = config.fields.filter(field => mode === 'create' || !field.createOnly);

    title.textContent = `${mode === 'create' ? 'Add' : 'Update'} ${config.title}`;
    form.innerHTML = fields.map(field => fieldMarkup(field, record ? record[field.name] : '')).join('') + `
        <div class="form-actions">
            <button type="button" class="btn btn-secondary" onclick="closeCrudModal()">Cancel</button>
            <button type="submit" class="btn btn-primary">${mode === 'create' ? 'Add' : 'Update'}</button>
        </div>
    `;

    modal.classList.add('active');
}

function closeCrudModal() {
    const modal = document.getElementById('crudModal');
    modal.classList.remove('active');
    activeModal = null;
}

async function submitCrudForm(event) {
    event.preventDefault();

    if (!activeModal) {
        return;
    }

    const config = formConfigs[activeModal.type];
    const formData = new FormData(event.target);
    const payload = {};
    const fields = config.fields.filter(field => activeModal.mode === 'create' || !field.createOnly);
    const fieldByName = Object.fromEntries(fields.map(field => [field.name, field]));

    for (const [key, value] of formData.entries()) {
        const field = fieldByName[key];
        if (value === '' && field && !field.required) {
            continue;
        }
        payload[key] = value;
    }

    const endpoint = activeModal.mode === 'create'
        ? config.endpoint
        : `${config.endpoint}/${activeModal.id}`;
    const method = activeModal.mode === 'create' ? 'POST' : 'PUT';
    const result = await apiCall(endpoint, method, payload);

    if (!result || !result.success) {
        alert(result && result.message ? result.message : 'Unable to save record');
        return;
    }

    closeCrudModal();
    await config.reload();
    loadDashboardStats();
}

async function deleteRecord(type, id, label) {
    if (!confirm(`Delete this ${label}?`)) {
        return;
    }

    const config = formConfigs[type];
    const result = await apiCall(`${config.endpoint}/${id}`, 'DELETE');

    if (!result || !result.success) {
        alert(result && result.message ? result.message : `Unable to delete ${label}`);
        return;
    }

    await config.reload();
    loadDashboardStats();
}

function deleteInventoryItem(id) { deleteRecord('inventory', id, 'item'); }
function deleteSupplier(id) { deleteRecord('suppliers', id, 'supplier'); }
function deleteCustomer(id) { deleteRecord('customers', id, 'customer'); }
function deletePurchase(id) { deleteRecord('purchases', id, 'purchase order'); }
function deleteSales(id) { deleteRecord('sales', id, 'sales order'); }
function deleteReceipt(id) { deleteRecord('receipts', id, 'receipt'); }
function deletePayment(id) { deleteRecord('payments', id, 'payment'); }

function editRecord(type, id) {
    const record = findRecord(type, id);
    if (!record) {
        alert('Record data is not loaded yet. Refresh the page and try again.');
        return;
    }
    openCrudModal(type, 'update', record);
}

function editInventoryItem(id) { editRecord('inventory', id); }
function editSupplier(id) { editRecord('suppliers', id); }
function editCustomer(id) { editRecord('customers', id); }
function editPurchase(id) { editRecord('purchases', id); }
function editSales(id) { editRecord('sales', id); }
function editReceipt(id) { editRecord('receipts', id); }
function editPayment(id) { editRecord('payments', id); }

function openInventoryModal() { openCrudModal('inventory', 'create'); }
function openSupplierModal() { openCrudModal('suppliers', 'create'); }
function openCustomerModal() { openCrudModal('customers', 'create'); }
function openPurchaseModal() { openCrudModal('purchases', 'create'); }
function openSalesModal() { openCrudModal('sales', 'create'); }
function openReceiptModal() { openCrudModal('receipts', 'create'); }
function openPaymentModal() { openCrudModal('payments', 'create'); }

// Sidebar toggle
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// Logout
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

// Initialize
window.addEventListener('load', function() {
    console.log('Dashboard page loaded, checking authentication...');
    
    const token = getToken();
    console.log('Token check result:', token ? 'Token found' : 'No token');
    
    if (!token) {
        console.log('No authentication token, redirecting to login');
        window.location.href = '/login.html';
        return;
    }

    const user = getUserInfo();
    console.log('User data:', user);
    
    if (user.username) {
        document.getElementById('username').textContent = user.username;
    }

    console.log('Navigation to dashboard');
    // Load initial dashboard
    navigateTo('dashboard');
});
