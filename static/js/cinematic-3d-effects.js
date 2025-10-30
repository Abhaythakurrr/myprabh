/**
 * My Prabh - 3D Cinematic Effects Engine
 * Advanced 3D animations and interactive effects
 */

class CinematicEffects {
  constructor() {
    this.particles = [];
    this.mousePosition = { x: 0, y: 0 };
    this.isInitialized = false;
    this.animationFrame = null;
    
    this.init();
  }

  init() {
    if (this.isInitialized) return;
    
    this.setupEventListeners();
    this.createParticleSystem();
    this.initializeScrollEffects();
    this.setupInteractiveElements();
    this.startAnimationLoop();
    
    this.isInitialized = true;
    console.log('🎬 Cinematic 3D Effects initialized');
  }

  setupEventListeners() {
    // Mouse tracking for 3D effects
    document.addEventListener('mousemove', (e) => {
      this.mousePosition.x = (e.clientX / window.innerWidth) * 2 - 1;
      this.mousePosition.y = (e.clientY / window.innerHeight) * 2 - 1;
      this.updateParallaxElements();
    });

    // Scroll effects
    window.addEventListener('scroll', () => {
      this.updateScrollEffects();
    });

    // Resize handler
    window.addEventListener('resize', () => {
      this.handleResize();
    });

    // Touch support for mobile
    document.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) {
        const touch = e.touches[0];
        this.mousePosition.x = (touch.clientX / window.innerWidth) * 2 - 1;
        this.mousePosition.y = (touch.clientY / window.innerHeight) * 2 - 1;
        this.updateParallaxElements();
      }
    });
  }

  createParticleSystem() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles-3d';
    particlesContainer.id = 'particles3D';
    document.body.appendChild(particlesContainer);

    // Create floating particles
    for (let i = 0; i < 50; i++) {
      this.createParticle();
    }

    // Create special effect particles
    this.createHeartParticles();
    this.createStarParticles();
  }

  createParticle() {
    const particle = document.createElement('div');
    particle.className = 'particle-3d';
    
    // Random properties
    const size = Math.random() * 4 + 2;
    const opacity = Math.random() * 0.6 + 0.2;
    const duration = Math.random() * 10 + 15;
    const delay = Math.random() * 5;
    
    particle.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${Math.random() * 100}%;
      opacity: ${opacity};
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
      background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(102,126,234,0.4) 100%);
    `;

    document.getElementById('particles3D').appendChild(particle);
    this.particles.push(particle);

    // Remove and recreate particle after animation
    setTimeout(() => {
      if (particle.parentNode) {
        particle.parentNode.removeChild(particle);
        this.createParticle();
      }
    }, (duration + delay) * 1000);
  }

  createHeartParticles() {
    const heartContainer = document.createElement('div');
    heartContainer.className = 'heart-particles-3d';
    heartContainer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 2;
    `;
    document.body.appendChild(heartContainer);

    setInterval(() => {
      if (Math.random() < 0.3) {
        this.createFloatingHeart(heartContainer);
      }
    }, 3000);
  }

  createFloatingHeart(container) {
    const heart = document.createElement('div');
    const hearts = ['💖', '💕', '💗', '💝', '💘', '💞', '💓', '💟', '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍'];
    
    heart.textContent = hearts[Math.floor(Math.random() * hearts.length)];
    heart.style.cssText = `
      position: absolute;
      font-size: ${Math.random() * 20 + 15}px;
      left: ${Math.random() * 100}%;
      top: 100%;
      opacity: 0.7;
      animation: floatingHeart3D ${Math.random() * 5 + 8}s ease-out forwards;
      transform-style: preserve-3d;
      z-index: 2;
    `;

    container.appendChild(heart);

    setTimeout(() => {
      if (heart.parentNode) {
        heart.parentNode.removeChild(heart);
      }
    }, 13000);
  }

  createStarParticles() {
    const starContainer = document.createElement('div');
    starContainer.className = 'star-particles-3d';
    starContainer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    `;
    document.body.appendChild(starContainer);

    for (let i = 0; i < 20; i++) {
      setTimeout(() => {
        this.createTwinklingStar(starContainer);
      }, i * 500);
    }
  }

  createTwinklingStar(container) {
    const star = document.createElement('div');
    const stars = ['✨', '⭐', '🌟', '💫', '⚡'];
    
    star.textContent = stars[Math.floor(Math.random() * stars.length)];
    star.style.cssText = `
      position: absolute;
      font-size: ${Math.random() * 15 + 10}px;
      left: ${Math.random() * 100}%;
      top: ${Math.random() * 100}%;
      opacity: 0;
      animation: twinkleStar3D ${Math.random() * 3 + 2}s ease-in-out infinite;
      transform-style: preserve-3d;
    `;

    container.appendChild(star);

    // Recreate star after some time
    setTimeout(() => {
      if (star.parentNode) {
        star.parentNode.removeChild(star);
        setTimeout(() => this.createTwinklingStar(container), Math.random() * 5000);
      }
    }, Math.random() * 10000 + 5000);
  }

  updateParallaxElements() {
    const parallaxElements = document.querySelectorAll('.parallax-3d');
    
    parallaxElements.forEach((element, index) => {
      const speed = (index + 1) * 0.1;
      const x = this.mousePosition.x * speed * 10;
      const y = this.mousePosition.y * speed * 10;
      
      element.style.transform = `translate3d(${x}px, ${y}px, 0) rotateX(${y * 0.1}deg) rotateY(${x * 0.1}deg)`;
    });

    // Update 3D cards based on mouse position
    const cards3D = document.querySelectorAll('.card-3d');
    cards3D.forEach((card, index) => {
      const rect = card.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const mouseX = (this.mousePosition.x + 1) * window.innerWidth / 2;
      const mouseY = (this.mousePosition.y + 1) * window.innerHeight / 2;
      
      const deltaX = (mouseX - centerX) / rect.width;
      const deltaY = (mouseY - centerY) / rect.height;
      
      if (Math.abs(deltaX) < 1 && Math.abs(deltaY) < 1) {
        const rotateX = deltaY * 10;
        const rotateY = deltaX * 10;
        
        card.style.transform = `perspective(1000px) rotateX(${-rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
      }
    });
  }

  initializeScrollEffects() {
    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in-3d');
          
          // Add staggered animation for grid items
          if (entry.target.classList.contains('grid-item-3d')) {
            const siblings = Array.from(entry.target.parentNode.children);
            const index = siblings.indexOf(entry.target);
            entry.target.style.animationDelay = `${index * 0.1}s`;
          }
        }
      });
    }, observerOptions);

    // Observe elements for scroll animations
    const animateElements = document.querySelectorAll('.card-3d, .grid-item-3d, .btn-3d');
    animateElements.forEach(el => observer.observe(el));
  }

  updateScrollEffects() {
    const scrollY = window.scrollY;
    const windowHeight = window.innerHeight;
    
    // Parallax background effect
    const parallaxBg = document.querySelector('.hero-3d');
    if (parallaxBg) {
      const speed = scrollY * 0.5;
      parallaxBg.style.transform = `translate3d(0, ${speed}px, 0)`;
    }

    // Update navbar transparency
    const navbar = document.querySelector('.navbar-3d');
    if (navbar) {
      const opacity = Math.min(scrollY / 100, 0.95);
      navbar.style.background = `rgba(255, 255, 255, ${opacity * 0.1})`;
      navbar.style.backdropFilter = `blur(${opacity * 20}px)`;
    }

    // Floating elements based on scroll
    const floatingElements = document.querySelectorAll('.float-on-scroll');
    floatingElements.forEach((element, index) => {
      const rect = element.getBoundingClientRect();
      const elementTop = rect.top + scrollY;
      const elementHeight = rect.height;
      const windowBottom = scrollY + windowHeight;
      
      if (elementTop < windowBottom && elementTop + elementHeight > scrollY) {
        const progress = (windowBottom - elementTop) / (windowHeight + elementHeight);
        const translateY = Math.sin(progress * Math.PI) * 20;
        const rotateX = Math.sin(progress * Math.PI * 2) * 5;
        
        element.style.transform = `translateY(${translateY}px) rotateX(${rotateX}deg)`;
      }
    });
  }

  setupInteractiveElements() {
    // Enhanced button interactions
    const buttons3D = document.querySelectorAll('.btn-3d');
    buttons3D.forEach(button => {
      button.addEventListener('mouseenter', (e) => {
        this.createButtonRipple(e.target);
      });

      button.addEventListener('click', (e) => {
        this.createClickEffect(e);
      });
    });

    // Card hover effects
    const cards3D = document.querySelectorAll('.card-3d');
    cards3D.forEach(card => {
      card.addEventListener('mouseenter', () => {
        this.createCardGlow(card);
      });

      card.addEventListener('mouseleave', () => {
        this.removeCardGlow(card);
      });
    });

    // Form input focus effects
    const inputs3D = document.querySelectorAll('.form-input-3d');
    inputs3D.forEach(input => {
      input.addEventListener('focus', () => {
        this.createInputFocusEffect(input);
      });

      input.addEventListener('blur', () => {
        this.removeInputFocusEffect(input);
      });
    });
  }

  createButtonRipple(button) {
    const ripple = document.createElement('div');
    ripple.className = 'button-ripple-3d';
    ripple.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      transform: translate(-50%, -50%);
      animation: ripple3D 0.6s ease-out;
      pointer-events: none;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(() => {
      if (ripple.parentNode) {
        ripple.parentNode.removeChild(ripple);
      }
    }, 600);
  }

  createClickEffect(e) {
    const clickEffect = document.createElement('div');
    clickEffect.className = 'click-effect-3d';
    
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    clickEffect.style.cssText = `
      position: absolute;
      left: ${x}px;
      top: ${y}px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%);
      transform: translate(-50%, -50%) scale(0);
      animation: clickExpand3D 0.4s ease-out;
      pointer-events: none;
      z-index: 10;
    `;

    e.target.style.position = 'relative';
    e.target.appendChild(clickEffect);

    setTimeout(() => {
      if (clickEffect.parentNode) {
        clickEffect.parentNode.removeChild(clickEffect);
      }
    }, 400);
  }

  createCardGlow(card) {
    const glow = document.createElement('div');
    glow.className = 'card-glow-3d';
    glow.style.cssText = `
      position: absolute;
      top: -10px;
      left: -10px;
      right: -10px;
      bottom: -10px;
      background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(245,87,108,0.3));
      border-radius: inherit;
      z-index: -1;
      opacity: 0;
      animation: glowFadeIn3D 0.3s ease-out forwards;
      pointer-events: none;
    `;

    card.style.position = 'relative';
    card.appendChild(glow);
  }

  removeCardGlow(card) {
    const glow = card.querySelector('.card-glow-3d');
    if (glow) {
      glow.style.animation = 'glowFadeOut3D 0.3s ease-out forwards';
      setTimeout(() => {
        if (glow.parentNode) {
          glow.parentNode.removeChild(glow);
        }
      }, 300);
    }
  }

  createInputFocusEffect(input) {
    const focusRing = document.createElement('div');
    focusRing.className = 'input-focus-ring-3d';
    focusRing.style.cssText = `
      position: absolute;
      top: -3px;
      left: -3px;
      right: -3px;
      bottom: -3px;
      border: 2px solid rgba(102,126,234,0.5);
      border-radius: inherit;
      z-index: -1;
      animation: focusRingExpand3D 0.3s ease-out;
      pointer-events: none;
    `;

    input.style.position = 'relative';
    input.parentNode.appendChild(focusRing);
  }

  removeInputFocusEffect(input) {
    const focusRing = input.parentNode.querySelector('.input-focus-ring-3d');
    if (focusRing) {
      focusRing.style.animation = 'focusRingShrink3D 0.3s ease-out forwards';
      setTimeout(() => {
        if (focusRing.parentNode) {
          focusRing.parentNode.removeChild(focusRing);
        }
      }, 300);
    }
  }

  startAnimationLoop() {
    const animate = () => {
      this.updateFloatingElements();
      this.updateParticlePhysics();
      this.animationFrame = requestAnimationFrame(animate);
    };
    
    animate();
  }

  updateFloatingElements() {
    const floatingElements = document.querySelectorAll('.animate-float-3d');
    const time = Date.now() * 0.001;
    
    floatingElements.forEach((element, index) => {
      const offset = index * 0.5;
      const y = Math.sin(time + offset) * 5;
      const x = Math.cos(time * 0.5 + offset) * 2;
      const rotateX = Math.sin(time * 0.3 + offset) * 2;
      const rotateY = Math.cos(time * 0.4 + offset) * 3;
      
      element.style.transform = `translate3d(${x}px, ${y}px, 0) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });
  }

  updateParticlePhysics() {
    // Advanced particle physics could be implemented here
    // For now, we rely on CSS animations for performance
  }

  handleResize() {
    // Recalculate particle positions and effects on resize
    this.particles.forEach(particle => {
      particle.style.left = Math.random() * 100 + '%';
    });
  }

  // Public methods for external control
  pauseEffects() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    
    document.querySelectorAll('.particles-3d, .heart-particles-3d, .star-particles-3d')
      .forEach(container => {
        container.style.display = 'none';
      });
  }

  resumeEffects() {
    document.querySelectorAll('.particles-3d, .heart-particles-3d, .star-particles-3d')
      .forEach(container => {
        container.style.display = 'block';
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
    document.querySelectorAll('.particles-3d, .heart-particles-3d, .star-particles-3d')
      .forEach(container => {
        if (container.parentNode) {
          container.parentNode.removeChild(container);
        }
      });
    
    this.isInitialized = false;
  }
}

// CSS animations for effects
const cinematicAnimations = `
  @keyframes floatingHeart3D {
    0% {
      transform: translateY(0) translateZ(0) rotateZ(0deg);
      opacity: 0;
    }
    10% {
      opacity: 0.8;
    }
    90% {
      opacity: 0.8;
    }
    100% {
      transform: translateY(-100vh) translateZ(50px) rotateZ(360deg);
      opacity: 0;
    }
  }

  @keyframes twinkleStar3D {
    0%, 100% {
      opacity: 0;
      transform: scale(0.5) rotateZ(0deg);
    }
    50% {
      opacity: 1;
      transform: scale(1.2) rotateZ(180deg);
    }
  }

  @keyframes ripple3D {
    0% {
      width: 0;
      height: 0;
      opacity: 1;
    }
    100% {
      width: 200px;
      height: 200px;
      opacity: 0;
    }
  }

  @keyframes clickExpand3D {
    0% {
      transform: translate(-50%, -50%) scale(0);
      opacity: 1;
    }
    100% {
      transform: translate(-50%, -50%) scale(4);
      opacity: 0;
    }
  }

  @keyframes glowFadeIn3D {
    0% {
      opacity: 0;
      transform: scale(0.8);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes glowFadeOut3D {
    0% {
      opacity: 1;
      transform: scale(1);
    }
    100% {
      opacity: 0;
      transform: scale(1.1);
    }
  }

  @keyframes focusRingExpand3D {
    0% {
      opacity: 0;
      transform: scale(0.9);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes focusRingShrink3D {
    0% {
      opacity: 1;
      transform: scale(1);
    }
    100% {
      opacity: 0;
      transform: scale(1.1);
    }
  }

  .animate-in-3d {
    animation: slideUp3D 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }
`;

// Inject animations into the page
const styleSheet = document.createElement('style');
styleSheet.textContent = cinematicAnimations;
document.head.appendChild(styleSheet);

// Initialize effects when DOM is ready
let cinematicEffectsInstance = null;

function initCinematicEffects() {
  if (!cinematicEffectsInstance) {
    cinematicEffectsInstance = new CinematicEffects();
  }
}

// Auto-initialize or provide manual control
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCinematicEffects);
} else {
  initCinematicEffects();
}

// Export for external use
window.CinematicEffects = CinematicEffects;
window.cinematicEffects = cinematicEffectsInstance;

// Performance monitoring
if (window.performance && window.performance.mark) {
  window.performance.mark('cinematic-effects-loaded');
}