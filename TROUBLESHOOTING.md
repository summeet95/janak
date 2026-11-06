# FAQ & Troubleshooting Guide

## Frequently Asked Questions

### General Questions

#### Q: What's the difference between this and the Google Sheets version?
**A:** This is a complete rewrite:
- **Google Sheets**: Cloud-based, limited functionality
- **Local Version**: Desktop app, full features, local database, faster, more secure

#### Q: Do I need an internet connection?
**A:** No. Everything runs locally on your computer (except if you use MongoDB Atlas).

#### Q: Can multiple people use it at the same time?
**A:** Yes! Each user has a separate login and their data is isolated.

#### Q: Can I use this on a network?
**A:** Yes! Change `host='localhost'` to `host='0.0.0.0'` in run.py, then others can access via `http://your-ip:5000`

#### Q: Is my data secure?
**A:** Yes:
- Passwords are hashed
- User data is isolated
- Authentication is required
- Runs on your own computer

#### Q: Can I backup my data?
**A:** Yes! MongoDB data is stored in a database file that can be backed up.

---

## Installation Troubleshooting

### Problem: Python not found
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Download Python from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart command prompt
4. Try again: `python --version`

### Problem: MongoDB Connection Failed
```
Error: Unable to connect to MongoDB
```

**Solution:**
1. Download MongoDB from https://www.mongodb.com/try/download/community
2. Run MSI installer
3. Check "Install MongoDB as a Service"
4. Start MongoDB:
   - Press `Win + R`
   - Type `services.msc`
   - Find "MongoDB Server"
   - Click "Start"

### Problem: Port Already in Use
```
Address already in use
```

**Solution 1** - Change the port:
- Edit `run.py`
- Change `port=5000` to `port=8000` (or another number)

**Solution 2** - Kill existing process:
- Find what's using port 5000: `netstat -ano | findstr :5000`
- Kill it: `taskkill /PID <PID> /F`

### Problem: Virtual Environment Not Found
```
'venv' is not recognized
```

**Solution:**
1. Run `setup.bat` again
2. It will recreate the virtual environment

### Problem: Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
1. Make sure virtual environment is activated
2. Run: `pip install -r requirements.txt`
3. Verify: `pip list | grep -i flask`

---

## Runtime Troubleshooting

### Problem: Cannot Login
```
Invalid username or password (but I'm sure it's correct)
```

**Solution:**
1. Password is case-sensitive
2. Check CAPS LOCK
3. Passwords must be at least 6 characters
4. Try registering a new account to test

### Problem: Page Won't Load
```
This site can't be reached - localhost:5000 refused to connect
```

**Solution:**
1. Check if Flask is running: Should see "Running on http://127.0.0.1:5000"
2. Check if MongoDB is running (Services > MongoDB Server)
3. Restart Flask server
4. Try accessing: `http://localhost:5000`

### Problem: Database Connection Error
```
Error connecting to database
```

**Solution:**
1. Check MongoDB is running: `Services > MongoDB Server > Start`
2. Verify connection string in `.env`:
   - Should be: `mongodb://localhost:27017/inventory_app`
3. Check port 27017 is not blocked by firewall
4. Restart MongoDB service

### Problem: Data Not Saving
```
Added item but it disappeared after refresh
```

**Solution:**
1. Check MongoDB is running
2. Check browser console for errors (F12)
3. Check server logs in terminal
4. Try adding again
5. If persistent, run: `python init_db.py`

### Problem: Slowness
```
Application is very slow
```

**Solution:**
1. Check MongoDB: `Services > MongoDB Server > Status`
2. Check if hard drive full
3. Close other applications
4. Check available RAM
5. Restart Flask server

---

## Data Management

### How to Backup Data

**Automatic Backup:**
```bash
# Export all collections
mongodump --db inventory_app --out ./backup
```

**Restore from Backup:**
```bash
# Import collections
mongorestore --db inventory_app ./backup/inventory_app
```

### How to Clear All Data
```bash
# Connect to MongoDB
mongo

# In MongoDB shell
use inventory_app
db.dropDatabase()
```

### How to Keep Data Between Sessions
- Data is automatically saved to MongoDB
- Even after closing app, data persists
- Can access data immediately after restarting

---

## Performance Tips

