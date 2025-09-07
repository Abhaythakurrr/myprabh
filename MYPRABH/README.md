# MyPrabh MVP - AI Companion Platform

A complete MVP for creating personalized AI companions with memories, emotions, and authentic conversations.

## 🚀 Features

### 🌟 Landing Page
- Professional design with love/lofi theme
- Real-time user statistics
- Early access signup with survey
- Complete legal pages (Terms, Privacy, Refund)

### 🤖 AI Companion Creation
- Custom character creation with personality traits
- Story and memory input system
- Natural conversation generation
- Character-specific responses

### 📊 Analytics & Database
- SQLite database for user data
- Real-time statistics tracking
- Email notifications for signups
- User activity monitoring

### 🎨 Beautiful UI/UX
- Responsive design for all devices
- Animated elements and interactions
- Professional branding and styling
- Intuitive user experience

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with CSS Variables
- **Email**: SMTP integration
- **Hosting**: Free tier compatible (Railway, Render, Heroku)

## 📋 Setup Instructions

### Local Development

1. **Clone and Setup**
```bash
cd MYPRABH
pip install -r requirements.txt
```

2. **Environment Variables**
```bash
export EMAIL_PASSWORD="your_email_password"  # Optional for email notifications
```

3. **Run Application**
```bash
python app.py
```

4. **Access Application**
- Open http://localhost:5000
- Landing page with all features
- Create account and test AI companions

### Free Hosting Deployment

#### Option 1: Railway (Recommended)
1. Create account at railway.app
2. Connect GitHub repository
3. Deploy automatically
4. Set environment variables in Railway dashboard

#### Option 2: Render
1. Create account at render.com
2. Connect GitHub repository
3. Choose "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`

#### Option 3: Heroku
1. Create account at heroku.com
2. Install Heroku CLI
3. Create Procfile: `web: python app.py`
4. Deploy with git

## 📁 Project Structure

```
MYPRABH/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── myprabh.db            # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── landing.html      # Landing page
│   ├── early_access.html # Early access form
│   ├── create_account.html # Account creation
│   ├── dashboard.html    # User dashboard
│   ├── create_prabh.html # AI creation form
│   ├── chat.html         # Chat interface
│   ├── terms.html        # Terms of service
│   ├── privacy.html      # Privacy policy
│   └── refund.html       # Refund policy
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   │   ├── landing.css  # Landing page styles
│   │   ├── forms.css    # Form styles
│   │   └── legal.css    # Legal page styles
│   └── js/              # JavaScript files
│       └── landing.js   # Landing page interactions
└── README.md            # This file
```

## 🎯 Key Features Implemented

### 1. Professional Landing Page
- Hero section with animated elements
- Feature showcase with icons and descriptions
- How it works step-by-step guide
- Use cases and pricing sections
- Real-time statistics display
- Call-to-action buttons

### 2. Early Access System
- Comprehensive survey form
- Email notifications to abhay@aiprabh.com
- User interest and demographic tracking
- Automatic database storage
- Success/error handling

### 3. User Account System
- Simple registration process
- Session management
- User dashboard
- Account persistence

### 4. AI Companion Creation
- Story input system
- Character trait definition
- Personality customization
- Natural response generation

### 5. Chat Interface
- Real-time messaging
- Character-specific responses
- Conversation history
- Emotional context

### 6. Analytics Dashboard
- Real-time user statistics
- Early access tracking
- Activity monitoring
- Public statistics display

### 7. Legal Compliance
- Complete Terms of Service
- Privacy Policy with GDPR considerations
- Refund Policy
- Cookie and data handling

## 🔧 Configuration

### Email Setup (Optional)
Set environment variable for email notifications:
```bash
EMAIL_PASSWORD="your_app_password"
```

### Database
SQLite database is automatically created on first run with tables:
- users
- early_signups
- prabh_instances
- chat_sessions
- analytics

## 📊 Analytics Features

### Real-time Statistics
- Total users created
- Total AI companions
- Early access signups
- Active users (24h)

### Data Collection
- User registration events
- AI companion creation
- Chat message counts
- Page visits and interactions

## 🎨 Design Features

### Theme
- Love/romantic color scheme
- Lofi aesthetic elements
- Gradient backgrounds
- Soft shadows and rounded corners

### Animations
- Floating hearts
- Typing animations
- Scroll-triggered animations
- Hover effects
- Loading states

### Responsive Design
- Mobile-first approach
- Tablet optimization
- Desktop enhancement
- Touch-friendly interactions

## 🚀 Deployment Checklist

- [ ] Set up hosting platform account
- [ ] Configure environment variables
- [ ] Test database creation
- [ ] Verify email functionality
- [ ] Test all user flows
- [ ] Check mobile responsiveness
- [ ] Validate legal pages
- [ ] Monitor analytics

## 📈 Growth Features

### Viral Mechanics
- Public statistics display
- Social sharing buttons
- Referral system ready
- Community features planned

### Monetization Ready
- Subscription system framework
- Payment integration ready
- Usage tracking implemented
- Premium features planned

## 🔒 Security Features

- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure session management
- Data encryption ready

## 📞 Support

For questions or issues:
- Email: abhay@aiprabh.com
- Create GitHub issue
- Check documentation

## 🎉 Launch Ready

This MVP is production-ready with:
- Professional design
- Complete user flows
- Legal compliance
- Analytics tracking
- Free hosting compatibility
- Scalable architecture

Perfect for launching, gathering user feedback, and iterating based on real user data!

---

*Made with 💖 for meaningful AI connections*