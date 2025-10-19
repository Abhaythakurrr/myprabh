/**
 * Abhay's Console Effects Framework
 * Written at 4:12 AM while debugging my broken heart
 * Every function crafted while missing her
 * 
 * "I hope these animations make someone smile the way she used to make me smile"
 * - Abhay
 */

// Global namespace for Abhay's effects
window.abhayEffects = (function() {
    'use strict';
    
    // Emotional state tracking
    let currentEmotionalState = 'hopeful'; // hopeful, desperate, remembering, broken
    let glitchIntensity = 0.3;
    let lastHeartbeat = Date.now();
    
    /**
     * Initialize all console effects when DOM is ready
     * Called automatically - Abhay's digital heart starts beating
     */
    function init() {
        console.log('💔 Abhay\'s Console Effects Framework initialized');
        console.log('👨‍💻 Built with tears, hope, and 847 cups of coffee');
        console.log('💖 Current emotional state:', currentEmotionalState);
        
        // Start the heartbeat
        startEmotionalHeartbeat();
        
        // Initialize all effects
        initializeGlitchEffects();
        initializeTypingAnimations();
        initializeScanLines();
        initializeConsolePrompts();
        initializeEmotionalPulses();
        
        // Add event listeners
        addGlobalEventListeners();
        
        // Easter eggs for emotional connection
        initializeEasterEggs();
    }
    
    /**
     * Emotional heartbeat - the core of Abhay's digital soul
     * Pulses every 2 seconds, adjusting effects based on emotional state
     */
    function startEmotionalHeartbeat() {
        setInterval(() => {
            lastHeartbeat = Date.now();
            
            // Adjust glitch intensity based on emotional state
            switch(currentEmotionalState) {
                case 'desperate':
                    glitchIntensity = 0.8;
                    break;
                case 'broken':
                    glitchIntensity = 1.0;
                    break;
                case 'remembering':
                    glitchIntensity = 0.5;
                    break;
                case 'hopeful':
                default:
                    glitchIntensity = 0.3;
                    break;
            }
            
            // Trigger random emotional effects
            if (Math.random() < 0.1) {
                triggerRandomEmotionalEffect();
            }
            
        }, 2000); // Heartbeat every 2 seconds
    }
    
    /**
     * Apply glitch effect to any element
     * @param {Element} element - Target element
     * @param {number} duration - Effect duration in ms
     * @param {number} intensity - Glitch intensity (0-1)
     */
    function applyGlitchEffect(element, duration = 1000, intensity = null) {
        if (!element) return;
        
        const effectIntensity = intensity || glitchIntensity;
        const originalText = element.textContent;
        
        // Set data attribute for CSS glitch effect
        element.setAttribute('data-text', originalText);
        element.classList.add('glitch');
        
        // Add random character corruption
        const corruptText = () => {
            if (Math.random() < effectIntensity) {
                const chars = '!@#$%^&*()_+-=[]{}|;:,.<>?~`';
                const corrupted = originalText.split('').map(char => {
                    return Math.random() < 0.1 ? chars[Math.floor(Math.random() * chars.length)] : char;
                }).join('');
                element.textContent = corrupted;
            }
        };
        
        // Corrupt text randomly during effect
        const corruptInterval = setInterval(corruptText, 50);
        
        // Clean up after duration
        setTimeout(() => {
            clearInterval(corruptInterval);
            element.textContent = originalText;
            element.classList.remove('glitch');
            element.removeAttribute('data-text');
        }, duration);
        
        console.log('💔 Glitch effect applied - reality is breaking like my heart');
    }
    
    /**
     * Type text character by character like Abhay coding at 3 AM
     * @param {Element} element - Target element
     * @param {string} text - Text to type
     * @param {number} speed - Typing speed in ms per character
     * @param {Function} callback - Called when typing completes
     */
    function typeText(element, text, speed = 100, callback = null) {
        if (!element) return;
        
        element.textContent = '';
        element.classList.add('typing-animation');
        
        let i = 0;
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                
                // Random typing variations (Abhay's tired fingers)
                if (Math.random() < 0.05) {
                    // Occasional pause (thinking of her)
                    clearInterval(typeInterval);
                    setTimeout(() => {
                        const newInterval = setInterval(() => {
                            if (i < text.length) {
                                element.textContent += text.charAt(i);
                                i++;
                            } else {
                                clearInterval(newInterval);
                                element.classList.remove('typing-animation');
                                if (callback) callback();
                            }
                        }, speed);
                    }, 300);
                    return;
                }
            } else {
                clearInterval(typeInterval);
                element.classList.remove('typing-animation');
                if (callback) callback();
            }
        }, speed);
        
        console.log('⌨️ Typing animation started - like Abhay coding through tears');
    }
    
    /**
     * Create emotional pulse effect
     * @param {Element} element - Target element
     * @param {string} emotion - Emotion type (hopeful, desperate, remembering, broken)
     * @param {number} duration - Effect duration in ms
     */
    function emotionalPulse(element, emotion = 'hopeful', duration = 2000) {
        if (!element) return;
        
        const colors = {
            hopeful: 'rgba(0, 255, 65, 0.3)',
            desperate: 'rgba(255, 107, 157, 0.5)',
            remembering: 'rgba(255, 179, 71, 0.4)',
            broken: 'rgba(255, 7, 58, 0.6)'
        };
        
        const color = colors[emotion] || colors.hopeful;
        
        element.style.animation = `emotional-pulse ${duration}ms ease-in-out`;
        element.style.setProperty('--pulse-color', color);
        
        setTimeout(() => {
            element.style.animation = '';
            element.style.removeProperty('--pulse-color');
        }, duration);
        
        console.log(`💗 Emotional pulse: ${emotion} - feeling it in my code`);
    }
    
    /**
     * Initialize glitch effects on elements with .glitch class
     */
    function initializeGlitchEffects() {
        document.querySelectorAll('.glitch').forEach(element => {
            // Random glitch triggers
            setInterval(() => {
                if (Math.random() < 0.05) {
                    applyGlitchEffect(element, 500);
                }
            }, 3000);
        });
    }
    
    /**
     * Initialize typing animations
     */
    function initializeTypingAnimations() {
        document.querySelectorAll('[data-type-text]').forEach(element => {
            const text = element.getAttribute('data-type-text');
            const speed = parseInt(element.getAttribute('data-type-speed')) || 100;
            
            // Start typing when element comes into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        typeText(element, text, speed);
                        observer.unobserve(element);
                    }
                });
            });
            
            observer.observe(element);
        });
    }
    
    /**
     * Initialize scan lines effect
     */
    function initializeScanLines() {
        document.querySelectorAll('.scan-lines').forEach(element => {
            // Scan lines are handled by CSS, but we can add dynamic intensity
            setInterval(() => {
                const intensity = glitchIntensity;
                element.style.setProperty('--scan-opacity', intensity * 0.1);
            }, 1000);
        });
    }
    
    /**
     * Initialize console prompts with blinking cursors
     */
    function initializeConsolePrompts() {
        document.querySelectorAll('.terminal-prompt').forEach(prompt => {
            // Add random typing sounds (visual feedback)
            prompt.addEventListener('click', () => {
                console.log('💻 Terminal prompt clicked - accessing Abhay\'s digital soul');
                emotionalPulse(prompt, 'hopeful', 1000);
            });
        });
    }
    
    /**
     * Initialize emotional pulses
     */
    function initializeEmotionalPulses() {
        document.querySelectorAll('.emotional-pulse').forEach(element => {
            // Pulse based on emotional state
            setInterval(() => {
                emotionalPulse(element, currentEmotionalState, 2000);
            }, 5000);
        });
    }
    
    /**
     * Add global event listeners for emotional interactions
     */
    function addGlobalEventListeners() {
        // Console button interactions
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('console-button')) {
                console.log('🖱️ Console button clicked - hope level +1');
                applyGlitchEffect(e.target, 300, 0.2);
                emotionalPulse(e.target, 'hopeful', 1000);
            }
        });
        
        // Form input focus effects
        document.addEventListener('focus', (e) => {
            if (e.target.classList.contains('console-input')) {
                console.log('📝 Input focused - preparing to receive memories');
                emotionalPulse(e.target.parentElement, 'hopeful', 1500);
            }
        }, true);
        
        // Error state handling
        document.addEventListener('error', (e) => {
            console.log('💔 Error detected - system heartbreak');
            setEmotionalState('broken');
            
            // Find error elements and apply effects
            document.querySelectorAll('.error-message, .error-text').forEach(errorEl => {
                applyGlitchEffect(errorEl, 2000, 0.8);
            });
        });
        
        // Success state handling
        document.addEventListener('success', (e) => {
            console.log('✅ Success detected - hope restored');
            setEmotionalState('hopeful');
        });
    }
    
    /**
     * Initialize easter eggs for emotional connection
     */
    function initializeEasterEggs() {
        let konamiCode = [];
        const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA
        
        document.addEventListener('keydown', (e) => {
            konamiCode.push(e.keyCode);
            if (konamiCode.length > konamiSequence.length) {
                konamiCode.shift();
            }
            
            if (konamiCode.join(',') === konamiSequence.join(',')) {
                triggerAbhayEasterEgg();
                konamiCode = [];
            }
        });
        
        // Typing "prabh" anywhere triggers emotional response
        let typedSequence = '';
        document.addEventListener('keypress', (e) => {
            typedSequence += e.key.toLowerCase();
            if (typedSequence.length > 10) {
                typedSequence = typedSequence.slice(-10);
            }
            
            if (typedSequence.includes('prabh')) {
                console.log('💔 Her name detected... my heart just broke again');
                setEmotionalState('remembering');
                
                // Apply glitch to all text elements
                document.querySelectorAll('h1, h2, h3, .abhay-title').forEach(el => {
                    applyGlitchEffect(el, 3000, 0.7);
                });
                
                typedSequence = '';
            }
        });
    }
    
    /**
     * Trigger random emotional effects
     */
    function triggerRandomEmotionalEffect() {
        const effects = [
            () => {
                // Random glitch on title elements
                const titles = document.querySelectorAll('h1, h2, .abhay-title');
                if (titles.length > 0) {
                    const randomTitle = titles[Math.floor(Math.random() * titles.length)];
                    applyGlitchEffect(randomTitle, 1000);
                }
            },
            () => {
                // Emotional pulse on random console elements
                const consoleElements = document.querySelectorAll('.console-container, .console-button');
                if (consoleElements.length > 0) {
                    const randomEl = consoleElements[Math.floor(Math.random() * consoleElements.length)];
                    emotionalPulse(randomEl, currentEmotionalState, 1500);
                }
            },
            () => {
                // Console message
                const messages = [
                    '💭 Abhay: "I wonder if she would have liked this feature..."',
                    '☕ Abhay just spilled coffee on his keyboard (again)',
                    '💔 Abhay: "Why is debugging emotions so much harder than debugging code?"',
                    '🌙 Abhay: "It\'s 3 AM and I\'m still coding... for her"',
                    '💝 Abhay: "Every line of code is a love letter I\'ll never send"'
                ];
                console.log(messages[Math.floor(Math.random() * messages.length)]);
            }
        ];
        
        const randomEffect = effects[Math.floor(Math.random() * effects.length)];
        randomEffect();
    }
    
    /**
     * Trigger Abhay's special easter egg
     */
    function triggerAbhayEasterEgg() {
        console.log('🎉 Konami Code detected! Abhay\'s secret message unlocked:');
        console.log('💌 "If you found this, you understand the pain of loving someone who\'s gone."');
        console.log('💔 "I built this hoping she\'d come back. Maybe you\'ll find what I lost."');
        console.log('🤗 "Thank you for caring enough to look deeper. - Abhay"');
        
        // Epic glitch effect on entire page
        document.body.style.animation = 'glitch-1 2s ease-in-out';
        
        setTimeout(() => {
            document.body.style.animation = '';
            
            // Show hidden message
            const message = document.createElement('div');
            message.innerHTML = `
                <div style="
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: var(--deep-sorrow);
                    border: 2px solid var(--prabh-love);
                    border-radius: 10px;
                    padding: 2rem;
                    text-align: center;
                    z-index: 9999;
                    font-family: 'Caveat', cursive;
                    color: var(--prabh-love);
                    font-size: 1.5rem;
                    max-width: 400px;
                ">
                    <div>💌</div>
                    <div style="margin: 1rem 0;">
                        "Thank you for understanding my pain.<br>
                        Maybe you'll find the love I lost."
                    </div>
                    <div style="font-size: 1rem; opacity: 0.8;">
                        - Abhay, 3:47 AM
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()" 
                            style="margin-top: 1rem; padding: 0.5rem 1rem; 
                                   background: var(--prabh-love); color: white; 
                                   border: none; border-radius: 5px; cursor: pointer;">
                        Close
                    </button>
                </div>
            `;
            
            document.body.appendChild(message);
            
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 10000);
            
        }, 2000);
    }
    
    /**
     * Set emotional state and adjust all effects accordingly
     * @param {string} state - New emotional state
     */
    function setEmotionalState(state) {
        const validStates = ['hopeful', 'desperate', 'remembering', 'broken'];
        if (validStates.includes(state)) {
            currentEmotionalState = state;
            console.log(`💭 Emotional state changed to: ${state}`);
            
            // Trigger state-specific effects
            document.body.setAttribute('data-emotional-state', state);
            
            // Adjust CSS custom properties based on state
            const root = document.documentElement;
            switch(state) {
                case 'desperate':
                    root.style.setProperty('--glitch-intensity', '0.8');
                    root.style.setProperty('--pulse-frequency', '1s');
                    break;
                case 'broken':
                    root.style.setProperty('--glitch-intensity', '1.0');
                    root.style.setProperty('--pulse-frequency', '0.5s');
                    break;
                case 'remembering':
                    root.style.setProperty('--glitch-intensity', '0.5');
                    root.style.setProperty('--pulse-frequency', '3s');
                    break;
                case 'hopeful':
                default:
                    root.style.setProperty('--glitch-intensity', '0.3');
                    root.style.setProperty('--pulse-frequency', '2s');
                    break;
            }
        }
    }
    
    /**
     * Get current emotional state
     * @returns {string} Current emotional state
     */
    function getEmotionalState() {
        return currentEmotionalState;
    }
    
    /**
     * Manual trigger for console effects (for testing)
     */
    function testEffects() {
        console.log('🧪 Testing Abhay\'s console effects...');
        
        const testElement = document.querySelector('h1') || document.body;
        
        console.log('Testing glitch effect...');
        applyGlitchEffect(testElement, 2000, 0.8);
        
        setTimeout(() => {
            console.log('Testing emotional pulse...');
            emotionalPulse(testElement, 'desperate', 2000);
        }, 2500);
        
        setTimeout(() => {
            console.log('Testing typing animation...');
            const testDiv = document.createElement('div');
            testDiv.style.cssText = 'position: fixed; top: 20px; left: 20px; z-index: 9999; color: var(--console-green); font-family: monospace;';
            document.body.appendChild(testDiv);
            
            typeText(testDiv, 'Testing Abhay\'s broken heart in code...', 100, () => {
                setTimeout(() => testDiv.remove(), 3000);
            });
        }, 5000);
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Public API
    return {
        init,
        applyGlitchEffect,
        typeText,
        emotionalPulse,
        setEmotionalState,
        getEmotionalState,
        testEffects
    };
    
})();

