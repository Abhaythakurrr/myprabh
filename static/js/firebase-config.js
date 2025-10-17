// Firebase Configuration for My Prabh
// Configuration is loaded from server-side environment variables
// This prevents exposing sensitive API keys in client-side code

// Firebase config will be injected by the server
window.firebaseConfig = null;

// Function to initialize Firebase with server-provided config
function initializeFirebaseConfig(config) {
    window.firebaseConfig = config;
    
    // Initialize Firebase if SDK is loaded
    if (typeof firebase !== 'undefined') {
        firebase.initializeApp(config);
        console.log('🔥 Firebase initialized successfully');
    }
}

// Export for use in other files
window.initializeFirebaseConfig = initializeFirebaseConfig;