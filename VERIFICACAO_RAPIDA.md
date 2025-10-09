# ✅ Verificação Rápida - Railway Deploy

## Para garantir que o banco de dados seja populado no Railway:

### 1️⃣ Antes do Deploy

Verifique se estes arquivos estão no repositório:

- ✅ `nixpacks.toml` - Configuração do Railway
- ✅ `scripts/auto_migrate.py` - Script de população automática
- ✅ `popular_railway.py` - Script de população manual
- ✅ `requirements.txt` - Dependências Python

### 2️⃣ No Railway Dashboard

1. **Adicione o PostgreSQL:**
   - Vá em "+ New" → "Database" → "PostgreSQL"
   - O Railway cria automaticamente a variável `DATABASE_URL`

2. **Configure variáveis de ambiente:**
   ```
   SESSION_SECRET=cole-uma-chave-aleatoria-aqui
   ```
   (Você pode gerar uma chave com: `python -c "import secrets; print(secrets.token_hex(32))"`)

3. **Conecte o repositório:**
   - "+ New" → "GitHub Repo" → Selecione este repo

### 3️⃣ Faça o Push

```bash
git add .
git commit -m "Deploy para Railway"
git push
```

### 4️⃣ Monitore o Deploy

No Railway:
1. Vá em "Deployments"
2. Clique no deploy mais recente
3. Clique em "View Logs"

**Procure por estas mensagens nos logs:**
```
🚀 SISTEMA DE MIGRATION AUTOMÁTICO - RAILWAY
============================================================
📦 Criando/atualizando tabelas no banco...
✅ Tabelas criadas/atualizadas com sucesso!

📝 Banco vazio - Populando com dados iniciais...

✅ BANCO POPULADO COM SUCESSO!
============================================================

📊 DADOS CRIADOS:
   • Especialidades: 9
   • Médicos: 5
   • Agenda: 990 slots
```

### 5️⃣ Teste o Sistema

1. Acesse a URL do seu app no Railway (ex: `https://seu-app.up.railway.app`)
2. Vá para `/auth/login`
3. Tente fazer login:
   - Email: `admin@clinicadrraimundonunes.com.br`
   - Senha: `admin123`

Se o login funcionar, **o banco foi populado com sucesso!** 🎉

---

## 🚨 Se o banco estiver vazio:

### Opção A: Via Railway CLI

```bash
# Instale o Railway CLI
npm i -g @railway/cli

# Faça login
railway login

# Selecione o projeto
railway link

# Execute o script
railway run python popular_railway.py
```

### Opção B: Via Railway Dashboard

1. No Railway, vá em seu projeto
2. Clique em "Settings" → "Service Variables"
3. Verifique se `DATABASE_URL` está configurado
4. Use o botão "Deploy" para forçar um novo deploy

### Opção C: Script de Verificação

Execute o script de verificação:

```bash
railway run bash railway_deploy_check.sh
```

---

## 📋 Checklist Final

- [ ] PostgreSQL adicionado no Railway
- [ ] `DATABASE_URL` configurado automaticamente
- [ ] `SESSION_SECRET` configurado manualmente
- [ ] Repositório conectado ao Railway
- [ ] Push realizado
- [ ] Logs mostram "BANCO POPULADO COM SUCESSO"
- [ ] Login do admin funciona
- [ ] Especialidades aparecem no sistema
- [ ] Médicos aparecem no sistema
- [ ] Agendamentos funcionam

---

## 🎯 Resumo do que acontece automaticamente:

Quando você faz push para o Railway:

1. Railway detecta o `nixpacks.toml`
2. Instala as dependências do `requirements.txt`
3. **Executa `python scripts/auto_migrate.py`** ← Aqui o banco é populado!
4. Inicia o servidor com `gunicorn`

O script `auto_migrate.py`:
- Cria todas as tabelas
- Verifica se o banco está vazio
- Se vazio: popula com dados iniciais
- Se já tem dados: apenas garante que o admin existe

---

**Pronto!** Agora você tem certeza de que o banco será populado. 🚀

Se ainda tiver problemas, execute manualmente:
```bash
railway run python popular_railway.py
```
