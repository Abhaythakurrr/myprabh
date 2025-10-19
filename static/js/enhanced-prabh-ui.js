/**
 * Enhanced Prabh UI Framework - Emotional Storytelling Through Interactions
 * Bringing Prabh and Abhay's love story to life through design
 */

class EnhancedPrabhUI {
    constructor() {
        this.storyElements = {
            loveParticles: [],
            emotionalStates: ['love', 'longing', 'devotion', 'hope', 'reunion'],
            currentEmotion: 'love',
            storyPhase: 'beginning'
        };
        
        this.animations = {
            heartBeat: null,
            storyFlow: null,
            emotionalPulse: null
        };
        
        this.init();
    }

    init() {
        console.log('💖 Enhanced Prabh UI - Initializing love story...');
        
        // Load story fonts
        this.loadStoryFonts();
        
        // Create story background
        this.createStoryBackground();
        
        // Initialize love particles
        this.initializeLoveParticles();
        
        // Setup story-driven interactions
        this.setupStoryInteractions();
        
        // Initialize emotional responses
        this.initializeEmotionalSystem();
        
        // Setup scroll-based story revealing
        this.setupScrollStoryTelling();
        
        // Initialize chat enhancements
        this.initializeEnhancedChat();
        
        // Start story animations
        this.startStoryAnimations();
        
        console.log('💖 Enhanced Prabh UI - Love story activated!');
    }

