# Security Module - Human verification and face recognition
try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not available - face recognition disabled")

import base64
from io import BytesIO
import hashlib
import secrets
import time

class SecurityManager:
    """Handles security features including face recognition and human verification"""
    
    def __init__(self):
        self.face_cascade = None
        self.load_face_detector()
    
    def load_face_detector(self):
        """Load OpenCV face detector"""
        if not CV2_AVAILABLE:
            print("OpenCV not available - face detection disabled")
            return
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            print(f"Face detector not available: {e}")
    
    def verify_human_captcha(self, user_input: str, expected: str) -> bool:
        """Simple math captcha verification"""
        return user_input.strip().lower() == expected.strip().lower()
    
    def generate_math_captcha(self) -> dict:
        """Generate simple math captcha"""
        import random
        
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            answer = num1 + num2
            question = f"{num1} + {num2} = ?"
        else:
            # Ensure positive result
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
            question = f"{num1} - {num2} = ?"
        
        return {
            'question': question,
            'answer': str(answer),
            'token': self.generate_captcha_token()
        }
    
    def generate_captcha_token(self) -> str:
        """Generate secure captcha token"""
        return secrets.token_urlsafe(16)
    
    def detect_face_in_image(self, image_data: str) -> dict:
        """Detect face in base64 image data"""
        if not CV2_AVAILABLE:
            return {'success': False, 'error': 'OpenCV not available'}
            
        try:
            if not self.face_cascade:
                return {'success': False, 'error': 'Face detection not available'}
            
            # Decode base64 image
            image_data = image_data.split(',')[1] if ',' in image_data else image_data
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Generate face signature for comparison
                face_signature = self.generate_face_signature(gray, faces[0])
                return {
                    'success': True,
                    'faces_detected': len(faces),
                    'face_signature': face_signature
                }
            else:
                return {'success': False, 'error': 'No face detected'}
                
        except Exception as e:
            return {'success': False, 'error': f'Face detection failed: {str(e)}'
    
    def generate_face_signature(self, gray_image, face_coords) -> str:
        """Generate simple face signature for comparison"""
        if not CV2_AVAILABLE:
            return hashlib.md5(str(face_coords).encode()).hexdigest()
            
        x, y, w, h = face_coords
        face_roi = gray_image[y:y+h, x:x+w]
        
        # Resize to standard size
        face_roi = cv2.resize(face_roi, (100, 100))
        
        # Generate hash of face region
        face_hash = hashlib.md5(face_roi.tobytes()).hexdigest()
        return face_hash
    
    def compare_face_signatures(self, sig1: str, sig2: str, threshold: float = 0.8) -> bool:
        """Compare two face signatures"""
        # Simple comparison - in production use proper face recognition
        return sig1 == sig2
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Validate CSRF token"""
        return token == session_token
    
    def rate_limit_check(self, user_id: str, action: str, limit: int = 5, window: int = 300) -> bool:
        """Simple rate limiting"""
        # In production, use Redis or database
        # This is a basic implementation
        current_time = int(time.time())
        key = f"{user_id}:{action}:{current_time // window}"
        
        # For now, always allow (implement proper storage in production)
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input"""
        import re
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', user_input)
        return sanitized.strip()

# Global security manager
security_manager = SecurityManager()