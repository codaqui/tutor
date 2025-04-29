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

const mongoAuthState = require('./mongoAuthState'); // Import the MongoDB auth state handler
const { MongoClient } = require('mongodb'); // Import MongoClient for the clearMongoIfNeeded function

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

// --- Add MongoDB connection details (ideally from environment variables) ---
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017'; // Replace with your MongoDB URL
const MONGO_DB_NAME = process.env.MONGO_DB_NAME || 'whatsapp_api'; // Replace with your desired DB name
// --- End MongoDB connection details ---


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

/**
 * Establishes and manages the connection to WhatsApp Web.
 * Handles authentication, QR code generation, connection events, and message receiving.
 */
async function connectToWhatsApp() {
    // Use MongoDB authentication state instead of multi-file
    console.log(t('mongo.connecting', { url: MONGO_URL, db: MONGO_DB_NAME }));

    try {
        await clearMongoIfNeeded();
        
        // Pass proto and BufferJSON explicitly
        const { state, saveCreds, clearCreds } = await mongoAuthState(proto, BufferJSON, MONGO_URL, MONGO_DB_NAME);
        
        // Fetch the latest version of Baileys
        const { version, isLatest } = await fetchLatestBaileysVersion();
        console.log(t('whatsapp.version', { version: version.join('.'), isLatest }));

        console.log("\n===========================================");
        console.log(t('connection.starting'));
        console.log(t('connection.qr_coming'));
        console.log("===========================================\n");

        // Create a new WhatsApp socket instance with recommended settings
        const sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: true,
            connectTimeoutMs: 60000,
            qrTimeout: 60000,
            browser: ['Chrome', 'Desktop', '10.0'],
            logger: require('pino')({ level: 'silent' }) // Reduce log noise
        });

        // Listen for connection updates
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
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
                
                console.log(t('connection.closed', { reason: lastDisconnect?.error?.message || 'sem detalhes' }));
                
                if (shouldReconnect) {
                    console.log(t('connection.reconnecting'));
                    setTimeout(connectToWhatsApp, 3000);
                } else {
                    console.log(t('connection.logout'));
                    await clearCreds();
                }
            }
            
            if (connection === 'open') {
                console.log("\n===========================================");
                console.log(t('connection.success'));
                console.log(t('connection.connected_as', { user: sock.user?.id || 'Desconhecido' }));
                console.log("===========================================\n");
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

// Helper function to clear MongoDB if error condition persists
let errorCount = 0;
async function clearMongoIfNeeded() {
    try {
        const client = new MongoClient(MONGO_URL);
        await client.connect();
        const db = client.db(MONGO_DB_NAME);
        const collection = db.collection('baileys_auth_state');
        
        // If we've had multiple errors, clear the database
        if (errorCount > 2) {
            console.log(t('mongo.clearing'));
            await collection.deleteMany({});
            console.log(t('mongo.cleared'));
            errorCount = 0;
        } else {
            errorCount++;
        }
        
        await client.close();
    } catch (err) {
        console.error(t('mongo.error_checking', { error: err.message || err }));
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
