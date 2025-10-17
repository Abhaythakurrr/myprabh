/**
 * Modern UI JavaScript Framework for My Prabh
 * Includes GSAP animations, Three.js integration, and modern interactions
 */

class ModernUI {
    constructor() {
        this.init();
        this.setupAnimations();
        this.setupInteractions();
        this.setupTheme();
    }

    init() {
        console.log('🚀 Modern UI Framework initialized');
        
        // Initialize responsive layout first
        this.initResponsiveLayout();
        
        // Initialize touch gestures
        this.initTouchGestures();
        
        // Initialize GSAP
        if (typeof gsap !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger, TextPlugin);
            this.setupGSAPAnimations();
        }
        
        // Initialize Three.js if available (skip on mobile for performance)
        if (typeof THREE !== 'undefined' && !this.detectDevice().isMobile) {
            this.setupThreeJS();
        }
        
        // Setup intersection observer for animations
        this.setupIntersectionObserver();
        
        // Initialize performance optimizations
        this.initPerformanceOptimizations();
    }

    setupAnimations() {
        // Fade in animations for elements with data-animate
        const animatedElements = document.querySelectorAll('[data-animate]');
        
        animatedElements.forEach((element, index) => {
            const animationType = element.dataset.animate;
            const delay = element.dataset.delay || 0;
            
            switch (animationType) {
                case 'fade-in':
                    this.animateFadeIn(element, delay);
                    break;
                case 'slide-up':
                    this.animateSlideUp(element, delay);
                    break;
                case 'scale-in':
                    this.animateScaleIn(element, delay);
                    break;
                case 'bounce-in':
                    this.animateBounceIn(element, delay);
                    break;
                default:
                    this.animateFadeIn(element, delay);
            }
        });
    }

    setupGSAPAnimations() {
        // Hero text animation
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) {
            gsap.from(heroTitle, {
                duration: 1.2,
                y: 100,
                opacity: 0,
                ease: "power3.out",
                delay: 0.3
            });
        }

        // Stagger animations for cards
        const cards = document.querySelectorAll('.card');
        if (cards.length > 0) {
            gsap.from(cards, {
                duration: 0.8,
                y: 50,
                opacity: 0,
                stagger: 0.1,
                ease: "power2.out",
                scrollTrigger: {
                    trigger: cards[0],
                    start: "top 80%",
                    toggleActions: "play none none reverse"
                }
            });
        }

        // Floating animation for elements
        const floatingElements = document.querySelectorAll('.animate-float');
        floatingElements.forEach(element => {
            gsap.to(element, {
                y: -10,
                duration: 2,
                ease: "power1.inOut",
                yoyo: true,
                repeat: -1
            });
        });

        // Parallax scrolling
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        parallaxElements.forEach(element => {
            const speed = element.dataset.parallax || 0.5;
            gsap.to(element, {
                yPercent: -50 * speed,
                ease: "none",
                scrollTrigger: {
                    trigger: element,
                    start: "top bottom",
                    end: "bottom top",
                    scrub: true
                }
            });
        });
    }

    setupThreeJS() {
        // Create floating particles background
        const canvas = document.getElementById('particles-canvas');
        if (!canvas) return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
        
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);

        // Create particles
        const particlesGeometry = new THREE.BufferGeometry();
        const particlesCount = 1000;
        const posArray = new Float32Array(particlesCount * 3);

        for (let i = 0; i < particlesCount * 3; i++) {
            posArray[i] = (Math.random() - 0.5) * 10;
        }

        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

        const particlesMaterial = new THREE.PointsMaterial({
            size: 0.005,
            color: '#6366f1',
            transparent: true,
            opacity: 0.8
        });

        const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
        scene.add(particlesMesh);

        camera.position.z = 3;

        // Animation loop
        const animate = () => {
            requestAnimationFrame(animate);
            
            particlesMesh.rotation.x += 0.0005;
            particlesMesh.rotation.y += 0.0005;
            
            renderer.render(scene, camera);
        };

        animate();

        // Handle resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                    
                    // Add stagger delay for multiple elements
                    const siblings = Array.from(entry.target.parentNode.children);
                    const index = siblings.indexOf(entry.target);
                    entry.target.style.animationDelay = `${index * 0.1}s`;
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe elements with animation classes
        const elementsToAnimate = document.querySelectorAll('.card, .btn, .input, [data-animate]');
        elementsToAnimate.forEach(el => observer.observe(el));
    }

    setupInteractions() {
        // Enhanced button interactions
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', (e) => {
                this.createRippleEffect(e);
                if (typeof gsap !== 'undefined') {
                    gsap.to(button, { scale: 1.05, duration: 0.2, ease: "power2.out" });
                }
            });

            button.addEventListener('mouseleave', (e) => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(button, { scale: 1, duration: 0.2, ease: "power2.out" });
                }
            });

            button.addEventListener('click', (e) => {
                this.createClickEffect(e);
            });
        });

        // Card hover effects
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(card, { 
                        y: -8, 
                        rotationX: 5,
                        rotationY: 5,
                        duration: 0.3, 
                        ease: "power2.out" 
                    });
                }
            });

            card.addEventListener('mouseleave', () => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(card, { 
                        y: 0, 
                        rotationX: 0,
                        rotationY: 0,
                        duration: 0.3, 
                        ease: "power2.out" 
                    });
                }
            });
        });

        // Smooth scrolling for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    setupTheme() {
        // Theme toggle functionality
        const themeToggle = document.querySelector('[data-theme-toggle]');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Auto-detect system theme
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.classList.add('dark');
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (e.matches) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        });
    }

    // Animation methods
    animateFadeIn(element, delay = 0) {
        if (typeof gsap !== 'undefined') {
            gsap.from(element, {
                opacity: 0,
                duration: 0.8,
                delay: delay / 1000,
                ease: "power2.out"
            });
        } else {
            element.style.animationDelay = `${delay}ms`;
            element.classList.add('animate-fade-in');
        }
    }

    animateSlideUp(element, delay = 0) {
        if (typeof gsap !== 'undefined') {
            gsap.from(element, {
                y: 50,
                opacity: 0,
                duration: 0.8,
                delay: delay / 1000,
                ease: "power2.out"
            });
        } else {
            element.style.animationDelay = `${delay}ms`;
            element.classList.add('animate-slide-up');
        }
    }

    animateScaleIn(element, delay = 0) {
        if (typeof gsap !== 'undefined') {
            gsap.from(element, {
                scale: 0.8,
                opacity: 0,
                duration: 0.6,
                delay: delay / 1000,
                ease: "back.out(1.7)"
            });
        } else {
            element.style.animationDelay = `${delay}ms`;
            element.classList.add('animate-scale-in');
        }
    }

    animateBounceIn(element, delay = 0) {
        if (typeof gsap !== 'undefined') {
            gsap.from(element, {
                scale: 0,
                opacity: 0,
                duration: 0.8,
                delay: delay / 1000,
                ease: "bounce.out"
            });
        } else {
            element.style.animationDelay = `${delay}ms`;
            element.classList.add('animate-bounce-in');
        }
    }

    // Interactive effects
    createRippleEffect(e) {
        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    createClickEffect(e) {
        const button = e.currentTarget;
        
        if (typeof gsap !== 'undefined') {
            gsap.to(button, {
                scale: 0.95,
                duration: 0.1,
                yoyo: true,
                repeat: 1,
                ease: "power2.inOut"
            });
        }

        // Create particle burst effect
        this.createParticleBurst(e.clientX, e.clientY);
    }

    createParticleBurst(x, y) {
        const colors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981'];
        
        for (let i = 0; i < 8; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                border-radius: 50%;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
                z-index: 9999;
            `;

            document.body.appendChild(particle);

            const angle = (i / 8) * Math.PI * 2;
            const velocity = 100 + Math.random() * 50;
            const vx = Math.cos(angle) * velocity;
            const vy = Math.sin(angle) * velocity;

            if (typeof gsap !== 'undefined') {
                gsap.to(particle, {
                    x: vx,
                    y: vy,
                    opacity: 0,
                    scale: 0,
                    duration: 0.8,
                    ease: "power2.out",
                    onComplete: () => particle.remove()
                });
            } else {
                setTimeout(() => particle.remove(), 800);
            }
        }
    }

    toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }

        // Animate theme transition
        if (typeof gsap !== 'undefined') {
            gsap.to(document.body, {
                duration: 0.3,
                ease: "power2.inOut"
            });
        }
    }

    // Utility methods
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--white);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            z-index: var(--z-toast);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);

        // Animate out and remove
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    createLoadingSpinner(container) {
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = `
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        `;
        container.appendChild(spinner);
        return spinner;
    }

    removeLoadingSpinner(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.parentNode.removeChild(spinner);
        }
    }
}

// CSS for ripple effect
const rippleCSS = `
@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}
`;

// Add ripple CSS to document
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);

// Initialize Modern UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.modernUI = new ModernUI();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernUI;
}eea, wir
eframe: true, transparent: true }),
            new THREE.MeshBasicMaterial({ 
                color: 0xf093fb, wireframe: true, transparent: true }),
            new THREE.MeshBasicMaterial({ 
                color: 0x4facfe, wireframe: true, transparent: true }),
            new THREE.MeshBasicMaterial({ 
                color: 0x43e97b, wireframe: true, transparent: true }),
            new THREE.MeshBasicMaterial({ 
                color: 0xfa709a, wireframe: true, transparent: true })
        ];

        for (let i = 0; i < 15; i++) {
            const geometry = geometries[Math.floor(Math.random() * geometries.length)];
            const material = materials[Math.floor(Math.random() * materials.length)];
            const mesh = new THREE.Mesh(geometry, material);

            mesh.position.x = (Math.random() - 0.5) * 20;
            mesh.position.y = (Math.random() - 0.5) * 20;
            mesh.position.z = (Math.random() - 0.5) * 20;

            mesh.rotation.x = Math.random() * 2 * Math.PI;
            mesh.rotation.y = Math.random() * 2 * Math.PI;

            mesh.userData = {
                originalPosition: mesh.position.clone(),
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.02,
                    y: (Math.random() - 0.5) * 0.02,
                    z: (Math.random() - 0.5) * 0.02
                }
            };

            this.scene.add(mesh);
        }
    }

    animate3D() {
        requestAnimationFrame(() => this.animate3D());

        // Animate floating shapes
        this.scene.children.forEach(child => {
            if (child.userData && child.userData.rotationSpeed) {
                child.rotation.x += child.userData.rotationSpeed.x;
                child.rotation.y += child.userData.rotationSpeed.y;
                child.rotation.z += child.userData.rotationSpeed.z;

                // Mouse interaction
                const mouseInfluence = 0.0001;
                child.position.x += (this.mouse.x * mouseInfluence);
                child.position.y += (-this.mouse.y * mouseInfluence);
            }
        });

        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        this.windowHalf.x = window.innerWidth / 2;
        this.windowHalf.y = window.innerHeight / 2;

        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    initParticles() {
        // Create canvas for 2D particles
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        `;
        
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Create particles
        for (let i = 0; i < 50; i++) {
            this.particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2,
                color: `hsl(${Math.random() * 60 + 200}, 70%, 60%)`
            });
        }

        // Animate particles
        const animateParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            this.particles.forEach(particle => {
                particle.x += particle.vx;
                particle.y += particle.vy;

                // Wrap around screen
                if (particle.x < 0) particle.x = canvas.width;
                if (particle.x > canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = canvas.height;
                if (particle.y > canvas.height) particle.y = 0;

                // Draw particle
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fillStyle = particle.color;
                ctx.globalAlpha = particle.opacity;
                ctx.fill();
            });

            requestAnimationFrame(animateParticles);
        };

        animateParticles();

        // Handle resize
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    }

    initInteractions() {
        // Mouse tracking
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = (e.clientX - this.windowHalf.x);
            this.mouse.y = (e.clientY - this.windowHalf.y);
        });

        // Button interactions
        this.initButtonEffects();
        
        // Card interactions
        this.initCardEffects();
        
        // Form interactions
        this.initFormEffects();
        
        // Modal interactions
        this.initModalEffects();
    }

    initButtonEffects() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn')) {
                this.createRippleEffect(e.target, e);
            }
        });
    }

    createRippleEffect(element, event) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    initCardEffects() {
        const cards = document.querySelectorAll('.card-interactive');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(card, {
                        duration: 0.3,
                        rotationX: 8,
                        rotationY: 2,
                        y: -12,
                        ease: "power2.out"
                    });
                }
            });

            card.addEventListener('mouseleave', () => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(card, {
                        duration: 0.3,
                        rotationX: 0,
                        rotationY: 0,
                        y: 0,
                        ease: "power2.out"
                    });
                }
            });

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;

                if (typeof gsap !== 'undefined') {
                    gsap.to(card, {
                        duration: 0.1,
                        rotationX: rotateX,
                        rotationY: rotateY,
                        ease: "power2.out"
                    });
                }
            });
        });
    }

    initFormEffects() {
        const inputs = document.querySelectorAll('.input');
        
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(input, {
                        duration: 0.3,
                        y: -2,
                        scale: 1.02,
                        ease: "power2.out"
                    });
                }
            });

            input.addEventListener('blur', () => {
                if (typeof gsap !== 'undefined') {
                    gsap.to(input, {
                        duration: 0.3,
                        y: 0,
                        scale: 1,
                        ease: "power2.out"
                    });
                }
            });
        });
    }

    initModalEffects() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            const closeModal = () => {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            };

            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });

            const closeBtn = modal.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', closeModal);
            }
        });

        // Modal triggers
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-modal]');
            if (trigger) {
                const modalId = trigger.dataset.modal;
                const modal = document.getElementById(modalId);
                if (modal) {
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                }
            }
        });
    }

    initScrollAnimations() {
        if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
            console.warn('GSAP or ScrollTrigger not loaded, skipping scroll animations');
            return;
        }

        // Fade in animations
        gsap.utils.toArray('.animate-fade-in').forEach(element => {
            gsap.fromTo(element, 
                { opacity: 0, y: 50 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: element,
                        start: "top 80%",
                        end: "bottom 20%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        });

        // Scale in animations
        gsap.utils.toArray('.animate-scale-in').forEach(element => {
            gsap.fromTo(element,
                { scale: 0.8, opacity: 0 },
                {
                    scale: 1,
                    opacity: 1,
                    duration: 0.6,
                    ease: "back.out(1.7)",
                    scrollTrigger: {
                        trigger: element,
                        start: "top 80%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        });

        // Slide in animations
        gsap.utils.toArray('.animate-slide-in').forEach(element => {
            gsap.fromTo(element,
                { x: -100, opacity: 0 },
                {
                    x: 0,
                    opacity: 1,
                    duration: 0.8,
                    ease: "power2.out",
                    scrollTrigger: {
                        trigger: element,
                        start: "top 80%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        });
    }

    initPageTransitions() {
        // Page transition effects
        const pageTransition = {
            duration: 0.5,
            ease: "power2.inOut"
        };

        // Handle navigation clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (link && !link.target && link.href.startsWith(window.location.origin)) {
                e.preventDefault();
                this.transitionToPage(link.href);
            }
        });
    }

    transitionToPage(url) {
        if (typeof gsap === 'undefined') {
            window.location.href = url;
            return;
        }

        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            z-index: 9999;
            transform: translateY(100%);
        `;
        
        document.body.appendChild(overlay);

        gsap.to(overlay, {
            duration: 0.5,
            y: 0,
            ease: "power2.inOut",
            onComplete: () => {
                window.location.href = url;
            }
        });
    }

    initThemeSystem() {
        const themeToggle = document.querySelector('.theme-toggle');
        const currentTheme = localStorage.getItem('theme') || 'dark';
        
        document.documentElement.setAttribute('data-theme', currentTheme);
        
        if (themeToggle) {
            themeToggle.classList.toggle('active', currentTheme === 'light');
            
            themeToggle.addEventListener('click', () => {
                const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                themeToggle.classList.toggle('active', newTheme === 'light');
            });
        }
    }

    // Utility methods
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(20px);
            color: var(--dark-text);
            z-index: var(--z-tooltip);
            transform: translateX(100%);
            transition: transform var(--transition-normal);
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Animate out
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    createLoadingSpinner(container) {
        const spinner = document.createElement('div');
        spinner.className = 'loading';
        container.appendChild(spinner);
        return spinner;
    }

    removeLoadingSpinner(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.parentNode.removeChild(spinner);
        }
    }

    // Enhanced Device Detection
    detectDevice() {
        const userAgent = navigator.userAgent;
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        const isTablet = /iPad|Android(?=.*Mobile)|Tablet/i.test(userAgent) && window.innerWidth >= 768;
        const isDesktop = !isMobile && !isTablet;
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        return {
            isMobile: isMobile && !isTablet,
            isTablet,
            isDesktop,
            isTouchDevice,
            screenSize: {
                width: window.innerWidth,
                height: window.innerHeight,
                isSmall: window.innerWidth < 480,
                isMedium: window.innerWidth >= 480 && window.innerWidth < 768,
                isLarge: window.innerWidth >= 768 && window.innerWidth < 1024,
                isXLarge: window.innerWidth >= 1024
            }
        };
    }

    // Responsive Layout Manager
    initResponsiveLayout() {
        const device = this.detectDevice();
        document.body.classList.add(
            device.isMobile ? 'device-mobile' : 
            device.isTablet ? 'device-tablet' : 'device-desktop'
        );
        
        if (device.isTouchDevice) {
            document.body.classList.add('touch-device');
        }
        
        // Add screen size classes
        const sizeClass = device.screenSize.isSmall ? 'screen-sm' :
                         device.screenSize.isMedium ? 'screen-md' :
                         device.screenSize.isLarge ? 'screen-lg' : 'screen-xl';
        document.body.classList.add(sizeClass);
        
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });
        
        // Handle resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    }

    handleOrientationChange() {
        const device = this.detectDevice();
        
        // Update body classes
        document.body.className = document.body.className.replace(/screen-(sm|md|lg|xl)/, '');
        const sizeClass = device.screenSize.isSmall ? 'screen-sm' :
                         device.screenSize.isMedium ? 'screen-md' :
                         device.screenSize.isLarge ? 'screen-lg' : 'screen-xl';
        document.body.classList.add(sizeClass);
        
        // Trigger custom event
        window.dispatchEvent(new CustomEvent('responsiveLayoutChange', {
            detail: { device, orientation: screen.orientation?.angle || 0 }
        }));
    }

    handleResize() {
        this.handleOrientationChange();
        
        // Update viewport height for mobile browsers
        if (this.detectDevice().isMobile) {
            document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
        }
    }

    // Enhanced File Upload with Mobile Optimizations
    createFileUploadZone(container, options = {}) {
        const device = this.detectDevice();
        const dropZone = document.createElement('div');
        dropZone.className = 'file-upload-zone';
        
        const basePadding = device.isMobile ? 'var(--space-lg) var(--space-md)' : 
                           device.isTablet ? 'var(--space-xl) var(--space-lg)' : 
                           'var(--space-2xl)';
        
        dropZone.style.cssText = `
            border: 2px dashed var(--glass-border);
            border-radius: var(--radius-lg);
            padding: ${basePadding};
            text-align: center;
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            transition: all var(--transition-normal);
            cursor: pointer;
            touch-action: manipulation;
        `;

        const iconSize = device.isMobile ? '2.5rem' : device.isTablet ? '3rem' : '3.5rem';
        const titleSize = device.isMobile ? '1.125rem' : device.isTablet ? '1.25rem' : '1.5rem';
        
        dropZone.innerHTML = `
            <div class="upload-icon" style="font-size: ${iconSize}; margin-bottom: 1rem;">📁</div>
            <h3 style="font-size: ${titleSize}; margin-bottom: 0.5rem;">
                ${device.isMobile ? 'Tap to select files' : 'Drop files here or click to browse'}
            </h3>
            <p class="text-secondary" style="font-size: ${device.isMobile ? '0.875rem' : '1rem'};">
                Supports ${options.acceptedTypes || 'all file types'}
            </p>
            <input type="file" multiple style="display: none;" accept="${options.accept || '*/*'}">
        `;

        const fileInput = dropZone.querySelector('input[type="file"]');
        
        // Enhanced click handling for touch devices
        const handleClick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            if (device.isTouchDevice) {
                // Add visual feedback for touch
                dropZone.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    dropZone.style.transform = '';
                    fileInput.click();
                }, 100);
            } else {
                fileInput.click();
            }
        };
        
        dropZone.addEventListener('click', handleClick);
        dropZone.addEventListener('touchend', handleClick);

        // Enhanced drag and drop with touch support
        if (!device.isTouchDevice) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#667eea';
                dropZone.style.background = 'rgba(102, 126, 234, 0.1)';
                dropZone.style.transform = 'scale(1.02)';
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.style.borderColor = 'var(--glass-border)';
                dropZone.style.background = 'var(--glass-bg)';
                dropZone.style.transform = '';
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = 'var(--glass-border)';
                dropZone.style.background = 'var(--glass-bg)';
                dropZone.style.transform = '';
                
                const files = Array.from(e.dataTransfer.files);
                if (options.onFilesSelected) {
                    options.onFilesSelected(files);
                }
            });
        }

        // Enhanced file input handling
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            if (options.onFilesSelected) {
                options.onFilesSelected(files);
            }
            
            // Provide haptic feedback on supported devices
            if (navigator.vibrate && device.isMobile) {
                navigator.vibrate(50);
            }
        });

        container.appendChild(dropZone);
        return dropZone;
    }

    // Enhanced Touch Gestures
    initTouchGestures() {
        if (!this.detectDevice().isTouchDevice) return;
        
        let touchStartX = 0;
        let touchStartY = 0;
        let touchEndX = 0;
        let touchEndY = 0;
        
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
            touchStartY = e.changedTouches[0].screenY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            touchEndY = e.changedTouches[0].screenY;
            this.handleSwipeGesture();
        }, { passive: true });
        
        // Add pull-to-refresh for mobile
        if (this.detectDevice().isMobile) {
            this.initPullToRefresh();
        }
    }
    
    handleSwipeGesture() {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        const minSwipeDistance = 50;
        
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
                // Swipe right
                window.dispatchEvent(new CustomEvent('swipeRight'));
            } else {
                // Swipe left
                window.dispatchEvent(new CustomEvent('swipeLeft'));
            }
        } else if (Math.abs(deltaY) > minSwipeDistance) {
            if (deltaY > 0) {
                // Swipe down
                window.dispatchEvent(new CustomEvent('swipeDown'));
            } else {
                // Swipe up
                window.dispatchEvent(new CustomEvent('swipeUp'));
            }
        }
    }
    
    initPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        
        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
                isPulling = true;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!isPulling) return;
            
            currentY = e.touches[0].clientY;
            const pullDistance = currentY - startY;
            
            if (pullDistance > 0 && window.scrollY === 0) {
                e.preventDefault();
                
                if (pullDistance > 100) {
                    // Trigger refresh
                    window.dispatchEvent(new CustomEvent('pullToRefresh'));
                    isPulling = false;
                }
            }
        });
        
        document.addEventListener('touchend', () => {
            isPulling = false;
        }, { passive: true });
    }

    createProgressBar(container, label = '') {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container';
        progressContainer.style.cssText = `
            margin: var(--space-md) 0;
        `;

        progressContainer.innerHTML = `
            ${label ? `<div class="progress-label" style="margin-bottom: var(--space-sm);">${label}</div>` : ''}
            <div class="progress">
                <div class="progress-bar" style="width: 0%;"></div>
            </div>
            <div class="progress-text" style="margin-top: var(--space-sm); font-size: 0.875rem; color: var(--dark-text-secondary);">0%</div>
        `;

        const progressBar = progressContainer.querySelector('.progress-bar');
        const progressText = progressContainer.querySelector('.progress-text');

        const updateProgress = (percentage) => {
            progressBar.style.width = `${percentage}%`;
            progressText.textContent = `${Math.round(percentage)}%`;
        };

        container.appendChild(progressContainer);
        
        return {
            container: progressContainer,
            update: updateProgress,
            remove: () => progressContainer.remove()
        };
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.modernUI = new ModernUI();
});

// Add CSS animations for notifications and ripples
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .notification {
        box-shadow: var(--shadow-xl);
    }
    
    .notification-success {
        border-left: 4px solid #43e97b;
    }
    
    .notification-warning {
        border-left: 4px solid #fa709a;
    }
    
    .notification-error {
        border-left: 4px solid #ff6b6b;
    }
    
    .file-upload-zone:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .progress-container {
        animation: fadeIn 0.3s ease-out;
    }
`;
document.head.appendChild(style);    // Pe
rformance Optimizations
    initPerformanceOptimizations() {
        const device = this.detectDevice();
        
        // Reduce animations on low-end devices
        if (device.isMobile && device.screenSize.isSmall) {
            document.body.classList.add('reduced-animations');
            
            // Disable expensive animations
            const style = document.createElement('style');
            style.textContent = `
                .reduced-animations * {
                    animation-duration: 0.2s !important;
                    transition-duration: 0.2s !important;
                }
                .reduced-animations .animate-float,
                .reduced-animations .animate-pulse {
                    animation: none !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Optimize images for device
        this.optimizeImages();
        
        // Lazy load content
        this.initLazyLoading();
        
        // Optimize scroll performance
        this.optimizeScrolling();
        
        // Memory management
        this.initMemoryManagement();
    }
    
    optimizeImages() {
        const images = document.querySelectorAll('img');
        const device = this.detectDevice();
        
        images.forEach(img => {
            // Add loading="lazy" for better performance
            if (!img.hasAttribute('loading')) {
                img.setAttribute('loading', 'lazy');
            }
            
            // Optimize image quality based on device
            if (device.isMobile && img.src) {
                // Add webp support detection
                const supportsWebP = this.supportsWebP();
                if (supportsWebP && !img.src.includes('.webp')) {
                    // Could implement WebP conversion here
                }
            }
        });
    }
    
    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }
    
    initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const lazyElements = document.querySelectorAll('[data-lazy]');
            
            const lazyObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        
                        if (element.dataset.lazySrc) {
                            element.src = element.dataset.lazySrc;
                            element.removeAttribute('data-lazy-src');
                        }
                        
                        if (element.dataset.lazyBg) {
                            element.style.backgroundImage = `url(${element.dataset.lazyBg})`;
                            element.removeAttribute('data-lazy-bg');
                        }
                        
                        element.classList.add('lazy-loaded');
                        lazyObserver.unobserve(element);
                    }
                });
            }, {
                rootMargin: '50px'
            });
            
            lazyElements.forEach(element => {
                lazyObserver.observe(element);
            });
        }
    }
    
    optimizeScrolling() {
        let ticking = false;
        
        const optimizedScroll = () => {
            // Throttle scroll events
            if (!ticking) {
                requestAnimationFrame(() => {
                    // Handle scroll-based animations here
                    this.handleScrollAnimations();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        // Use passive listeners for better performance
        window.addEventListener('scroll', optimizedScroll, { passive: true });
        
        // Optimize touch scrolling on mobile
        if (this.detectDevice().isTouchDevice) {
            document.body.style.webkitOverflowScrolling = 'touch';
        }
    }
    
    handleScrollAnimations() {
        // Implement scroll-based animations with performance in mind
        const scrollY = window.scrollY;
        const windowHeight = window.innerHeight;
        
        // Only animate elements in viewport
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        animatedElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const isVisible = rect.top < windowHeight && rect.bottom > 0;
            
            if (isVisible && !element.classList.contains('animated')) {
                element.classList.add('animated');
                // Trigger animation
            }
        });
    }
    
    initMemoryManagement() {
        // Clean up unused event listeners
        this.cleanupEventListeners();
        
        // Monitor memory usage on mobile
        if (this.detectDevice().isMobile && 'memory' in performance) {
            setInterval(() => {
                const memInfo = performance.memory;
                if (memInfo.usedJSHeapSize > memInfo.jsHeapSizeLimit * 0.9) {
                    console.warn('High memory usage detected, cleaning up...');
                    this.performMemoryCleanup();
                }
            }, 30000); // Check every 30 seconds
        }
    }
    
    cleanupEventListeners() {
        // Remove unused event listeners to prevent memory leaks
        const elements = document.querySelectorAll('[data-cleanup]');
        elements.forEach(element => {
            // Remove old event listeners if they exist
            const oldListeners = element._eventListeners;
            if (oldListeners) {
                oldListeners.forEach(({ event, handler }) => {
                    element.removeEventListener(event, handler);
                });
            }
        });
    }
    
    performMemoryCleanup() {
        // Force garbage collection if available
        if (window.gc) {
            window.gc();
        }
        
        // Clear unused caches
        this.clearUnusedCaches();
        
        // Reduce animation complexity
        document.body.classList.add('low-memory-mode');
    }
    
    clearUnusedCaches() {
        // Clear any internal caches
        if (this.imageCache) {
            this.imageCache.clear();
        }
        
        if (this.animationCache) {
            this.animationCache.clear();
        }
    }
    
    // Enhanced Notification System for Mobile
    showNotification(message, type = 'info', duration = 3000) {
        const device = this.detectDevice();
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // Adjust positioning for mobile
        const position = device.isMobile ? 'bottom: 20px; left: 50%; transform: translateX(-50%);' : 'top: 20px; right: 20px;';
        const width = device.isMobile ? 'width: calc(100% - 40px); max-width: 400px;' : 'max-width: 400px;';
        
        notification.style.cssText = `
            position: fixed;
            ${position}
            ${width}
            padding: 1rem 1.5rem;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            backdrop-filter: blur(20px);
            color: var(--dark-text);
            z-index: var(--z-toast);
            transform: ${device.isMobile ? 'translateX(-50%) translateY(100%)' : 'translateX(100%)'};
            transition: transform var(--transition-normal);
            box-shadow: var(--shadow-xl);
        `;
        
        // Add icon based on type
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">${icons[type] || icons.info}</span>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = device.isMobile ? 'translateX(-50%) translateY(0)' : 'translateX(0)';
        }, 10);

        // Add haptic feedback on mobile
        if (device.isMobile && navigator.vibrate) {
            const vibrationPattern = type === 'error' ? [100, 50, 100] : [50];
            navigator.vibrate(vibrationPattern);
        }

        // Animate out
        setTimeout(() => {
            notification.style.transform = device.isMobile ? 'translateX(-50%) translateY(100%)' : 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }
    
    // Enhanced Modal System for Mobile
    createResponsiveModal(content, options = {}) {
        const device = this.detectDevice();
        const modal = document.createElement('div');
        modal.className = 'modal responsive-modal';
        
        const modalSize = device.isMobile ? '95%' : device.isTablet ? '80%' : '60%';
        const modalHeight = device.isMobile ? '90vh' : 'auto';
        
        modal.innerHTML = `
            <div class="modal-content" style="
                width: ${modalSize};
                max-height: ${modalHeight};
                margin: ${device.isMobile ? '5vh auto' : '10vh auto'};
                overflow-y: auto;
                -webkit-overflow-scrolling: touch;
            ">
                <div class="modal-header" style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem;
                    border-bottom: 1px solid var(--glass-border);
                    position: sticky;
                    top: 0;
                    background: var(--glass-bg);
                    backdrop-filter: blur(20px);
                ">
                    <h3>${options.title || 'Modal'}</h3>
                    <button class="modal-close btn btn-secondary btn-sm">✕</button>
                </div>
                <div class="modal-body" style="padding: 1rem;">
                    ${content}
                </div>
            </div>
        `;
        
        // Enhanced close functionality
        const closeModal = () => {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
            document.body.style.overflow = '';
        };
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        
        modal.querySelector('.modal-close').addEventListener('click', closeModal);
        
        // Handle escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
        
        // Prevent body scroll on mobile
        document.body.style.overflow = 'hidden';
        
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('active'), 10);
        
        return modal;
    }
}