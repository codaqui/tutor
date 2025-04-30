/**
 * WhatsApp Connection Manager
 * Utilities to help manage WebSocket connections and reconnection strategies
 */

const MAX_RECONNECT_RETRIES = 10;
const MAX_RECONNECT_INTERVAL_MS = 60000; // 1 minute

/**
 * Creates a connection manager for handling WebSocket connections
 * @returns {Object} Connection manager functions
 */
function createConnectionManager() {
    let reconnectCount = 0;
    let reconnectTimer = null;
    let isReconnecting = false;

    /**
     * Get the next reconnect interval with exponential backoff
     * @returns {number} Interval in milliseconds
     */
    const getNextReconnectInterval = () => {
        // Exponential backoff with some randomness
        const baseDelay = Math.min(
            3000 * Math.pow(1.5, reconnectCount),
            MAX_RECONNECT_INTERVAL_MS
        );
        // Add jitter (±20%)
        const jitter = baseDelay * (0.8 + Math.random() * 0.4);
        return Math.floor(jitter);
    };

    /**
     * Handle WebSocket connection error
     * @param {Error} error - WebSocket error
     * @param {Function} reconnectCallback - Function to call for reconnection
     */
    const handleConnectionError = (error, reconnectCallback) => {
        console.log(`WebSocket error: ${error?.message || 'Unknown error'}`);
        console.log('Connection details:', JSON.stringify({
            reconnectCount,
            isReconnecting,
            nextInterval: getNextReconnectInterval()
        }));
        
        if (isReconnecting) {
            console.log('Already attempting to reconnect...');
            return;
        }
        
        isReconnecting = true;
        
        if (reconnectCount < MAX_RECONNECT_RETRIES) {
            const reconnectDelay = getNextReconnectInterval();
            console.log(`Will attempt to reconnect in ${reconnectDelay/1000} seconds (attempt ${reconnectCount + 1}/${MAX_RECONNECT_RETRIES})...`);
            
            // Clear any existing timer
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
            }
            
            // Schedule reconnection
            reconnectTimer = setTimeout(() => {
                reconnectCount++;
                isReconnecting = false;
                reconnectCallback();
            }, reconnectDelay);
        } else {
            console.log(`Maximum reconnection attempts (${MAX_RECONNECT_RETRIES}) reached. Stopping reconnection.`);
            // At this point, you might want to implement a more drastic recovery strategy
            // like restarting the entire process or notifying administrators
        }
    };

    /**
     * Reset the connection state after successful connection
     */
    const onSuccessfulConnection = () => {
        console.log('Connection successful, resetting reconnection counter');
        reconnectCount = 0;
        isReconnecting = false;
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
    };

    /**
     * Check if websocket error is transient (can be retried)
     * @param {Error} error - WebSocket error
     * @returns {boolean} Whether the error is transient
     */
    const isTransientError = (error) => {
        // These error types typically mean temporary network issues
        const transientErrorTypes = [
            'ECONNRESET', 'ETIMEDOUT', 'ECONNREFUSED', 'EPIPE', 
            'EHOSTUNREACH', 'ENOTFOUND', 'ENETUNREACH'
        ];
        
        // Check for WebSocket close codes that indicate temporary issues
        const transientWsCloseCodes = [
            1001, // Going Away
            1006, // Abnormal Closure
            1012, // Service Restart
            1013, // Try Again Later
            1014  // Bad Gateway
        ];
        
        if (!error) return true;
        
        // Check error code
        if (error.code && transientErrorTypes.includes(error.code)) {
            return true;
        }
        
        // Check WebSocket close code
        if (error.closeCode && transientWsCloseCodes.includes(error.closeCode)) {
            return true;
        }
        
        // Network errors are usually transient
        if (error.message && /network|timeout|reset|refused|unavailable/i.test(error.message)) {
            return true;
        }
        
        // Default to assuming transient for unknown errors
        return true;
    };

    return {
        handleConnectionError,
        onSuccessfulConnection,
        isTransientError,
        getReconnectCount: () => reconnectCount,
        resetReconnectCount: () => { reconnectCount = 0; }
    };
}

module.exports = { createConnectionManager };
