const { Pool } = require('pg');
const { initAuthCreds } = require('baileys');

/**
 * Implementation of PostgreSQL-based auth state storage for Baileys.
 * Based on the original mongoAuthState implementation.
 */
const postgresAuthState = async (proto, BufferJSON, postgresUrl, schema = 'public', tableName = 'baileys_auth_state') => {
    if (!postgresUrl) throw new Error('PostgreSQL connection URL is required');
    
    let pool;
    const fullTableName = `${schema}.${tableName}`;

    try {
        pool = new Pool({
            connectionString: postgresUrl
        });
        
        // Test connection
        const client = await pool.connect();
        
        // Check if schema exists, create if not
        await client.query(`CREATE SCHEMA IF NOT EXISTS ${schema}`);
        
        // Create table if not exists
        await client.query(`
            CREATE TABLE IF NOT EXISTS ${fullTableName} (
                id VARCHAR(255) PRIMARY KEY,
                value JSONB NOT NULL
            )
        `);
        
        client.release();
        // Se a função t estiver disponível no escopo global, use-a
        if (typeof t === 'function') {
            console.log(t('postgres.connected'));
        } else {
            console.log('✅ Conectado com sucesso ao PostgreSQL para autenticação');
        }
    } catch (error) {
        if (typeof t === 'function') {
            console.error(t('postgres.connection_failed', { error: error.message || error }));
        } else {
            console.error('❌ Falha ao conectar ao PostgreSQL para autenticação:', error);
        }
        throw error;
    }

    const writeData = async (id, data) => {
        try {
            if (data === null || data === undefined) {
                await pool.query(`DELETE FROM ${fullTableName} WHERE id = $1`, [id]);
                return;
            }
            
            // Add safety check for Buffer objects
            const safeData = JSON.parse(JSON.stringify(data, (key, value) => {
                if (value?.type === 'Buffer' && Array.isArray(value.data)) {
                    return { type: 'Buffer', data: value.data };
                }
                return value;
            }));
            
            // First stringify with the special BufferJSON replacer to handle Buffer objects
            const serializedData = JSON.stringify(safeData, BufferJSON.replacer);
            // Then parse it back to a plain object that can be stored in PostgreSQL
            const value = JSON.parse(serializedData);
            
            await pool.query(
                `INSERT INTO ${fullTableName} (id, value) 
                 VALUES ($1, $2::jsonb) 
                 ON CONFLICT (id) DO UPDATE 
                 SET value = $2::jsonb`,
                [id, value]
            );
        } catch (error) {
            console.error(`Error writing auth data for ${id}:`, error);
            if (error.toString().includes('circular')) {
                console.error('Detected circular reference in data, attempting to sanitize...');
                try {
                    // Try to sanitize circular references
                    const seen = new WeakSet();
                    const sanitizedData = JSON.parse(JSON.stringify(data, (key, value) => {
                        if (typeof value === 'object' && value !== null) {
                            if (seen.has(value)) {
                                return '[Circular]';
                            }
                            seen.add(value);
                        }
                        return value;
                    }));
                    
                    const serializedData = JSON.stringify(sanitizedData, BufferJSON.replacer);
                    const value = JSON.parse(serializedData);
                    
                    await pool.query(
                        `INSERT INTO ${fullTableName} (id, value) 
                         VALUES ($1, $2::jsonb) 
                         ON CONFLICT (id) DO UPDATE 
                         SET value = $2::jsonb`,
                        [id, value]
                    );
                    console.log(`Successfully saved sanitized data for ${id}`);
                } catch (sanitizeError) {
                    console.error('Failed to sanitize data:', sanitizeError);
                    throw sanitizeError;
                }
            } else {
                throw error; // Propagate error for better debugging
            }
        }
    };

    const readData = async (id) => {
        try {
            const result = await pool.query(
                `SELECT value FROM ${fullTableName} WHERE id = $1`,
                [id]
            );
            
            if (result.rows.length === 0) {
                return null;
            }
            
            try {
                // First stringify the value to ensure we have a clean string
                const serializedData = JSON.stringify(result.rows[0].value);
                // Then parse with the BufferJSON reviver to convert string back to Buffer
                return JSON.parse(serializedData, BufferJSON.reviver);
            } catch (parseError) {
                console.error(`Error parsing auth data for ${id}:`, parseError);
                // Fall back to raw value if parsing fails
                return result.rows[0].value;
            }
        } catch (error) {
            console.error(`Error reading auth data for ${id}:`, error);
            throw error; // Propagate error for better debugging
        }
    };

    const removeData = async (id) => {
        try {
            await pool.query(`DELETE FROM ${fullTableName} WHERE id = $1`, [id]);
        } catch (error) {
            console.error(`Error removing auth data for ${id}:`, error);
        }
    };

    const clearCreds = async () => {
        try {
            await pool.query(`DELETE FROM ${fullTableName}`);
            console.log('All auth data cleared from PostgreSQL');
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

module.exports = postgresAuthState;
