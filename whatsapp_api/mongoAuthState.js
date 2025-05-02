const { MongoClient } = require('mongodb');
const { initAuthCreds } = require('baileys');

/**
 * Implementation of MongoDB-based auth state storage for Baileys.
 * Based on the original useMultiFileAuthState implementation.
 */
const mongoAuthState = async (proto, BufferJSON, mongoUrl, dbName, collectionName = 'baileys_auth_state') => {
    if (!mongoUrl) throw new Error('MongoDB URL is required');
    
    let client;
    let collection;

    try {
        client = new MongoClient(mongoUrl);
        await client.connect();
        const db = client.db(dbName);
        collection = db.collection(collectionName);
        console.log('Connected successfully to MongoDB for auth state');
    } catch (error) {
        console.error('Failed to connect to MongoDB for auth state:', error);
        throw error;
    }

    const writeData = async (id, data) => {
        try {
            if (data === null || data === undefined) {
                await collection.deleteOne({ _id: id });
                return;
            }
            
            // Use BufferJSON.replacer to properly handle Buffers
            const serialized = JSON.stringify(data, BufferJSON.replacer);
            const value = JSON.parse(serialized);
            
            await collection.replaceOne(
                { _id: id }, 
                { _id: id, value }, 
                { upsert: true }
            );
        } catch (error) {
            console.error(`Error writing auth data for ${id}:`, error);
        }
    };

    const readData = async (id) => {
        try {
            const data = await collection.findOne({ _id: id });
            if (!data) {
                return null;
            }
            
            // Use BufferJSON.reviver to properly convert string back to Buffer
            return JSON.parse(JSON.stringify(data.value), BufferJSON.reviver);
        } catch (error) {
            console.error(`Error reading auth data for ${id}:`, error);
            return null;
        }
    };

    const removeData = async (id) => {
        try {
            await collection.deleteOne({ _id: id });
        } catch (error) {
            console.error(`Error removing auth data for ${id}:`, error);
        }
    };

    const clearCreds = async () => {
        try {
            await collection.deleteMany({});
            console.log('All auth data cleared from MongoDB');
        } catch (error) {
            console.error('Error clearing auth data:', error);
        }
    };

    const creds = await readData('creds') || initAuthCreds();

    return {
        state: {
            creds,
            keys: {
                get: async (type, ids) => {
                    const data = {};
                    await Promise.all(ids.map(async (id) => {
                        const key = `${type}-${id}`;
                        data[id] = await readData(key);
                    }));
                    return data;
                },
                set: async (data) => {
                    const tasks = [];
                    for (const category in data) {
                        for (const id in data[category]) {
                            const value = data[category][id];
                            const key = `${category}-${id}`;
                            tasks.push(value ? writeData(key, value) : removeData(key));
                        }
                    }
                    await Promise.all(tasks);
                }
            }
        },
        saveCreds: async () => {
            await writeData('creds', creds);
        },
        clearCreds
    };
};

module.exports = mongoAuthState;
