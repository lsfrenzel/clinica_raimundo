# 🚀 Sistema de Migração Automática

## ✅ Como Funciona

O projeto **já possui migração automática** configurada! Quando você faz deploy no Railway, o sistema automaticamente:

1. ✅ Cria/atualiza todas as tabelas do banco de dados
2. ✅ Verifica se o usuário admin existe
3. ✅ Cria o admin se não existir (email: `admin@clinicadrraimundonunes.com.br`, senha: `admin123`)
4. ✅ Reseta a senha do admin para `admin123` se necessário
5. ✅ Garante que o admin está ativo

**Isso acontece automaticamente a cada deploy!**

## 📋 Configuração Atual

### nixpacks.toml
```toml
[start]
cmd = "python scripts/auto_migrate.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app"
```

O Railway executa `auto_migrate.py` **antes** de iniciar o gunicorn. Se a migration falhar, o app não inicia.

## 🔧 Como Fazer Deploy

### 1. Push para GitHub
```bash
git add .
git commit -m "Sistema com migração automática"
git push
```

### 2. Railway Detecta e Faz Redeploy
- O Railway detecta o `nixpacks.toml`
- Executa `python scripts/auto_migrate.py`
- Inicia o gunicorn após migração bem-sucedida

### 3. Verificar Logs do Railway
No dashboard do Railway:
1. Clique no seu serviço
2. Vá em **"Deployments"**
3. Clique no último deployment
4. Veja os logs - você deve ver:
```
🚀 SISTEMA DE MIGRATION AUTOMÁTICO
✅ Tabelas criadas/atualizadas com sucesso!
✅ Admin criado com sucesso!
✨ Migration completa!
```

## 🔑 Credenciais do Admin

Após o deploy automático:
- **Email:** `admin@clinicadrraimundonunes.com.br`
- **Senha:** `admin123`
- **URL Login:** `https://seu-app.railway.app/auth/login`

## 🐛 Troubleshooting

### Problema: Admin não foi criado
**Causa:** Migration falhou ou não executou
**Solução:**
1. Verifique os logs do Railway
2. Procure por erros no `auto_migrate.py`
3. Verifique se `DATABASE_URL` está configurado
4. Tente fazer redeploy manual

### Problema: "relation 'users' does not exist"
**Causa:** Migration não rodou
**Solução:**
1. Verifique se o `nixpacks.toml` está no root do projeto
2. Force um redeploy no Railway
3. Verifique os logs de build

### Problema: Migration roda mas admin não funciona
**Causa:** Erro no hash da senha
**Solução:** O sistema já tenta resetar automaticamente. Se persistir:
```bash
railway run python scripts/fix_railway_admin.py
```

## ✅ Vantagens da Migração Automática

- ✅ Não precisa executar scripts manualmente
- ✅ Não precisa acessar endpoints especiais
- ✅ Admin sempre disponível
- ✅ Banco sempre atualizado
- ✅ Zero configuração manual

## 📊 O Que é Criado Automaticamente

**Apenas:**
- Todas as tabelas do banco
- 1 usuário administrador

**Não cria:**
- Especialidades (use `scripts/seed_data.py` se precisar)
- Médicos (use `scripts/seed_data.py` se precisar)
- Agendamentos de exemplo

## 💡 Dados de Demonstração (Opcional)

Se quiser popular com dados de exemplo (especialidades, médicos, etc):

```bash
# Via Railway CLI
railway run python scripts/seed_data.py
```

Isso vai criar:
- 9 especialidades
- 5 médicos
- 5 pacientes
- Agenda para 30 dias
- 10 agendamentos de exemplo

---

## 🎯 Resumo

**O sistema de migração automática já está funcionando!** 

Basta fazer push para o GitHub que o Railway:
1. Detecta as mudanças
2. Faz build
3. Roda migration automática
4. Inicia o app

**Credenciais sempre serão:**
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

⚠️ **Lembre-se:** Altere a senha do admin após o primeiro login em produção!
