const { read } = require('fs');
const CriacaoTabela = require('./scripts/CriacaoTabela');
const connectToDatabase = require('./scripts/Conexao');
const LeituraLog = require('./scripts/LeituraLog');

async function main() {
  let conn;

  try {
    conn = await connectToDatabase(); 
    await CriacaoTabela(conn);
    LeituraLog();
  } catch (error) {
    if (conn) {
      await conn.query('ROLLBACK');
    }
    console.error('Erro', error);
  } finally {
    if (conn) {
      await conn.end(); 
    }
  }

  /*async function imprimirConteudoBanco() {
    try {
      const db = await connectToDatabase();
      const result = await db.query('SELECT * FROM DATA');
      console.log("Conteúdo do banco de dados atualizado:");
      console.table(result.rows);
    } catch (error) {
      console.error('Erro ao imprimir o conteúdo do banco de dados:', error);
    }
  }
  
  // Chame esta função após a execução do UNDO
  imprimirConteudoBanco();*/
}

main();
