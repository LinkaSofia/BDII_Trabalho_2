import re
from scripts.Conexao import conexao

# Define expressões regulares para cada tipo de linha
# Transações no formato: <start T1>
rx_start = r"<start T\d+>"
# Transações no formato: <T1,1,A,11>
rx_transacao = r"<T\d+,\d+, .+,\d+>"
# Transações no formato: <commit T1>
rx_commit = r"<commit T\d+>"
# Transações no formato: <START CKPT (T1)>
rx_ckpt = r"<START CKPT\(T\d+\)>"
rx_end_ckpt = r"<END CKPT>"

in_checkpoint = False
committed = False
committed_transactions = set()
pending_transactions = []
uncommitted_starts = []
active_transactions = []
transaction_changes = {}
undo_list = []
queries_pending = []

# Tira caracteres não numéricos
def clean_value(value):
    return ''.join(filter(str.isdigit, value))

def LeituraLog():
    try:
        connection = conexao()
        cursor = connection.cursor()
        log_file = open("./scripts/Files/entradaLog.txt", "r", encoding="utf-8")
        log_lines = log_file.readlines()
        log_lines.reverse()

        # Verifica estado inicial da tabela no banco
        cursor.execute("SELECT * FROM data;")
        results = cursor.fetchall()
        print("Valores iniciais: ")
        for row in results:
            print(row)
        print('\n')

        # Percorre o arquivo de log e processa com base nas expressões regulares
        for line in log_lines:
            if re.search(rx_transacao, line):
                transaction = re.search(r"<T(\d+),", line).group(1)
                commit_found = any(re.search(rx_commit, l) and f"T{transaction}" in l for l in log_lines)
                start_found = any(re.search(rx_start, l) and f"T{transaction}" in l for l in log_lines)

                if not commit_found and transaction not in committed_transactions:
                    pending_transactions.append(line)
                    committed_transactions.add(transaction)

            elif re.search(rx_start, line):
                transaction = re.search(r"<start T(\d+)>", line).group(1)
                commit_found = any(re.search(rx_commit, l) and f"T{transaction}" in l for l in log_lines)
                transaction_found = any(re.search(rx_transacao, l) and f"T{transaction}" in l for l in log_lines)
                if not commit_found and not transaction_found and transaction not in committed_transactions:
                    uncommitted_starts.append(line)
                    committed_transactions.add(transaction)

            elif re.search(rx_ckpt, line) and in_checkpoint:
                break
            elif re.search(rx_end_ckpt, line):
                in_checkpoint = True
            else:
                continue

        for index in uncommitted_starts:
            transaction = re.search(r'<start (T\d+)>', index).group(1)
            transaction_number = re.search(r'T(\d+)', transaction).group(1)
            undo_list.append(transaction_number)
            print("Transação {} realizou UNDO".format(transaction))

        for index in pending_transactions:
            values = re.search(r"<.+>", index).group(0).replace("<", "").replace(">", "").split(", ")[1:]
            try:
                cursor.execute(f"UPDATE data SET {values[1]} = {values[2]} WHERE id = {values[0]};")
                cursor.commit()
                transaction = re.search(r'<T(\d+),', index).group(1)
                change = "UPDATE data SET {} = {} WHERE id = {};".format(values[1], values[2], values[0])
                transaction_changes.setdefault(transaction, []).append(change)

            except Exception as error:
                print("Erro ao realizar UNDO:", error)

        with open("./scripts/Files/entradaLog.txt", 'r') as file:
            for line in file:
                parts = line.strip().split(',')

                match = re.search(r"<start T(\d+)>", line)
                if match:
                    transaction = int(match.group(1))
                    active_transactions.append(transaction)
                # Verifica se tem 4 partes (<T1,1,A,20>)
                if len(parts) == 4:
                    transaction, identifier, name, value = parts
                    cleaned_value = clean_value(value)
                    if name == 'A':
                        column = 'a'
                    elif name == 'B':
                        column = 'b'
                    else:
                        continue

                    transaction1 = int(re.search(r'T(\d+)', line).group(1))
                    # Cria uma tupla com as informações da transação atual (número da transação, coluna, valor númerico e identificador)
                    queries_pending.append((transaction1, column, cleaned_value, identifier))

        undo_list2 = [int(x) for x in undo_list]

        for transaction1, column, cleaned_value, identifier in queries_pending:
            query_sql = f"SELECT {column} FROM data WHERE id = %s"
            cursor.execute(query_sql, (identifier,))
            result = cursor.fetchone()

            if result is not None:
                original_value = result[0]
                
                if transaction1 not in active_transactions:
                    print('Transação ignorada T', transaction1, '\n')

                if transaction1 in active_transactions:
                    query_sql = f"UPDATE data SET {column} = %s WHERE id = %s"
                    cursor.execute(query_sql, (cleaned_value, identifier))

                if transaction1 in transaction_changes:
                    transaction_changes[transaction1].append(f"alterou id {identifier} coluna {column} para {cleaned_value}")
                else:
                    transaction_changes[transaction1] = [f"alterou id {identifier} coluna {column} para {cleaned_value}"]

                if transaction1 in undo_list2:
                    query_sql = f"UPDATE data SET {column} = %s WHERE id = %s"
                    cursor.execute(query_sql, (original_value, identifier))

        updated_values = set()
        for transaction, changes in transaction_changes.items():
            for change in changes:
                value = re.search(r"para (\d+)", change).group(1)
                updated_values.add(value)

        updated_values = ', '.join(updated_values)
        print('\n')
        print(f"{updated_values} são os novos valores")

        cursor.execute("SELECT * FROM data;")
        print('\n')

        results = cursor.fetchall()
        print("Valores finais: ")
        for row in results:
            print(row)

        connection.commit()
        cursor.close()
        connection.close()

    except Exception as error:
        print("Erro:", error)