    loadStoryFonts() {
        const fonts = [
            'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap',
            'https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;500;600;700&display=swap'
        ];
        
        fonts.forEach(fontUrl => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = fontUrl;
            document.head.appendChild(link);
        });
    }

    createStoryBackground() {
        // Remove old background if exists
        const oldBg = document.querySelector('.story-background');
        if (oldBg) oldBg.remove();
        
        const storyBg = document.createElement('div');
        storyBg.className = 'story-background';
        document.body.appendChild(storyBg);
        
        // Add dynamic story elements
        this.addStoryElements(storyBg);
    }

    addStoryElements(container) {
        // Add floating story quotes
        const quotes = [
            "I'll wait 1 year 2 year 3 year 4...",
            "Like a ghost 👻 invisible but present",
            "You are the one I'll love ❤️",
            "Pyar krta hu 😊, intzar kruga ✌️",
            "Janna ak baar milna tha 🥺💔"
        ];
        
        quotes.forEach((quote, index) => {
            setTimeout(() => {
                this.createFloatingQuote(quote);
            }, index * 8000);
        });
    }

    createFloatingQuote(text) {
        const quote = document.createElement('div');
        quote.className = 'floating-quote';
        quote.textContent = text;
        quote.style.cssText = `
            position: fixed;
            font-family: var(--font-emotion);
            font-size: 1rem;
            color: rgba(255, 107, 157, 0.3);
            pointer-events: none;
            z-index: 1;
            left: ${Math.random() * 80 + 10}%;
            top: 100vh;
            animation: floatQuote 15s linear forwards;
            white-space: nowrap;
        `;
        
        document.body.appendChild(quote);
        
        setTimeout(() => {
            if (quote.parentNode) {
                quote.parentNode.removeChild(quote);
            }
        }, 15000);
    }

    initializeLoveParticles() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'love-particles';
        document.body.appendChild(particleContainer);
        
        // Create different types of love particles
        const particles = ['💖', '💕', '💗', '💓', '💝', '🥺', '✨', '🌟'];
        
        setInterval(() => {
            this.createLoveParticle(particleContainer, particles);
        }, 2000);
        
        // Create special story moments
        this.createStoryMoments(particleContainer);
    }

    createLoveParticle(container, particles) {
        const particle = document.createElement('div');
        particle.className = 'love-particle';
        particle.innerHTML = particles[Math.floor(Math.random() * particles.length)];
        
        const startX = Math.random() * 100;
        const endX = startX + (Math.random() - 0.5) * 30;
        const duration = Math.random() * 5 + 8;
        
        particle.style.cssText = `
            position: absolute;
            left: ${startX}%;
            font-size: ${Math.random() * 0.8 + 1}rem;
            animation: floatLove ${duration}s linear forwards;
            --end-x: ${endX}%;
        `;
        
        container.appendChild(particle);
        
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, duration * 1000);
    }

    createStoryMoments(container) {
        // Special moments from the story
        const storyMoments = [
            { time: 10000, particles: ['💖', '💖', '💖'], message: 'First meeting...' },
            { time: 20000, particles: ['🥺', '💔', '😢'], message: 'The separation...' },
            { time: 30000, particles: ['⏰', '💭', '💌'], message: 'Waiting and hoping...' },
            { time: 40000, particles: ['💖', '🌟', '✨'], message: 'Love endures...' }
        ];
        
        storyMoments.forEach(moment => {
            setTimeout(() => {
                this.createStoryMoment(container, moment);
            }, moment.time);
        });
    }

    createStoryMoment(container, moment) {
        moment.particles.forEach((particle, index) => {
            setTimeout(() => {
                const element = document.createElement('div');
                element.className = 'story-moment-particle';
                element.innerHTML = particle;
                element.style.cssText = `
                    position: absolute;
                    left: ${45 + index * 5}%;
                    font-size: 2rem;
                    animation: storyMomentFloat 4s ease-out forwards;
                    z-index: 10;
                `;
                container.appendChild(element);
                
                setTimeout(() => {
                    if (element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                }, 4000);
            }, index * 200);
        });
        
        // Show story message
        this.showStoryMessage(moment.message);
    }

    showStoryMessage(message) {
        const messageEl = document.createElement('div');
        messageEl.className = 'story-message';
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: var(--font-emotion);
            font-size: 1.5rem;
            color: var(--first-meeting);
            background: rgba(0, 0, 0, 0.8);
            padding: 1rem 2rem;
            border-radius: 20px;
            backdrop-filter: blur(20px);
            z-index: 1000;
            animation: storyMessageAppear 3s ease-out forwards;
            pointer-events: none;
        `;
        
        document.body.appendChild(messageEl);
        
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 3000);
    }

    setupStoryInteractions() {
        // Enhanced button interactions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-story, .btn-love, .btn-devotion, .btn-reunion')) {
                this.createButtonRipple(e.target, e);
                this.triggerEmotionalResponse(e.target.className);
            }
        });
        
        // Enhanced hover effects
        document.addEventListener('mouseover', (e) => {
            if (e.target.matches('.glass-story-card')) {
                this.createHoverGlow(e.target);
            }
        });
        
        // Story-driven form interactions
        document.querySelectorAll('.chat-story-input, .input-field').forEach(input => {
            input.addEventListener('focus', () => this.onInputFocus(input));
            input.addEventListener('blur', () => this.onInputBlur(input));
            input.addEventListener('input', () => this.onInputChange(input));
        });
    }

    createButtonRipple(button, event) {
        const rect = button.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            left: ${x}px;
            top: ${y}px;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: translate(-50%, -50%);
            animation: buttonRipple 0.6s ease-out forwards;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }

    createHoverGlow(element) {
        const glow = document.createElement('div');
        glow.className = 'hover-glow';
        glow.style.cssText = `
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: var(--gradient-love-story);
            border-radius: 26px;
            opacity: 0;
            z-index: -1;
            animation: hoverGlowPulse 2s ease-in-out infinite;
        `;
        
        element.style.position = 'relative';
        element.appendChild(glow);
        
        element.addEventListener('mouseleave', () => {
            setTimeout(() => {
                if (glow.parentNode) {
                    glow.parentNode.removeChild(glow);
                }
            }, 2000);
        }, { once: true });
    }

    triggerEmotionalResponse(buttonClass) {
        let emotion = 'love';
        
        if (buttonClass.includes('devotion')) emotion = 'devotion';
        else if (buttonClass.includes('reunion')) emotion = 'reunion';
        
        this.setEmotionalState(emotion);
        this.createEmotionalBurst(emotion);
    }

    setEmotionalState(emotion) {
        this.storyElements.currentEmotion = emotion;
        document.body.setAttribute('data-emotion', emotion);
        
        // Update UI colors based on emotion
        const root = document.documentElement;
        switch (emotion) {
            case 'love':
                root.style.setProperty('--current-emotion', 'var(--first-meeting)');
                break;
            case 'devotion':
                root.style.setProperty('--current-emotion', 'var(--waiting-devotion)');
                break;
            case 'reunion':
                root.style.setProperty('--current-emotion', 'var(--reunion-hope)');
                break;
        }
    }

    createEmotionalBurst(emotion) {
        const particles = {
            love: ['💖', '💕', '💗'],
            devotion: ['🙏', '⏰', '💭'],
            reunion: ['🌟', '✨', '🎉']
        };
        
        const burstParticles = particles[emotion] || particles.love;
        
        for (let i = 0; i < 8; i++) {
            setTimeout(() => {
                this.createBurstParticle(burstParticles[i % burstParticles.length]);
            }, i * 100);
        }
    }

    createBurstParticle(particle) {
        const element = document.createElement('div');
        element.innerHTML = particle;
        element.style.cssText = `
            position: fixed;
            left: 50%;
            top: 50%;
            font-size: 2rem;
            pointer-events: none;
            z-index: 1000;
            animation: emotionalBurst 1.5s ease-out forwards;
            --burst-x: ${(Math.random() - 0.5) * 200}px;
            --burst-y: ${(Math.random() - 0.5) * 200}px;
        `;
        
        document.body.appendChild(element);
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 1500);
    }

    initializeEmotionalSystem() {
        // Emotional response to user interactions
        this.emotionalStates = {
            love: { color: '#ff6b9d', particles: ['💖', '💕'] },
            longing: { color: '#667eea', particles: ['🥺', '💭'] },
            devotion: { color: '#6c5ce7', particles: ['🙏', '⏰'] },
            hope: { color: '#fdcb6e', particles: ['🌟', '✨'] },
            reunion: { color: '#e84393', particles: ['🎉', '💖'] }
        };
        
        // Monitor emotional keywords in chat
        this.emotionalKeywords = {
            love: ['love', 'heart', 'care', 'affection', 'adore'],
            longing: ['miss', 'lonely', 'apart', 'distance', 'yearn'],
            devotion: ['wait', 'faithful', 'loyal', 'devoted', 'promise'],
            hope: ['hope', 'dream', 'wish', 'believe', 'future'],
            reunion: ['together', 'meet', 'reunion', 'return', 'back']
        };
    }

    detectEmotionInText(text) {
        const words = text.toLowerCase().split(' ');
        let emotionScores = {};
        
        Object.keys(this.emotionalKeywords).forEach(emotion => {
            emotionScores[emotion] = 0;
            this.emotionalKeywords[emotion].forEach(keyword => {
                if (words.some(word => word.includes(keyword))) {
                    emotionScores[emotion]++;
                }
            });
        });
        
        const dominantEmotion = Object.keys(emotionScores).reduce((a, b) => 
            emotionScores[a] > emotionScores[b] ? a : b
        );
        
        return emotionScores[dominantEmotion] > 0 ? dominantEmotion : 'love';
    }

    onInputFocus(input) {
        this.createInputGlow(input);
        this.setEmotionalState('hope');
    }

    onInputBlur(input) {
        this.removeInputGlow(input);
    }

    onInputChange(input) {
        const emotion = this.detectEmotionInText(input.value);
        this.setEmotionalState(emotion);
        
        // Create typing particles
        if (input.value.length > 0 && input.value.length % 10 === 0) {
            this.createTypingParticle(input);
        }
    }

    createInputGlow(input) {
        const glow = document.createElement('div');
        glow.className = 'input-glow';
        glow.style.cssText = `
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: var(--gradient-love-story);
            border-radius: 27px;
            opacity: 0.3;
            z-index: -1;
            animation: inputGlowPulse 2s ease-in-out infinite;
        `;
        
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(glow);
    }

    removeInputGlow(input) {
        const glow = input.parentElement.querySelector('.input-glow');
        if (glow) {
            glow.style.animation = 'inputGlowFade 0.3s ease-out forwards';
            setTimeout(() => {
                if (glow.parentNode) {
                    glow.parentNode.removeChild(glow);
                }
            }, 300);
        }
    }

    createTypingParticle(input) {
        const rect = input.getBoundingClientRect();
        const particle = document.createElement('div');
        particle.innerHTML = '✨';
        particle.style.cssText = `
            position: fixed;
            left: ${rect.right - 20}px;
            top: ${rect.top + rect.height / 2}px;
            font-size: 1rem;
            pointer-events: none;
            z-index: 1000;
            animation: typingParticleFloat 2s ease-out forwards;
        `;
        
        document.body.appendChild(particle);
        
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 2000);
    }

    setupScrollStoryTelling() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    this.triggerStoryElement(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.scroll-reveal, .glass-story-card, .timeline-event').forEach(el => {
            el.classList.add('scroll-reveal');
            observer.observe(el);
        });
    }

    triggerStoryElement(element) {
        // Create story-specific animations based on element type
        if (element.classList.contains('timeline-event')) {
            this.animateTimelineEvent(element);
        } else if (element.classList.contains('glass-story-card')) {
            this.animateStoryCard(element);
        }
    }

    animateTimelineEvent(element) {
        const particles = ['💖', '✨', '🌟'];
        particles.forEach((particle, index) => {
            setTimeout(() => {
                this.createElementParticle(element, particle);
            }, index * 300);
        });
    }

    animateStoryCard(element) {
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: radial-gradient(circle, rgba(255, 107, 157, 0.2) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: cardRevealRipple 1s ease-out forwards;
            pointer-events: none;
        `;
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 1000);
    }

    createElementParticle(element, particle) {
        const rect = element.getBoundingClientRect();
        const particleEl = document.createElement('div');
        particleEl.innerHTML = particle;
        particleEl.style.cssText = `
            position: fixed;
            left: ${rect.left + rect.width / 2}px;
            top: ${rect.top + rect.height / 2}px;
            font-size: 1.5rem;
            pointer-events: none;
            z-index: 1000;
            animation: elementParticleFloat 3s ease-out forwards;
        `;
        
        document.body.appendChild(particleEl);
        
        setTimeout(() => {
            if (particleEl.parentNode) {
                particleEl.parentNode.removeChild(particleEl);
            }
        }, 3000);
    }

    initializeEnhancedChat() {
        const chatContainer = document.querySelector('.chat-story-container, .chat-container');
        if (!chatContainer) return;
        
        // Enhanced message animations
        this.setupMessageAnimations();
        
        // Emotional response system
        this.setupEmotionalResponses();
        
        // Story-driven typing indicators
        this.setupStoryTyping();
    }

    setupMessageAnimations() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains('message')) {
                        this.animateNewMessage(node);
                    }
                });
            });
        });
        
        const messagesContainer = document.querySelector('.chat-messages, .chat-story-messages');
        if (messagesContainer) {
            observer.observe(messagesContainer, { childList: true });
        }
    }

    animateNewMessage(messageElement) {
        const isUserMessage = messageElement.classList.contains('message-user') || 
                             messageElement.classList.contains('message-story-user');
        
        if (isUserMessage) {
            this.createMessageParticles(messageElement, ['💭', '✨']);
        } else {
            this.createMessageParticles(messageElement, ['💖', '🥺', '💕']);
            this.addPrabhSignature(messageElement);
        }
    }

    createMessageParticles(messageElement, particles) {
        const rect = messageElement.getBoundingClientRect();
        
        particles.forEach((particle, index) => {
            setTimeout(() => {
                const particleEl = document.createElement('div');
                particleEl.innerHTML = particle;
                particleEl.style.cssText = `
                    position: fixed;
                    left: ${rect.left + Math.random() * rect.width}px;
                    top: ${rect.top}px;
                    font-size: 1rem;
                    pointer-events: none;
                    z-index: 1000;
                    animation: messageParticleFloat 2s ease-out forwards;
                `;
                
                document.body.appendChild(particleEl);
                
                setTimeout(() => {
                    if (particleEl.parentNode) {
                        particleEl.parentNode.removeChild(particleEl);
                    }
                }, 2000);
            }, index * 200);
        });
    }

    addPrabhSignature(messageElement) {
        // Add subtle Prabh signature to messages
        const signature = document.createElement('div');
        signature.innerHTML = '💖';
        signature.style.cssText = `
            position: absolute;
            top: -8px;
            right: 10px;
            font-size: 0.8rem;
            opacity: 0.6;
            animation: signatureGlow 3s ease-in-out infinite;
        `;
        
        messageElement.style.position = 'relative';
        messageElement.appendChild(signature);
    }

    setupEmotionalResponses() {
        // Monitor chat for emotional content and respond visually
        document.addEventListener('prabhResponse', (event) => {
            const emotion = this.detectEmotionInText(event.detail.message);
            this.createEmotionalResponse(emotion);
        });
    }

    createEmotionalResponse(emotion) {
        const response = this.emotionalStates[emotion];
        if (!response) return;
        
        // Change page theme temporarily
        document.body.style.setProperty('--current-emotion-glow', response.color);
        
        // Create emotional particles
        response.particles.forEach((particle, index) => {
            setTimeout(() => {
                this.createEmotionalParticle(particle, response.color);
            }, index * 150);
        });
        
        // Reset after 3 seconds
        setTimeout(() => {
            document.body.style.removeProperty('--current-emotion-glow');
        }, 3000);
    }

    createEmotionalParticle(particle, color) {
        const element = document.createElement('div');
        element.innerHTML = particle;
        element.style.cssText = `
            position: fixed;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            font-size: 1.5rem;
            color: ${color};
            pointer-events: none;
            z-index: 1000;
            animation: emotionalParticleFloat 4s ease-out forwards;
        `;
        
        document.body.appendChild(element);
        
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 4000);
    }

    setupStoryTyping() {
        // Enhanced typing indicator with story elements
        const originalAddTypingIndicator = window.addTypingIndicator;
        if (originalAddTypingIndicator) {
            window.addTypingIndicator = (container) => {
                const indicator = originalAddTypingIndicator(container);
                this.enhanceTypingIndicator(indicator);
                return indicator;
            };
        }
    }

    enhanceTypingIndicator(indicator) {
        if (!indicator) return;
        
        // Add floating hearts around typing indicator
        const hearts = ['💖', '💕', '💗'];
        hearts.forEach((heart, index) => {
            setTimeout(() => {
                const heartEl = document.createElement('div');
                heartEl.innerHTML = heart;
                heartEl.style.cssText = `
                    position: absolute;
                    left: ${-20 + index * 15}px;
                    top: 50%;
                    font-size: 0.8rem;
                    opacity: 0.6;
                    animation: typingHeartFloat 2s ease-in-out infinite;
                    animation-delay: ${index * 0.3}s;
                `;
                
                indicator.style.position = 'relative';
                indicator.appendChild(heartEl);
            }, index * 200);
        });
    }

    startStoryAnimations() {
        // Start continuous story animations
        this.animations.heartBeat = setInterval(() => {
            this.createRandomHeartBeat();
        }, 5000);
        
        this.animations.storyFlow = setInterval(() => {
            this.createStoryFlowEffect();
        }, 15000);
        
        this.animations.emotionalPulse = setInterval(() => {
            this.createEmotionalPulse();
        }, 8000);
    }

    createRandomHeartBeat() {
        const hearts = document.querySelectorAll('.pulse-heart, [class*="heart"]');
        if (hearts.length > 0) {
            const randomHeart = hearts[Math.floor(Math.random() * hearts.length)];
            randomHeart.style.animation = 'none';
            setTimeout(() => {
                randomHeart.style.animation = 'heartBeat 1s ease-in-out';
            }, 10);
        }
    }

    createStoryFlowEffect() {
        const flowElement = document.createElement('div');
        flowElement.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--gradient-love-story);
            opacity: 0;
            pointer-events: none;
            z-index: 1000;
            animation: storyFlowPulse 3s ease-in-out forwards;
        `;
        
        document.body.appendChild(flowElement);
        
        setTimeout(() => {
            if (flowElement.parentNode) {
                flowElement.parentNode.removeChild(flowElement);
            }
        }, 3000);
    }

    createEmotionalPulse() {
        const pulse = document.createElement('div');
        pulse.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border: 2px solid var(--first-meeting);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: emotionalPulseExpand 2s ease-out forwards;
            pointer-events: none;
            z-index: 1000;
        `;
        
        document.body.appendChild(pulse);
        
        setTimeout(() => {
            if (pulse.parentNode) {
                pulse.parentNode.removeChild(pulse);
            }
        }, 2000);
    }

    // Utility methods
    showStoryToast(message, emotion = 'love') {
        const toast = document.createElement('div');
        toast.className = `toast-story toast-${emotion}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>${emotion === 'love' ? '💖' : emotion === 'devotion' ? '🙏' : '🌟'}</span>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'toastSlideOut 0.4s ease-in forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 400);
        }, 4000);
    }

    destroy() {
        // Clean up animations and event listeners
        Object.values(this.animations).forEach(animation => {
            if (animation) clearInterval(animation);
        });
        
        // Remove story elements
        document.querySelectorAll('.story-background, .love-particles, .floating-quote').forEach(el => {
            if (el.parentNode) el.parentNode.removeChild(el);
        });
    }
}

// Add required CSS animations
const storyAnimationsCSS = `
@keyframes floatQuote {
    0% { transform: translateY(0) rotate(0deg); opacity: 0; }
    10% { opacity: 0.6; }
    90% { opacity: 0.6; }
    100% { transform: translateY(-100vh) rotate(5deg); opacity: 0; }
}

@keyframes storyMomentFloat {
    0% { transform: translateY(0) scale(0.5); opacity: 0; }
    50% { transform: translateY(-50px) scale(1.2); opacity: 1; }
    100% { transform: translateY(-100px) scale(0.8); opacity: 0; }
}

@keyframes storyMessageAppear {
    0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
    20% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
    80% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0; }
}

