import psycopg2
# biblioteca para ler o arquivo env.ini
import configparser

def conexao():
    try:
        config = configparser.ConfigParser()
        config.read('env.ini')
        postgresql_config = config['postgresql']

        # Extraia as configurações de conexão.
        user = postgresql_config['user']
        host = postgresql_config['host']
        database = postgresql_config['database']
        password = postgresql_config['password']
        port = postgresql_config['port']
        # Cria a conexão
        connection = psycopg2.connect(
            user=user,
            host=host,
            database=database,
            password=password,
            port=port
        )
        return connection

    except (psycopg2.Error, Exception) as error:
        print("Erro na conexão:", error)
        raise error