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
# <T1,1,A,20>
pending_transactions = []
# <start T1>
uncommitted_starts = []
active_transactions = []
transaction_changes = {}
undo_list = []
queries_pending = []

log = "./scripts/Files/entradaLog.txt"

def LeituraLog():
    try:
        connection = conexao()
        cursor = connection.cursor()
        
        log_file = open(log, "r", encoding="utf-8")
        # Lê linha a linha de baixo para cima
        log_lines = log_file.readlines()
        log_lines.reverse()

        # Imprime estado inicial da tabela no banco
        cursor.execute("SELECT * FROM data;")
        results = cursor.fetchall()
        print("-------------------")
        print("Valores iniciais: ")
        for row in results:
            print(row)
        print("-------------------")
        print('\n')

        # Percorre o arquivo de log, linha a linha e processa com base nas expressões regulares
        for line in log_lines:
            # Se a linha corresponde a uma transação 
            if re.search(rx_transacao, line):
                # Extrai o numero da transação
                transaction = re.search(r"<T(\d+),", line).group(1)
                # Verifica se alguma linha corresponde a um commit, de uma transação específica
                # o for percorre todas as linhas e verifica se para essa transação tem commit 
                commit_found = any(re.search(rx_commit, l) and f"T{transaction}" in l for l in log_lines)
                # Se não encontrar nenhum commit para a transação e se a transação não estiver na lista de transações com commit
                if not commit_found and transaction not in committed_transactions:
                    # transação pendente aguardando confirmação
                    pending_transactions.append(line)
                    # O identificador da transação é adicionado à lista committed_transactions para rastrear que a transação foi considerada.
                    committed_transactions.add(transaction)
            # Se a linha não corresponde a uma transação (<T1,1,A,20>) e deu start e não deu commit, salva em uncommitted_starts
            elif re.search(rx_start, line):
                # Extrai o numero da transação
                transaction = re.search(r"<start T(\d+)>", line).group(1)
                commit_found = any(re.search(rx_commit, l) and f"T{transaction}" in l for l in log_lines)
                # Verifica se a transação foi encontrada em alguma linha do arquivo
                transaction_found = any(re.search(rx_transacao, l) and f"T{transaction}" in l for l in log_lines)
                # Se a transação não foi confirmada e não foi encontrada em outras linhas do arquivo, é adicionada ás transações não confirmadas
                if not commit_found and not transaction_found and transaction not in committed_transactions:
                    # Não econtrou start
                    uncommitted_starts.append(line)
                    # Transação Considerada
                    committed_transactions.add(transaction)

            elif re.search(rx_ckpt, line) and in_checkpoint:
                break
            elif re.search(rx_end_ckpt, line):
                in_checkpoint = True
            else:
                continue

        # Percorre as transações que não foram confirmadas
        for index in uncommitted_starts:
            transaction = re.search(r'<start (T\d+)>', index).group(1)
            transaction_number = re.search(r'T(\d+)', transaction).group(1)
            undo_list.append(transaction_number)
            print("-------------------")
            print("Transação {} realizou UNDO".format(transaction))
            
        print("-------------------")

        # Percorre toda a lista pendente de confirmação
        for index in pending_transactions:
            # Procura por um padrão que inicie com "<", quando encontra, remove os caracteres "<" e ">" e divide as informações com ","
            values = re.search(r"<.+>", index).group(0).replace("<", "").replace(">", "").split(", ")[1:]
            try:
                # Atualiza o banco com as informações de values
                cursor.execute(f"UPDATE data SET {values[1]} = {values[2]} WHERE id = {values[0]};")
                cursor.commit()
                # Extrai o número da transação
                transaction = re.search(r'<T(\d+),', index).group(1)
                change = "UPDATE data SET {} = {} WHERE id = {};".format(values[1], values[2], values[0])
                # rastreia todas as alterações feitas nas transações, associando o número da transação com as alterações realizadas 
                transaction_changes.setdefault(transaction, []).append(change)

            except Exception as error:
                print("Erro ao realizar UNDO:", error)

        with open(log, 'r') as file:
            for line in file:
                # Divide a linha com "," e retira os espaços em branco
                parts = line.strip().split(',')
                match = re.search(r"<start T(\d+)>", line)
                if match:
                    # Extrai o número da transação
                    transaction = int(match.group(1))
                    # Adiciona o número da transação na lista de transações ativas
                    active_transactions.append(transaction)
                # Verifica se tem 4 partes (<T1,1,A,20>)
                if len(parts) == 4:
                    transaction, identifier, name, num = parts
                    # Tira caracteres não numéricos da quarta parte
                    value = num.replace(">", "")
                    if name == 'A': column = 'a'
                    elif name == 'B': column = 'b'
                    else:
                        continue

                    transaction1 = int(re.search(r'T(\d+)', line).group(1))
                    # Cria uma tupla com as informações da transação atual (número da transação, coluna, valor e identificador)
                    # Informações para atualizar o bd
                    queries_pending.append((transaction1, column, value, identifier))

        # Percorre a lista de transações pendentes
        for transaction1, column, cleaned_value, identifier in queries_pending:
            # Lê o valor atual da coluna no bd
            query_sql = f"SELECT {column} FROM data WHERE id = %s"
            cursor.execute(query_sql, (identifier,))
            result = cursor.fetchone()

            # Se a consult não retornou nulo
            if result is not None:
                # Armazena o valor original do bd
                original_value = result[0]
                # Verifica se a transação está ativa, atualiza o banco com o novo valor - cleaned_value
                if transaction1 in active_transactions:
                    query_sql = f"UPDATE data SET {column} = %s WHERE id = %s"
                    cursor.execute(query_sql, (cleaned_value, identifier))

                if transaction1 not in active_transactions:
                    print('Transação não ativa T', transaction1, '\n')
                # Registra a alteração
                if transaction1 in transaction_changes:
                    transaction_changes[transaction1].append(f"Alterou o id {identifier} coluna {column} para o valor {cleaned_value}")
                else:
                    transaction_changes[transaction1] = [f"Alterou o id {identifier} coluna {column} para o valor {cleaned_value}"]
                # Verifica se a transação precisa ser desfeita, se precisar, atualiza o valor do banco com o valor inicial do banco
                if transaction1 in undo_list:
                    query_sql = f"UPDATE data SET {column} = %s WHERE id = %s"
                    cursor.execute(query_sql, (original_value, identifier))
        # para guardar os novos valores resultantes das alterações nas transações, através do "para o valor"
        updated_values = set()
        for transaction, changes in transaction_changes.items():
            for change in changes:
                value = re.search(r"para o valor (\d+)", change).group(1)
                updated_values.add(value)

        updated_values = ', '.join(updated_values)
        print('\n')
        print("-------------------")
        print(f"{updated_values} são os novos valores")
        print("-------------------")

        cursor.execute("SELECT * FROM data;")
        print('\n')

        results = cursor.fetchall()
        print("-------------------")
        print("Valores finais: ")
        for row in results:
            print(row)
        print("-------------------")

        connection.commit()
        cursor.close()
        connection.close()

    except Exception as error:
        print("Erro:", error)

