/**
 * My Prabh - Cyberpunk Lofi Love Interactive Experience
 * A melancholic digital love story brought to life through code
 * Built with nostalgic vibes and futuristic interactions
 */

class MyPrabhCyberpunkExperience {
    constructor() {
        this.isInitialized = false;
        this.audioContext = null;
        this.glitchInterval = null;
        this.particleSystem = null;
        this.typingEffect = null;
        this.heartbeatAnimation = null;
        
        // Lofi color palette
        this.colors = {
            neonPink: '#ff0080',
            neonCyan: '#00ffff',
            neonPurple: '#8a2be2',
            electricBlue: '#0066ff',
            cyberGreen: '#00ff41',
            warmAmber: '#ffb347',
            dustyRose: '#d4a5a5'
        };
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        document.addEventListener('DOMContentLoaded', () => {
            this.setupCyberpunkEffects();
            this.initializeParticleSystem();
            this.setupInteractiveElements();
            this.initializeAudioVisualization();
            this.setupLofiTypingEffects();
            this.createFloatingMemories();
            this.setupGlitchEffects();
            this.initializeHeartbeat();
            this.setupScrollEffects();
            
            this.isInitialized = true;
            console.log('🌸 My Prabh Cyberpunk Lofi Experience initialized');
        });
    }
    
    // ===== CYBERPUNK VISUAL EFFECTS =====
    
    setupCyberpunkEffects() {
        // Create dynamic background grid
        this.createDynamicGrid();
        
        // Setup neon glow effects
        this.setupNeonGlows();
        
        // Initialize scan line effects
        this.createScanLines();
        
        // Setup holographic overlays
        this.createHolographicOverlays();
    }
    
    createDynamicGrid() {
        const gridOverlay = document.createElement('div');
        gridOverlay.className = 'cyber-grid-overlay';
        gridOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 60px 60px;
            animation: grid-pulse 6s ease-in-out infinite;
        `;
        
        document.body.appendChild(gridOverlay);
        
        // Animate grid intensity based on user interaction
        let lastInteraction = Date.now();
        document.addEventListener('mousemove', () => {
            lastInteraction = Date.now();
            gridOverlay.style.opacity = '0.8';
            
            setTimeout(() => {
                if (Date.now() - lastInteraction > 2000) {
                    gridOverlay.style.opacity = '0.3';
                }
            }, 2000);
        });
    }
    
    setupNeonGlows() {
        // Add dynamic neon glow to interactive elements
        const glowElements = document.querySelectorAll('.neon-button, .cyber-container, .holo-card');
        
        glowElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.addNeonGlow(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.removeNeonGlow(e.target);
            });
        });
    }
    
    addNeonGlow(element) {
        const glowColor = this.getRandomNeonColor();
        element.style.boxShadow = `
            0 0 20px ${glowColor},
            0 0 40px ${glowColor},
            0 0 60px ${glowColor},
            inset 0 0 20px rgba(255, 255, 255, 0.1)
        `;
        element.style.borderColor = glowColor;
    }
    
    removeNeonGlow(element) {
        element.style.boxShadow = '';
        element.style.borderColor = '';
    }
    
    getRandomNeonColor() {
        const colors = Object.values(this.colors);
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    createScanLines() {
        const scanLines = document.createElement('div');
        scanLines.className = 'cyber-scan-lines';
        scanLines.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
            background: linear-gradient(
                transparent 50%, 
                rgba(0, 255, 255, 0.02) 50%
            );
            background-size: 100% 4px;
            animation: scan-lines 0.1s linear infinite;
            opacity: 0.6;
        `;
        
        document.body.appendChild(scanLines);
    }
    
