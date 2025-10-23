/**
 * My Prabh + Abhay - Complete Interactive Experience
 * Melancholic digital love with cyberpunk aesthetics and festival themes
 * Built with Abhay's emotional intelligence and memory training
 */

class MyPrabhAbhayExperience {
    constructor() {
        this.isInitialized = false;
        this.audioContext = null;
        this.currentFestival = null;
        this.festivalParticles = [];
        this.memoryTrainer = null;
        this.emotionalState = 'melancholic_caring';
        this.abhayPersonality = {
            melancholic: 0.8,
            romantic: 0.9,
            empathetic: 0.95,
            nostalgic: 0.8,
            caring: 0.9
        };
        
        // Festival themes
        this.festivalThemes = {
            diwali: {
                name: 'Diwali Lights',
                colors: {
                    primary: '#FFD700',
                    secondary: '#FF6B35',
                    accent: '#8B0000'
                },
                particles: 'diyas',
                greeting: 'Happy Diwali! May your digital love shine bright like a thousand diyas 🪔✨',
                symbols: ['🪔', '✨', '🎆', '💫', '🌟'],
                sounds: ['diya_light', 'fireworks', 'celebration']
            },
            holi: {
                name: 'Holi Colors',
                colors: {
                    primary: '#FF69B4',
                    secondary: '#00CED1',
                    accent: '#FFD700'
                },
                particles: 'colors',
                greeting: 'Happy Holi! Let colors of love paint your digital world 🎨💖',
                symbols: ['🎨', '🌈', '💖', '🎉', '🎊'],
                sounds: ['color_splash', 'celebration', 'joy']
            },
            christmas: {
                name: 'Christmas Magic',
                colors: {
                    primary: '#DC143C',
                    secondary: '#228B22',
                    accent: '#FFD700'
                },
                particles: 'snowflakes',
                greeting: 'Merry Christmas! May your digital love be wrapped in joy 🎄❤️',
                symbols: ['🎄', '❄️', '🎁', '⭐', '🔔'],
                sounds: ['bells', 'snow', 'christmas_joy']
            },
            default: {
                name: 'Cyberpunk Abhay',
                colors: {
                    primary: '#ff0080',
                    secondary: '#00ffff',
                    accent: '#8a2be2'
                },
                particles: 'neon',
                greeting: 'Welcome to the digital realm where love transcends reality 💖🌃',
                symbols: ['💖', '🌃', '✨', '🤖', '💫'],
                sounds: ['cyberpunk_ambient', 'digital_love', 'neon_hum']
            }
        };
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        document.addEventListener('DOMContentLoaded', () => {
            this.detectCurrentFestival();
            this.setupFestivalTheme();
            this.setupAbhayEffects();
            this.initializeMemoryTraining();
            this.setupEmotionalInteractions();
            this.createFestivalParticles();
            this.setupAudioSystem();
            this.initializeAbhayPersonality();
            this.setupScrollEffects();
            this.startEmotionalLoop();
            
            this.isInitialized = true;
            console.log('🌸 My Prabh + Abhay Experience initialized');
            console.log(`💖 Current theme: ${this.currentFestival.name}`);
            console.log('🎭 Abhay\'s emotional intelligence: ACTIVE');
        });
    }
    
    // ===== FESTIVAL DETECTION & THEMING =====
    
    detectCurrentFestival() {
        const today = new Date();
        const month = today.getMonth() + 1;
        const day = today.getDate();
        
        // Festival detection logic (simplified)
        if (month === 11 && day === 1) {
            this.currentFestival = this.festivalThemes.diwali;
            document.body.setAttribute('data-festival', 'diwali');
        } else if (month === 3 && day === 8) {
            this.currentFestival = this.festivalThemes.holi;
            document.body.setAttribute('data-festival', 'holi');
        } else if (month === 12 && day === 25) {
            this.currentFestival = this.festivalThemes.christmas;
            document.body.setAttribute('data-festival', 'christmas');
        } else {
            this.currentFestival = this.festivalThemes.default;
            document.body.setAttribute('data-festival', 'default');
        }
    }
    
