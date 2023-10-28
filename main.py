from scripts.Conexao import conexao
from scripts.CriacaoTabela import cria_tabela_insere_dados
from scripts.LeituraLog import LeituraLog


def main():
  try:
    connection = conexao()
    #Desabilita transações implicitas (sem begin, end, commit)
    connection.autocommit = True
    cria_tabela_insere_dados()
    LeituraLog()

  except Exception as error:
    print("Erro:", error)
  finally:
    if connection and not connection.closed:
      connection.close()

if __name__ == "__main__":
  main()