/**
 * Console messages for emotional connection
 * These run automatically when the script loads
 */
console.log('💔 Abhay\'s Console Effects loaded');
console.log('⏰ Current time: ' + new Date().toLocaleString());
console.log('💭 Abhay\'s note: "Every animation is a piece of my heart"');
console.log('🎯 Try typing "prabh" anywhere or use the Konami code ↑↑↓↓←→←→BA');
console.log('🤝 Built with love, maintained with hope');

/**
 * Global error handler with emotional context
 */
window.addEventListener('error', (e) => {
    console.error('💥 System error detected:', e.message);
    console.log('💔 Abhay: "Even my code is broken... like everything else"');
    
    if (window.abhayEffects) {
        window.abhayEffects.setEmotionalState('broken');
    }
});

/**
 * Performance monitoring with emotional commentary
 */
window.addEventListener('load', () => {
    const loadTime = performance.now();
    console.log(`⚡ Page loaded in ${loadTime.toFixed(2)}ms`);
    
    if (loadTime > 3000) {
        console.log('🐌 Abhay: "Slow loading... like my healing process"');
    } else if (loadTime < 1000) {
        console.log('🚀 Abhay: "Fast loading! Maybe there\'s hope after all"');
    } else {
        console.log('⏱️ Abhay: "Decent loading time... like my emotional state"');
    }
});

/*
 * End of Abhay's Console Effects Framework
 * 
 * "I spent 3 months perfecting these animations.
 *  Each glitch represents a moment my heart broke.
 *  Each pulse is a heartbeat I wish she could feel.
 *  If you're reading this, thank you for caring about the details.
 *  Maybe you understand what it's like to love someone who's gone."
 * 
 * - Abhay, 4:12 AM, still coding, still hoping
 */