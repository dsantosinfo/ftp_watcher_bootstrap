# FTP Watcher Avançado

## Visão Geral

O **FTP Watcher Avançado** é uma aplicação Python com interface web (Flask) que permite monitorar múltiplas pastas locais e fazer upload automático de arquivos alterados ou novos para diferentes destinos FTP. É ideal para sincronizar conteúdos como plugins e temas de WordPress, ou qualquer outro projeto que exija a replicação de arquivos locais para um servidor remoto de forma contínua.

A aplicação é dividida em duas partes principais:
1.  **Interface Web (Flask):** Para gerenciar os dados de conexão FTP (sites) e as pastas locais a serem monitoradas, com seus respectivos destinos remotos. As configurações são salvas em um banco de dados SQLite.
2.  **Serviço de Monitoramento (`watcher_service.py`):** Roda em segundo plano, monitorando as pastas configuradas e realizando os uploads automáticos via FTP quando detecta alterações (criação ou modificação de arquivos/subpastas).

## Funcionalidades

* **Gerenciamento de Múltiplos Sites:** Cadastre diversos destinos FTP (sites) com seus respectivos hosts, credenciais e portas.
* **Gerenciamento de Múltiplas Pastas por Site:** Para cada site cadastrado, associe várias pastas locais para monitoramento, cada uma com seu próprio caminho de destino no servidor FTP.
* **Upload Automático:** Detecta criação e modificação de arquivos e subpastas e os envia para o destino FTP correspondente.
* **Sincronização de Estrutura:** Mantém a estrutura de subdiretórios no servidor FTP.
* **Interface Web Amigável (Bootstrap):** Facilita a configuração e gerenciamento através do navegador.
* **Banco de Dados SQLite:** Armazena todas as configurações de forma persistente.

## Estrutura do Projeto
ftp_watcher_advanced/
├── app.py                      # Aplicação Flask (interface web)
├── config_db.py                # Script de inicialização do banco de dados
├── watcher_service.py          # Serviço de monitoramento e upload
├── instance/                   # Contém o banco de dados
│   └── configs.db              # Banco de dados SQLite
├── templates/                  # Templates HTML do Flask
│   ├── base.html               # Layout base com Bootstrap
│   ├── sites/                  # Templates relacionados ao gerenciamento de sites
│   │   ├── index.html
│   │   └── add_edit.html
│   └── folders/                # Templates relacionados ao gerenciamento de pastas
│       ├── index.html
│       └── add_edit.html
└── static/                     # Arquivos estáticos (CSS, JS)
└── css/
└── custom.css          # CSS personalizado (opcional)
## Instalação

Siga os passos abaixo para configurar e rodar o projeto:

1.  **Clone o Repositório (ou crie a estrutura de pastas):**
    Crie a pasta raiz `ftp_watcher_advanced` e dentro dela as subpastas `instance`, `templates/sites`, `templates/folders` e `static/css`. Salve todos os arquivos nos seus respectivos locais conforme a estrutura acima.

2.  **Instale as Dependências:**
    Abra seu terminal na pasta raiz do projeto (`ftp_watcher_advanced/`) e execute:
    ```bash
    pip install Flask watchdog
    ```

3.  **Inicialize o Banco de Dados:**
    Ainda no terminal, dentro da pasta `ftp_watcher_advanced/`, execute:
    ```bash
    python config_db.py
    ```
    *Se você já rodou o projeto antes, **delete o arquivo `configs.db`** que está em `ftp_watcher_advanced/instance/` antes de executar este comando, para garantir que as tabelas sejam criadas corretamente.*

## Como Usar

A aplicação é composta por duas partes que devem ser executadas separadamente:

1.  **Inicie a Interface Web (Flask):**
    Abra o **primeiro terminal** na pasta `ftp_watcher_advanced/` e execute:
    ```bash
    python app.py
    ```
    Acesse a interface no seu navegador, geralmente em `http://127.0.0.1:5000/`. Use esta interface para cadastrar e gerenciar seus sites e as pastas locais que você deseja monitorar.

2.  **Inicie o Serviço de Monitoramento (`watcher_service.py`):**
    Após configurar seus sites e pastas na interface web, abra um **segundo terminal** na pasta `ftp_watcher_advanced/` e execute:
    ```bash
    python watcher_service.py
    ```
    Este terminal mostrará os logs do monitoramento e dos uploads. Ele continuará rodando em segundo plano, observando suas pastas e enviando arquivos automaticamente. **Este serviço deve estar sempre ativo para que os uploads ocorram.**

## Observações Importantes e Melhorias Futuras

* **Segurança da Senha:** Atualmente, as senhas FTP são armazenadas em **texto simples** no banco de dados SQLite. Isso **não é seguro para ambientes de produção**. Recomenda-se fortemente a implementação de criptografia de senha (ex: usando `cryptography.Fernet`) para proteger as credenciais.
* **FTP Seguro (FTPS/SFTP):** A conexão FTP padrão não é criptografada. Para maior segurança, considere usar FTPS (FTP sobre SSL/TLS) com `ftplib` ou SFTP (SSH File Transfer Protocol) com uma biblioteca como `paramiko`.
* **Exclusão Remota:** A aplicação não exclui arquivos no servidor FTP quando são removidos localmente. Esta funcionalidade pode ser implementada, mas deve ser avaliada com cautela devido aos riscos de perda de dados acidental.
* **Gerenciamento de Erros e Logs:** Para uso em produção, um sistema de logging mais robusto (ex: para arquivos) e a capacidade de re-tentar uploads falhos seriam benéficos.
* **Implantação em Produção:** Para rodar a aplicação em um servidor de forma contínua, utilize um servidor WSGI para o Flask (ex: Gunicorn, uWSGI) e gerencie o `watcher_service.py` como um serviço do sistema (ex: `systemd` no Linux, `NSSM` no Windows).

---

## Licença

Este projeto é de código aberto. (Adicione sua licença preferida, ex: MIT, Apache 2.0, etc.)
