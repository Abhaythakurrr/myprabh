"""
Firestore Database Service for My Prabh
Simple and efficient NoSQL database operations
"""

import os
from google.cloud import firestore
from datetime import datetime
import uuid

class FirestoreDB:
    """Firestore database service for My Prabh"""
    
    def __init__(self):
        # Initialize Firestore client with admin privileges
        from config.secure_config import config
        project_id = config.firebase_project_id
        
        try:
            # Try to initialize with service account (for admin access)
            self.db = firestore.Client(project=project_id)
            print(f"✅ Connected to Firestore project: {project_id}")
        except Exception as e:
            print(f"⚠️ Firestore connection warning: {e}")
            # Fallback initialization
            self.db = firestore.Client(project=project_id)
            
        self._ensure_database_setup()
    
    def _ensure_database_setup(self):
        """Ensure database collections exist"""
        try:
            # Test database connection and create initial collections if needed
            collections = ['users', 'prabhs', 'messages', 'memories', 'early_access']
            
            for collection_name in collections:
                # Check if collection exists by trying to get a document
                try:
                    docs = list(self.db.collection(collection_name).limit(1).stream())
                    print(f"✅ Collection '{collection_name}' exists")
                except Exception:
                    # Collection doesn't exist, create it with a placeholder document
                    self.db.collection(collection_name).document('_init').set({
                        'initialized': True,
                        'created_at': datetime.now(),
                        'collection': collection_name
                    })
                    print(f"✅ Created collection '{collection_name}'")
                    
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
            # Continue anyway - collections will be created when first used
    
    # User Management
    def create_user(self, email, name, password_hash):
        """Create a new user"""
        user_id = str(uuid.uuid4())
        user_data = {
            'user_id': user_id,
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'created_at': datetime.now(),
            'is_admin': False
        }
        
        self.db.collection('users').document(user_id).set(user_data)
        return user_id
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self.db.collection('users').where('email', '==', email).limit(1).stream()
        for user in users:
            return user.to_dict()
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    # Prabh Management
    def create_prabh(self, user_id, prabh_name, character_description, story_content, character_tags="", personality_traits=""):
        """Create a new Prabh companion"""
        prabh_id = str(uuid.uuid4())
        prabh_data = {
            'id': prabh_id,
            'user_id': user_id,
            'prabh_name': prabh_name,
            'character_description': character_description,
            'story_content': story_content,
            'character_tags': character_tags,
            'personality_traits': personality_traits,
            'created_at': datetime.now(),
            'is_trained': False
        }
        
        self.db.collection('prabhs').document(prabh_id).set(prabh_data)
        return prabh_id
    
    def get_user_prabhs(self, user_id):
        """Get all Prabhs for a user"""
        prabhs = self.db.collection('prabhs').where('user_id', '==', user_id).stream()
        return [prabh.to_dict() for prabh in prabhs]
    
    def get_prabh_by_id(self, prabh_id, user_id):
        """Get specific Prabh by ID"""
        doc = self.db.collection('prabhs').document(prabh_id).get()
        if doc.exists:
            prabh_data = doc.to_dict()
            if prabh_data.get('user_id') == user_id:
                return prabh_data
        return None
    
    # Chat Messages
    def save_chat_message(self, prabh_id, user_id, user_message, ai_response):
        """Save chat message"""
        message_id = str(uuid.uuid4())
        message_data = {
            'id': message_id,
            'prabh_id': prabh_id,
            'user_id': user_id,
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': datetime.now()
        }
        
        self.db.collection('messages').document(message_id).set(message_data)
        return message_id
    
    def get_chat_history(self, prabh_id, user_id, limit=10):
        """Get recent chat history"""
        messages = (self.db.collection('messages')
                   .where('prabh_id', '==', prabh_id)
                   .where('user_id', '==', user_id)
                   .order_by('timestamp', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
        
        return [msg.to_dict() for msg in messages]
    
    # Memory System
    def save_memory(self, prabh_id, user_id, memory_text, memory_type="general"):
        """Save user memory"""
        memory_id = str(uuid.uuid4())
        memory_data = {
            'id': memory_id,
            'prabh_id': prabh_id,
            'user_id': user_id,
            'memory_text': memory_text,
            'memory_type': memory_type,
            'created_at': datetime.now()
        }
        
        self.db.collection('memories').document(memory_id).set(memory_data)
        return memory_id
    
    def get_memories(self, prabh_id, user_id, limit=10):
        """Get user memories"""
        memories = (self.db.collection('memories')
                   .where('prabh_id', '==', prabh_id)
                   .where('user_id', '==', user_id)
                   .order_by('created_at', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
        
        return [memory.to_dict() for memory in memories]
    
    # Early Access Signups
    def save_early_access_signup(self, email, name=""):
        """Save early access signup"""
        signup_id = str(uuid.uuid4())
        signup_data = {
            'id': signup_id,
            'email': email,
            'name': name,
            'signup_date': datetime.now(),
            'status': 'pending'
        }
        
        self.db.collection('early_access').document(signup_id).set(signup_data)
        return signup_id
    
    # Subscription Management
    def create_subscription(self, subscription_data):
        """Create user subscription"""
        subscription_id = str(uuid.uuid4())
        subscription_data['id'] = subscription_id
        subscription_data['created_at'] = datetime.now()
        
        self.db.collection('subscriptions').document(subscription_id).set(subscription_data)
        
        # Update user subscription status
        self.db.collection('users').document(subscription_data['user_id']).update({
            'subscription_status': 'active',
            'subscription_plan': subscription_data['plan_type'],
            'subscription_end': subscription_data['end_date']
        })
        
        return subscription_id
    
    def get_user_subscription(self, user_id):
        """Get user's active subscription"""
        try:
            subscriptions = (self.db.collection('subscriptions')
                           .where('user_id', '==', user_id)
                           .where('status', '==', 'active')
                           .order_by('created_at', direction=firestore.Query.DESCENDING)
                           .limit(1)
                           .stream())
            
            for sub in subscriptions:
                return sub.to_dict()
            return None
        except Exception as e:
            print(f"Error getting subscription: {e}")
            return None
    
    # Enhanced Analytics
    def get_stats(self):
        """Get platform statistics"""
        try:
            # Count users
            users_count = len(list(self.db.collection('users').stream()))
            
            # Count Prabhs
            prabhs_count = len(list(self.db.collection('prabhs').stream()))
            
            # Count messages
            messages_count = len(list(self.db.collection('messages').stream()))
            
            # Count early access signups
            early_signups_count = len(list(self.db.collection('early_access').stream()))
            
            # Count active subscriptions
            active_subs = len(list(self.db.collection('subscriptions')
                                 .where('status', '==', 'active').stream()))
            
            return {
                'total_users': users_count,
                'total_prabhs': prabhs_count,
                'total_messages': messages_count,
                'early_signups': early_signups_count,
                'active_subscriptions': active_subs
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_users': 0,
                'total_prabhs': 0,
                'total_messages': 0,
                'early_signups': 0,
                'active_subscriptions': 0
            }
    
    def get_admin_stats(self):
        """Get comprehensive admin statistics"""
        try:
            # Basic stats
            stats = self.get_stats()
            
            # Today's activity
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # New users today
            new_users_today = len(list(self.db.collection('users')
                                     .where('created_at', '>=', today).stream()))
            
            # New Prabhs today
            new_prabhs_today = len(list(self.db.collection('prabhs')
                                      .where('created_at', '>=', today).stream()))
            
            # Messages today
            messages_today = len(list(self.db.collection('messages')
                                    .where('timestamp', '>=', today).stream()))
            
            stats.update({
                'new_users_today': new_users_today,
                'new_prabhs_today': new_prabhs_today,
                'messages_today': messages_today,
                'revenue_today': 0,  # Calculate from subscriptions
                'active_users_today': new_users_today  # Simplified
            })
            
            return stats
        except Exception as e:
            print(f"Error getting admin stats: {e}")
            return self.get_stats()
    
    def get_recent_users(self, limit=10):
        """Get recently registered users"""
        try:
            users = (self.db.collection('users')
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .limit(limit)
                    .stream())
            
            return [user.to_dict() for user in users]
        except Exception as e:
            print(f"Error getting recent users: {e}")
            return []
    
    def get_recent_prabhs(self, limit=10):
        """Get recently created Prabhs"""
        try:
            prabhs = (self.db.collection('prabhs')
                     .order_by('created_at', direction=firestore.Query.DESCENDING)
                     .limit(limit)
                     .stream())
            
            return [prabh.to_dict() for prabh in prabhs]
        except Exception as e:
            print(f"Error getting recent prabhs: {e}")
            return []
    
    def get_recent_messages(self, limit=20):
        """Get recent chat messages"""
        try:
            messages = (self.db.collection('messages')
                       .order_by('timestamp', direction=firestore.Query.DESCENDING)
                       .limit(limit)
                       .stream())
            
            return [msg.to_dict() for msg in messages]
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []
    
    def get_growth_stats(self, start_date, end_date):
        """Get growth statistics for date range"""
        try:
            # Users in date range
            users_growth = len(list(self.db.collection('users')
                                  .where('created_at', '>=', start_date)
                                  .where('created_at', '<', end_date)
                                  .stream()))
            
            # Prabhs in date range
            prabhs_growth = len(list(self.db.collection('prabhs')
                                   .where('created_at', '>=', start_date)
                                   .where('created_at', '<', end_date)
                                   .stream()))
            
            return {
                'new_users': users_growth,
                'new_prabhs': prabhs_growth,
                'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            }
        except Exception as e:
            print(f"Error getting growth stats: {e}")
            return {'new_users': 0, 'new_prabhs': 0}

# Global instance
firestore_db = FirestoreDB()