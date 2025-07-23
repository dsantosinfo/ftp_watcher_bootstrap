import sqlite3
import os

# Define o caminho para o banco de dados dentro da subpasta 'instance'
DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'configs.db')

def init_db():
    """Inicializa o banco de dados e cria as tabelas 'sites' e 'folders' se não existirem."""
    # Garante que o diretório 'instance' exista antes de tentar criar o DB
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Tabela para os sites (destinos FTP)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE, -- Nome descritivo para o site (ex: "Meu Site Principal")
                ftp_host TEXT NOT NULL,
                ftp_user TEXT NOT NULL,
                ftp_password TEXT NOT NULL, -- ATENÇÃO: Senha armazenada em texto simples (para simplicidade, mas NÃO recomendado para produção)
                ftp_port INTEGER DEFAULT 21
            )
        ''')

        # Tabela para as pastas (origens de monitoramento), relacionadas a um site
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL, -- Chave estrangeira para a tabela 'sites'
                local_path TEXT NOT NULL UNIQUE, -- Caminho local da pasta a ser monitorada
                remote_path TEXT NOT NULL, -- Caminho de destino no servidor FTP
                FOREIGN KEY (site_id) REFERENCES sites (id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        print(f"Banco de dados SQLite inicializado/verificado em: {DATABASE}")
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()