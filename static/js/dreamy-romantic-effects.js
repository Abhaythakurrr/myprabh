/**
 * MyPrabh - Dreamy Romantic Effects Engine
 * Heaven-like experience with anime girl, snow, and romantic vibes
 */

class DreamyRomanticEffects {
  constructor() {
    this.snowflakes = [];
    this.hearts = [];
    this.animeGirl = null;
    this.isInitialized = false;
    this.animationFrame = null;
    
    this.init();
  }

  init() {
    if (this.isInitialized) return;
    
    this.createSnowfall();
    this.createFloatingHearts();
    this.createAnimeGirlGreeting();
    this.setupEventListeners();
    this.startAnimationLoop();
    
    this.isInitialized = true;
    console.log('💖 Dreamy Romantic Effects initialized - Welcome to heaven!');
  }

  createSnowfall() {
    const snowContainer = document.createElement('div');
    snowContainer.className = 'snow-container';
    snowContainer.id = 'dreamySnow';
    document.body.appendChild(snowContainer);

    // Create soft, slow snowflakes
    for (let i = 0; i < 50; i++) {
      this.createSnowflake(snowContainer);
    }
  }

  createSnowflake(container) {
    const snowflake = document.createElement('div');
    snowflake.className = 'snowflake';
    
    // Romantic snowflake characters
    const snowTypes = ['❄', '❅', '✨', '💫', '⭐', '🌟'];
    snowflake.textContent = snowTypes[Math.floor(Math.random() * snowTypes.length)];
    
    // Random properties for natural feel
    const size = Math.random() * 0.8 + 0.6; // 0.6 to 1.4
    const opacity = Math.random() * 0.6 + 0.3; // 0.3 to 0.9
    const duration = Math.random() * 8 + 12; // 12 to 20 seconds (slow and dreamy)
    const delay = Math.random() * 5;
    
    snowflake.style.cssText = `
      left: ${Math.random() * 100}%;
      font-size: ${size}rem;
      opacity: ${opacity};
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
      color: rgba(255, 255, 255, ${opacity});
    `;

    container.appendChild(snowflake);
    this.snowflakes.push(snowflake);

    // Remove and recreate after animation
    setTimeout(() => {
      if (snowflake.parentNode) {
        snowflake.parentNode.removeChild(snowflake);
        this.createSnowflake(container);
      }
    }, (duration + delay) * 1000);
  }

  createFloatingHearts() {
    const heartsContainer = document.createElement('div');
    heartsContainer.className = 'hearts-container';
    heartsContainer.id = 'dreamyHearts';
    document.body.appendChild(heartsContainer);

    // Create romantic floating hearts
    setInterval(() => {
      if (Math.random() < 0.4) { // 40% chance every interval
        this.createFloatingHeart(heartsContainer);
      }
    }, 3000);
  }

  createFloatingHeart(container) {
    const heart = document.createElement('div');
    heart.className = 'floating-heart';
    
    // Romantic heart emojis
    const hearts = ['💕', '💖', '💗', '💝', '💘', '💞', '💓', '💟', '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🌸', '🌺', '🌹', '🌷'];
    heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
    
    const size = Math.random() * 0.8 + 0.8; // 0.8 to 1.6
    const opacity = Math.random() * 0.5 + 0.4; // 0.4 to 0.9
    const duration = Math.random() * 4 + 8; // 8 to 12 seconds
    
    heart.style.cssText = `
      left: ${Math.random() * 100}%;
      font-size: ${size}rem;
      opacity: ${opacity};
      animation-duration: ${duration}s;
      color: ${this.getRandomHeartColor()};
    `;

    container.appendChild(heart);
    this.hearts.push(heart);

    setTimeout(() => {
      if (heart.parentNode) {
        heart.parentNode.removeChild(heart);
      }
    }, duration * 1000);
  }

