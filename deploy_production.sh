#!/bin/bash

# 🚀 My Prabh - Production Deployment Script
# This script deploys My Prabh to Google Cloud Run with all environment variables

echo "🚀 Deploying My Prabh to Production..."

# Set project
gcloud config set project myprabh

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable firebase.googleapis.com

# Create Firestore database if it doesn't exist
echo "🔥 Setting up Firestore database..."
gcloud firestore databases create --region=us-central --quiet 2>/dev/null || echo "Firestore database already exists"

# Deploy to Cloud Run with all environment variables
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy myprabh \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=myprabh,FIREBASE_PROJECT_ID=myprabh,SECRET_KEY=myprabh-production-secret-key-2024-secure,FLASK_ENV=production,ADMIN_EMAIL=abhay@aiprabh.com,OPENROUTER_API_KEY=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,RAZORPAY_KEY_ID=rzp_live_RFCUrmIElPNS5m,RAZORPAY_KEY_SECRET=IzybX6ykve4VJ8GxldZhVJEC,WORKSPACE_EMAIL=noreply@aiprabh.com"

echo "✅ Deployment complete!"
echo "🌐 Your My Prabh platform is now live!"
echo "📱 Visit: https://myprabh-[hash]-uc.a.run.app"
echo ""
echo "🔧 Next steps:"
echo "1. Set up custom domain (optional)"
echo "2. Configure Google OAuth client ID"
echo "3. Set up Google Workspace service account for emails"
echo "4. Test all features"
echo ""
echo "💖 My Prabh is ready for users!"