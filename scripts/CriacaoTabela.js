const ConexaoBD = require('./Conexao');
const metadata = require('../Files/metadata.json');

async function CriacaoTabela() {
  try {
    const db = await ConexaoBD();
    const { table } = metadata;
    await db.query(`DROP TABLE IF EXISTS DATA;`);
    
    const tableColumns = Object.keys(table).map((columnName) => `${columnName} INT`);
    const createTableSQL = `
      CREATE TABLE IF NOT EXISTS DATA (
        ${tableColumns.join(', ')}
      );
    `;
    await db.query(createTableSQL);

    const columnNames = Object.keys(table).join(', ');
    const insertInitialValuesSQL = `
      INSERT INTO DATA (${columnNames})
      VALUES 
        ${table.id.map((id, index) => `(${Object.values(table).map((column) => column[index]).join(', ')})`).join(', ')}
    `;

    await db.query(insertInitialValuesSQL);
  } catch (error) {
    console.error('Erro para criar tabela: ', error);
  }
}
module.exports = CriacaoTabela;