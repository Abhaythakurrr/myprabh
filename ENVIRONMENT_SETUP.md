# 🔧 Environment Variables Setup for My Prabh

## Google Cloud Run Environment Variables

Set these in your Google Cloud Run service:

### **Core Configuration**
```bash
GOOGLE_CLOUD_PROJECT=myprabh
FIREBASE_PROJECT_ID=myprabh
SECRET_KEY=myprabh-production-secret-key-2024-secure
FLASK_ENV=production
```

### **Firebase Authentication**
```bash
# Get this from Google Cloud Console > APIs & Services > Credentials
GOOGLE_CLIENT_ID=26708699201-YOUR_OAUTH_CLIENT_ID.apps.googleusercontent.com

# Firebase Web API Key (already configured in frontend)
FIREBASE_API_KEY=AIzaSyDLcA32A8FDafvtmuD3xFk9t3qIceAIM5I
```

### **Google Workspace Email**
```bash
# Service Account JSON for Gmail API
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"myprabh",...}

# Your professional email
WORKSPACE_EMAIL=noreply@aiprabh.com
```

### **AI Service**
```bash
# OpenRouter API Key for AI responses
OPENROUTER_API_KEY=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
```

### **Payment Integration**
```bash
# Razorpay LIVE credentials
RAZORPAY_KEY_ID=rzp_live_RFCUrmIElPNS5m
RAZORPAY_KEY_SECRET=IzybX6ykve4VJ8GxldZhVJEC
```

### **Admin Configuration**
```bash
ADMIN_EMAIL=abhay@aiprabh.com
```

## 🚀 Quick Setup Commands

### 1. Set Environment Variables in Cloud Run:
```bash
gcloud run services update myprabh \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=myprabh,FIREBASE_PROJECT_ID=myprabh,SECRET_KEY=myprabh-production-secret-key-2024-secure,FLASK_ENV=production,ADMIN_EMAIL=abhay@aiprabh.com,OPENROUTER_API_KEY=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,RAZORPAY_KEY_ID=rzp_live_RFCUrmIElPNS5m,RAZORPAY_KEY_SECRET=IzybX6ykve4VJ8GxldZhVJEC" \
  --region=us-central1
```

### 2. Enable Required APIs:
```bash
gcloud services enable firestore.googleapis.com
gcloud services enable firebase.googleapis.com
gcloud services enable gmail.googleapis.com
```

### 3. Set up Firestore Database:
```bash
gcloud firestore databases create --region=us-central
```

### 4. Configure Firestore Security Rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

## 🔑 Getting Missing Credentials

### **Google OAuth Client ID:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project "myprabh"
3. Go to APIs & Services > Credentials
4. Create OAuth 2.0 Client ID for Web Application
5. Add authorized domains: `myprabh.as.r.appspot.com`

### **Service Account for Gmail:**
1. Go to Google Cloud Console > IAM & Admin > Service Accounts
2. Create new service account
3. Grant Gmail API permissions
4. Download JSON key
5. Set as GOOGLE_SERVICE_ACCOUNT_JSON environment variable

### **Razorpay Credentials:**
1. Sign up at [Razorpay](https://razorpay.com/)
2. Go to Settings > API Keys
3. Generate Test/Live keys
4. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET

## ✅ Verification

After setup, your app should show:
```
✅ My Prabh Platform Starting...
✅ Firestore Database: Connected
✅ Firebase Auth: Enabled
✅ Email Service: Google Workspace
✅ Phone Verification: Enabled
✅ Environment: production
✅ Admin: abhay@aiprabh.com
```

## 🎯 Test Features

1. **Landing Page**: Visit your app URL
2. **Registration**: Create new account
3. **Google Sign-In**: Test OAuth login
4. **Create Prabh**: Test AI companion creation
5. **Chat**: Test AI conversations
6. **Admin Dashboard**: Login as admin
7. **Payments**: Test subscription flow

Your My Prabh platform is ready for production! 🚀💖