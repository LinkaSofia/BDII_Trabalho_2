import json
from scripts.Conexao import conexao

def cria_tabela_insere_dados():
    try:
        connection = conexao()
        cursor = connection.cursor()
        
        with open("./scripts/Files/metadata.json", "r") as metadata_arquivo:
            metadata = json.load(metadata_arquivo)

        drop_table = f"DROP TABLE IF EXISTS data"
        cursor.execute(drop_table)

        columns = [f"{col} INTEGER" for col in metadata["table"].keys()]
        create_table = f"CREATE TABLE data ({', '.join(columns)});"
        cursor.execute(create_table)

        # Obtém os nomes das colunas da tabela.
        column_names = ", ".join(metadata["table"].keys())

        # Pega os valores do arquivo JSON e insere no banco.
        values = ", ".join([f"({', '.join(map(str, row))})" for row in zip(*metadata["table"].values())])
        insert_initial_values_query = f"INSERT INTO data ({column_names}) VALUES {values};"
        cursor.execute(insert_initial_values_query)
        connection.commit()

        cursor.close()
        connection.close()

    except Exception as e:
        print("Erro: ", e)
