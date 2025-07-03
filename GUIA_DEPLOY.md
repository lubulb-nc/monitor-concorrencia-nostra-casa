# Guia de Deploy - Sistema de Monitoramento da Concorrência

## 📋 Visão Geral

Este guia fornece instruções detalhadas para colocar o Sistema de Monitoramento da Concorrência Imobiliária em produção usando plataformas de hospedagem gratuitas. O sistema foi desenvolvido com Flask (backend) e HTML/JavaScript (frontend) integrados em uma única aplicação.

## 🏗️ Arquitetura do Sistema

O sistema é composto por:
- **Backend Flask**: APIs REST para execução de scrapers e gerenciamento de dados
- **Frontend Web**: Interface responsiva para visualização e controle
- **Banco de Dados SQLite**: Armazenamento de imóveis e histórico de execuções
- **Scrapers**: Módulos para coleta de dados dos sites concorrentes

## 🚀 Opção 1: Deploy no Render.com (Recomendado)

### Pré-requisitos
- Conta no GitHub
- Conta no Render.com (gratuita)
- Repositório Git com o código do projeto

### Passo 1: Preparar o Repositório

1. **Criar repositório no GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Sistema de monitoramento inicial"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/monitor-concorrencia.git
   git push -u origin main
   ```

2. **Estrutura de arquivos necessária**:
   ```
   monitor_backend/
   ├── src/
   │   ├── main.py
   │   ├── models/
   │   ├── routes/
   │   ├── static/
   │   └── scrapers_gerais.py
   ├── requirements.txt
   └── render.yaml
   ```

### Passo 2: Configurar Arquivo render.yaml

Criar arquivo `render.yaml` na raiz do projeto:

```yaml
services:
  - type: web
    name: monitor-concorrencia
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "cd src && python main.py"
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: FLASK_ENV
        value: production
    
  - type: cron
    name: scraper-diario
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "cd src && python -c 'from scrapers_gerais import executar_todos_scrapers; executar_todos_scrapers()'"
    schedule: "0 8 * * *"  # Executa diariamente às 8h
    plan: free
```

### Passo 3: Deploy no Render

1. **Acessar Render.com** e fazer login
2. **Conectar repositório GitHub**:
   - Clique em "New +"
   - Selecione "Blueprint"
   - Conecte sua conta GitHub
   - Selecione o repositório do projeto

3. **Configurar variáveis de ambiente** (se necessário):
   - `FLASK_ENV=production`
   - `PYTHON_VERSION=3.11.0`

4. **Iniciar deploy**:
   - O Render detectará automaticamente o `render.yaml`
   - O deploy será iniciado automaticamente
   - Aguarde a conclusão (5-10 minutos)

### Passo 4: Verificar Deploy

1. **Acessar URL fornecida** pelo Render
2. **Testar funcionalidades**:
   - Interface web carregando
   - Botão de monitoramento funcionando
   - APIs respondendo corretamente

## 🚀 Opção 2: Deploy no Railway.app

### Passo 1: Preparar Projeto

1. **Instalar Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Fazer login**:
   ```bash
   railway login
   ```

### Passo 2: Configurar Projeto

1. **Inicializar projeto Railway**:
   ```bash
   cd monitor_backend
   railway init
   ```

2. **Criar arquivo `railway.json`**:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "cd src && python main.py",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

3. **Configurar variáveis de ambiente**:
   ```bash
   railway variables set FLASK_ENV=production
   railway variables set PORT=5000
   ```

### Passo 3: Deploy

1. **Fazer deploy**:
   ```bash
   railway up
   ```

2. **Gerar domínio público**:
   ```bash
   railway domain
   ```

## 🚀 Opção 3: Deploy no Fly.io

### Passo 1: Instalar Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Passo 2: Configurar Aplicação

1. **Fazer login**:
   ```bash
   flyctl auth login
   ```

2. **Inicializar app**:
   ```bash
   cd monitor_backend
   flyctl launch
   ```

3. **Configurar `fly.toml`**:
   ```toml
   app = "monitor-concorrencia"
   primary_region = "gru"

   [build]
     builder = "paketobuildpacks/builder:base"

   [env]
     FLASK_ENV = "production"
     PORT = "8080"

   [[services]]
     http_checks = []
     internal_port = 8080
     processes = ["app"]
     protocol = "tcp"
     script_checks = []

     [services.concurrency]
       hard_limit = 25
       soft_limit = 20
       type = "connections"

     [[services.ports]]
       force_https = true
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443

     [[services.tcp_checks]]
       grace_period = "1s"
       interval = "15s"
       restart_limit = 0
       timeout = "2s"
   ```

### Passo 3: Deploy

```bash
flyctl deploy
```

## ⚙️ Configurações de Produção

### Variáveis de Ambiente

```bash
# Obrigatórias
FLASK_ENV=production
PORT=5000

# Opcionais
DATABASE_URL=sqlite:///app.db
SECRET_KEY=sua_chave_secreta_aqui
```

### Configuração de Banco de Dados

Para produção, recomenda-se PostgreSQL:

```python
# Em main.py, substituir:
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
    f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
