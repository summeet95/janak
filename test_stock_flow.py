import tempfile
import unittest
from unittest.mock import patch

from app import create_app, mongo
from config import config


class StockFlowTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        db_path = self.temp_dir.name + '/stock.sqlite'
        with patch.object(config['development'], 'SQLITE_PATH', db_path):
            self.app = create_app('development')
        self.client = self.app.test_client()
        self.client.post('/api/auth/register', json={
            'username': 'stock-test', 'email': 'stock@example.com', 'password': 'test'
        })
        token = self.client.post('/api/auth/login', json={
            'username': 'stock-test', 'password': 'test'
        }).json['token']
        self.headers = {'Authorization': f'Bearer {token}'}
        self.item_id = self.client.post('/api/inventory', headers=self.headers, json={
            'item_name': 'Widget', 'item_type': 'Product', 'item_category': 'Test',
            'qty_purchased': 5, 'remaining_qty': 5, 'reorder_level': 2
        }).json['item']['item_id']

    def stock(self):
        return self.client.get('/api/inventory', headers=self.headers).json['items'][0]

    def test_orders_change_stock_and_reverse_on_delete(self):
        purchase = self.client.post('/api/purchases', headers=self.headers, json={
            'supplier_id': 'supplier', 'item_id': self.item_id,
            'quantity': 10, 'unit_price': 2
        })
        self.assertEqual(purchase.status_code, 201)
        self.assertEqual(self.stock()['remaining_qty'], 15)

        sale = self.client.post('/api/sales', headers=self.headers, json={
            'customer_id': 'customer', 'item_id': self.item_id,
            'quantity': 12, 'unit_price': 3
        })
        self.assertEqual(sale.status_code, 201)
        self.assertEqual(self.stock()['remaining_qty'], 3)
        sale_id = sale.json['so']['so_id']
        purchase_id = purchase.json['po']['po_id']

        denied = self.client.post('/api/sales', headers=self.headers, json={
            'customer_id': 'customer', 'item_id': self.item_id,
            'quantity': 4, 'unit_price': 3
        })
        self.assertEqual(denied.status_code, 400)
        self.assertEqual(self.stock()['remaining_qty'], 3)
        self.assertEqual(self.client.put('/api/sales/' + sale_id, headers=self.headers,
                                         json={'quantity': 13}).status_code, 200)
        self.assertEqual(self.stock()['remaining_qty'], 2)
        self.assertTrue(self.stock()['reorder_required'])
        self.assertEqual(self.client.delete('/api/purchases/' + purchase_id,
                                            headers=self.headers).status_code, 400)
        self.assertEqual(self.client.delete('/api/inventory/' + self.item_id,
                                            headers=self.headers).status_code, 400)

        self.assertEqual(self.client.delete('/api/sales/' + sale_id,
                                            headers=self.headers).status_code, 200)
        self.assertEqual(self.client.delete('/api/purchases/' + purchase_id,
                                            headers=self.headers).status_code, 200)
        item = self.stock()
        self.assertEqual((item['remaining_qty'], item['qty_purchased'], item['qty_sold']),
                         (5, 5, 0))

    def test_old_order_updates_do_not_change_stock(self):
        user = mongo.db.users.find_one({'username': 'stock-test'})
        mongo.db.purchase_orders.insert_one({
            'po_id': 'OLD-1', 'user_id': user['_id'], 'item_id': self.item_id,
            'quantity': 2, 'unit_price': 1
        })
        self.assertEqual(self.client.put('/api/purchases/OLD-1', headers=self.headers,
                                         json={'quantity': 3}).status_code, 200)
        self.assertEqual(self.stock()['remaining_qty'], 5)
        self.assertEqual(self.client.delete('/api/purchases/OLD-1',
                                            headers=self.headers).status_code, 200)
        self.assertEqual(self.stock()['remaining_qty'], 5)


if __name__ == '__main__':
    unittest.main()
