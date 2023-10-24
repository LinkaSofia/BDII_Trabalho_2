const ConexaoBD = require('./Conexao');

async function Print() {
  const db = await ConexaoBD();
  const { rows } = await db.query('SELECT a, b FROM data ORDER BY id;');
  const formattedData = {
    A: [],
    B: []
  };

  rows.forEach(row => {
    formattedData.A.push(row.a);
    formattedData.B.push(row.b);
  });

  const allValues = [];

  for (const columnName in formattedData) {
    allValues.push(formattedData[columnName]);
  }

  const formattedOutput = allValues.join(', ');

  console.log(`${formattedOutput} são os novos valores`);

  await db.end();
}

module.exports = Print;
