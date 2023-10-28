from scripts.Conexao import conexao
from scripts.CriacaoTabela import cria_tabela_insere_dados
from scripts.LeituraLog import LeituraLog


def main():
    connection = conexao()
    #Desabilita transações implicitas (sem begin, end, commit)
    connection.autocommit = True
    cria_tabela_insere_dados()
    LeituraLog()


if __name__ == "__main__":
  main()

