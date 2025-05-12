// Import necessary modules from the Baileys library for WhatsApp interaction
// Use a namespace import for Baileys
const { default: makeWASocket, 
        DisconnectReason, 
        fetchLatestBaileysVersion, 
        useMultiFileAuthState, 
        makeInMemoryStore, 
        proto, 
        BufferJSON,
        initAuthCreds } = require('baileys');

const { createConnectionManager } = require('./connection-manager'); // Import our connection manager

const postgresAuthState = require('./postgresAuthState'); // Import the PostgreSQL auth state handler
const { Pool } = require('pg'); // Import Pool from pg for the clearDBIfNeeded function

// Import module to generate QR codes in the terminal
const qrcode = require('qrcode-terminal');

// Import Boom for handling HTTP-friendly errors
const { Boom } = require('@hapi/boom');

// Import Node.js path module for handling file paths
const path = require('path');

// Import Node.js file system module for file operations
const fs = require('fs');

// Import Express framework for creating the API
const express = require('express');

// Import body-parser middleware to parse request bodies
const bodyParser = require('body-parser');

// Import axios for making HTTP requests
const axios = require('axios');

// Load localization strings from a JSON file
const localePath = path.join(__dirname, 'locales', 'pt-BR.json');
const localeData = JSON.parse(fs.readFileSync(localePath, 'utf8'));

// --- Add PostgreSQL connection details (ideally from environment variables) ---
const PG_URL = process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/intranet';
const PG_SCHEMA = process.env.PG_SCHEMA || 'public';
const PG_TABLE = process.env.PG_TABLE || 'baileys_auth_state';
// --- End PostgreSQL connection details ---


// Helper function to get localized strings with variable substitution
function t(key, variables = {}) {
    // Retrieve the translation for the given key, defaulting to the key itself if not found
    let translation = localeData[key] || key;
    // Replace placeholders (e.g., ${variable}) with actual values
    for (const variable in variables) {
        translation = translation.replace(`\${${variable}}`, variables[variable]);
    }
    return translation;
}

// Create a connection manager instance to handle reconnections
const connectionManager = createConnectionManager();

/**
 * Establishes and manages the connection to WhatsApp Web.
 * Handles authentication, QR code generation, connection events, and message receiving.
 */
