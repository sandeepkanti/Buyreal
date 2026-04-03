#!/usr/bin/env python
"""
Setup script for BuyReal project
Run this after copying all code files
"""

import os
import sys
import django

def run_command(cmd):
    print(f"\n>>> Running: {cmd}")
    result = os.system(cmd)
    if result != 0:
        print(f"Command failed with exit code {result}")
        return False
    return True

def main():
    print("=" * 50)
    print("BuyReal Setup Script")
    print("=" * 50)
    
    # Run migrations
    print("\n1. Creating migrations...")
    run_command("python manage.py makemigrations users")
    run_command("python manage.py makemigrations shops")
    run_command("python manage.py makemigrations products")
    run_command("python manage.py makemigrations orders")
    run_command("python manage.py makemigrations chat")
    
    print("\n2. Applying migrations...")
    run_command("python manage.py migrate")
    
    print("\n3. Setting up initial data...")
    run_command("python manage.py setup_initial_data")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Create superuser: python manage.py createsuperuser")
    print("2. Run server: python manage.py runserver")
    print("3. Open http://localhost:8000")

if __name__ == "__main__":
    main()