```

### Configuração de Logs

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/monitor.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## 🔄 Configuração de Cron Jobs

### Render.com
Usar o arquivo `render.yaml` com configuração de cron job (já incluído acima).

### Railway.app
Criar serviço separado para cron:
```bash
railway add
# Selecionar "Cron Job"
# Configurar comando: cd src && python -c "from scrapers_gerais import executar_todos_scrapers; executar_todos_scrapers()"
# Configurar schedule: 0 8 * * *
```

### Fly.io
Usar Fly Machines para cron jobs:
```bash
flyctl machine run --schedule="0 8 * * *" --dockerfile=Dockerfile.cron
```

## 📊 Monitoramento e Logs

### Health Check
O sistema inclui endpoint de health check em `/health`:
```json
{
  "status": "ok",
  "service": "Monitor de Concorrência Imobiliária"
}
```

### Logs de Aplicação
- Logs de execução dos scrapers
- Logs de erros e exceções
- Métricas de performance

### Alertas
Configurar alertas para:
- Falhas nos scrapers
- Tempo de resposta elevado
- Erros de banco de dados

## 🔒 Segurança

### Configurações Recomendadas

1. **Variáveis de Ambiente**:
   ```bash
   SECRET_KEY=chave_secreta_complexa
   FLASK_ENV=production
   ```

2. **Headers de Segurança**:
   ```python
   from flask_talisman import Talisman
   Talisman(app)
   ```

3. **Rate Limiting**:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   ```

## 🧪 Testes Antes do Deploy

### Checklist de Pré-Deploy

- [ ] Todas as dependências em `requirements.txt`
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados inicializado
- [ ] Scrapers funcionando localmente
- [ ] Interface web responsiva
- [ ] APIs retornando dados corretos
- [ ] Logs configurados
- [ ] Health check funcionando

### Comandos de Teste Local

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
cd src && python main.py

# Testar APIs
curl http://localhost:5000/health
curl http://localhost:5000/api/monitor/imoveis
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de Importação**:
   - Verificar estrutura de diretórios
   - Confirmar `__init__.py` nos pacotes
   - Verificar imports relativos

2. **Banco de Dados não Criado**:
   - Verificar permissões de escrita
   - Confirmar inicialização do SQLAlchemy
   - Verificar migrations

3. **Scrapers Falhando**:
   - Verificar conectividade de rede
   - Confirmar estrutura dos sites alvo
   - Verificar user-agents e headers

4. **Interface não Carregando**:
   - Verificar arquivos estáticos
   - Confirmar rotas do Flask
   - Verificar CORS configurado

### Logs Úteis

```bash
# Render.com
# Acessar logs pelo dashboard

# Railway.app
railway logs

# Fly.io
flyctl logs
```

## 📈 Escalabilidade

### Otimizações para Crescimento

1. **Banco de Dados**:
   - Migrar para PostgreSQL
   - Implementar índices otimizados
   - Configurar connection pooling

2. **Cache**:
   - Implementar Redis para cache
   - Cache de consultas frequentes
   - Cache de resultados de scrapers

3. **Processamento**:
   - Implementar filas (Celery)
   - Processamento assíncrono
   - Workers dedicados para scrapers

4. **Monitoramento**:
   - Implementar métricas (Prometheus)
   - Dashboards (Grafana)
   - Alertas automatizados

## 💰 Custos e Limites

### Render.com (Plano Gratuito)
- 750 horas/mês de compute
- 1GB PostgreSQL
- SSL gratuito
- Cron jobs inclusos

### Railway.app (Plano Gratuito)
- $5 crédito mensal
- PostgreSQL incluído
- Execução contínua
- Métricas básicas

### Fly.io (Plano Gratuito)
- 3 VMs compartilhadas
- 256MB RAM cada
- PostgreSQL limitado
- Volumes persistentes

## 🔄 Atualizações e Manutenção

### Processo de Atualização

1. **Desenvolvimento Local**:
   ```bash
   git checkout -b feature/nova-funcionalidade
   # Desenvolver e testar
   git commit -m "Nova funcionalidade"
   git push origin feature/nova-funcionalidade
   ```

2. **Deploy Automático**:
   - Merge para branch main
   - Deploy automático ativado
   - Verificar logs de deploy

3. **Rollback se Necessário**:
   ```bash
   # Render.com: usar interface web
   # Railway.app: railway rollback
   # Fly.io: flyctl releases list && flyctl releases rollback
   ```

### Backup e Recuperação

1. **Backup do Banco**:
   ```python
   # Script de backup automático
   import sqlite3
   import datetime
   
   def backup_database():
       timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
       backup_name = f'backup_{timestamp}.db'
       # Implementar backup
   ```

2. **Backup de Configurações**:
   - Variáveis de ambiente documentadas
   - Configurações de deploy versionadas
   - Scripts de inicialização salvos

Este guia fornece uma base sólida para colocar o sistema em produção. Recomenda-se começar com o Render.com devido à sua simplicidade e recursos gratuitos generosos.

