"""
Firebase Authentication Service for My Prabh
Handles Google Auth, user management, and email notifications
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from flask import session, request
import requests
from datetime import datetime

class FirebaseAuth:
    """Firebase Authentication and user management"""
    
    def __init__(self):
        self._initialize_firebase()
        self.db = firestore.client()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            print("✅ Firebase already initialized")
        except ValueError:
            # Initialize Firebase with default credentials (Google Cloud Run)
            try:
                # Use default credentials in Google Cloud
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': 'myprabh'
                })
                print("✅ Firebase initialized with default credentials")
            except Exception as e:
                print(f"⚠️ Firebase initialization warning: {e}")
                # Initialize without credentials for local development
                firebase_admin.initialize_app()
    
    def verify_id_token(self, id_token):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def create_user_record(self, email, name, uid=None, phone_number=None, provider='google'):
        """Create user record in Firestore"""
        try:
            user_data = {
                'uid': uid,
                'email': email,
                'name': name,
                'phone_number': phone_number,
                'created_at': datetime.now(),
                'provider': provider,
                'is_active': True,
                'email_verified': True if provider == 'google' else False,
                'phone_verified': bool(phone_number),
                'total_prabhs': 0,
                'last_login': datetime.now(),
                'profile_complete': bool(email and name)
            }
            
            # Save to Firestore
            doc_ref = self.db.collection('users').document(uid or email)
            doc_ref.set(user_data)
            
            print(f"✅ User record created: {email}")
            return user_data
            
        except Exception as e:
            print(f"Error creating user record: {e}")
            return None
    
    def get_user_by_uid(self, uid):
        """Get user by Firebase UID"""
        try:
            doc = self.db.collection('users').document(uid).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_last_login(self, uid):
        """Update user's last login time"""
        try:
            self.db.collection('users').document(uid).update({
                'last_login': datetime.now()
            })
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    def update_user_phone(self, uid, phone_number):
        """Update user's phone number"""
        try:
            self.db.collection('users').document(uid).update({
                'phone_number': phone_number,
                'phone_verified': True,
                'updated_at': datetime.now()
            })
            print(f"✅ Phone number updated for user {uid}")
            return True
        except Exception as e:
            print(f"Error updating phone number: {e}")
            return False
    
    def verify_user_email(self, uid):
        """Mark user's email as verified"""
        try:
            self.db.collection('users').document(uid).update({
                'email_verified': True,
                'updated_at': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error verifying email: {e}")
            return False

# Global instance
firebase_auth = FirebaseAuth()