async function connectToWhatsApp() {
    // Use PostgreSQL authentication state
    console.log(t('postgres.connecting'));

    try {
        await clearDBIfNeeded();
        
        // Pass proto and BufferJSON explicitly
        const { state, saveCreds, clearCreds } = await postgresAuthState(proto, BufferJSON, PG_URL, PG_SCHEMA, PG_TABLE);
        
        // Fetch the latest version of Baileys
        const { version, isLatest } = await fetchLatestBaileysVersion();
        console.log(t('whatsapp.version', { version: version.join('.'), isLatest }));

        console.log("\n===========================================");
        console.log(t('connection.starting'));
        console.log(t('connection.qr_coming'));
        console.log("===========================================\n");

        // Create a new WhatsApp socket instance with improved connection settings
        const sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: true,
            connectTimeoutMs: 120000, // Increased timeout for initial connection
            qrTimeout: 60000,
            browser: ['Chrome', 'Desktop', '10.0'],
            logger: require('pino')({ 
                level: process.env.LOG_LEVEL || 'silent',
                transport: {
                    target: 'pino-pretty',
                    options: {
                        colorize: true
                    }
                }
            }),
            // Enhanced WebSocket configuration
            customUploadHosts: [],
            markOnlineOnConnect: true, // Mark as online when connected
            retryRequestDelayMs: 5000, // Wait longer between retries
            maxRetryRequestCount: 10, // More retry attempts
            syncFullHistory: false, // Don't sync full history which can cause timeouts
            // More aggressive keepalive to prevent connection drops
            keepAliveIntervalMs: 5000,
            // Handle connection termination better
            emitOwnEvents: true,
            // Additional options to prevent timeouts
            defaultQueryTimeoutMs: 60000,
            getMessage: async () => { return { conversation: '' } }
        });

        // Listen for connection updates with improved error handling
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) {
                console.log("\n===========================================");
                console.log(t('connection.qr_ready'));
                console.log("===========================================\n");
            }
            
            if (connection) {
                console.log(t('connection.status', { status: connection }));
            }
            
            if (connection === 'close') {
                // Extract the detailed error information
                const error = lastDisconnect?.error;
                const statusCode = error?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
                
                // Detailed error logging
                if (error) {
                    console.log('Connection closed with error:', JSON.stringify({
                        name: error.name,
                        message: error.message,
                        statusCode: statusCode,
                        output: error.output
                    }, null, 2));
                }
                
                // Log detailed error information for better debugging
                console.log(t('connection.closed', { 
                    reason: error ? `${error.name || 'Error'}: ${error.message}` : 'WebSocket Closed (Timeout or network issue)'
                }));
                
                if (shouldReconnect) {
                    console.log(t('connection.reconnecting'));
                    
                    // Use our connection manager for intelligent reconnection handling
                    connectionManager.handleConnectionError(error, connectToWhatsApp);
                    
                    // Clear the table if we've had multiple consecutive failures
                    if (connectionManager.getReconnectCount() > 5) {
                        try {
                            console.log('Clearing auth state due to persistent connection issues...');
                            await clearCreds();
                            connectionManager.resetReconnectCount();
                        } catch (clearError) {
                            console.error('Failed to clear auth state:', clearError);
                        }
                    }
                } else {
                    console.log(t('connection.logout'));
                    await clearCreds();
                    connectionManager.resetReconnectCount();
                }
            }
            
            if (connection === 'open') {
                console.log("\n===========================================");
                console.log(t('connection.success'));
                console.log(t('connection.connected_as', { user: sock.user?.id || 'Desconhecido' }));
                console.log("===========================================\n");
                
                // Reset connection manager on successful connection
                connectionManager.onSuccessfulConnection();
            }
        });
        
        // Listen for credential updates
        sock.ev.on('creds.update', saveCreds);
        
        // Listen for incoming messages
        sock.ev.on('messages.upsert', async m => {
            // Log the message type in a more structured way
            console.log("\n===========================================");
            console.log(t('message.received', { type: m.type }));

            // Enhanced logging for 'notify' type messages
            if (m.type === 'notify' && m.messages && m.messages.length > 0) {
                const msg = m.messages[0];                
                // Log sender details without exposing full message content
                const senderJid = msg.key.remoteJid;
                const senderId = msg.key.participant || senderJid;
                // Try to get sender's name from contact name or extract from JID
                const senderName = msg.pushName || senderId.split('@')[0];
                // Get recipient info (could be a group or individual)
                const recipient = senderJid.includes('@g.us') ? 'grupo' : 'chat privado';
                // Determine the message type
                const messageType = Object.keys(msg.message || {}).join(', ') || 'desconhecido';
                // Check if it's a group message
                const isGroup = senderJid.includes('@g.us') ? 'sim' : 'não';
                // Format timestamp
                const timestamp = new Date(msg.messageTimestamp * 1000).toLocaleString('pt-BR');
                
                // Log detailed but secure information about the message
                console.log(t('message.notify_received', { 
                    senderName,
                    senderId: senderId.split('@')[0], // Remove the @s.whatsapp.net part
                    recipient 
                }));
                console.log(t('message.message_type', { messageType }));
                console.log(t('message.group_message', { isGroup }));
                console.log(t('message.timestamp', { timestamp }));
            }

            // Send the raw event to the logger service
            const eventLoggerUrl = process.env.EVENT_LOGGER_URL;
            if (eventLoggerUrl) {
                try {
                    await axios.post(eventLoggerUrl, m);
                    console.log(t('event.sent_to_logger'));
                } catch (error) {
                    console.error(t('event.error_sending_to_logger', { error: error.message || error }));
                }
            }
            console.log("===========================================\n");
        });

        return sock;
    } catch (error) {
        console.error(t('error.connecting', { error: error.message || error }));
        console.log(t('error.retry', { seconds: 5 }));
        setTimeout(connectToWhatsApp, 5000);
    }
}

