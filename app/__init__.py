from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import config
from app.local_db import SQLiteMongo
import os
import sys

mongo = SQLiteMongo()

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    if getattr(sys, 'frozen', False):
        resource_dir = sys._MEIPASS
        static_folder = os.path.join(resource_dir, 'app', 'static')
        template_folder = os.path.join(resource_dir, 'app', 'templates')
    else:
        static_folder = 'static'
        template_folder = 'templates'

    app = Flask(__name__, static_folder=static_folder, static_url_path='/static', template_folder=template_folder)
    app.config.from_object(config[config_name])
    
    # Initialize local SQLite database
    mongo.init_app(app)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from app.routes import auth_bp, inventory_bp, suppliers_bp, customers_bp, purchases_bp, sales_bp, receipts_bp, payments_bp, dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(dashboard_bp)
    
    @app.route('/')
    def login():
        return render_template('login.html')
    
    @app.route('/login.html')
    def login_page():
        return render_template('login.html')
    
    @app.route('/dashboard.html')
    def dashboard():
        return render_template('dashboard.html')
    
    return app
