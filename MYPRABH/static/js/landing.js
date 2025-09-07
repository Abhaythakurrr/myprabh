// MyPrabh Landing Page JavaScript

class LandingPage {
    constructor() {
        this.initializeAnimations();
        this.initializeMobileMenu();
        this.initializeScrollEffects();
        this.initializeStatsCounter();
        
        console.log('💖 MyPrabh Landing Page initialized');
    }
    
    initializeAnimations() {
        // Floating hearts animation
        this.animateFloatingHearts();
        
        // Typing animation for hero text
        this.initializeTypingAnimation();
        
        // Intersection Observer for scroll animations
        this.initializeScrollAnimations();
    }
    
    animateFloatingHearts() {
        const hearts = document.querySelectorAll('.floating-hearts .heart');
        
        hearts.forEach((heart, index) => {
            // Random animation delays and durations
            const delay = Math.random() * 2;
            const duration = 4 + Math.random() * 2;
            
            heart.style.animationDelay = `${delay}s`;
            heart.style.animationDuration = `${duration}s`;
            
            // Add random movement
            setInterval(() => {
                const x = Math.random() * 20 - 10; // -10 to 10
                const y = Math.random() * 20 - 10; // -10 to 10
                heart.style.transform = `translate(${x}px, ${y}px)`;
            }, 3000 + Math.random() * 2000);
        });
    }
    
    initializeTypingAnimation() {
        const typingElement = document.querySelector('.gradient-text');
        if (!typingElement) return;
        
        const phrases = [
            'AI Companion',
            'Digital Soulmate',
            'Virtual Partner',
            'AI Friend',
            'Emotional Connection'
        ];
        
        let currentPhrase = 0;
        let currentChar = 0;
        let isDeleting = false;
        
        const typeSpeed = 100;
        const deleteSpeed = 50;
        const pauseTime = 2000;
        
        function type() {
            const current = phrases[currentPhrase];
            
            if (isDeleting) {
                typingElement.textContent = current.substring(0, currentChar - 1);
                currentChar--;
                
                if (currentChar === 0) {
                    isDeleting = false;
                    currentPhrase = (currentPhrase + 1) % phrases.length;
                    setTimeout(type, 500);
                    return;
                }
                
                setTimeout(type, deleteSpeed);
            } else {
                typingElement.textContent = current.substring(0, currentChar + 1);
                currentChar++;
                
                if (currentChar === current.length) {
                    isDeleting = true;
                    setTimeout(type, pauseTime);
                    return;
                }
                
                setTimeout(type, typeSpeed);
            }
        }
        
        // Start typing animation after a delay
        setTimeout(type, 1000);
    }
    
    initializeScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe elements for animation
        const animateElements = document.querySelectorAll(
            '.feature-card, .step, .use-case, .pricing-card'
        );
        
        animateElements.forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });
    }
    
    initializeMobileMenu() {
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        if (mobileToggle && navLinks) {
            mobileToggle.addEventListener('click', () => {
                navLinks.classList.toggle('mobile-open');
                mobileToggle.classList.toggle('active');
            });
        }
    }
    
    initializeScrollEffects() {
        let lastScrollY = window.scrollY;
        const navbar = document.querySelector('.navbar');
        
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            // Navbar hide/show on scroll
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                navbar.classList.add('navbar-hidden');
            } else {
                navbar.classList.remove('navbar-hidden');
            }
            
            // Navbar background opacity
            if (currentScrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
            
            lastScrollY = currentScrollY;
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    initializeStatsCounter() {
        const statsNumbers = document.querySelectorAll('.stat-number');
        let hasAnimated = false;
        
        const animateStats = () => {
            if (hasAnimated) return;
            hasAnimated = true;
            
            statsNumbers.forEach(stat => {
                const target = parseInt(stat.textContent);
                const duration = 2000;
                const increment = target / (duration / 16);
                let current = 0;
                
                const updateStat = () => {
                    current += increment;
                    if (current < target) {
                        stat.textContent = Math.floor(current);
                        requestAnimationFrame(updateStat);
                    } else {
                        stat.textContent = target;
                    }
                };
                
                updateStat();
            });
        };
        
        // Trigger animation when stats come into view
        const statsSection = document.querySelector('.hero-stats');
        if (statsSection) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateStats();
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(statsSection);
        }
    }
    
    // Utility method to update stats in real-time
    updateStats(stats) {
        const elements = {
            totalUsers: document.getElementById('totalUsers'),
            totalPrabhs: document.getElementById('totalPrabhs'),
            earlySignups: document.getElementById('earlySignups')
        };
        
        Object.entries(stats).forEach(([key, value]) => {
            if (elements[key]) {
                this.animateNumber(elements[key], value);
            }
        });
    }
    
    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const difference = targetValue - currentValue;
        const duration = 1000;
        const increment = difference / (duration / 16);
        let current = currentValue;
        
        const updateNumber = () => {
            current += increment;
            if ((increment > 0 && current < targetValue) || (increment < 0 && current > targetValue)) {
                element.textContent = Math.floor(current);
                requestAnimationFrame(updateNumber);
            } else {
                element.textContent = targetValue;
            }
        };
        
        if (difference !== 0) {
            updateNumber();
        }
    }
}

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
    
    .animate-on-scroll.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .navbar-hidden {
        transform: translateY(-100%);
    }
    
    .navbar-scrolled {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
    }
    
    .mobile-open {
        display: flex !important;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-radius: 0 0 1rem 1rem;
    }
    
    .mobile-menu-toggle.active i {
        transform: rotate(90deg);
    }
    
    @media (max-width: 768px) {
        .nav-links {
            display: none;
        }
        
        .mobile-menu-toggle {
            display: block !important;
        }
    }
    
    /* Gradient text animation */
    .gradient-text {
        background: linear-gradient(135deg, #ffffff, #ffeaa7, #ff6b9d);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 3s ease-in-out infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Chat preview animation */
    .chat-preview .message {
        animation: messageSlide 0.5s ease-out;
        animation-fill-mode: both;
    }
    
    .chat-preview .message:nth-child(1) { animation-delay: 0.5s; }
    .chat-preview .message:nth-child(2) { animation-delay: 1s; }
    .chat-preview .message:nth-child(3) { animation-delay: 1.5s; }
    
    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Hover effects */
    .feature-card:hover,
    .use-case:hover,
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    .step:hover .step-number {
        transform: scale(1.1);
        box-shadow: 0 8px 16px rgba(255, 107, 157, 0.3);
    }
`;
document.head.appendChild(style);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.landingPage = new LandingPage();
});

// Handle page visibility changes for performance
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause animations when tab is not visible
        document.body.classList.add('paused');
    } else {
        // Resume animations when tab becomes visible
        document.body.classList.remove('paused');
    }
});

// Export for global access
window.LandingPage = LandingPage;