// Helper function to clear PostgreSQL if error condition persists
let errorCount = 0;
async function clearDBIfNeeded() {
    try {
        const pool = new Pool({
            connectionString: PG_URL
        });
        
        // Test connection first
        const client = await pool.connect();
        client.release();
        console.log(t('postgres.connected_for_auth'));
        
        // If we've had multiple errors, clear the database
        if (errorCount > 2) {
            console.log(t('postgres.clearing'));
            try {
                await pool.query(`DELETE FROM ${PG_SCHEMA}.${PG_TABLE}`);
                console.log(t('postgres.cleared'));
                errorCount = 0;
            } catch (clearError) {
                console.error(t('postgres.error_clearing', { error: clearError.message }));
                // If table doesn't exist yet, that's fine
                if (!clearError.message.includes('does not exist')) {
                    throw clearError;
                }
            }
        } else {
            errorCount++;
        }
        
        await pool.end();
        return true;
    } catch (err) {
        console.error(t('postgres.error_checking', { error: err.message || err }));
        return false;
    }
}

// Helper function to gracefully restart the WhatsApp connection
async function restartWhatsApp() {
    console.log(t('connection.restarting'));
    try {
        // Clear the database entirely to start fresh
        const pool = new Pool({
            connectionString: PG_URL
        });
        
        try {
            await pool.query(`DROP TABLE IF EXISTS ${PG_SCHEMA}.${PG_TABLE}`);
            console.log(t('postgres.table_dropped'));
        } catch (dropError) {
            console.error(t('postgres.error.dropping_table', { error: dropError.message }));
        }
        
        await pool.end();
        
        // Reset error count
        errorCount = 0;
        
        // Restart after a short delay
        setTimeout(connectToWhatsApp, 5000);
    } catch (error) {
        console.error(t('error.restarting', { error: error.message || error }));
        // Try again after a longer delay
        setTimeout(connectToWhatsApp, 15000);
    }
}

/**
 * Sets up and runs the Express API server.
 * Defines endpoints for sending various types of WhatsApp messages.
 * @param {object} sock - The initialized WhatsApp socket instance.
 */
