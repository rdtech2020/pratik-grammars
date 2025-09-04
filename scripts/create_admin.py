#!/usr/bin/env python3
"""
Create Admin User Script

This script creates an admin user for the Grammar Correction API.
Run this script after setting up the database to create the first admin user.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from grammar_app.database import SessionLocal, engine
from grammar_app.models import Base, User
from grammar_app.crud import create_admin_user
from config.settings import settings


def create_admin_user(email: str, full_name: str, password: str):
    """Create an admin user in the database."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            return existing_admin
        
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists. Updating to admin role...")
            existing_user.role = "admin"
            db.commit()
            db.refresh(existing_user)
            print(f"User {existing_user.email} is now an admin!")
            return existing_user
        
        # Create new admin user using the CRUD function
        admin_user = create_admin_user(db, email=email, full_name=full_name, password=password)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Full Name: {admin_user.full_name}")
        print(f"   Role: {admin_user.role}")
        print(f"   ID: {admin_user.id}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function to create admin user."""
    print("🚀 Creating Admin User for Grammar Correction API")
    print("=" * 50)
    
    # Get admin details from environment variables or use defaults
    admin_email = os.getenv("ADMIN_EMAIL", "admin@grammar-api.com")
    admin_name = os.getenv("ADMIN_NAME", "System Administrator")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    print(f"Admin Email: {admin_email}")
    print(f"Admin Name: {admin_name}")
    print(f"Admin Password: {admin_password}")
    print()
    
    # If environment variables are set, create admin automatically
    if os.getenv("ADMIN_EMAIL") and os.getenv("ADMIN_PASSWORD"):
        print("✅ Environment variables detected. Creating admin user automatically...")
        try:
            admin_user = create_admin_user(admin_email, admin_name, admin_password)
            print()
            print("🎉 Admin user setup complete!")
            print("You can now use this account to access admin-only endpoints.")
            print()
            print("Example login:")
            print(f"POST /users/login")
            print(f"Body: {{'email': '{admin_email}', 'password': '{admin_password}'}}")
        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")
            sys.exit(1)
    else:
        # Confirm creation only for default values
        confirm = input("Do you want to create this admin user? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Admin user creation cancelled.")
            return
        
        try:
            admin_user = create_admin_user(admin_email, admin_name, admin_password)
            print()
            print("🎉 Admin user setup complete!")
            print("You can now use this account to access admin-only endpoints.")
            print()
            print("Example login:")
            print(f"POST /users/login")
            print(f"Body: {{'email': '{admin_email}', 'password': '{admin_password}'}}")
            
        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
