/**
 * MyPrabh Mobile Optimization System
 * Touch-optimized interactions and mobile-specific enhancements
 */

class MobileOptimizationManager {
    constructor() {
        this.isMobile = false;
        this.isTablet = false;
        this.touchSupported = false;
        this.orientation = 'portrait';
        this.viewportHeight = window.innerHeight;
        this.safeAreaInsets = { top: 0, bottom: 0, left: 0, right: 0 };
        
        this.touchHandlers = new Map();
        this.gestureRecognizer = null;
        this.hapticFeedback 