    createHolographicOverlays() {
        const containers = document.querySelectorAll('.cyber-container, .holo-card');
        
        containers.forEach(container => {
            const overlay = document.createElement('div');
            overlay.className = 'holographic-overlay';
            overlay.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, 
                    transparent 30%, 
                    rgba(255, 255, 255, 0.05) 50%, 
                    transparent 70%);
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            `;
            
            container.style.position = 'relative';
            container.appendChild(overlay);
            
            container.addEventListener('mouseenter', () => {
                overlay.style.opacity = '1';
                overlay.style.animation = 'hologram-sweep 2s ease-in-out';
            });
            
            container.addEventListener('mouseleave', () => {
                overlay.style.opacity = '0';
                overlay.style.animation = '';
            });
        });
    }
    
    // ===== PARTICLE SYSTEM =====
    
    initializeParticleSystem() {
        this.particleSystem = new CyberpunkParticleSystem();
        this.particleSystem.init();
    }
    
    // ===== INTERACTIVE ELEMENTS =====
    
    setupInteractiveElements() {
        // Enhanced button interactions
        this.setupButtonEffects();
        
        // Form field enhancements
        this.setupFormEffects();
        
        // Card hover effects
        this.setupCardEffects();
        
        // Navigation enhancements
        this.setupNavigationEffects();
    }
    
    setupButtonEffects() {
        const buttons = document.querySelectorAll('.neon-button');
        
        buttons.forEach(button => {
            // Add ripple effect
            button.addEventListener('click', (e) => {
                this.createRippleEffect(e);
                this.playButtonSound();
            });
            
            // Add hover sound
            button.addEventListener('mouseenter', () => {
                this.playHoverSound();
            });
        });
    }
    
    createRippleEffect(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    setupFormEffects() {
        const inputs = document.querySelectorAll('.cyber-input');
        
        inputs.forEach(input => {
            // Add focus glow effect
            input.addEventListener('focus', () => {
                this.addInputGlow(input);
            });
            
            input.addEventListener('blur', () => {
                this.removeInputGlow(input);
            });
            
            // Add typing sound effects
            input.addEventListener('input', () => {
                this.playTypingSound();
            });
        });
    }
    
    addInputGlow(input) {
        input.style.boxShadow = `
            0 0 0 2px rgba(0, 255, 255, 0.4),
            0 0 20px rgba(0, 255, 255, 0.2),
            inset 0 0 20px rgba(0, 255, 255, 0.1)
        `;
    }
    
    removeInputGlow(input) {
        input.style.boxShadow = '';
    }
    
    setupCardEffects() {
        const cards = document.querySelectorAll('.holo-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.animateCard(card, 'enter');
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateCard(card, 'leave');
            });
        });
    }
    
    animateCard(card, action) {
        if (action === 'enter') {
            card.style.transform = 'translateY(-10px) rotateX(5deg) rotateY(2deg)';
            card.style.boxShadow = `
                0 20px 60px rgba(0, 0, 0, 0.4),
                0 0 0 1px rgba(0, 255, 255, 0.3),
                0 0 30px rgba(0, 255, 255, 0.2)
            `;
        } else {
            card.style.transform = '';
            card.style.boxShadow = '';
        }
    }
    
    setupNavigationEffects() {
        const navItems = document.querySelectorAll('nav a, .nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                this.addNavGlow(item);
            });
            
            item.addEventListener('mouseleave', () => {
                this.removeNavGlow(item);
            });
        });
    }
    
    addNavGlow(item) {
        item.style.textShadow = `
            0 0 10px ${this.colors.neonCyan},
            0 0 20px ${this.colors.neonCyan},
            0 0 30px ${this.colors.neonCyan}
        `;
    }
    
    removeNavGlow(item) {
        item.style.textShadow = '';
    }
    
    // ===== AUDIO VISUALIZATION =====
    
    initializeAudioVisualization() {
        this.createMusicVisualizer();
        this.setupAmbientSounds();
    }
    
    createMusicVisualizer() {
        const visualizer = document.createElement('div');
        visualizer.className = 'lofi-music-visualizer';
        visualizer.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            align-items: end;
            gap: 2px;
            height: 40px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid ${this.colors.neonCyan};
            border-radius: 8px;
            backdrop-filter: blur(10px);
            z-index: 1000;
        `;
        
        // Create visualizer bars
        for (let i = 0; i < 8; i++) {
            const bar = document.createElement('div');
            bar.className = 'visualizer-bar';
            bar.style.cssText = `
                width: 3px;
                background: linear-gradient(to top, ${this.colors.neonPink}, ${this.colors.neonCyan});
                border-radius: 2px;
                animation: visualizer ${1 + Math.random()}s ease-in-out infinite;
                animation-delay: ${i * 0.1}s;
            `;
            visualizer.appendChild(bar);
        }
        
        document.body.appendChild(visualizer);
        
        // Add click to toggle
        visualizer.addEventListener('click', () => {
            this.toggleLofiMode();
        });
    }
    
    setupAmbientSounds() {
        // Create audio context for sound effects
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.log('Audio context not supported');
        }
    }
    
