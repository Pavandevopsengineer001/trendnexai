#!/usr/bin/env python
"""
Simple test script to validate admin authentication works correctly
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, '/home/pavan-kalyan-penchikalapati/Desktop/trendnexai/backend')

try:
    from app.security import authenticate_user
    
    # Test 1: Try authenticating with correct credentials
    print("\n" + "="*60)
    print("Testing Admin Authentication")
    print("="*60 + "\n")
    
    username = "admin"
    password = "admin"
    
    print(f"Testing credentials:")
    print(f"  Username: {username}")
    print(f"  Password: {password}\n")
    
    user = authenticate_user(username, password)
    
    if user:
        print("✓ Login successful!")
        print(f"  User: {user.username}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print("\n✓✓✓ Admin authentication is WORKING!")
    else:
        print("✗ Login failed - credentials rejected")
        print("\nTrying with alternate credentials...")
        user2 = authenticate_user(username, "wrongpassword")
        if user2:
            print("Unexpected: wrong password accepted!")
        else:
            print("Correct behavior: wrong password rejected")
            
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()