function setupApi(sock) {
    // Create an Express application
    const app = express();
    // Use body-parser middleware to handle JSON request bodies
    app.use(bodyParser.json());
    // Define the port for the API server, using environment variable or default
    const port = process.env.PORT || 3000;

    // API endpoint to send a text message
    app.post('/send/text', async (req, res) => {
        const { jid, message } = req.body; // Extract JID and message from request body
        // Validate required parameters
        if (!jid || !message) {
            return res.status(400).json({ error: t('api.error.missing_params_jid_message') });
        }
        try {
            // Validate JID existence on WhatsApp
            const [result] = await sock.onWhatsApp(jid);
            if (!result?.exists) {
                 console.error(t('api.error.invalid_jid', { jid }));
                 return res.status(400).json({ success: false, error: t('api.fail.invalid_jid', { jid }) });
            }

            console.log(t('api.log.sending_text', { jid }));
            // Send the text message using the WhatsApp socket
            await sock.sendMessage(jid, { text: message });
            console.log(t('api.log.sent_text', { jid }));
            // Respond with success
            res.status(200).json({ success: true, message: t('api.success.text_sent') });
        } catch (error) {
            console.error(t('api.error.sending_text', { error: error.message || error }));
            // Respond with error - Consider more specific error handling if needed
            res.status(500).json({ success: false, error: t('api.fail.sending_text') });
        }
    });

    // API endpoint to send an image message
    app.post('/send/image', async (req, res) => {
        const { jid, url, caption } = req.body; // Extract JID, image URL, and optional caption
        // Validate required parameters
        if (!jid || !url) {
            return res.status(400).json({ error: t('api.error.missing_params_jid_url') });
        }
        try {
            console.log(t('api.log.sending_image', { jid }));
            // Prepare message options for the image
            const messageOptions = {
                image: { url: url }, // Image source URL
                caption: caption || '' // Optional caption
            };
            // Send the image message
            await sock.sendMessage(jid, messageOptions);
            console.log(t('api.log.sent_image', { jid }));
            // Respond with success
            res.status(200).json({ success: true, message: t('api.success.image_sent') });
        } catch (error) {
            console.error(t('api.error.sending_image', { error: error.message || error }));
            // Respond with error
            res.status(500).json({ success: false, error: t('api.fail.sending_image') });
        }
    });

    // API endpoint to send a video message
    app.post('/send/video', async (req, res) => {
        const { jid, url, caption } = req.body; // Extract JID, video URL, and optional caption
        // Validate required parameters
        if (!jid || !url) {
            return res.status(400).json({ error: t('api.error.missing_params_jid_url') });
        }
        try {
            console.log(t('api.log.sending_video', { jid }));
            // Prepare message options for the video
             const messageOptions = {
                video: { url: url }, // Video source URL
                caption: caption || '' // Optional caption
            };
            // Send the video message
            await sock.sendMessage(jid, messageOptions);
            console.log(t('api.log.sent_video', { jid }));
            // Respond with success
            res.status(200).json({ success: true, message: t('api.success.video_sent') });
        } catch (error) {
            console.error(t('api.error.sending_video', { error: error.message || error }));
            // Respond with error
            res.status(500).json({ success: false, error: t('api.fail.sending_video') });
        }
    });

    // API endpoint to send an audio message
    app.post('/send/audio', async (req, res) => {
        // Extract JID, audio URL, and optional ptt flag (push-to-talk)
        const { jid, url, ptt = false } = req.body;
        // Validate required parameters
        if (!jid || !url) {
            return res.status(400).json({ error: t('api.error.missing_params_jid_url') });
        }
        try {
            console.log(t('api.log.sending_audio', { jid }));
            // Prepare message options for the audio
            const messageOptions = {
                audio: { url: url }, // Audio source URL
                ptt: ptt // Send as a voice note if true
                // mimetype: 'audio/ogg; codecs=opus' // Optional: Specify mimetype if needed
            };
            // Send the audio message
            await sock.sendMessage(jid, messageOptions);
            console.log(t('api.log.sent_audio', { jid }));
            // Respond with success
            res.status(200).json({ success: true, message: t('api.success.audio_sent') });
        } catch (error) {
            console.error(t('api.error.sending_audio', { error: error.message || error }));
            // Respond with error
            res.status(500).json({ success: false, error: t('api.fail.sending_audio') });
        }
    });

    // API endpoint for health check
    app.get('/health', (req, res) => {
        console.log(t('api.log.health_check_requested'));
        // Check if WhatsApp connection is active
        const isConnected = sock.user !== undefined;
        // Prepare health status response
        const healthStatus = {
            status: isConnected ? 'healthy' : 'degraded',
            whatsapp: {
                connected: isConnected,
                user: isConnected ? sock.user?.id : null
            },
            api: {
                status: 'online',
                timestamp: new Date().toISOString()
            }
        };
        
        // Send appropriate status code based on WhatsApp connection
        const statusCode = isConnected ? 200 : 200; // Still 200 even if WhatsApp is disconnected as API is working
        res.status(statusCode).json(healthStatus);
    });

    // Start the API server and listen on the specified port
    app.listen(port, () => {
        console.log(t('api.log.listening', { port }));
    });
}

// Main execution block
// Connect to WhatsApp first
connectToWhatsApp()
    .then(sock => {
        // Once connected, set up and start the API server
        setupApi(sock);
    })
    // Catch and log any errors during the connection process
    .catch(err => console.log(t('error.unexpected', { error: err })));