### Slow Database Queries
1. **Increase Connection Timeout:**
   - Edit `.env`
   - Change: `MONGO_URI=mongodb://localhost:27017/inventory_app?serverSelectionTimeoutMS=10000`

2. **Rebuild Indexes:**
   - Run: `python init_db.py`
   - This recreates all indexes

3. **Check MongoDB Status:**
   - Run: `mongo --eval "db.adminCommand('status')"`

### Improve Browser Performance
1. Clear browser cache
2. Close unused tabs
3. Use recent browser version
4. Disable browser extensions
5. Try different browser

---

## Security Issues

### Problem: "Suspicious Activity" Warning
**Solution:**
- This is normal for localhost
- Click "Advanced" then "Proceed"
- (Only happens in HTTPS when deployed)

### Problem: Password Strength
**Best Practices:**
- Use 8+ characters
- Mix uppercase, lowercase, numbers, symbols
- Don't use common words
- Don't share passwords

### Problem: Token Expiration
```
You've been logged out
```
**Solution:**
- Tokens expire after 24 hours (by default)
- Just login again
- To change expiration, edit `config.py`:
  ```python
  JWT_EXPIRATION = timedelta(hours=48)  # 48 hours
  ```

---

## Common Errors & Fixes

### Error: CORS Error in Console
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:**
- This shouldn't happen with included configuration
- If it does, run: `pip install Flask-CORS==4.0.0`
- Restart Flask

### Error: 405 Method Not Allowed
```
POST /api/inventory - 405 Method Not Allowed
```
**Solution:**
- Method doesn't exist for that endpoint
- Check request type (GET, POST, PUT, DELETE)
- Check endpoint URL is correct
- See README.md for correct endpoints

### Error: 404 Not Found
```
404 - The requested URL was not found
```
**Solution:**
- Check URL is correct
- Check Flask is running
- Try: `http://localhost:5000/login.html`

### Error: 500 Internal Server Error
```
Internal Server Error
```
**Solution:**
1. Check server logs (terminal window)
2. Check `.env` configuration
3. Check MongoDB connection
4. Restart Flask server
5. Run: `python init_db.py`

### Error: Token Invalid or Expired
```
Token is invalid or expired
```
**Solution:**
1. Logout (if possible)
2. Clear browser localStorage: F12 > Application > Clear All
3. Login again
4. Token will be refreshed

---

## Advanced Troubleshooting

### Enable Debug Logging
Edit `run.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
app.run(debug=True)
```

### Test MongoDB Connection Directly
```bash
python
>>> from pymongo import MongoClient
>>> client = MongoClient('mongodb://localhost:27017/')
>>> client.admin.command('ping')
{'ok': 1.0}
```

### Check Flask Configuration
```bash
python
>>> from app import create_app
>>> app = create_app()
>>> print(app.config)
```

### Monitor MongoDB
```bash
mongo
> db.currentOp()  # Show running operations
> db.stats()       # Database statistics
```

---

## Contact & Support

### For Issues:
1. Check this FAQ first
2. Check README.md
3. Check CONFIGURATION.md
4. Check browser console (F12)
5. Check Flask server terminal for errors

### Documentation:
- Flask: https://flask.palletsprojects.com/
- MongoDB: https://docs.mongodb.com/
- PyMongo: https://pymongo.readthedocs.io/

---

## Quick Reference Commands

```bash
# Start setup
setup.bat

# Run application
run.bat

# Initialize database manually
python init_db.py

# Test MongoDB
mongo

# Install dependencies
pip install -r requirements.txt

# Upgrade dependencies
pip install --upgrade -r requirements.txt
```

---

## Before You Call for Help

Please provide:
1. ✓ Error message (copy-paste)
2. ✓ Steps to reproduce
3. ✓ Screenshot if visual issue
4. ✓ Log output from terminal
5. ✓ Your system: Windows version, Python version, MongoDB version

---

## Known Limitations

- **No built-in backup** (use mongodump)
- **Single computer deployment** (no automatic scaling)
- **No email notifications** (can be added)
- **No mobile app** (only web)
- **English only** (can be translated)

---

## Planned Future Features

- [ ] Advanced reporting
- [ ] Export to Excel
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Email notifications
- [ ] Two-factor authentication
- [ ] Advanced security audit logging

---

Last Updated: May 3, 2026
Version: 1.0

For more help, refer to the complete documentation in README.md and CONFIGURATION.md
