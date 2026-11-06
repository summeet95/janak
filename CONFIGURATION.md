# Configuration Guide

## Environment Variables (.env)

The `.env` file contains all configuration settings for your application.

### Default .env File
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_change_in_production
MONGO_URI=mongodb://localhost:27017/inventory_app
JWT_SECRET=your_jwt_secret_change_in_production
```

## Configuration Options

### FLASK_ENV
- **development** - Debug mode enabled, auto-reloads on code changes
- **production** - Production mode, no debugging information exposed
- **testing** - Test mode for running tests

### FLASK_DEBUG
- **True** - Shows detailed error pages and auto-reloads
- **False** - Production mode, hides error details

### SECRET_KEY
- Used for session management and security
- **Change this in production!**
- Generate a secure key: `python -c "import secrets; print(secrets.token_hex(16))"`

### MONGO_URI
- MongoDB connection string
- Format: `mongodb://[username:password@]host:port/database`
- Default: `mongodb://localhost:27017/inventory_app`
- For MongoDB Atlas: `mongodb+srv://username:password@cluster.mongodb.net/database`

### JWT_SECRET
- Used for signing JWT tokens for authentication
- **Change this in production!**
- Generate a secure key: `python -c "import secrets; print(secrets.token_hex(32))"`

## Database Configuration

### Local MongoDB
```
MONGO_URI=mongodb://localhost:27017/inventory_app
```

### MongoDB with Authentication
```
MONGO_URI=mongodb://username:password@localhost:27017/inventory_app
```

### MongoDB Atlas (Cloud)
```
MONGO_URI=mongodb+srv://username:password@cluster0.abcd1.mongodb.net/inventory_app?retryWrites=true&w=majority
```

## Application Configuration (config.py)

Edit `config.py` to modify application settings:

```python
class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/inventory_app')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key-change-this')
    JWT_EXPIRATION = timedelta(hours=24)  # Token expiration time
```

### Changing Token Expiration
Edit the `JWT_EXPIRATION` in `config.py`:

```python
JWT_EXPIRATION = timedelta(hours=48)  # 48 hours
JWT_EXPIRATION = timedelta(days=7)    # 7 days
JWT_EXPIRATION = timedelta(minutes=30) # 30 minutes
```

## Production Setup

### For Live Deployment:

1. **Update Secret Keys**
   ```bash
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
   python -c "import secrets; print('JWT_SECRET=' + secrets.token_hex(64))"
   ```
   Add these to your `.env` file

2. **Set Flask Environment**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

3. **Use Production Database**
   - Set up MongoDB Atlas or self-hosted MongoDB with authentication
   - Update MONGO_URI with proper credentials

4. **Setup with WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

5. **Enable HTTPS**
   - Use a reverse proxy like Nginx
   - Configure SSL/TLS certificates

6. **Database Backups**
   - Enable MongoDB backup/replication
   - Set up automated backup procedures

## Port Configuration

To use a different port, modify `run.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8000)  # Changed to 8000
```

## CORS Configuration

Edit `app/__init__.py` to allow specific origins:

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Logging Configuration

Add logging to `run.py`:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Database Indexes

Indexes are automatically created by `init_db.py`:
- Unique indexes on `users.username` and `users.email`
- Compound indexes on user_id + item_id for faster queries

To add custom indexes, edit `init_db.py`:

```python
db['inventory_items'].create_index([('user_id', 1), ('remaining_qty', -1)])
```

## Troubleshooting Configuration Issues

### "Unable to connect to MongoDB"
- Check MONGO_URI in .env
- Verify MongoDB is running
- Check connection credentials

### "JWT Token Invalid"
- JWT_SECRET has changed
- Users need to login again with new tokens
- Check token expiration time

### "Port Already in Use"
- Change port in `run.py`
- Or kill existing process: `lsof -ti:5000 | xargs kill -9`

### "Database Connection Timeout"
- Increase timeout in MONGO_URI: `?serverSelectionTimeoutMS=10000`
- Check network connectivity to MongoDB server

## Performance Tuning

### Increase JWT Expiration
```python
JWT_EXPIRATION = timedelta(days=30)
```

### Connection Pooling
Add to MONGO_URI:
```
mongodb://localhost:27017/inventory_app?maxPoolSize=50&minPoolSize=10
```

### Database Caching
Can be added to routes for better performance

---

For more help, see README.md
