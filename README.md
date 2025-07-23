# FTP Watcher Avançado

## 📋 Visão Geral

O **FTP Watcher Avançado** é uma solução completa para sincronização automática de arquivos locais com servidores FTP. Desenvolvido em Python com interface web Flask, oferece monitoramento em tempo real de múltiplas pastas e upload automático para diferentes destinos FTP.

### ✨ Principais Características

- **🔄 Sincronização Automática**: Upload instantâneo de arquivos novos ou modificados
- **🌐 Múltiplos Sites FTP**: Gerencie diversos servidores FTP simultaneamente
- **📁 Múltiplas Pastas**: Configure várias pastas por site com destinos específicos
- **🎨 Interface Web Intuitiva**: Gerenciamento completo via navegador com Bootstrap
- **🗃️ Banco de Dados SQLite**: Configurações persistentes e confiáveis
- **📊 Logs em Tempo Real**: Monitoramento detalhado das operações

### 🎯 Casos de Uso Ideais

- Sincronização de plugins e temas WordPress
- Deploy automático de aplicações web
- Backup contínuo de projetos
- Sincronização de documentos e assets

## 🏗️ Arquitetura

A aplicação é composta por dois módulos principais:

1. **Interface Web (Flask)**: Gerenciamento de configurações via navegador
2. **Serviço de Monitoramento**: Processo em background para uploads automáticos

## 📁 Estrutura do Projeto

```
ftp_watcher_advanced/
├── app.py                    # Aplicação Flask principal
├── config_db.py              # Inicializador do banco de dados
├── watcher_service.py        # Serviço de monitoramento
├── instance/
│   └── configs.db           # Banco de dados SQLite
├── templates/
│   ├── base.html            # Layout base Bootstrap
│   ├── sites/               # Templates de gerenciamento de sites
│   │   ├── index.html
│   │   └── add_edit.html
│   └── folders/             # Templates de gerenciamento de pastas
│       ├── index.html
│       └── add_edit.html
└── static/
    └── css/
        └── custom.css       # Estilos personalizados
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone ou crie a estrutura do projeto**
   ```bash
   mkdir ftp_watcher_advanced
   cd ftp_watcher_advanced
   ```

2. **Instale as dependências**
   ```bash
   pip install Flask watchdog
   ```

3. **Inicialize o banco de dados**
   ```bash
   python config_db.py
   ```
   
   > ⚠️ **Nota**: Se já executou o projeto anteriormente, delete o arquivo `instance/configs.db` antes de executar este comando.

## 💻 Como Usar

### 1. Inicie a Interface Web

Abra o primeiro terminal e execute:

```bash
python app.py
```

Acesse `http://127.0.0.1:5000` no seu navegador para configurar:
- Sites FTP (hosts, credenciais, portas)
- Pastas locais para monitoramento
- Destinos remotos correspondentes

### 2. Inicie o Serviço de Monitoramento

Em um segundo terminal, execute:

```bash
python watcher_service.py
```

Este processo:
- Monitora continuamente as pastas configuradas
- Realiza uploads automáticos quando detecta alterações
- Exibe logs detalhados das operações
- **Deve permanecer ativo** para funcionamento contínuo

## 📝 Configuração Típica

1. **Cadastre um Site FTP**:
   - Host: `seu-servidor.com`
   - Usuário: `seu_usuario`
   - Senha: `sua_senha`
   - Porta: `21` (padrão)

2. **Configure uma Pasta Local**:
   - Caminho Local: `/home/usuario/projeto`
   - Destino Remoto: `/public_html/projeto`
   - Site: Selecione o site cadastrado

3. **Inicie o monitoramento** e veja os uploads acontecerem automaticamente!

## ⚠️ Considerações de Segurança

### Limitações Atuais
- **Senhas em texto simples**: Armazenadas sem criptografia no SQLite
- **FTP não criptografado**: Conexões sem SSL/TLS por padrão
- **Sem autenticação**: Interface web sem controle de acesso

### Recomendações para Produção
- Implementar criptografia de senhas (ex: `cryptography.Fernet`)
- Usar FTPS/SFTP para conexões seguras
- Adicionar autenticação à interface web
- Configurar HTTPS com certificados SSL

## 🔧 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] Exclusão remota de arquivos deletados localmente
- [ ] Sistema de logs para arquivos
- [ ] Re-tentativa automática para uploads falhos
- [ ] Filtros de arquivos por extensão
- [ ] Notificações via email/webhook
- [ ] Dashboard com estatísticas

### Produção
- [ ] Suporte a WSGI (Gunicorn, uWSGI)
- [ ] Serviços do sistema (systemd, NSSM)
- [ ] Docker containerization
- [ ] Monitoramento de performance

## 🐛 Solução de Problemas

### Problemas Comuns

**Erro de conexão FTP**
- Verifique host, porta e credenciais
- Teste conectividade de rede
- Confirme se o servidor aceita conexões FTP

**Arquivos não sendo detectados**
- Verifique permissões da pasta local
- Confirme se o serviço de monitoramento está ativo
- Verifique logs para mensagens de erro

**Interface web não carrega**
- Confirme se o Flask está rodando na porta correta
- Verifique se há conflitos de porta
- Teste em `localhost:5000`

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma [issue](https://github.com/seu-usuario/ftp-watcher-advanced/issues)
- Consulte a documentação completa
- Entre em contato via email

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**