#!/usr/bin/env python
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'course_management.settings')

# Import Django and configure
import django
django.setup()

from django.conf import settings

print("=== Django Settings Debug ===")
print(f"Settings module: {settings.SETTINGS_MODULE}")
print(f"DEBUG: {settings.DEBUG}")
print(f"BASE_DIR: {settings.BASE_DIR}")
print(f"DATABASES: {settings.DATABASES}")

# Try to import the base settings directly
print("\n=== Direct Import Test ===")
try:
    from course_management.settings.base import DATABASES as BASE_DATABASES
    print(f"Base DATABASES: {BASE_DATABASES}")
except Exception as e:
    print(f"Error importing base settings: {e}")

# Check if there are any other settings files
print("\n=== Settings Files ===")
import course_management.settings
print(f"Settings package: {course_management.settings}")
print(f"Settings file: {course_management.settings.__file__}")
