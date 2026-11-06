import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app import mongo

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_value):
    """Verify password against hash"""
    return hash_password(password) == hash_value

def create_jwt_token(user_id, username):
    """Create JWT token for user"""
    payload = {
        'user_id': str(user_id),
        'username': username,
        'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION'],
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    print(f"Created token for user {username}: {token[:50]}...")
    return token

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
        print(f"Token verified for user: {payload.get('username')}")
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                print("Invalid token format in header")
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            print("No token provided")
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            print("Token verification failed")
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Verify user still exists
        user_id_str = payload['user_id']
        user = mongo.db.users.find_one({'_id': user_id_str})
        
        if not user:
            print(f"User not found: {user_id_str}")
            return jsonify({'message': 'User not found'}), 401
        
        request.current_user = payload
        return f(*args, **kwargs)
    
    return decorated

def register_user(username, email, password):
    """Register new user"""
    # Check if user exists
    if mongo.db.users.find_one({'username': username}):
        print(f"Username already exists: {username}")
        return {'success': False, 'message': 'Username already exists'}
    
    if mongo.db.users.find_one({'email': email}):
        print(f"Email already registered: {email}")
        return {'success': False, 'message': 'Email already registered'}
    
    # Create user
    user = {
        'username': username,
        'email': email,
        'password': hash_password(password),
        'created_at': datetime.utcnow(),
        'active': True
    }
    
    result = mongo.db.users.insert_one(user)
    user_id = str(result.inserted_id)
    print(f"User registered: {username} with ID: {user_id}")
    
    return {
        'success': True,
        'message': 'User registered successfully',
        'user_id': user_id
    }

def login_user(username, password):
    """Authenticate user and return token"""
    user = mongo.db.users.find_one({'username': username})
    
    if not user:
        print(f"Login failed: User not found - {username}")
        return {'success': False, 'message': 'Invalid username or password'}
    
    if not verify_password(password, user['password']):
        print(f"Login failed: Wrong password - {username}")
        return {'success': False, 'message': 'Invalid username or password'}
    
    if not user.get('active', True):
        print(f"Login failed: User inactive - {username}")
        return {'success': False, 'message': 'User account is disabled'}
    
    user_id = str(user['_id'])
    print(f"Login successful: {username} (ID: {user_id})")
    
    token = create_jwt_token(user_id, user['username'])
    
    return {
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user_id,
            'username': user['username'],
            'email': user['email']
        }
    }
