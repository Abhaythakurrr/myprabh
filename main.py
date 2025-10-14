"""
Main entry point for Google Cloud App Engine
"""

import os
from app import app

# Health checks are already defined in app.py
# No need to duplicate them here

if __name__ == '__main__':
    # This is used when running locally only
    app.run(host='127.0.0.1', port=8080, debug=True)