"""
Payment Service for My Prabh
Handles Razorpay integration for premium subscriptions
"""

import os
import razorpay
import hmac
import hashlib
from datetime import datetime, timedelta

class PaymentService:
    """Razorpay payment service for My Prabh subscriptions"""
    
    def __init__(self):
        self.key_id = os.getenv('RAZORPAY_KEY_ID')
        self.key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        
        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            print(f"✅ Razorpay payment service initialized (Live: {self.key_id.startswith('rzp_live')})")
        else:
            self.client = None
            print("⚠️ Razorpay credentials not found")
    
    def create_subscription_order(self, user_id, plan_type, amount):
        """Create Razorpay order for subscription"""
        if not self.client:
            return {'error': 'Payment service not configured'}
        
        try:
            # Define subscription plans
            plans = {
                'basic': {'amount': 299, 'duration': 30, 'name': 'Basic Plan'},
                'premium': {'amount': 599, 'duration': 30, 'name': 'Premium Plan'},
                'pro': {'amount': 999, 'duration': 30, 'name': 'Pro Plan'}
            }
            
            if plan_type not in plans:
                return {'error': 'Invalid plan type'}
            
            plan = plans[plan_type]
            
            # Create Razorpay order
            order_data = {
                'amount': plan['amount'] * 100,  # Amount in paise
                'currency': 'INR',
                'receipt': f'myprabh_{user_id}_{plan_type}_{int(datetime.now().timestamp())}',
                'notes': {
                    'user_id': user_id,
                    'plan_type': plan_type,
                    'plan_name': plan['name'],
                    'duration_days': plan['duration']
                }
            }
            
            order = self.client.order.create(data=order_data)
            
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': self.key_id,
                'plan': plan
            }
            
        except Exception as e:
            print(f"Payment order creation error: {e}")
            return {'error': 'Failed to create payment order'}
    
    def verify_payment(self, payment_data):
        """Verify Razorpay payment signature"""
        if not self.client:
            return {'error': 'Payment service not configured'}
        
        try:
            # Extract payment details
            razorpay_order_id = payment_data.get('razorpay_order_id')
            razorpay_payment_id = payment_data.get('razorpay_payment_id')
            razorpay_signature = payment_data.get('razorpay_signature')
            
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return {'error': 'Missing payment details'}
            
            # Verify signature
            generated_signature = hmac.new(
                self.key_secret.encode('utf-8'),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if generated_signature == razorpay_signature:
                # Get payment details from Razorpay
                payment = self.client.payment.fetch(razorpay_payment_id)
                
                return {
                    'success': True,
                    'verified': True,
                    'payment_id': razorpay_payment_id,
                    'order_id': razorpay_order_id,
                    'amount': payment['amount'],
                    'status': payment['status'],
                    'method': payment['method']
                }
            else:
                return {'error': 'Payment verification failed'}
                
        except Exception as e:
            print(f"Payment verification error: {e}")
            return {'error': 'Payment verification failed'}
    
    def get_subscription_plans(self):
        """Get available subscription plans"""
        return {
            'basic': {
                'name': 'Basic Plan',
                'price': 299,
                'duration': '30 days',
                'features': [
                    '1 AI Prabh companion',
                    'Unlimited conversations',
                    'Basic personality traits',
                    'Email support'
                ]
            },
            'premium': {
                'name': 'Premium Plan',
                'price': 599,
                'duration': '30 days',
                'features': [
                    '3 AI Prabh companions',
                    'Unlimited conversations',
                    'Advanced personality traits',
                    'Custom story integration',
                    'Priority support',
                    'Memory enhancement'
                ]
            },
            'pro': {
                'name': 'Pro Plan',
                'price': 999,
                'duration': '30 days',
                'features': [
                    'Unlimited AI Prabh companions',
                    'Unlimited conversations',
                    'Premium personality traits',
                    'Advanced story integration',
                    'Voice messages (coming soon)',
                    'Priority support',
                    'Advanced memory system',
                    'Custom AI training'
                ]
            }
        }

# Global instance
payment_service = PaymentService()