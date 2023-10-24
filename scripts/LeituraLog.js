const fs = require("fs");
const ConexaoBD = require("./Conexao");

// Expressões regulares
const erStart = /<start T\d+>/;
const erTransacao = /<T\d+,\d+, .+,\d+>/;
const erCommit = /<commit T\d+>/;

const StartSCommitESTransacao = [];
const TransacaoSCommit = [];
const transacoesJaImpressas = new Set(); 

async function LerLog() {
  const log = fs.readFileSync("./Files/entradaLog.txt", "utf-8");
  const logArray = log.split("\n");
  logArray.reverse();

  for (const linha of logArray) {
    if (erTransacao.test(linha)) {
      const transacao = linha.match(/<T(\d+),/)[1]; 
      const commitEncontrado = logArray.some(
        (l) => erCommit.test(l) && l.includes(`T${transacao}`)
      );
      if (!commitEncontrado && !transacoesJaImpressas.has(transacao)) {
        TransacaoSCommit.push(linha);
        transacoesJaImpressas.add(transacao); 
      }
    } else if (erStart.test(linha)) {
      const transacao = linha.match(/<start T(\d+)>/)[1]; 
      const commitEncontrado = logArray.some(
        (l) => erCommit.test(l) && l.includes(`T${transacao}`)
      );
      const transacaoEncontrada = logArray.some(
        (l) => erTransacao.test(l) && l.includes(`T${transacao}`)
      );
      if (
        !commitEncontrado &&
        !transacaoEncontrada &&
        !transacoesJaImpressas.has(transacao)
      ) {
        StartSCommitESTransacao.push(linha);
        transacoesJaImpressas.add(transacao); 
      }
    } else {
      continue;
    }
  }

  for (const index of StartSCommitESTransacao) {
    console.log(`Transação ${index.match(/<start (T\d+)>/)[1]} realizou UNDO`);
  }
  for (const index of TransacaoSCommit) {
    const valores = index
      .match(/<.+>/)[0]
      .match(/[^<>, ]+/g)
      .slice(1);
    try {
      const db = await ConexaoBD();
      // UNDO
      const undo = `UPDATE DATA SET ${valores[1]} = ${valores[2]} WHERE id = ${valores[0]};`;
      await db.query(undo);
      console.log(`Transação T${index.match(/<T(\d+),/)[1]} realizou UNDO`);
    } catch (error) {
      console.error("Erro ao realizar UNDO:", error);
    }
  }
}

module.exports = LerLog;
