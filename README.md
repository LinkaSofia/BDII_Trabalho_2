# Trabalho Prático - LOG <br>

Objetivo: implementar o mecanismo de log Undo com checkpoint usando o SGBD 

## Funcionamento: 
O código, que poderá utilizar qualquer linguagem de programação, deverá ser capaz de ler o arquivo de log (entradaLog) e o arquivo de Metadado e validar as informações no banco de dados através do modelo UNDO. 

O código receberá como entrada o arquivo de metadados (dados salvos) e os dados da tabela que irá operar no banco de dados. 

Exemplo de tabela do banco de dados: 

  ID  |  A  |  B
 ---- | --- | ---
  1   |  20 | 55
  2   |  20 | 30

### Arquivo de Metadado (json): 
```
	{  "table": {
		“id”:[1,2],
		"A": [20,20],
		"B": [55,30]
	  }
	}
```
Arquivo de log no formato <transação, “id da tupla”,”coluna”, “valor antigo”>. 

### Exemplo:
Arquivo de Log: 
```
<start T1>
<T1,1, A,20>
<start T2>
<commit T1>
<START CKPT(T2)>
<T2,2, B,20>	
<commit T2>
<END CKPT>
<start T3>
<start T4>
<T4,1, B,55>
```

Saída: 
```
“Transação T3 realizou UNDO”
“Transação T4 realizou UNDO”

Imprima o valor das variáveis, exemplo:
{  "table": {
	"A": [500,20],
	"B": [20,30]
  }
} * 500 e 30 são os novos valores
```

## Detalhes:
### Funções a serem implementadas:
- Carregar o banco de dados com a tabela antes de executar o código do log (para zerar as configurações e dados parciais). Notem que a tabela pode ter um número diferente de colunas e linhas. 
- Carregar o arquivo de log;
- Verifique quais transações devem realizar UNDO. Imprimir o nome das transações que irão sofrer Undo. 
- Checar quais valores estão salvos nas tabelas (com o select) e atualizar valores inconsistentes (update);
- Reportar quais dados foram atualizados;
- Seguir o fluxo de execução conforme o método de UNDO, conforme visto em aula; 

### Execução:
- Pode ser implementado em duplas;
- A nota será individual;
- Deve ser enviado o repositório no GIT (será avaliado a participação dos membros através dos commits). Um único commit com o código pronto será entendido como uma cópia e receberá nota zero.  Os commits irão interferir na nota final dos membros da dupla;
- Poderá ser testado com outro arquivo de log a execução do programa;
