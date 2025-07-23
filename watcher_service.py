import os
import time
import sqlite3
from ftplib import FTP, error_perm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import threading

# Define o caminho para o banco de dados
DATABASE = os.path.join(os.path.dirname(__file__), 'instance', 'configs.db')

def get_all_configs():
    """Busca TODAS as configurações de sites e suas pastas associadas do banco de dados SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Busca todos os sites
        sites = cursor.execute('SELECT * FROM sites').fetchall()
        
        # Para cada site, busca suas pastas associadas
        all_configs = []
        for site in sites:
            folders = cursor.execute('SELECT * FROM folders WHERE site_id = ?', (site['id'],)).fetchall()
            for folder in folders:
                # Combina as informações do site e da pasta em uma única configuração para o handler
                config = {
                    'site_id': site['id'],
                    'site_name': site['name'],
                    'ftp_host': site['ftp_host'],
                    'ftp_user': site['ftp_user'],
                    'ftp_password': site['ftp_password'],
                    'ftp_port': site['ftp_port'],
                    'folder_id': folder['id'],
                    'local_path': folder['local_path'],
                    'remote_path': folder['remote_path']
                }
                all_configs.append(config)
        return all_configs
    except Exception as e:
        print(f"Erro ao carregar configurações do DB: {e}", file=sys.stderr)
        return []
    finally:
        if conn:
            conn.close()

class FTPEventHandler(FileSystemEventHandler):
    """Manipulador de eventos do sistema de arquivos para uploads FTP."""
    def __init__(self, config):
        if not config:
            raise ValueError("As configurações não foram carregadas ou estão vazias.")
        self.site_id = config['site_id']
        self.site_name = config['site_name']
        self.folder_id = config['folder_id']
        self.ftp_host = config['ftp_host']
        self.ftp_user = config['ftp_user']
        self.ftp_password = config['ftp_password']
        self.ftp_port = config['ftp_port']
        self.local_path = config['local_path']
        self.remote_path = config['remote_path']
        print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Monitorando: '{self.local_path}' para '{self.ftp_host}{self.remote_path}'")

    def connect_ftp(self):
        """Tenta conectar e logar no servidor FTP."""
        try:
            ftp = FTP()
            ftp.connect(self.ftp_host, self.ftp_port, timeout=10)
            ftp.login(self.ftp_user, self.ftp_password)
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Conectado ao FTP: {self.ftp_host}")
            return ftp
        except Exception as e:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Erro ao conectar ou logar no FTP: {e}", file=sys.stderr)
            return None

    def upload_file(self, event_path):
        """Faz o upload de um arquivo para o servidor FTP."""
        if not os.path.isfile(event_path):
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] '{event_path}' não é um arquivo válido ou foi excluído. Pulando upload.", file=sys.stderr)
            return

        file_name = os.path.basename(event_path)
        try:
            relative_path = os.path.relpath(event_path, self.local_path)
        except ValueError:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Atenção: '{event_path}' não está dentro da pasta monitorada '{self.local_path}'. Pulando.", file=sys.stderr)
            return

        remote_full_path = os.path.join(self.remote_path, relative_path).replace("\\", "/")
        remote_dir = os.path.dirname(remote_full_path)
        
        ftp = None
        try:
            ftp = self.connect_ftp()
            if ftp:
                self.create_remote_directories(ftp, remote_dir)
                
                with open(event_path, 'rb') as fp:
                    print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Iniciando upload de: '{event_path}' para '{remote_full_path}'...")
                    ftp.storbinary(f'STOR {remote_full_path}', fp)
                    print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Upload de '{file_name}' concluído com sucesso para '{remote_full_path}'.")
        except error_perm as e:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Erro de permissão FTP ao fazer upload de '{file_name}': {e}. Verifique as permissões no servidor.", file=sys.stderr)
        except Exception as e:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Erro ao fazer upload de '{file_name}': {e}", file=sys.stderr)
        finally:
            if ftp:
                try:
                    ftp.quit()
                    print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Conexão FTP fechada.")
                except Exception as e:
                    print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Erro ao fechar conexão FTP: {e}", file=sys.stderr)

    def create_remote_directories(self, ftp, remote_path):
        """Cria recursivamente diretórios no servidor FTP se não existirem."""
        if not remote_path or remote_path == '/' or remote_path == '.':
            return

        try:
            ftp.cwd('/')
        except error_perm as e:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Não foi possível mudar para o diretório raiz ('/'): {e}. Verifique permissões.", file=sys.stderr)
            pass

        parts = remote_path.split('/')
        for part in parts:
            if part:
                try:
                    ftp.mkd(part)
                    print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Diretório remoto '{part}' criado.")
                except error_perm as e:
                    if "File exists" in str(e) or "directory exists" in str(e).lower() or "exist" in str(e).lower():
                        pass
                    else:
                        raise e
                finally:
                    try:
                        ftp.cwd(part)
                    except error_perm as e:
                        print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Erro ao mudar para o diretório '{part}': {e}. Verifique as permissões no servidor.", file=sys.stderr)
                        raise e

    def on_created(self, event):
        if not event.is_directory:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Arquivo criado: {event.src_path}")
            threading.Thread(target=self.upload_file, args=(event.src_path,)).start()

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Arquivo modificado: {event.src_path}")
            threading.Thread(target=self.upload_file, args=(event.src_path,)).start()

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"[{self.site_name} - Pasta ID:{self.folder_id}] Arquivo excluído: {event.src_path}")
            # Lógica opcional para exclusão remota, se necessário.

# --- Função Principal do Serviço ---
def main():
    """Função principal para iniciar o serviço de monitoramento para todas as pastas cadastradas."""
    all_configs = get_all_configs()

    if not all_configs:
        print("Nenhuma configuração de monitoramento (site e pasta) encontrada no banco de dados. Por favor, configure via interface web primeiro.", file=sys.stderr)
        sys.exit(1)

    observers = []
    
    for config in all_configs:
        local_path = config['local_path']
        site_name = config['site_name']
        folder_id = config['folder_id']
        
        if not os.path.isdir(local_path):
            print(f"[{site_name} - Pasta ID:{folder_id}] Erro: A pasta local '{local_path}' não existe. Ignorando esta configuração.", file=sys.stderr)
            continue

        try:
            event_handler = FTPEventHandler(config)
            observer = Observer()
            observer.schedule(event_handler, local_path, recursive=True)
            observers.append(observer)
            print(f"[{site_name} - Pasta ID:{folder_id}] Monitoramento agendado para '{local_path}'.")
        except ValueError as e:
            print(f"[{site_name} - Pasta ID:{folder_id}] Erro ao inicializar o monitor de arquivos: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[{site_name} - Pasta ID:{folder_id}] Erro inesperado ao configurar o monitor: {e}", file=sys.stderr)

    if not observers:
        print("Nenhum monitoramento foi iniciado devido a erros nas configurações ou pastas inexistentes. Verifique as configurações.", file=sys.stderr)
        sys.exit(1)

    for observer in observers:
        observer.start()

    print("\nTodos os monitoramentos iniciados. Pressione Ctrl+C para parar.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupção detectada. Parando todos os monitoramentos...")
    except Exception as e:
        print(f"Erro inesperado no loop principal do serviço: {e}", file=sys.stderr)
    finally:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
        print("Todos os monitoramentos parados.")

if __name__ == "__main__":
    main()