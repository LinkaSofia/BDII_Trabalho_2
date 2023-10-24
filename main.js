const InitializeDatabase = require('./scripts/CriacaoTabela');
const ConnectToDB = require('./scripts/Conexao');
const ProcessLog = require('./scripts/LeituraLog');
const DisplayResults = require('./scripts/Print');

async function application() {
  let Conexao;

  try {
    Conexao = await ConnectToDB(); 
    await Conexao.query('BEGIN');
    await InitializeDatabase(Conexao);
    await ProcessLog();
    await DisplayResults(Conexao);
    await Conexao.query('COMMIT');
  } catch (error) {
    if (Conexao) {
      await Conexao.query('ROLLBACK');
    }
    console.error('Erro na aplicação', error);
  } finally {
    if (Conexao) {
      await Conexao.end(); 
    }
  }
}

application();
