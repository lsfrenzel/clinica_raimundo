# 🚂 Guia de Deploy no Railway

Este guia mostra como fazer deploy da Clínica Dr. Raimundo Nunes no Railway com PostgreSQL.

## ✅ Sistema de Migração Automática Configurado

O projeto possui **migração automática** que roda a cada deploy:
- ✅ Cria/atualiza todas as tabelas do banco automaticamente
- ✅ Garante que o usuário admin existe e está funcional  
- ✅ Reseta senha do admin se necessário (sempre será: admin123)
- ✅ Roda automaticamente antes do gunicorn iniciar

**Como funciona:**
```toml
# nixpacks.toml
[start]
cmd = "python scripts/auto_migrate.py && gunicorn --bind 0.0.0.0:$PORT main:app"
```

**Vantagens:**
- ✅ Deploy simples - apenas push para GitHub
- ✅ Sem comandos manuais
- ✅ Admin sempre disponível: `admin@clinicadrraimundonunes.com.br` / `admin123`
- ✅ Banco sempre atualizado

**Ver detalhes em:** `MIGRATION_AUTOMATICA.md`

## 📋 Pré-requisitos

- Conta no [Railway](https://railway.app) (gratuita)
- Conta no GitHub
- Código do projeto versionado no GitHub

## 🚀 Método 1: Deploy via GitHub (Recomendado)

### 1. Preparar o Repositório

Certifique-se de que seu projeto tem os seguintes arquivos (já inclusos):
- ✅ `requirements.txt` - Dependências Python
- ✅ `nixpacks.toml` - Configuração de build do Railway
- ✅ `main.py` - Aplicação Flask configurada

### 2. Push para o GitHub

```bash
git add .
git commit -m "Preparar para deploy no Railway"
git push origin main
```

### 3. Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha o repositório do projeto
5. Clique em **"Deploy Now"**

### 4. Adicionar PostgreSQL

1. No dashboard do projeto, clique em **"+ New"**
2. Selecione **"Database"** → **"Add PostgreSQL"**
3. O Railway cria automaticamente a variável `DATABASE_URL`

### 5. Configurar Variáveis de Ambiente

No painel do serviço Flask, vá em **Variables** e adicione:

```env
SESSION_SECRET=sua-chave-secreta-aqui
GEMINI_API_KEY=sua-chave-gemini-aqui (opcional)
```

**⚠️ SESSION_SECRET é OBRIGATÓRIO** - Para gerar uma chave segura:
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Ou use um gerador online: https://randomkeygen.com/
```

**Importante:** O Railway já configura automaticamente:
- `DATABASE_URL` - Conexão com PostgreSQL
- `PORT` - Porta do servidor

### 6. Verificar Migração Automática

A migração roda automaticamente! Verifique nos logs:

1. No Railway dashboard → Deployments → View Logs
2. Procure por:
```
🚀 SISTEMA DE MIGRATION AUTOMÁTICO
✅ Tabelas criadas/atualizadas com sucesso!
✅ Admin criado com sucesso!
```

3. Faça login:
   - URL: `https://seu-app.railway.app/auth/login`
   - Email: `admin@clinicadrraimundonunes.com.br`
   - Senha: `admin123`

**Opcional - Popular com dados de exemplo:**
```bash
# Via Railway CLI
railway run python scripts/seed_data.py
```

### 7. Gerar Domínio Público

1. Vá em **Settings** → **Networking**
2. Clique em **"Generate Domain"**
3. Seu app estará disponível em `https://xxx.up.railway.app`

## 🛠️ Método 2: Deploy via Railway CLI

```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Inicializar projeto
railway init

# 4. Adicionar PostgreSQL
railway add -d postgres

# 5. Deploy
railway up

# 6. Abrir no navegador
railway open
```

## 🔧 Configuração de Variáveis de Ambiente

### Variáveis Automáticas (Railway)
```env
DATABASE_URL=postgresql://user:pass@host:port/db
PORT=3000
```

### Variáveis Necessárias (Configurar Manualmente)
```env
SESSION_SECRET=<gere uma chave aleatória forte>
GEMINI_API_KEY=<sua chave da API Gemini> (opcional)
```

### Variáveis Opcionais
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
MAIL_DEFAULT_SENDER=noreply@clinica.com.br
```

## 📊 Estrutura do Banco de Dados

O Railway criará automaticamente o PostgreSQL. Para popular:

```bash
# Método 1: Via Railway CLI
railway run python scripts/seed_data.py

# Método 2: Conectar localmente
export DATABASE_URL="<railway_database_url>"
python scripts/seed_data.py
```

### Dados Criados Automaticamente
- ✅ 9 especialidades médicas
- ✅ 5 médicos da equipe
- ✅ 448 slots de agenda (30 dias)
- ✅ 5 pacientes exemplo
- ✅ 10 agendamentos exemplo
- ✅ 1 usuário administrador

### Credenciais Padrão (Desenvolvimento)
```
Admin: admin@clinicadrraimundonunes.com.br / admin123
Médicos: [email] / medico123
Pacientes: [email] / paciente123
```

## 🔍 Monitoramento e Logs

### Ver Logs em Tempo Real
```bash
# Via CLI
railway logs

# Ou no dashboard: Clique no serviço → View Logs
```

### Comandos Úteis
```bash
# Status do deploy
railway status

# Variáveis de ambiente
railway variables

# Abrir dashboard
railway open

# SSH no container
railway shell
```

## 🐛 Troubleshooting

### Erro: "Internal Server Error" nas páginas de login/cadastro
**Causa:** SESSION_SECRET não configurado
**Solução:** 
1. No Railway dashboard → seu serviço → Variables
2. Adicione a variável `SESSION_SECRET` com uma chave segura:
```bash
# Gere uma chave segura com:
python -c "import secrets; print(secrets.token_hex(32))"
```
3. Cole o resultado em SESSION_SECRET
4. Aguarde o redeploy automático

**Nota:** O app gera uma chave temporária se SESSION_SECRET não existir, mas **isso é inseguro** e as sessões não persistem entre restarts.

### Erro: "Application failed to respond"
**Causa:** Comando de start incorreto
**Solução:** Verifique o `nixpacks.toml`:
```toml
[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT main:app"
```

### Erro: "Database connection failed"
**Causa:** DATABASE_URL não configurado
**Solução:** 
1. Verifique se o PostgreSQL está adicionado ao projeto
2. No serviço Flask → Variables → Verifique se `DATABASE_URL` existe
3. Se não, adicione referência ao database nas configurações

### Erro: "Module not found"
**Causa:** Dependência faltando no requirements.txt
**Solução:**
```bash
# Regenerar requirements.txt
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "Atualizar dependências"
git push
```

### Tabelas não criadas
**Causa:** Seed não executado
**Solução:**
```bash
railway run python scripts/seed_data.py
```

## 💰 Custos e Planos

### Trial Plan (Gratuito)
- $5 de crédito por mês
- Ideal para desenvolvimento e testes
- Requer conta GitHub (90+ dias)

### Hobby Plan
- Baseado em uso (CPU, memória, storage)
- ~$5-20/mês para apps pequenos/médios
- Escalável conforme necessidade

## 📚 Recursos Adicionais

- [Documentação Railway](https://docs.railway.com)
- [Guia Flask Railway](https://docs.railway.com/guides/flask)
- [PostgreSQL Railway](https://docs.railway.com/guides/postgresql)
- [Community Forum](https://help.railway.app)

## ✅ Checklist de Deploy

- [ ] Código no GitHub
- [ ] Projeto criado no Railway
- [ ] PostgreSQL adicionado
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados populado (seed)
- [ ] Domínio gerado
- [ ] Aplicação acessível
- [ ] Chatbot funcionando
- [ ] Agendamentos testados

## 🔐 Segurança em Produção

**Importante para produção:**

1. **Alterar senhas padrão** do seed_data.py
2. **Usar senhas fortes** para SESSION_SECRET
3. **Configurar HTTPS** (Railway faz automaticamente)
4. **Ativar CSRF protection** (já configurado)
5. **Configurar CORS** adequadamente para seu domínio
6. **Backup regular** do banco de dados

---

**🎉 Pronto!** Seu sistema de gestão médica agora está rodando no Railway com PostgreSQL!
