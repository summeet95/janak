import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace


COLLECTIONS = [
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


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


class SQLiteMongo:
    def __init__(self):
        self.db = None

    def init_app(self, app):
        db_path = Path(app.config['SQLITE_PATH'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = SQLiteDatabase(db_path)
        self.db.init_schema()


class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = str(db_path)

    def init_schema(self):
        with self._connect() as conn:
            for collection in COLLECTIONS:
                conn.execute(
                    f'''
                    CREATE TABLE IF NOT EXISTS {collection} (
                        _id TEXT PRIMARY KEY,
                        document TEXT NOT NULL
                    )
                    '''
                )
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users (json_extract(document, "$.username"))')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users (json_extract(document, "$.email"))')

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def __getattr__(self, name):
        if name in COLLECTIONS:
            return SQLiteCollection(self, name)
        raise AttributeError(name)

    def has_tracked_orders(self, user_id, item_id):
        with self._connect() as conn:
            for kind in ('purchase_orders', 'sales_orders'):
                row = conn.execute(
                    f'SELECT 1 FROM {kind} WHERE json_extract(document, "$.user_id") = ? '
                    'AND json_extract(document, "$.item_id") = ? '
                    'AND json_extract(document, "$.stock_applied") = 1 LIMIT 1',
                    (user_id, item_id)
                ).fetchone()
                if row:
                    return True
        return False

    def save_order_with_stock(self, kind, user_id, document, order_id=None, delete=False):
        if kind not in ('purchase_orders', 'sales_orders'):
            raise ValueError('Invalid order type')
        id_key = 'po_id' if kind == 'purchase_orders' else 'so_id'
        with self._connect() as conn:
            conn.execute('BEGIN IMMEDIATE')
            old = None
            if order_id is not None:
                row = conn.execute(
                    f'SELECT _id, document FROM {kind} WHERE json_extract(document, ?) = ? '
                    'AND json_extract(document, "$.user_id") = ?',
                    (f'$.{id_key}', order_id, user_id)
                ).fetchone()
                if row is None:
                    raise LookupError('Order not found')
                old = json.loads(row['document'])
                old['_id'] = row['_id']

            if old and not old.get('stock_applied'):
                if delete:
                    conn.execute(f'DELETE FROM {kind} WHERE _id = ?', (old['_id'],))
                else:
                    old.update(document)
                    conn.execute(f'UPDATE {kind} SET document = ? WHERE _id = ?',
                                 (json.dumps(old, default=_json_default), old['_id']))
                return old

            tracked_old = float(old['quantity']) if old and old.get('stock_applied') else 0.0
            new_quantity = 0.0 if delete else float(document['quantity'])
            if new_quantity <= 0 and not delete:
                raise ValueError('Quantity must be greater than zero')
            stock_delta = new_quantity - tracked_old
            if kind == 'sales_orders':
                stock_delta = -stock_delta

            item_id = (old or document)['item_id']
            item_row = conn.execute(
                'SELECT _id, document FROM inventory_items '
                'WHERE json_extract(document, "$.item_id") = ? '
                'AND json_extract(document, "$.user_id") = ?',
                (item_id, user_id)
            ).fetchone()
            if item_row is None:
                raise ValueError('Inventory item not found')
            item = json.loads(item_row['document'])
            remaining = float(item.get('remaining_qty', 0)) + stock_delta
            if remaining < -1e-9:
                raise ValueError('Insufficient stock for this change')
            item['remaining_qty'] = max(0.0, remaining)
            counter = 'qty_purchased' if kind == 'purchase_orders' else 'qty_sold'
            item[counter] = max(0.0, float(item.get(counter, 0)) + (new_quantity - tracked_old))
            item['reorder_required'] = item['remaining_qty'] <= float(item.get('reorder_level', 0))
            item['updated_at'] = datetime.utcnow()

            if delete:
                conn.execute(f'DELETE FROM {kind} WHERE _id = ?', (old['_id'],))
            elif old:
                old.update(document)
                old['stock_applied'] = True
                conn.execute(f'UPDATE {kind} SET document = ? WHERE _id = ?',
                             (json.dumps(old, default=_json_default), old['_id']))
            else:
                document = dict(document)
                document['_id'] = str(uuid.uuid4())
                document['stock_applied'] = True
                conn.execute(f'INSERT INTO {kind} (_id, document) VALUES (?, ?)',
                             (document['_id'], json.dumps(document, default=_json_default)))

            conn.execute('UPDATE inventory_items SET document = ? WHERE _id = ?',
                         (json.dumps(item, default=_json_default), item_row['_id']))
            return document if old is None and not delete else old


class SQLiteCollection:
    def __init__(self, database, name):
        self.database = database
        self.name = name

    def find(self, query=None):
        query = query or {}
        with self.database._connect() as conn:
            rows = conn.execute(f'SELECT _id, document FROM {self.name}').fetchall()

        documents = [self._row_to_document(row) for row in rows]
        return [doc for doc in documents if self._matches(doc, query)]

    def find_one(self, query=None):
        for document in self.find(query):
            return document
        return None

    def insert_one(self, document):
        document = dict(document)
        document.setdefault('_id', str(uuid.uuid4()))
        document['_id'] = str(document['_id'])

        with self.database._connect() as conn:
            conn.execute(
                f'INSERT INTO {self.name} (_id, document) VALUES (?, ?)',
                (document['_id'], self._serialize(document))
            )

        return SimpleNamespace(inserted_id=document['_id'])

    def update_one(self, query, update):
        document = self.find_one(query)
        if not document:
            return SimpleNamespace(modified_count=0)

        if '$set' in update:
            document.update(update['$set'])
        else:
            document.update(update)

        with self.database._connect() as conn:
            conn.execute(
                f'UPDATE {self.name} SET document = ? WHERE _id = ?',
                (self._serialize(document), document['_id'])
            )

        return SimpleNamespace(modified_count=1)

    def delete_one(self, query):
        document = self.find_one(query)
        if not document:
            return SimpleNamespace(deleted_count=0)

        with self.database._connect() as conn:
            conn.execute(f'DELETE FROM {self.name} WHERE _id = ?', (document['_id'],))

        return SimpleNamespace(deleted_count=1)

    def count_documents(self, query=None):
        return len(self.find(query or {}))

    def aggregate(self, pipeline):
        documents = self.find()

        for stage in pipeline:
            if '$match' in stage:
                documents = [doc for doc in documents if self._matches(doc, stage['$match'])]
            elif '$group' in stage:
                group = stage['$group']
                total_spec = group.get('total', {})
                sum_field = total_spec.get('$sum', '').lstrip('$')
                total = sum(float(doc.get(sum_field, 0) or 0) for doc in documents)
                return [{'_id': group.get('_id'), 'total': total}]

        return documents

    def _row_to_document(self, row):
        document = json.loads(row['document'])
        document['_id'] = row['_id']
        return document

    def _serialize(self, document):
        return json.dumps(document, default=_json_default)

    def _matches(self, document, query):
        for key, expected in query.items():
            if document.get(key) != expected:
                return False
        return True