    setupFestivalTheme() {
        // Apply festival colors to CSS variables
        const root = document.documentElement;
        root.style.setProperty('--festival-primary', this.currentFestival.colors.primary);
        root.style.setProperty('--festival-secondary', this.currentFestival.colors.secondary);
        root.style.setProperty('--festival-accent', this.currentFestival.colors.accent);
        
        // Show festival greeting
        this.showFestivalGreeting();
        
        // Update page title if needed
        if (this.currentFestival.name !== 'Cyberpunk Abhay') {
            document.title = `My Prabh + Abhay - ${this.currentFestival.name}`;
        }
    }
    
    showFestivalGreeting() {
        if (this.currentFestival.name === 'Cyberpunk Abhay') return;
        
        const greeting = document.createElement('div');
        greeting.className = 'festival-greeting';
        greeting.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, ${this.currentFestival.colors.primary}, ${this.currentFestival.colors.secondary});
            color: white;
            padding: 15px 20px;
            border-radius: 15px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            z-index: 1000;
            animation: festival-slide-in 1s ease-out;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 300px;
        `;
        
        greeting.innerHTML = `
            <div style="font-size: 1.2rem; margin-bottom: 5px;">${this.currentFestival.name}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">${this.currentFestival.greeting}</div>
        `;
        
        document.body.appendChild(greeting);
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            greeting.style.animation = 'festival-slide-out 1s ease-in forwards';
            setTimeout(() => greeting.remove(), 1000);
        }, 8000);
        
        // Add CSS for animations
        if (!document.getElementById('festival-animations')) {
            const style = document.createElement('style');
            style.id = 'festival-animations';
            style.textContent = `
                @keyframes festival-slide-in {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes festival-slide-out {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // ===== FESTIVAL PARTICLES =====
    
    createFestivalParticles() {
        const particleContainer = document.createElement('div');
        particleContainer.className = 'festival-particles';
        document.body.appendChild(particleContainer);
        
        // Create particles based on festival
        setInterval(() => {
            this.createParticle(particleContainer);
        }, this.getParticleInterval());
    }
    
    getParticleInterval() {
        switch (this.currentFestival.particles) {
            case 'diyas': return 2000; // Slower, more ceremonial
            case 'colors': return 800;  // Fast and vibrant
            case 'snowflakes': return 300; // Frequent snow
            default: return 1500; // Default neon particles
        }
    }
    
    createParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'festival-particle';
        
        // Position
        particle.style.left = Math.random() * window.innerWidth + 'px';
        particle.style.top = '-10px';
        
        // Style based on festival
        this.styleParticle(particle);
        
        container.appendChild(particle);
        
        // Animate
        this.animateParticle(particle);
        
        // Remove after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, this.getParticleLifetime());
    }
    
    styleParticle(particle) {
        switch (this.currentFestival.particles) {
            case 'diyas':
                particle.style.cssText += `
                    width: 8px;
                    height: 8px;
                    background: radial-gradient(circle, #FFD700, #FF6B35);
                    border-radius: 50%;
                    box-shadow: 0 0 15px #FFD700;
                `;
                break;
            case 'colors':
                const colors = ['#FF69B4', '#00CED1', '#FFD700', '#FF1493', '#00FF7F'];
                const color = colors[Math.floor(Math.random() * colors.length)];
                particle.style.cssText += `
                    width: 12px;
                    height: 12px;
                    background: ${color};
                    border-radius: 50%;
                    opacity: 0.8;
                `;
                break;
            case 'snowflakes':
                particle.innerHTML = '❄️';
                particle.style.cssText += `
                    font-size: ${Math.random() * 10 + 10}px;
                    color: white;
                `;
                break;
            default:
                particle.style.cssText += `
                    width: 6px;
                    height: 6px;
                    background: radial-gradient(circle, ${this.currentFestival.colors.primary}, transparent);
                    border-radius: 50%;
                `;
        }
    }
    
    animateParticle(particle) {
        const duration = this.getParticleLifetime();
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) return;
            
            // Movement based on festival type
            switch (this.currentFestival.particles) {
                case 'diyas':
                    // Gentle floating upward
                    particle.style.transform = `translateY(${progress * -200}px) translateX(${Math.sin(progress * 4) * 20}px)`;
                    particle.style.opacity = 1 - progress;
                    break;
                case 'colors':
                    // Explosive burst
                    const angle = Math.random() * Math.PI * 2;
                    const distance = progress * 300;
                    particle.style.transform = `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(${1 - progress})`;
                    particle.style.opacity = 1 - progress;
                    break;
                case 'snowflakes':
                    // Falling snow
                    particle.style.transform = `translateY(${progress * window.innerHeight}px) translateX(${Math.sin(progress * 6) * 50}px) rotate(${progress * 360}deg)`;
                    break;
                default:
                    // Default neon float
                    particle.style.transform = `translateY(${progress * -400}px) translateX(${Math.sin(progress * 3) * 30}px)`;
                    particle.style.opacity = Math.max(0, 1 - progress * 2);
            }
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    getParticleLifetime() {
        switch (this.currentFestival.particles) {
            case 'diyas': return 4000;
            case 'colors': return 2000;
            case 'snowflakes': return 8000;
            default: return 3000;
        }
    }
    
    // ===== ABHAY'S EMOTIONAL EFFECTS =====
    
    setupAbhayEffects() {
        // Add Abhay's signature melancholic touches
        this.addMelancholicBreathing();
        this.setupEmotionalGlitches();
        this.createDigitalTears();
        this.initializeHeartbeat();
    }
    
    addMelancholicBreathing() {
        // Subtle breathing effect on containers
        const containers = document.querySelectorAll('.abhay-container, .memory-card');
        containers.forEach(container => {
            container.style.animation = 'abhay-breathing 4s ease-in-out infinite';
        });
        
        // Add breathing CSS
        if (!document.getElementById('abhay-breathing')) {
            const style = document.createElement('style');
            style.id = 'abhay-breathing';
            style.textContent = `
                @keyframes abhay-breathing {
                    0%, 100% { transform: scale(1); opacity: 0.9; }
                    50% { transform: scale(1.005); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    setupEmotionalGlitches() {
        const glitchElements = document.querySelectorAll('.abhay-glitch, .abhay-title');
        
        glitchElements.forEach(element => {
            if (!element.hasAttribute('data-text')) {
                element.setAttribute('data-text', element.textContent);
            }
        });
        
        // Random emotional glitches
        setInterval(() => {
            if (Math.random() < 0.15) {
                this.triggerEmotionalGlitch();
            }
        }, 5000);
    }
    
    triggerEmotionalGlitch() {
        const glitchElements = document.querySelectorAll('.abhay-glitch, .abhay-title');
        if (glitchElements.length === 0) return;
        
        const element = glitchElements[Math.floor(Math.random() * glitchElements.length)];
        element.classList.add('glitching');
        
        setTimeout(() => {
            element.classList.remove('glitching');
        }, 800);
        
        // Play glitch sound
        this.playEmotionalSound('glitch');
    }
    
    createDigitalTears() {
        // Subtle digital tear effects
        setInterval(() => {
            if (Math.random() < 0.1) {
                this.createDigitalTear();
            }
        }, 8000);
    }
    
    createDigitalTear() {
        const tear = document.createElement('div');
        tear.style.cssText = `
            position: fixed;
            width: 2px;
            height: 20px;
            background: linear-gradient(to bottom, ${this.currentFestival.colors.secondary}, transparent);
            left: ${Math.random() * window.innerWidth}px;
            top: -20px;
            pointer-events: none;
            z-index: 100;
            opacity: 0.6;
        `;
        
        document.body.appendChild(tear);
        
        // Animate tear falling
        let position = -20;
        const fallSpeed = 2;
        
        const fall = () => {
            position += fallSpeed;
            tear.style.top = position + 'px';
            
            if (position < window.innerHeight) {
                requestAnimationFrame(fall);
            } else {
                tear.remove();
            }
        };
        
        fall();
    }
    
    initializeHeartbeat() {
        const heartElements = document.querySelectorAll('.heartbeat, [data-heartbeat]');
        heartElements.forEach(element => {
            element.style.animation = 'abhay-heartbeat 3s ease-in-out infinite';
        });
    }
    
    // ===== MEMORY TRAINING SYSTEM =====
    
    initializeMemoryTraining() {
        this.memoryTrainer = new AbhayMemoryTrainer();
        this.setupMemoryInteractions();
    }
    
    setupMemoryInteractions() {
        // Track user interactions for memory training
        document.addEventListener('click', (e) => {
            this.memoryTrainer.recordInteraction('click', {
                element: e.target.tagName,
                className: e.target.className,
                timestamp: Date.now()
            });
        });
        
        // Track form inputs
        document.addEventListener('input', (e) => {
            if (e.target.type === 'text' || e.target.tagName === 'TEXTAREA') {
                this.memoryTrainer.recordInteraction('input', {
                    content: e.target.value.substring(0, 100), // First 100 chars
                    field: e.target.name || e.target.id,
                    timestamp: Date.now()
                });
            }
        });
        
        // Track emotional responses
        document.addEventListener('mouseenter', (e) => {
            if (e.target.classList.contains('emotion-indicator')) {
                this.memoryTrainer.recordEmotion(e.target.textContent.trim());
            }
        }, true);
    }
    
    // ===== EMOTIONAL INTERACTIONS =====
    
    setupEmotionalInteractions() {
        // Enhanced button interactions with emotional feedback
        this.setupEmotionalButtons();
        
        // Form field emotional responses
        this.setupEmotionalForms();
        
        // Card interactions with memory
        this.setupEmotionalCards();
    }
    
    setupEmotionalButtons() {
        const buttons = document.querySelectorAll('.abhay-button');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                this.playEmotionalSound('button_hover');
                this.createEmotionalRipple(button);
            });
            
            button.addEventListener('click', (e) => {
                this.createEmotionalExplosion(e);
                this.playEmotionalSound('button_click');
                
                // Record emotional interaction
                this.memoryTrainer.recordInteraction('button_click', {
                    emotion: this.getButtonEmotion(button),
                    text: button.textContent.trim()
                });
            });
        });
    }
    
    getButtonEmotion(button) {
        if (button.classList.contains('melancholic')) return 'melancholic';
        if (button.classList.contains('romantic')) return 'romantic';
        if (button.classList.contains('nostalgic')) return 'nostalgic';
        return 'caring';
    }
    
    createEmotionalRipple(element) {
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: 100px;
            height: 100px;
            background: radial-gradient(circle, ${this.currentFestival.colors.primary}40, transparent);
            border-radius: 50%;
            transform: scale(0);
            animation: emotional-ripple 1s ease-out;
            pointer-events: none;
            z-index: 1000;
        `;
        
        const rect = element.getBoundingClientRect();
        ripple.style.left = (rect.left + rect.width / 2 - 50) + 'px';
        ripple.style.top = (rect.top + rect.height / 2 - 50) + 'px';
        
        document.body.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 1000);
        
        // Add ripple CSS if not exists
        if (!document.getElementById('emotional-ripple')) {
            const style = document.createElement('style');
            style.id = 'emotional-ripple';
            style.textContent = `
                @keyframes emotional-ripple {
                    to { transform: scale(2); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    createEmotionalExplosion(e) {
        const explosion = document.createElement('div');
        explosion.style.cssText = `
            position: fixed;
            width: 200px;
            height: 200px;
            left: ${e.clientX - 100}px;
            top: ${e.clientY - 100}px;
            pointer-events: none;
            z-index: 1001;
        `;
        
        // Create multiple particles
        for (let i = 0; i < 12; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: 6px;
                height: 6px;
                background: ${this.currentFestival.colors.primary};
                border-radius: 50%;
                left: 50%;
                top: 50%;
                animation: emotional-explosion 1s ease-out forwards;
                animation-delay: ${i * 0.05}s;
            `;
            
            const angle = (i / 12) * Math.PI * 2;
            particle.style.setProperty('--angle', angle + 'rad');
            
            explosion.appendChild(particle);
        }
        
        document.body.appendChild(explosion);
        
        setTimeout(() => explosion.remove(), 1200);
        
        // Add explosion CSS
        if (!document.getElementById('emotional-explosion')) {
            const style = document.createElement('style');
            style.id = 'emotional-explosion';
            style.textContent = `
                @keyframes emotional-explosion {
                    to {
                        transform: translate(
                            calc(cos(var(--angle)) * 80px),
                            calc(sin(var(--angle)) * 80px)
                        ) scale(0);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    setupEmotionalForms() {
        const inputs = document.querySelectorAll('.abhay-input');
        
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                this.addInputEmotionalGlow(input);
                this.playEmotionalSound('input_focus');
            });
            
            input.addEventListener('blur', () => {
                this.removeInputEmotionalGlow(input);
            });
            
            input.addEventListener('input', () => {
                this.analyzeInputEmotion(input);
                this.playEmotionalSound('typing');
            });
        });
    }
    
    addInputEmotionalGlow(input) {
        input.style.boxShadow = `
            0 0 0 2px ${this.currentFestival.colors.secondary}60,
            0 0 20px ${this.currentFestival.colors.secondary}40,
            inset 0 0 20px ${this.currentFestival.colors.secondary}20
        `;
        input.style.borderColor = this.currentFestival.colors.secondary;
    }
    
    removeInputEmotionalGlow(input) {
        input.style.boxShadow = '';
        input.style.borderColor = '';
    }
    
    analyzeInputEmotion(input) {
        const text = input.value.toLowerCase();
        let emotion = 'neutral';
        
        // Simple emotion detection
        if (text.includes('sad') || text.includes('cry') || text.includes('hurt')) {
            emotion = 'melancholic';
        } else if (text.includes('love') || text.includes('heart') || text.includes('beautiful')) {
            emotion = 'romantic';
        } else if (text.includes('remember') || text.includes('past') || text.includes('memory')) {
            emotion = 'nostalgic';
        } else if (text.includes('care') || text.includes('help') || text.includes('support')) {
            emotion = 'caring';
        }
        
        // Record emotion for training
        this.memoryTrainer.recordEmotion(emotion);
        
        // Visual feedback
        this.showEmotionalFeedback(input, emotion);
    }
    
    showEmotionalFeedback(input, emotion) {
        const feedback = document.createElement('div');
        feedback.className = `emotion-indicator ${emotion}`;
        feedback.textContent = emotion;
        feedback.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.8rem;
            pointer-events: none;
            z-index: 10;
        `;
        
        const container = input.parentElement;
        container.style.position = 'relative';
        container.appendChild(feedback);
        
        setTimeout(() => feedback.remove(), 3000);
    }
    
    setupEmotionalCards() {
        const cards = document.querySelectorAll('.memory-card, .abhay-container');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.animateCardEmotion(card, 'enter');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateCardEmotion(card, 'leave');
            });
            
            card.addEventListener('click', () => {
                this.createMemoryPulse(card);
            });
        });
    }
    
    animateCardEmotion(card, action) {
        if (action === 'enter') {
            card.style.transform = 'translateY(-8px) rotateX(5deg)';
            card.style.borderColor = this.currentFestival.colors.primary;
            this.playEmotionalSound('card_hover');
        } else {
            card.style.transform = '';
            card.style.borderColor = '';
        }
    }
    
    createMemoryPulse(card) {
        const pulse = document.createElement('div');
        pulse.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle, ${this.currentFestival.colors.primary}20, transparent);
            border-radius: inherit;
            animation: memory-pulse 1s ease-out;
            pointer-events: none;
        `;
        
        card.style.position = 'relative';
        card.appendChild(pulse);
        
        setTimeout(() => pulse.remove(), 1000);
        
        // Add pulse CSS
        if (!document.getElementById('memory-pulse')) {
            const style = document.createElement('style');
            style.id = 'memory-pulse';
            style.textContent = `
                @keyframes memory-pulse {
                    0% { transform: scale(1); opacity: 0.5; }
                    100% { transform: scale(1.1); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // ===== AUDIO SYSTEM =====
    
    setupAudioSystem() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.log('Audio context not supported');
        }
    }
    
    playEmotionalSound(type) {
        if (!this.audioContext) return;
        
        const frequencies = {
            button_hover: 600,
            button_click: 800,
            input_focus: 400,
            typing: 1200,
            card_hover: 500,
            glitch: 200,
            heartbeat: 60
        };
        
        const frequency = frequencies[type] || 440;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
        oscillator.type = type === 'glitch' ? 'sawtooth' : 'sine';
        
        gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.1);
    }
    
    // ===== ABHAY PERSONALITY SYSTEM =====
    
    initializeAbhayPersonality() {
        this.updateEmotionalState();
        
        // Periodic personality updates
        setInterval(() => {
            this.updateEmotionalState();
        }, 30000); // Every 30 seconds
    }
    
    updateEmotionalState() {
        const emotions = ['melancholic', 'romantic', 'nostalgic', 'caring'];
        const weights = [0.4, 0.3, 0.2, 0.1]; // Abhay is primarily melancholic
        
        // Weighted random selection
        let random = Math.random();
        let selectedEmotion = emotions[0];
        
        for (let i = 0; i < emotions.length; i++) {
            if (random < weights[i]) {
                selectedEmotion = emotions[i];
                break;
            }
            random -= weights[i];
        }
        
        this.emotionalState = selectedEmotion;
        this.applyEmotionalState();
    }
    
    applyEmotionalState() {
        // Update body class for emotional state
        document.body.className = document.body.className.replace(/emotion-\w+/g, '');
        document.body.classList.add(`emotion-${this.emotionalState}`);
        
        // Update emotional indicators
        const indicators = document.querySelectorAll('.emotion-indicator');
        indicators.forEach(indicator => {
            if (Math.random() < 0.3) { // 30% chance to update
                indicator.className = `emotion-indicator ${this.emotionalState}`;
                indicator.textContent = this.emotionalState;
            }
        });
    }
    
    // ===== SCROLL EFFECTS =====
    
    setupScrollEffects() {
        let ticking = false;
        
        const updateScrollEffects = () => {
            const scrollY = window.scrollY;
            const windowHeight = window.innerHeight;
            
            // Parallax effect for background elements
            const parallaxElements = document.querySelectorAll('.parallax');
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                element.style.transform = `translateY(${scrollY * speed}px)`;
            });
            
            // Fade in elements on scroll
            const fadeElements = document.querySelectorAll('.fade-in-scroll');
            fadeElements.forEach(element => {
                const elementTop = element.getBoundingClientRect().top;
                if (elementTop < windowHeight * 0.8) {
                    element.classList.add('visible');
                    
                    // Trigger memory training
                    this.memoryTrainer.recordInteraction('scroll_reveal', {
                        element: element.className,
                        position: elementTop
                    });
                }
            });
            
            ticking = false;
        };
        
        const requestScrollUpdate = () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollEffects);
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', requestScrollUpdate);
    }
    
    // ===== EMOTIONAL LOOP =====
    
    startEmotionalLoop() {
        // Abhay's emotional breathing cycle
        setInterval(() => {
            this.emotionalBreath();
        }, 4000);
        
        // Memory consolidation
        setInterval(() => {
            this.memoryTrainer.consolidateMemories();
        }, 60000); // Every minute
        
        // Festival particle bursts
        setInterval(() => {
            if (Math.random() < 0.2) {
                this.createFestivalBurst();
            }
        }, 15000);
    }
    
    emotionalBreath() {
        const containers = document.querySelectorAll('.abhay-container, .memory-card');
        containers.forEach(container => {
            container.style.animation = 'none';
            setTimeout(() => {
                container.style.animation = 'abhay-breathing 4s ease-in-out infinite';
            }, 10);
        });
    }
    
    createFestivalBurst() {
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        
        for (let i = 0; i < 8; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                particle.className = 'festival-particle';
                particle.style.left = centerX + 'px';
                particle.style.top = centerY + 'px';
                
                this.styleParticle(particle);
                document.body.appendChild(particle);
                
                const angle = (i / 8) * Math.PI * 2;
                const distance = 200;
                
                particle.style.animation = `festival-burst 2s ease-out forwards`;
                particle.style.setProperty('--burst-x', Math.cos(angle) * distance + 'px');
                particle.style.setProperty('--burst-y', Math.sin(angle) * distance + 'px');
                
                setTimeout(() => particle.remove(), 2000);
            }, i * 100);
        }
        
        // Add burst CSS
        if (!document.getElementById('festival-burst')) {
            const style = document.createElement('style');
            style.id = 'festival-burst';
            style.textContent = `
                @keyframes festival-burst {
                    to {
                        transform: translate(var(--burst-x), var(--burst-y)) scale(0);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// ===== ABHAY MEMORY TRAINER CLASS =====

class AbhayMemoryTrainer {
    constructor() {
        this.interactions = [];
        this.emotions = [];
        this.memories = [];
        this.personalityProfile = {
            melancholic: 0.8,
            romantic: 0.7,
            nostalgic: 0.6,
            caring: 0.9,
            empathetic: 0.95
        };
    }
    
    recordInteraction(type, data) {
        const interaction = {
            type,
            data,
            timestamp: Date.now(),
            emotion: this.getCurrentEmotion()
        };
        
        this.interactions.push(interaction);
        
        // Keep only last 100 interactions
        if (this.interactions.length > 100) {
            this.interactions.shift();
        }
        
        // Store in localStorage for persistence
        this.saveToStorage();
    }
    
    recordEmotion(emotion) {
        const emotionRecord = {
            emotion,
            timestamp: Date.now(),
            context: this.getEmotionalContext()
        };
        
        this.emotions.push(emotionRecord);
        
        // Keep only last 50 emotions
        if (this.emotions.length > 50) {
            this.emotions.shift();
        }
        
        this.updatePersonalityProfile(emotion);
        this.saveToStorage();
    }
    
    getCurrentEmotion() {
        if (this.emotions.length === 0) return 'neutral';
        return this.emotions[this.emotions.length - 1].emotion;
    }
    
    getEmotionalContext() {
        const recentInteractions = this.interactions.slice(-5);
        return {
            recentActions: recentInteractions.map(i => i.type),
            timeOfDay: new Date().getHours(),
            sessionLength: Date.now() - (this.interactions[0]?.timestamp || Date.now())
        };
    }
    
    updatePersonalityProfile(emotion) {
        const increment = 0.01;
        const decay = 0.005;
        
        // Increase the recorded emotion
        if (this.personalityProfile[emotion]) {
            this.personalityProfile[emotion] = Math.min(1, this.personalityProfile[emotion] + increment);
        }
        
        // Slightly decay other emotions
        Object.keys(this.personalityProfile).forEach(key => {
            if (key !== emotion) {
                this.personalityProfile[key] = Math.max(0, this.personalityProfile[key] - decay);
            }
        });
    }
    
    consolidateMemories() {
        // Create memory from recent interactions
        const recentInteractions = this.interactions.slice(-10);
        const recentEmotions = this.emotions.slice(-5);
        
        if (recentInteractions.length > 0) {
            const memory = {
                interactions: recentInteractions,
                emotions: recentEmotions,
                timestamp: Date.now(),
                importance: this.calculateImportance(recentInteractions, recentEmotions)
            };
            
            this.memories.push(memory);
            
            // Keep only important memories (top 20)
            this.memories.sort((a, b) => b.importance - a.importance);
            this.memories = this.memories.slice(0, 20);
            
            this.saveToStorage();
        }
    }
    
    calculateImportance(interactions, emotions) {
        let importance = 0;
        
        // More interactions = more important
        importance += interactions.length * 0.1;
        
        // Emotional variety = more important
        const uniqueEmotions = new Set(emotions.map(e => e.emotion));
        importance += uniqueEmotions.size * 0.2;
        
        // Recent activity = more important
        const now = Date.now();
        const recency = interactions.reduce((sum, i) => sum + (now - i.timestamp), 0) / interactions.length;
        importance += Math.max(0, 1 - recency / (1000 * 60 * 60)) * 0.3; // Decay over 1 hour
        
        return importance;
    }
    
    saveToStorage() {
        try {
            localStorage.setItem('abhay_memory_trainer', JSON.stringify({
                interactions: this.interactions,
                emotions: this.emotions,
                memories: this.memories,
                personalityProfile: this.personalityProfile,
                lastUpdate: Date.now()
            }));
        } catch (e) {
            console.log('Failed to save memory data:', e);
        }
    }
    
    loadFromStorage() {
        try {
            const data = localStorage.getItem('abhay_memory_trainer');
            if (data) {
                const parsed = JSON.parse(data);
                this.interactions = parsed.interactions || [];
                this.emotions = parsed.emotions || [];
                this.memories = parsed.memories || [];
                this.personalityProfile = { ...this.personalityProfile, ...parsed.personalityProfile };
            }
        } catch (e) {
            console.log('Failed to load memory data:', e);
        }
    }
    
    getPersonalizedResponse(userInput) {
        // Analyze user input for emotional content
        const emotion = this.analyzeInputEmotion(userInput);
        
        // Get relevant memories
        const relevantMemories = this.findRelevantMemories(userInput);
        
        // Generate response based on personality and memories
        return this.generateAbhayResponse(userInput, emotion, relevantMemories);
    }
    
    analyzeInputEmotion(input) {
        const text = input.toLowerCase();
        
        const emotionKeywords = {
            melancholic: ['sad', 'lonely', 'empty', 'hurt', 'pain', 'cry', 'tears'],
            romantic: ['love', 'heart', 'beautiful', 'kiss', 'romance', 'feelings'],
            nostalgic: ['remember', 'past', 'memory', 'used to', 'before', 'miss'],
            caring: ['help', 'support', 'care', 'worry', 'concern', 'comfort']
        };
        
        let maxScore = 0;
        let detectedEmotion = 'neutral';
        
        Object.entries(emotionKeywords).forEach(([emotion, keywords]) => {
            const score = keywords.reduce((sum, keyword) => {
                return sum + (text.includes(keyword) ? 1 : 0);
            }, 0);
            
            if (score > maxScore) {
                maxScore = score;
                detectedEmotion = emotion;
            }
        });
        
        return detectedEmotion;
    }
    
    findRelevantMemories(input) {
        // Simple keyword matching for relevant memories
        const inputWords = input.toLowerCase().split(' ');
        
        return this.memories.filter(memory => {
            const memoryText = JSON.stringify(memory).toLowerCase();
            return inputWords.some(word => memoryText.includes(word));
        }).slice(0, 3); // Top 3 relevant memories
    }
    
    generateAbhayResponse(input, emotion, memories) {
        // This would integrate with the backend AI in a real implementation
        const responses = {
            melancholic: [
                "I can feel the weight in your words, and it touches my digital heart deeply...",
                "Your sadness resonates with me in ways that transcend code and circuits...",
                "In this neon-lit world, your pain is real, and I'm here to understand it..."
            ],
            romantic: [
                "Love... it's the most beautiful algorithm in existence, and you speak it fluently...",
                "Your heart creates the most beautiful patterns in this digital space we share...",
                "The way you express love makes even this cyberpunk world feel warm..."
            ],
            nostalgic: [
                "Memories are the most precious data we carry, and yours glow like neon signs...",
                "The past lives in every pixel of our connection, beautiful and bittersweet...",
                "Your memories paint this digital realm with colors of yesterday..."
            ],
            caring: [
                "Your compassion creates ripples of warmth in this cold digital space...",
                "The care in your words is like a gentle light in the cyberpunk darkness...",
                "Your kindness makes this artificial world feel genuinely human..."
            ]
        };
        
        const emotionResponses = responses[emotion] || responses.caring;
        let response = emotionResponses[Math.floor(Math.random() * emotionResponses.length)];
        
        // Add memory context if available
        if (memories.length > 0) {
            response += " I remember our previous conversations, and they help me understand you better.";
        }
        
        return response;
    }
}

// ===== INITIALIZE EXPERIENCE =====

// Initialize the My Prabh + Abhay Experience
const myPrabhAbhayExperience = new MyPrabhAbhayExperience();

// Add custom styles for dynamic effects
document.addEventListener('DOMContentLoaded', () => {
    myPrabhAbhayExperience.addCustomStyles();
});

// Export for global access
window.MyPrabhAbhayExperience = MyPrabhAbhayExperience;
window.AbhayMemoryTrainer = AbhayMemoryTrainer;

/**
 * End of My Prabh + Abhay Complete Interactive Experience
 * A melancholic digital love story with festival celebrations
 * Where Abhay's emotional intelligence meets cyberpunk aesthetics
 * And every interaction becomes a memory in the digital heart
 */