    playButtonSound() {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(400, this.audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.1);
    }
    
    playHoverSound() {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
        
        gainNode.gain.setValueAtTime(0.05, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.05);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.05);
    }
    
    playTypingSound() {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.setValueAtTime(1200 + Math.random() * 200, this.audioContext.currentTime);
        
        gainNode.gain.setValueAtTime(0.03, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.02);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.02);
    }
    
    toggleLofiMode() {
        const body = document.body;
        const isLofiMode = body.classList.contains('lofi-mode');
        
        if (isLofiMode) {
            body.classList.remove('lofi-mode');
            this.stopAmbientLoop();
        } else {
            body.classList.add('lofi-mode');
            this.startAmbientLoop();
        }
    }
    
    startAmbientLoop() {
        // Add subtle ambient sound loop
        console.log('🎵 Starting lofi ambient mode');
    }
    
    stopAmbientLoop() {
        console.log('🔇 Stopping lofi ambient mode');
    }
    
    // ===== TYPING EFFECTS =====
    
    setupLofiTypingEffects() {
        const typewriterElements = document.querySelectorAll('[data-typewriter]');
        
        typewriterElements.forEach(element => {
            this.createTypewriterEffect(element);
        });
    }
    
    createTypewriterEffect(element) {
        const text = element.textContent;
        const speed = parseInt(element.dataset.typewriterSpeed) || 50;
        
        element.textContent = '';
        element.style.borderRight = '2px solid ' + this.colors.neonCyan;
        
        let i = 0;
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                
                // Play typing sound
                this.playTypingSound();
            } else {
                clearInterval(typeInterval);
                
                // Blinking cursor effect
                setInterval(() => {
                    element.style.borderRight = element.style.borderRight === 'none' 
                        ? '2px solid ' + this.colors.neonCyan 
                        : 'none';
                }, 500);
            }
        }, speed);
    }
    
    // ===== FLOATING MEMORIES =====
    
    createFloatingMemories() {
        const memories = [
            '💭', '🌸', '💫', '🎵', '💝', '🌙', '✨', '💌'
        ];
        
        setInterval(() => {
            this.createFloatingMemory(memories[Math.floor(Math.random() * memories.length)]);
        }, 3000);
    }
    
    createFloatingMemory(emoji) {
        const memory = document.createElement('div');
        memory.textContent = emoji;
        memory.style.cssText = `
            position: fixed;
            font-size: 24px;
            pointer-events: none;
            z-index: 100;
            opacity: 0.7;
            left: ${Math.random() * window.innerWidth}px;
            top: ${window.innerHeight + 50}px;
            animation: float-up 8s ease-out forwards;
        `;
        
        document.body.appendChild(memory);
        
        setTimeout(() => {
            memory.remove();
        }, 8000);
    }
    
    // ===== GLITCH EFFECTS =====
    
    setupGlitchEffects() {
        const glitchElements = document.querySelectorAll('.glitch-text');
        
        glitchElements.forEach(element => {
            this.addGlitchEffect(element);
        });
        
        // Random glitch on page elements
        setInterval(() => {
            this.randomGlitch();
        }, 10000);
    }
    
    addGlitchEffect(element) {
        const text = element.textContent;
        element.setAttribute('data-text', text);
        
        element.addEventListener('mouseenter', () => {
            this.triggerGlitch(element);
        });
    }
    
    triggerGlitch(element) {
        element.classList.add('glitching');
        
        setTimeout(() => {
            element.classList.remove('glitching');
        }, 500);
    }
    
    randomGlitch() {
        const elements = document.querySelectorAll('h1, h2, h3, .brand-title');
        if (elements.length === 0) return;
        
        const randomElement = elements[Math.floor(Math.random() * elements.length)];
        this.triggerGlitch(randomElement);
    }
    
    // ===== HEARTBEAT ANIMATION =====
    
    initializeHeartbeat() {
        const heartElements = document.querySelectorAll('.heartbeat, [data-heartbeat]');
        
        heartElements.forEach(element => {
            this.addHeartbeatEffect(element);
        });
    }
    
    addHeartbeatEffect(element) {
        element.style.animation = 'heartbeat 2s ease-in-out infinite';
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
    
    // ===== UTILITY METHODS =====
    
    addCustomStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            @keyframes visualizer {
                0%, 100% { height: 5px; }
                50% { height: 30px; }
            }
            
            @keyframes float-up {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 0.7;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
            
            @keyframes heartbeat {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @keyframes scan-lines {
                0% { transform: translateY(0); }
                100% { transform: translateY(4px); }
            }
            
            .glitching::before,
            .glitching::after {
                animation: glitch-1 0.3s infinite, glitch-2 0.3s infinite;
            }
            
            .fade-in-scroll {
                opacity: 0;
                transform: translateY(30px);
                transition: all 0.6s ease;
            }
            
            .fade-in-scroll.visible {
                opacity: 1;
                transform: translateY(0);
            }
            
            .lofi-mode {
                filter: sepia(0.2) saturate(0.8);
            }
            
            .lofi-mode .cyber-container {
                background: linear-gradient(135deg, 
                    rgba(255, 179, 71, 0.1) 0%, 
                    rgba(212, 165, 165, 0.1) 100%);
            }
        `;
        
        document.head.appendChild(style);
    }
}

// ===== PARTICLE SYSTEM CLASS =====

class CyberpunkParticleSystem {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.particles = [];
        this.animationId = null;
    }
    
    init() {
        this.createCanvas();
        this.setupParticles();
        this.animate();
    }
    
    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.6;
        `;
        
        this.ctx = this.canvas.getContext('2d');
        document.body.appendChild(this.canvas);
        
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    setupParticles() {
        const particleCount = Math.min(50, Math.floor(window.innerWidth / 20));
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                color: this.getRandomColor(),
                opacity: Math.random() * 0.5 + 0.2,
                pulse: Math.random() * Math.PI * 2
            });
        }
    }
    
    getRandomColor() {
        const colors = ['#ff0080', '#00ffff', '#8a2be2', '#00ff41', '#ffb347'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
            
            // Update pulse
            particle.pulse += 0.02;
            const pulsedOpacity = particle.opacity + Math.sin(particle.pulse) * 0.2;
            
            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = particle.color;
            this.ctx.globalAlpha = Math.max(0, pulsedOpacity);
            this.ctx.fill();
            
            // Draw connections
            this.drawConnections(particle);
        });
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    drawConnections(particle) {
        this.particles.forEach(otherParticle => {
            if (particle === otherParticle) return;
            
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
                this.ctx.beginPath();
                this.ctx.moveTo(particle.x, particle.y);
                this.ctx.lineTo(otherParticle.x, otherParticle.y);
                this.ctx.strokeStyle = particle.color;
                this.ctx.globalAlpha = (100 - distance) / 100 * 0.2;
                this.ctx.lineWidth = 0.5;
                this.ctx.stroke();
            }
        });
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas) {
            this.canvas.remove();
        }
    }
}

// ===== INITIALIZE EXPERIENCE =====

// Initialize the My Prabh Cyberpunk Lofi Experience
const myPrabhExperience = new MyPrabhCyberpunkExperience();

// Add custom styles
document.addEventListener('DOMContentLoaded', () => {
    myPrabhExperience.addCustomStyles();
});

// Export for global access
window.MyPrabhCyberpunkExperience = MyPrabhCyberpunkExperience;

/**
 * End of My Prabh Cyberpunk Lofi Interactive Experience
 * A digital love story told through interactive code
 * Where every click echoes with memories of tomorrow
 */