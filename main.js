const CriacaoTabela = require('./scripts/CriacaoTabela');
const ConexaoBD = require('./scripts/Conexao');
const LeituraLog = require('./scripts/LeituraLog');
const Print = require('./scripts/Print');

async function main() {
  let conn;

  try {
    conn = await ConexaoBD(); 
    await CriacaoTabela(conn);
    await LeituraLog();
    await Print(conn);
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
      const db = await ConexaoBD();
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