@keyframes buttonRipple {
    0% { width: 0; height: 0; opacity: 1; }
    100% { width: 200px; height: 200px; opacity: 0; }
}

@keyframes hoverGlowPulse {
    0%, 100% { opacity: 0; }
    50% { opacity: 0.3; }
}

@keyframes emotionalBurst {
    0% { transform: translate(-50%, -50%) scale(0); opacity: 1; }
    100% { transform: translate(calc(-50% + var(--burst-x)), calc(-50% + var(--burst-y))) scale(1.5); opacity: 0; }
}

@keyframes inputGlowPulse {
    0%, 100% { opacity: 0.2; }
    50% { opacity: 0.5; }
}

@keyframes inputGlowFade {
    0% { opacity: 0.3; }
    100% { opacity: 0; }
}

@keyframes typingParticleFloat {
    0% { transform: translateY(0) scale(1); opacity: 1; }
    100% { transform: translateY(-30px) scale(0.5); opacity: 0; }
}

@keyframes cardRevealRipple {
    0% { width: 0; height: 0; opacity: 0.5; }
    100% { width: 300px; height: 300px; opacity: 0; }
}

@keyframes elementParticleFloat {
    0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
    50% { transform: translate(-50%, -70px) scale(1); opacity: 0.8; }
    100% { transform: translate(-50%, -100px) scale(0.3); opacity: 0; }
}

