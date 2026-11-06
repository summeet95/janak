"""
Diagnostic script to test the API
Run this after the app is running to verify everything works
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_api():
    print("=" * 50)
    print("AIC Inventory App - API Diagnostic Test")
    print("=" * 50)
    print()
    
    # Test 1: Register
    print("1. Testing Registration...")
    try:
        response = requests.post(
            f'{BASE_URL}/auth/register',
            headers={'Content-Type': 'application/json'},
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'test123'
            },
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code not in [201, 400]:
            print("   ✗ Unexpected status code")
        else:
            print("   ✓ Registration endpoint working")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    print()
    
    # Test 2: Login
    print("2. Testing Login...")
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            headers={'Content-Type': 'application/json'},
            json={
                'username': 'testuser',
                'password': 'test123'
            },
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        if response.status_code == 200 and data.get('success'):
            token = data.get('token')
            print(f"   ✓ Login successful")
            print(f"   Token received: {token[:20]}..." if token else "   ✗ No token received")
            
            # Test 3: Use token to get inventory
            print()
            print("3. Testing Protected Endpoint (Get Inventory)...")
            try:
                response = requests.get(
                    f'{BASE_URL}/inventory',
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=5
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
                
                if response.status_code == 200:
                    print("   ✓ Protected endpoint working")
                else:
                    print("   ✗ Protected endpoint failed")
            except Exception as e:
                print(f"   ✗ Error: {e}")
        else:
            print("   ✗ Login failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    print("=" * 50)
    print("Diagnostic test complete!")
    print("=" * 50)

if __name__ == '__main__':
    print()
    print("Make sure the Flask app is running (run.bat)")
    print("Make sure MongoDB is running")
    print()
    input("Press Enter to start tests...")
    print()
    
    test_api()
