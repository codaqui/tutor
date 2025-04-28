// Import necessary modules from the Baileys library for WhatsApp interaction
const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');

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
    // Use multi-file authentication state to store credentials persistently
    const { state, saveCreds } = await useMultiFileAuthState(path.join(__dirname, 'auth_info_baileys'));
    // Fetch the latest version of Baileys
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(t('whatsapp.version', { version: version.join('.'), isLatest }));

    // Create a new WhatsApp socket instance
    const sock = makeWASocket({
        version,
        printQRInTerminal: true, // Automatically print QR code to terminal if needed
        auth: state, // Provide the authentication state
        logger: require('pino')({ level: 'silent' }) // Configure logger level (silent, info, debug)
    });

    // Handle QR code display if the user is not registered yet
    if (!sock.authState.creds.registered) {
        console.log(t('qrcode.scan'));
        // qrcode-terminal handles the display in the terminal
    }

    // Listen for connection updates
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        // If a QR code is received, display it in the terminal
        if (qr) {
            console.log(t('qrcode.received'));
            qrcode.generate(qr, { small: true }); // Generate a smaller QR code
        }
        // Handle connection close events
        if (connection === 'close') {
            // Check if reconnection is needed (i.e., not logged out)
            const shouldReconnect = (lastDisconnect.error instanceof Boom) && lastDisconnect.error.output.statusCode !== DisconnectReason.loggedOut;
            console.log(t('connection.closed'), lastDisconnect.error, t('connection.reconnecting'), shouldReconnect);
            // Reconnect if the disconnection was not due to logging out
            if (shouldReconnect) {
                connectToWhatsApp();
            } else {
                console.log(t('connection.closed_logout'));
                // Optional: Clean up authentication files upon logout
                // fs.rmdirSync(path.join(__dirname, 'auth_info_baileys'), { recursive: true });
            }
        // Handle successful connection opening
        } else if (connection === 'open') {
            console.log(t('connection.opened'));
        }
    });

    // Listen for credential updates and save them
    sock.ev.on('creds.update', saveCreds);

    // Listen for incoming messages
    sock.ev.on('messages.upsert', async m => {
        // console.log(JSON.stringify(m, undefined, 2)); // Uncomment to log the full message structure

        // Send the raw event to the logger service
        const eventLoggerUrl = process.env.EVENT_LOGGER_URL;
        if (eventLoggerUrl) {
            try {
                await axios.post(eventLoggerUrl, m);
                console.log(t('event.sent_to_logger'));
            } catch (error) {
                console.error(t('event.error_sending_to_logger'), error.message || error);
            }
        }
        // const msg = m.messages[0];
        // Save example.
        // // Process only messages not sent by the bot itself and of type 'notify'
        // if (!msg.key.fromMe && m.type === 'notify') {
        //     console.log(t('message.replying_to'), msg.key.remoteJid);
        //     // Extract the text content from the message
        //     const messageText = msg.message?.conversation || msg.message?.extendedTextMessage?.text;
        //     // Check if the message matches a specific trigger phrase
        //     if (messageText === 'Oi, eu preciso de ajuda!') {
        //         console.log(t('message.received_help_request', { remoteJid: msg.key.remoteJid }));
        //         // Send a predefined response
        //         await sock.sendMessage(msg.key.remoteJid, { text: t('message.help_response') });
        //         console.log(t('message.replied_to', { remoteJid: msg.key.remoteJid }));
        //     }
        // }
    });

    // Return the initialized socket instance
    return sock;
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
            console.error(t('api.error.sending_text'), error);
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
            console.error(t('api.error.sending_image'), error);
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
            console.error(t('api.error.sending_video'), error);
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
            console.error(t('api.error.sending_audio'), error);
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
    .catch(err => console.log(t('error.unexpected'), err));
