#!/usr/bin/env python3
"""
My Prabh - Google Cloud Entry Point
Abhay's heartbroken system deployed to the cloud
"""

# Import Abhay's main application
from app_abhay_version import app

# Google Cloud App Engine entry point
if __name__ == '__main__':
    # This will be called by gunicorn in production
    app.run(debug=False, host='0.0.0.0', port=8080)