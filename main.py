"""
Main entry point for Google Cloud App Engine
"""

import os
from app import app

# Add health check endpoint for Google Cloud
@app.route('/health')
def health_check():
    """Health check endpoint for Google Cloud Load Balancer"""
    return {'status': 'healthy', 'service': 'my-prabh'}, 200

# Add readiness check
@app.route('/ready')
def readiness_check():
    """Readiness check for Google Cloud"""
    return {'status': 'ready'}, 200

if __name__ == '__main__':
    # This is used when running locally only
    app.run(host='127.0.0.1', port=8080, debug=True)