// Snow and Love Effects for MyPrabh
class SnowEffects {
    constructor() {
        this.snowflakes = [];
        this.hearts = [];
        this.init();
    }

    init() {
        this.createSnowContainer();
        this.startSnowfall();
        this.startHeartFloat();
        this.addInteractiveEffects();
    }

    createSnowContainer() {
        const container = document.createElement('div');
        container.className = 'particle-container';
        container.id = 'snow-container';
        document.body.appendChild(container);
    }

    createSnowflake() {
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';
        snowflake.innerHTML = Math.random() > 0.5 ? '❄️' : '✨';
        snowflake.style.left = Math.random() * 100 + 'vw';
        snowflake.style.animationDuration = (Math.random() * 3 + 2) + 's';
        snowflake.style.opacity = Math.random();
        snowflake.style.fontSize = (Math.random() * 10 + 10) + 'px';
        
        document.getElementById('snow-container').appendChild(snowflake);
        
        setTimeout(() => {
            snowflake.remove();
        }, 5000);
    }

    createFloatingHeart() {
        const heart = document.createElement('div');
        heart.className = 'floating-heart';
        heart.innerHTML = Math.random() > 0.5 ? '💖' : '💕';
        heart.style.left = Math.random() * 100 + 'vw';
        heart.style.animationDuration = (Math.random() * 4 + 6) + 's';
        heart.style.fontSize = (Math.random() * 8 + 12) + 'px';
        
        document.getElementById('snow-container').appendChild(heart);
        
        setTimeout(() => {
            heart.remove();
        }, 10000);
    }

    startSnowfall() {
        setInterval(() => {
            if (Math.random() > 0.7) {
                this.createSnowflake();
            }
        }, 300);
    }

    startHeartFloat() {
        setInterval(() => {
            if (Math.random() > 0.8) {
                this.createFloatingHeart();
            }
        }, 2000);
    }

    addInteractiveEffects() {
        // Add click effects
        document.addEventListener('click', (e) => {
            this.createClickEffect(e.clientX, e.clientY);
        });

        // Add hover effects to buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                this.createHoverEffect(btn);
            });
        });
    }

    createClickEffect(x, y) {
        const effect = document.createElement('div');
        effect.innerHTML = '💖';
        effect.style.position = 'fixed';
        effect.style.left = x + 'px';
        effect.style.top = y + 'px';
        effect.style.pointerEvents = 'none';
        effect.style.zIndex = '9999';
        effect.style.fontSize = '20px';
        effect.style.animation = 'floatUp 2s ease-out forwards';
        
        document.body.appendChild(effect);
        
        setTimeout(() => {
            effect.remove();
        }, 2000);
    }

    createHoverEffect(element) {
        const rect = element.getBoundingClientRect();
        const effect = document.createElement('div');
        effect.innerHTML = '✨';
        effect.style.position = 'fixed';
        effect.style.left = (rect.left + rect.width / 2) + 'px';
        effect.style.top = rect.top + 'px';
        effect.style.pointerEvents = 'none';
        effect.style.zIndex = '9999';
        effect.style.fontSize = '16px';
        effect.style.animation = 'pulse 1s ease-out forwards';
        
        document.body.appendChild(effect);
        
        setTimeout(() => {
            effect.remove();
        }, 1000);
    }
}

// Initialize effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SnowEffects();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
@keyframes floatUp {
    0% {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
    100% {
        transform: translateY(-100px) scale(0.5);
        opacity: 0;
    }
}

.particle-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
    overflow: hidden;
}

.snowflake {
    position: absolute;
    animation: snowfall linear infinite;
    user-select: none;
}

.floating-heart {
    position: absolute;
    animation: floatUp 6s linear infinite;
    user-select: none;
}

@keyframes snowfall {
    0% {
        transform: translateY(-100px) rotate(0deg);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(100vh) rotate(360deg);
        opacity: 0;
    }
}
`;
document.head.appendChild(style);