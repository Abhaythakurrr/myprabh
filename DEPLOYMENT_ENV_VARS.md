# 🔐 Environment Variables for MyPrabh Deployment

## Required Environment Variables

Set these in your hosting platform (Railway, Render, etc.):

### **Razorpay Configuration**
```bash
RAZORPAY_KEY_ID=your_new_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key
```

### **Flask Configuration**
```bash
FLASK_ENV=production
```

## 🚨 Security Checklist

### ✅ **COMPLETED:**
- [x] Removed hardcoded API keys from code
- [x] All Razorpay keys now use environment variables
- [x] Code is secure and ready for deployment

### ⚠️ **YOU MUST DO:**
1. **Regenerate your Razorpay API key** in Razorpay Dashboard
2. **Set environment variables** in your hosting platform
3. **Test payment flow** after deployment

## 🚀 Deployment Steps

### **Railway.app:**
1. Go to your Railway project dashboard
2. Click "Variables" tab
3. Add the environment variables above
4. Redeploy your application

### **Render.com:**
1. Go to your service dashboard
2. Click "Environment" tab
3. Add the environment variables above
4. Save and redeploy

### **Other Platforms:**
Follow similar steps to set environment variables in your hosting platform.

## 🧪 Testing

After deployment, test:
1. Create account ✅
2. Create Prabh ✅
3. Payment flow ✅
4. Chat functionality ✅

## 📞 Support

If you encounter issues:
- Check environment variables are set correctly
- Verify new Razorpay key is active
- Check application logs for errors

Contact: abhay@aiprabh.com