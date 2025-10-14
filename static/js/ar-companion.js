/**
 * MyPrabh AR Companion System
 * 8th Wall AR integration for immersive companion experience
 */

class ARCompanionSystem {
    constructor() {
        this.isARSupported = false;
        this.isXR8Loaded = false;
        this.arSession = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.arCompanion = null;
        this.heartParticles = [];
        this.animationMixer = null;
        this.clock = new THREE.Clock();
        
        this.init();
    }
    
    init() {
        // Check for AR support
        this.checkARSupport().then(supported => {
            this.isARSupported = supported;
            if (supported) {
                this.load8thWall();
            } else {
                console.log('📱 AR not supported on this device');
                this.createFallbackExperience();
            }
        });
    }
    
    async checkARSupport() {
        // Check for basic AR requirements
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            return false;
        }
        
        // Check for WebXR support
        if ('xr' in navigator) {
            try {
                const isSupported = await navigator.xr.isSessionSupported('immersive-ar');
                return isSupported;
            } catch (error) {
                console.log('WebXR not supported:', error);
            }
        }
        
        // Fallback: check for mobile device
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        return isMobile;
    }
    
    async load8thWall() {
        try {
            // Load 8th Wall SDK
            await this.loadScript('https://apps.8thwall.com/xrweb');
            
            // Check if XR8 is available
            if (typeof XR8 !== 'undefined') {
                this.isXR8Loaded = true;
                this.setup8thWall();
                console.log('🥽 8th Wall AR System initialized');
            } else {
                throw new Error('8th Wall SDK not loaded');
            }
        } catch (error) {
            console.log('8th Wall not available:', error);
            this.createFallbackExperience();
        }
    }
    
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    setup8thWall() {
        // Configure 8th Wall pipeline
        XR8.addCameraPipelineModules([
            XR8.GlTextureRenderer.pipelineModule(),
            XR8.Threejs.pipelineModule(),
            XR8.XrController.pipelineModule(),
            {
                name: 'myprabhAR',
                onStart: ({ canvas, canvasWidth, canvasHeight }) => {
                    this.setupARScene(canvas, canvasWidth, canvasHeight);
                },
                onUpdate: () => {
                    this.updateARScene();
                },
                onDetach: () => {
                    this.cleanupARScene();
                }
            }
        ]);
        
        // Start AR session
        XR8.run({ canvas: this.createARCanvas() });
    }
    
    createARCanvas() {
        const canvas = document.createElement('canvas');
        canvas.id = 'ar-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1000;
            display: none;
        `;
        document.body.appendChild(canvas);
        return canvas;
    }
    
    setupARScene(canvas, canvasWidth, canvasHeight) {
        // Get Three.js scene from XR8
        const { scene, camera, renderer } = XR8.Threejs.xrScene();
        this.scene = scene;
        this.camera = camera;
        this.renderer = renderer;
        
        // Setup lighting for AR
        this.setupARLighting();
        
        // Create AR companion
        this.createARCompanion();
        
        // Create AR heart particles
        this.createARHeartParticles();
        
        // Setup AR interactions
        this.setupARInteractions();
        
        console.log('🎮 AR Scene initialized');
    }
    
    setupARLighting() {
        // Ambient light for AR
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        // Directional light to match real world
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 10, 5);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
        
        // Point light for companion glow
        const companionLight = new THREE.PointLight(0xff69b4, 1, 10);
        companionLight.position.set(0, 1, 0);
        this.scene.add(companionLight);
    }
    
    createARCompanion() {
        // Create companion geometry (simplified humanoid)
        const companionGroup = new THREE.Group();
        
        // Body
        const bodyGeometry = new THREE.CapsuleGeometry(0.3, 1.2, 4, 8);
        const bodyMaterial = new THREE.MeshPhongMaterial({
            color: 0xff69b4,
            transparent: true,
            opacity: 0.8,
            emissive: 0x221122
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.6;
        companionGroup.add(body);
        
        // Head
        const headGeometry = new THREE.SphereGeometry(0.25, 16, 16);
        const headMaterial = new THREE.MeshPhongMaterial({
            color: 0xffb3d9,
            transparent: true,
            opacity: 0.9
        });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.5;
        companionGroup.add(head);
        
        // Eyes (glowing)
        const eyeGeometry = new THREE.SphereGeometry(0.05, 8, 8);
        const eyeMaterial = new THREE.MeshBasicMaterial({
            color: 0x00ffff,
            emissive: 0x00ffff
        });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.1, 1.55, 0.2);
        companionGroup.add(leftEye);
        
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.1, 1.55, 0.2);
        companionGroup.add(rightEye);
        
        // Aura effect
        const auraGeometry = new THREE.SphereGeometry(0.8, 16, 16);
        const auraMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                color: { value: new THREE.Color(0xff69b4) }
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec3 vPosition;
                
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float time;
                uniform vec3 color;
                varying vec3 vNormal;
                varying vec3 vPosition;
                
                void main() {
                    float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
                    float pulse = sin(time * 2.0) * 0.3 + 0.7;
                    
                    gl_FragColor = vec4(color * intensity * pulse, intensity * 0.3);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            side: THREE.BackSide
        });
        
        const aura = new THREE.Mesh(auraGeometry, auraMaterial);
        aura.position.y = 0.8;
        companionGroup.add(aura);
        
        // Position companion in AR space
        companionGroup.position.set(0, 0, -2);
        companionGroup.scale.setScalar(0.5);
        
        this.scene.add(companionGroup);
        this.arCompanion = companionGroup;
        
        // Add floating animation
        this.addCompanionAnimation();
    }
    
    addCompanionAnimation() {
        if (!this.arCompanion) return;
        
        // Create floating animation
        const floatAnimation = () => {
            const time = Date.now() * 0.001;
            
            // Floating motion
            this.arCompanion.position.y = Math.sin(time * 2) * 0.1;
            
            // Gentle rotation
            this.arCompanion.rotation.y = Math.sin(time * 0.5) * 0.2;
            
            // Update aura
            const aura = this.arCompanion.children.find(child => 
                child.material && child.material.uniforms && child.material.uniforms.time
            );
            if (aura) {
                aura.material.uniforms.time.value = time;
            }
            
            requestAnimationFrame(floatAnimation);
        };
        
        floatAnimation();
    }
    
    createARHeartParticles() {
        const particleCount = 20;
        
        for (let i = 0; i < particleCount; i++) {
            // Create heart geometry
            const heartShape = new THREE.Shape();
            heartShape.moveTo(0, 0);
            heartShape.bezierCurveTo(0, -0.3, -0.6, -0.3, -0.6, 0);
            heartShape.bezierCurveTo(-0.6, 0.3, 0, 0.6, 0, 1);
            heartShape.bezierCurveTo(0, 0.6, 0.6, 0.3, 0.6, 0);
            heartShape.bezierCurveTo(0.6, -0.3, 0, -0.3, 0, 0);
            
            const heartGeometry = new THREE.ShapeGeometry(heartShape);
            const heartMaterial = new THREE.MeshBasicMaterial({
                color: 0xff1493,
                transparent: true,
                opacity: 0.7,
                side: THREE.DoubleSide
            });
            
            const heart = new THREE.Mesh(heartGeometry, heartMaterial);
            heart.scale.setScalar(0.1);
            
            // Random position around companion
            const angle = (Math.PI * 2 * i) / particleCount;
            const radius = 1 + Math.random() * 0.5;
            heart.position.set(
                Math.cos(angle) * radius,
                Math.random() * 2,
                Math.sin(angle) * radius - 2
            );
            
            // Random rotation
            heart.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
            );
            
            this.scene.add(heart);
            this.heartParticles.push({
                mesh: heart,
                originalPosition: heart.position.clone(),
                phase: Math.random() * Math.PI * 2
            });
        }
        
        // Animate heart particles
        this.animateHeartParticles();
    }
    
    animateHeartParticles() {
        const animateHearts = () => {
            const time = Date.now() * 0.001;
            
            this.heartParticles.forEach((particle, index) => {
                // Floating motion
                particle.mesh.position.y = particle.originalPosition.y + 
                    Math.sin(time * 2 + particle.phase) * 0.2;
                
                // Rotation
                particle.mesh.rotation.z += 0.01;
                
                // Orbit around companion
                const orbitSpeed = 0.5;
                const angle = time * orbitSpeed + particle.phase;
                const radius = 1 + Math.sin(time + particle.phase) * 0.3;
                
                particle.mesh.position.x = particle.originalPosition.x + 
                    Math.cos(angle) * radius * 0.2;
                particle.mesh.position.z = particle.originalPosition.z + 
                    Math.sin(angle) * radius * 0.2;
                
                // Fade in/out
                const opacity = 0.7 + Math.sin(time * 3 + particle.phase) * 0.3;
                particle.mesh.material.opacity = Math.max(0.2, opacity);
            });
            
            requestAnimationFrame(animateHearts);
        };
        
        animateHearts();
    }
    
    setupARInteractions() {
        // Touch interactions
        const canvas = document.getElementById('ar-canvas');
        if (canvas) {
            canvas.addEventListener('touchstart', (e) => {
                this.handleARTouch(e);
            });
            
            canvas.addEventListener('click', (e) => {
                this.handleARClick(e);
            });
        }
    }
    
    handleARTouch(event) {
        event.preventDefault();
        
        // Create heart burst at touch location
        const touch = event.touches[0];
        this.createARHeartBurst(touch.clientX, touch.clientY);
        
        // Make companion react
        this.companionReaction('touch');
    }
    
    handleARClick(event) {
        // Create heart burst at click location
        this.createARHeartBurst(event.clientX, event.clientY);
        
        // Make companion react
        this.companionReaction('click');
    }
    
    createARHeartBurst(x, y) {
        // Convert screen coordinates to world coordinates
        const vector = new THREE.Vector3();
        vector.set(
            (x / window.innerWidth) * 2 - 1,
            -(y / window.innerHeight) * 2 + 1,
            0.5
        );
        vector.unproject(this.camera);
        
        // Create burst hearts
        const burstCount = 8;
        for (let i = 0; i < burstCount; i++) {
            const heartShape = new THREE.Shape();
            heartShape.moveTo(0, 0);
            heartShape.bezierCurveTo(0, -0.3, -0.6, -0.3, -0.6, 0);
            heartShape.bezierCurveTo(-0.6, 0.3, 0, 0.6, 0, 1);
            heartShape.bezierCurveTo(0, 0.6, 0.6, 0.3, 0.6, 0);
            heartShape.bezierCurveTo(0.6, -0.3, 0, -0.3, 0, 0);
            
            const heartGeometry = new THREE.ShapeGeometry(heartShape);
            const heartMaterial = new THREE.MeshBasicMaterial({
                color: 0xff1493,
                transparent: true,
                opacity: 1,
                side: THREE.DoubleSide
            });
            
            const heart = new THREE.Mesh(heartGeometry, heartMaterial);
            heart.scale.setScalar(0.05);
            heart.position.copy(vector);
            
            this.scene.add(heart);
            
            // Animate burst
            const angle = (Math.PI * 2 * i) / burstCount;
            const velocity = new THREE.Vector3(
                Math.cos(angle) * 2,
                Math.sin(angle) * 2,
                (Math.random() - 0.5) * 2
            );
            
            const animateBurst = () => {
                heart.position.add(velocity.clone().multiplyScalar(0.02));
                heart.rotation.z += 0.1;
                heart.material.opacity -= 0.02;
                heart.scale.multiplyScalar(0.98);
                
                if (heart.material.opacity > 0) {
                    requestAnimationFrame(animateBurst);
                } else {
                    this.scene.remove(heart);
                }
            };
            
            animateBurst();
        }
    }
    
    companionReaction(type) {
        if (!this.arCompanion) return;
        
        // Scale pulse reaction
        const originalScale = this.arCompanion.scale.clone();
        
        // Animate reaction
        let pulsePhase = 0;
        const pulseAnimation = () => {
            pulsePhase += 0.2;
            const scale = 1 + Math.sin(pulsePhase) * 0.1;
            this.arCompanion.scale.setScalar(originalScale.x * scale);
            
            if (pulsePhase < Math.PI * 2) {
                requestAnimationFrame(pulseAnimation);
            } else {
                this.arCompanion.scale.copy(originalScale);
            }
        };
        
        pulseAnimation();
        
        // Change companion color briefly
        const body = this.arCompanion.children[0];
        if (body && body.material) {
            const originalColor = body.material.color.clone();
            body.material.color.setHex(0x00ffff);
            
            setTimeout(() => {
                body.material.color.copy(originalColor);
            }, 500);
        }
    }
    
    updateARScene() {
        // Update animations and effects
        if (this.animationMixer) {
            const delta = this.clock.getDelta();
            this.animationMixer.update(delta);
        }
    }
    
    cleanupARScene() {
        // Clean up AR resources
        if (this.arCompanion) {
            this.scene.remove(this.arCompanion);
        }
        
        this.heartParticles.forEach(particle => {
            this.scene.remove(particle.mesh);
        });
        this.heartParticles = [];
    }
    
    createFallbackExperience() {
        // Create 2D fallback for non-AR devices
        console.log('📱 Creating fallback AR experience');
        
        const fallbackContainer = document.createElement('div');
        fallbackContainer.id = 'ar-fallback';
        fallbackContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(255, 105, 180, 0.1), rgba(0, 212, 255, 0.1));
            display: none;
            z-index: 1000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        `;
        
        fallbackContainer.innerHTML = `
            <div style="text-align: center; color: white; font-family: 'Orbitron', monospace;">
                <h2 style="font-size: 2rem; margin-bottom: 1rem; text-shadow: 0 0 20px #ff69b4;">
                    💖 AR Companion Experience
                </h2>
                <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.8;">
                    Your Prabh companion is here with you in spirit
                </p>
                <div id="fallback-companion" style="
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    background: radial-gradient(circle, rgba(255, 105, 180, 0.8), rgba(255, 105, 180, 0.2));
                    margin: 0 auto 2rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 4rem;
                    animation: pulse 2s ease-in-out infinite;
                    box-shadow: 0 0 50px rgba(255, 105, 180, 0.5);
                ">
                    💖
                </div>
                <button id="close-ar-fallback" style="
                    background: linear-gradient(135deg, #ff69b4, #ff1493);
                    color: white;
                    border: none;
                    padding: 1rem 2rem;
                    border-radius: 50px;
                    font-size: 1rem;
                    cursor: pointer;
                    box-shadow: 0 5px 15px rgba(255, 105, 180, 0.4);
                ">
                    Close
                </button>
            </div>
        `;
        
        document.body.appendChild(fallbackContainer);
        
        // Add close functionality
        document.getElementById('close-ar-fallback').addEventListener('click', () => {
            fallbackContainer.style.display = 'none';
        });
        
        // Add pulse animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Public API methods
    startARExperience() {
        if (this.isXR8Loaded) {
            const canvas = document.getElementById('ar-canvas');
            if (canvas) {
                canvas.style.display = 'block';
            }
        } else {
            const fallback = document.getElementById('ar-fallback');
            if (fallback) {
                fallback.style.display = 'flex';
            }
        }
    }
    
    stopARExperience() {
        const canvas = document.getElementById('ar-canvas');
        if (canvas) {
            canvas.style.display = 'none';
        }
        
        const fallback = document.getElementById('ar-fallback');
        if (fallback) {
            fallback.style.display = 'none';
        }
        
        if (this.isXR8Loaded && typeof XR8 !== 'undefined') {
            XR8.stop();
        }
    }
    
    isARAvailable() {
        return this.isARSupported;
    }
}

// Initialize AR Companion System
let arCompanionSystem;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        arCompanionSystem = new ARCompanionSystem();
        window.arCompanionSystem = arCompanionSystem;
    });
} else {
    arCompanionSystem = new ARCompanionSystem();
    window.arCompanionSystem = arCompanionSystem;
}

// Export for use in other scripts
window.ARCompanionSystem = ARCompanionSystem;