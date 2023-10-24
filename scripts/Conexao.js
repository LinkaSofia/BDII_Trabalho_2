const { Client } = require('pg');

const dbConfig = {
  user: 'postgres',
  host: 'localhost',
  database: 'postgres',
  password: '123',
  port: 5432,
};

async function connectToDatabase() {
  const client = new Client(dbConfig);
  try {
    await client.connect();
    return client;
  } catch (error) {
    console.error('Erro na conexão:', error);
    throw error;
  }
}

module.exports = connectToDatabase;