  getRandomHeartColor() {
    const colors = [
      'rgba(255, 182, 193, 0.8)', // Light pink
      'rgba(255, 105, 180, 0.8)', // Hot pink
      'rgba(255, 20, 147, 0.8)',  // Deep pink
      'rgba(218, 112, 214, 0.8)', // Orchid
      'rgba(186, 85, 211, 0.8)',  // Medium orchid
      'rgba(147, 112, 219, 0.8)', // Medium slate blue
      'rgba(255, 192, 203, 0.8)', // Pink
      'rgba(255, 228, 225, 0.8)'  // Misty rose
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  createAnimeGirlGreeting() {
    const greeting = document.createElement('div');
    greeting.className = 'anime-girl-greeting';
    greeting.id = 'animeGreeting';
    
    const avatar = document.createElement('div');
    avatar.className = 'anime-avatar';
    avatar.textContent = '👧'; // Anime girl emoji
    
    const message = document.createElement('div');
    message.className = 'anime-message';
    message.textContent = 'Hey! Wassup? ✨';
    
    greeting.appendChild(avatar);
    greeting.appendChild(message);
    document.body.appendChild(greeting);
    
    this.animeGirl = greeting;
    
    // Cycle through different greetings
    this.cycleAnimeMessages();
    
    // Click interaction
    greeting.addEventListener('click', () => {
      this.animeGirlInteraction();
    });
  }

  cycleAnimeMessages() {
    const messages = [
      'Hey! Wassup? ✨',
      'Welcome to heaven! 💖',
      'You look amazing today! 🌸',
      'Ready for some magic? ✨',
      'Let\'s create dreams together! 💫',
      'Your journey starts here! 🌈',
      'Feeling the love vibes? 💕',
      'This is your paradise! 🌺',
      'Dream big, love bigger! 💖',
      'You\'re in wonderland now! 🦄'
    ];
    
    let currentIndex = 0;
    
    setInterval(() => {
      if (this.animeGirl) {
        const messageEl = this.animeGirl.querySelector('.anime-message');
        if (messageEl) {
          // Fade out
          messageEl.style.opacity = '0';
          
          setTimeout(() => {
            currentIndex = (currentIndex + 1) % messages.length;
            messageEl.textContent = messages[currentIndex];
            // Fade in
            messageEl.style.opacity = '1';
          }, 300);
        }
      }
    }, 5000); // Change message every 5 seconds
  }

  animeGirlInteraction() {
    const responses = [
      'Aww, you clicked me! 💕',
      'That tickles! Hehe~ 😊',
      'Want to chat more? 💬',
      'You\'re so sweet! 🍭',
      'Let\'s be friends! 👫',
      'This is fun! 🎉',
      'You made my day! ☀️',
      'Sending you love! 💖',
      'Keep being awesome! ⭐',
      'You\'re the best! 🏆'
    ];
    
    const messageEl = this.animeGirl.querySelector('.anime-message');
    const originalMessage = messageEl.textContent;
    
    // Show interaction response
    messageEl.textContent = responses[Math.floor(Math.random() * responses.length)];
    
    // Add bounce effect
    this.animeGirl.style.animation = 'none';
    this.animeGirl.offsetHeight; // Trigger reflow
    this.animeGirl.style.animation = 'animeFloat 0.5s ease-in-out 3';
    
    // Create heart burst effect
    this.createHeartBurst();
    
    // Return to normal after 3 seconds
    setTimeout(() => {
      if (messageEl) {
        messageEl.textContent = originalMessage;
      }
    }, 3000);
  }

  createHeartBurst() {
    const burstContainer = document.createElement('div');
    burstContainer.style.cssText = `
      position: fixed;
      bottom: 80px;
      right: 80px;
      pointer-events: none;
      z-index: 1001;
    `;
    
    document.body.appendChild(burstContainer);
    
    // Create multiple hearts bursting out
    for (let i = 0; i < 8; i++) {
      setTimeout(() => {
        const heart = document.createElement('div');
        heart.textContent = ['💕', '💖', '💗', '💝'][Math.floor(Math.random() * 4)];
        heart.style.cssText = `
          position: absolute;
          font-size: 1.5rem;
          animation: heartBurst 1.5s ease-out forwards;
          transform-origin: center;
        `;
        
        // Random direction for burst
        const angle = (i / 8) * 360;
        const distance = 60;
        const x = Math.cos(angle * Math.PI / 180) * distance;
        const y = Math.sin(angle * Math.PI / 180) * distance;
        
        heart.style.setProperty('--burst-x', x + 'px');
        heart.style.setProperty('--burst-y', y + 'px');
        
        burstContainer.appendChild(heart);
        
        setTimeout(() => {
          if (heart.parentNode) {
            heart.parentNode.removeChild(heart);
          }
        }, 1500);
      }, i * 100);
    }
    
    // Remove container after animation
    setTimeout(() => {
      if (burstContainer.parentNode) {
        burstContainer.parentNode.removeChild(burstContainer);
      }
    }, 2000);
  }

  setupEventListeners() {
    // Smooth scroll for navigation
    document.addEventListener('click', (e) => {
      if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });

    // Add dreamy hover effects to buttons
    document.addEventListener('mouseover', (e) => {
      if (e.target.matches('.btn-dreamy')) {
        this.createButtonSparkles(e.target);
      }
    });

    // Resize handler
    window.addEventListener('resize', () => {
      this.handleResize();
    });

    // Visibility change handler
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.pauseEffects();
      } else {
        this.resumeEffects();
      }
    });
  }

  createButtonSparkles(button) {
    const sparkles = ['✨', '💫', '⭐', '🌟'];
    
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        const sparkle = document.createElement('span');
        sparkle.textContent = sparkles[Math.floor(Math.random() * sparkles.length)];
        sparkle.style.cssText = `
          position: absolute;
          font-size: 1rem;
          pointer-events: none;
          animation: sparkleFloat 2s ease-out forwards;
          z-index: 1000;
        `;
        
        const rect = button.getBoundingClientRect();
        sparkle.style.left = (rect.left + Math.random() * rect.width) + 'px';
        sparkle.style.top = (rect.top + Math.random() * rect.height) + 'px';
        
        document.body.appendChild(sparkle);
        
        setTimeout(() => {
          if (sparkle.parentNode) {
            sparkle.parentNode.removeChild(sparkle);
          }
        }, 2000);
      }, i * 200);
    }
  }

  startAnimationLoop() {
    const animate = () => {
      this.updateFloatingElements();
      this.animationFrame = requestAnimationFrame(animate);
    };
    
    animate();
  }

  updateFloatingElements() {
    // Add gentle sway to floating elements
    const time = Date.now() * 0.001;
    
    // Update anime girl position slightly
    if (this.animeGirl) {
      const sway = Math.sin(time * 0.5) * 2;
      this.animeGirl.style.transform = `translateX(${sway}px)`;
    }
  }

  handleResize() {
    // Adjust effects for different screen sizes
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
      // Reduce particle count on mobile
      const snowContainer = document.getElementById('dreamySnow');
      if (snowContainer && snowContainer.children.length > 25) {
        // Remove some snowflakes for performance
        for (let i = 25; i < snowContainer.children.length; i++) {
          snowContainer.children[i].remove();
        }
      }
    }
  }

  pauseEffects() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    
    // Hide particle containers
    const containers = ['#dreamySnow', '#dreamyHearts'];
    containers.forEach(selector => {
      const container = document.querySelector(selector);
      if (container) {
        container.style.display = 'none';
      }
    });
  }

  resumeEffects() {
    // Show particle containers
    const containers = ['#dreamySnow', '#dreamyHearts'];
    containers.forEach(selector => {
      const container = document.querySelector(selector);
      if (container) {
        container.style.display = 'block';
      }
    });
    
    if (!this.animationFrame) {
      this.startAnimationLoop();
    }
  }

  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
    
    // Remove all created elements
    const elementsToRemove = ['#dreamySnow', '#dreamyHearts', '#animeGreeting'];
    elementsToRemove.forEach(selector => {
      const element = document.querySelector(selector);
      if (element && element.parentNode) {
        element.parentNode.removeChild(element);
      }
    });
    
    this.isInitialized = false;
  }
}