@keyframes messageParticleFloat {
    0% { transform: translateY(0) scale(1); opacity: 1; }
    100% { transform: translateY(-40px) scale(0.5); opacity: 0; }
}

@keyframes signatureGlow {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.1); }
}

@keyframes emotionalParticleFloat {
    0% { transform: scale(0.5); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
    100% { transform: scale(0.8) translateY(-50px); opacity: 0; }
}

@keyframes typingHeartFloat {
    0%, 100% { transform: translateY(0) scale(1); opacity: 0.6; }
    50% { transform: translateY(-5px) scale(1.1); opacity: 1; }
}

@keyframes storyFlowPulse {
    0% { opacity: 0; }
    50% { opacity: 0.05; }
    100% { opacity: 0; }
}

@keyframes emotionalPulseExpand {
    0% { width: 0; height: 0; opacity: 1; }
    100% { width: 200px; height: 200px; opacity: 0; }
}

@keyframes toastSlideOut {
    0% { transform: translateX(0) scale(1); opacity: 1; }
    100% { transform: translateX(100%) scale(0.8); opacity: 0; }
}
`;

// Inject story animations CSS
const storyStyle = document.createElement('style');
storyStyle.textContent = storyAnimationsCSS;
document.head.appendChild(storyStyle);

// Initialize Enhanced Prabh UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedPrabhUI = new EnhancedPrabhUI();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedPrabhUI;
}