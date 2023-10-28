from scripts.Conexao import conexao

# Definindo as expressoões regulares para cada tipo de linha
# Transações no formato: <start T1>
rx_start = r"<start T\d+>"
# Transações no formato: <T1,1,A,11>
rx_transacao = r"<T\d+,\d+, .+,\d+>"
# Transações no formato: <commit T1>
rx_commit = r"<commit T\d+>"
# Transações no formato: <START CKPT (T1)>
rx_ckpt = r"<START CKPT\(T\d+\)>"
rx_end_ckpt = r"<END CKPT>"