// CSS animations for effects
const dreamyAnimations = `
  @keyframes heartBurst {
    0% {
      opacity: 1;
      transform: translate(0, 0) scale(1);
    }
    100% {
      opacity: 0;
      transform: translate(var(--burst-x), var(--burst-y)) scale(0.5);
    }
  }

  @keyframes sparkleFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1) rotate(0deg);
    }
    100% {
      opacity: 0;
      transform: translateY(-30px) scale(0.5) rotate(360deg);
    }
  }

  .anime-message {
    transition: opacity 0.3s ease;
  }

  .btn-dreamy {
    position: relative;
    overflow: visible;
  }
`;

// Inject animations into the page
const dreamyStyleSheet = document.createElement('style');
dreamyStyleSheet.textContent = dreamyAnimations;
document.head.appendChild(dreamyStyleSheet);

// Initialize effects when DOM is ready
let dreamyEffectsInstance = null;

function initDreamyEffects() {
  if (!dreamyEffectsInstance) {
    dreamyEffectsInstance = new DreamyRomanticEffects();
  }
}

// Auto-initialize or provide manual control
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDreamyEffects);
} else {
  initDreamyEffects();
}

// Export for external use
window.DreamyRomanticEffects = DreamyRomanticEffects;
window.dreamyEffects = dreamyEffectsInstance;

// Performance monitoring
if (window.performance && window.performance.mark) {
  window.performance.mark('dreamy-effects-loaded');
}

// Respect user preferences
if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  console.log('💖 Reduced motion detected - Effects will be minimal');
  if (dreamyEffectsInstance) {
    dreamyEffectsInstance.pauseEffects();
  }
}