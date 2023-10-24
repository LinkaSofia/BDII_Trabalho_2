const InitializeDatabase = require('./scripts/CriacaoTabela');
const ConnectToDB = require('./scripts/Conexao');
const ProcessLog = require('./scripts/LeituraLog');
const DisplayResults = require('./scripts/Print');

async function application() {
  let dbConnection;

  try {
    dbConnection = await ConnectToDB(); 
    await dbConnection.query('BEGIN');
    await InitializeDatabase(dbConnection);
    await ProcessLog();
    await DisplayResults(dbConnection);
    await dbConnection.query('COMMIT');
  } catch (error) {
    if (dbConnection) {
      await dbConnection.query('ROLLBACK');
    }
    console.error('Erro na aplicação', error);
  } finally {
    if (dbConnection) {
      await dbConnection.end(); 
    }
  }
}

application();
