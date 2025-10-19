/**
 * Prabh UI Framework - Modern interactions and animations
 */

class PrabhUI {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.startAnimations();
    }

    init() {
        // Add animated background
        this.createAnimatedBackground();
        
        // Add floating hearts
        this.createFloatingHearts();
        
        // Initialize components
        this.initializeComponents();
        
        console.log('💖 Prabh UI initialized');
    }

    createAnimatedBackground() {
        if (!document.querySelector('.animated-bg')) {
            const bg = document.createElement('div');
            bg.className = 'animated-bg';
            document.body.appendChild(bg);
        }
    }

    createFloatingHearts() {
        if (!document.querySelector('.floating-hearts')) {
            const container = document.createElement('div');
            container.className = 'floating-hearts';
            document.body.appendChild(container);

            // Create hearts periodically
            setInterval(() => {
                this.createHeart(container);
            }, 3000);
        }
    }

    createHeart(container) {
        const heart = document.createElement('div');
        heart.className = 'heart';
        heart.innerHTML = '💖';
        heart.style.left = Math.random() * 100 + '%';
        heart.style.animationDelay = Math.random() * 2 + 's';
        heart.style.animationDuration = (Math.random() * 3 + 5) + 's';
        
        container.appendChild(heart);

        // Remove heart after animation
        setTimeout(() => {
            if (heart.parentNode) {
                heart.parentNode.removeChild(heart);
            }
        }, 8000);
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Button hover effects
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px)';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });
        });

        // Input focus effects
        document.querySelectorAll('.input-field').forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('focused');
            });
        });
    }

    initializeComponents() {
        // Initialize chat if present
        if (document.querySelector('.chat-container')) {
            this.initializeChat();
        }

        // Initialize onboarding if present
        if (document.querySelector('.onboarding-container')) {
            this.initializeOnboarding();
        }

        // Initialize training interface if present
        if (document.querySelector('.training-container')) {
            this.initializeTraining();
        }
    }

    initializeChat() {
        const chatInput = document.querySelector('.chat-input');
        const sendButton = document.querySelector('.chat-send-btn');
        const messagesContainer = document.querySelector('.chat-messages');

        if (!chatInput || !messagesContainer) return;

        const sendMessage = async () => {
            const message = chatInput.value.trim();
            if (!message) return;

            // Add user message
            this.addMessage(messagesContainer, message, 'user');
            chatInput.value = '';

            // Show typing indicator
            const typingIndicator = this.addTypingIndicator(messagesContainer);

            try {
                // Send to API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                
                // Remove typing indicator
                typingIndicator.remove();
                
                // Add Prabh's response
                this.addMessage(messagesContainer, data.response, 'prabh');
                
                // Show method info if available
                if (data.method) {
                    this.showToast(`Response via ${data.method}`, 'info');
                }

            } catch (error) {
                typingIndicator.remove();
                this.addMessage(messagesContainer, 
                    "I'm having some trouble right now, but I'm still here for you, janna 💖", 
                    'prabh'
                );
                this.showToast('Connection error', 'error');
            }
        };

        // Send on Enter key
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Send on button click
        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }
    }

    addMessage(container, text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        messageDiv.innerHTML = this.formatMessage(text);
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
        
        return messageDiv;
    }

    addTypingIndicator(container) {
        const indicator = document.createElement('div');
        indicator.className = 'message message-prabh typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        container.appendChild(indicator);
        container.scrollTop = container.scrollHeight;
        
        return indicator;
    }

    formatMessage(text) {
        // Convert emojis and format text
        return text
            .replace(/💖/g, '<span class="pulse-heart">💖</span>')
            .replace(/🥺/g, '<span class="pulse-heart">🥺</span>')
            .replace(/💕/g, '<span class="pulse-heart">💕</span>')
            .replace(/❤️/g, '<span class="pulse-heart">❤️</span>');
    }

    initializeOnboarding() {
        let currentStep = 0;
        const steps = document.querySelectorAll('.onboarding-step');
        const nextBtn = document.querySelector('.onboarding-next');
        const prevBtn = document.querySelector('.onboarding-prev');
        const indicators = document.querySelectorAll('.step');

        const updateStep = () => {
            // Hide all steps
            steps.forEach((step, index) => {
                step.style.display = index === currentStep ? 'block' : 'none';
            });

            // Update indicators
            indicators.forEach((indicator, index) => {
                indicator.classList.remove('active', 'completed');
                if (index < currentStep) {
                    indicator.classList.add('completed');
                } else if (index === currentStep) {
                    indicator.classList.add('active');
                }
            });

            // Update buttons
            if (prevBtn) prevBtn.style.display = currentStep === 0 ? 'none' : 'inline-flex';
            if (nextBtn) {
                nextBtn.textContent = currentStep === steps.length - 1 ? 'Get Started' : 'Next';
            }
        };

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    updateStep();
                } else {
                    // Complete onboarding
                    window.location.href = '/dashboard';
                }
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentStep > 0) {
                    currentStep--;
                    updateStep();
                }
            });
        }

        updateStep();
    }

    initializeTraining() {
        const uploadArea = document.querySelector('.upload-area');
        const fileInput = document.querySelector('.file-input');
        const progressBar = document.querySelector('.progress-fill');

        if (uploadArea && fileInput) {
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                this.handleFileUpload(files[0], progressBar);
            });

            // Click to upload
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileUpload(e.target.files[0], progressBar);
                }
            });
        }
    }

    async handleFileUpload(file, progressBar) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Show progress
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.parentElement.style.display = 'block';
            }

            // Simulate progress (replace with actual upload progress)
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 30;
                if (progress > 90) progress = 90;
                if (progressBar) {
                    progressBar.style.width = progress + '%';
                }
            }, 200);

            const response = await fetch('/api/memory/upload', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            
            if (progressBar) {
                progressBar.style.width = '100%';
            }

            if (response.ok) {
                const result = await response.json();
                this.showToast('Memory uploaded successfully! 💖', 'success');
                
                // Hide progress bar after delay
                setTimeout(() => {
                    if (progressBar) {
                        progressBar.parentElement.style.display = 'none';
                    }
                }, 2000);
            } else {
                throw new Error('Upload failed');
            }

        } catch (error) {
            this.showToast('Upload failed. Please try again.', 'error');
            if (progressBar) {
                progressBar.parentElement.style.display = 'none';
            }
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    startAnimations() {
        // Intersection Observer for fade-in animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });

        // Observe all cards and sections
        document.querySelectorAll('.glass-card, .feature-card, .hero-content').forEach(el => {
            observer.observe(el);
        });
    }

    // Utility methods
    async apiCall(endpoint, data = null, method = 'GET') {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(endpoint, options);
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatTime(date) {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.prabhUI = new PrabhUI();
});

// Add CSS for typing indicator
const typingCSS = `
.typing-indicator {
    padding: 1rem 1.5rem;
}

.typing-dots {
    display: flex;
    gap: 0.25rem;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--love-primary);
    animation: typingDot 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typingDot {
    0%, 80%, 100% {
        transform: scale(0);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

.drag-over {
    border-color: var(--love-primary) !important;
    background: rgba(255, 107, 157, 0.1) !important;
}

.toast-success {
    background: var(--gradient-vibrant);
}

.toast-error {
    background: var(--gradient-broken);
}

.toast-info {
    background: var(--gradient-love);
}
`;

// Inject typing CSS
const style = document.createElement('style');
style.textContent = typingCSS;
document.head.appendChild(style);