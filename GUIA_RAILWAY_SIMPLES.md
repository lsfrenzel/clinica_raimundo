# 🚀 Guia Simples - Deploy no Railway com Banco Populado

## 📝 O que você precisa saber:

**O banco de dados será populado AUTOMATICAMENTE quando você fizer o deploy no Railway!** ✨

---

## 🎯 Passos Simples:

### 1. No Railway:

1. **Crie um projeto novo**
2. **Adicione PostgreSQL:**
   - Clique "+ New"
   - Escolha "Database"
   - Selecione "PostgreSQL"
   
3. **Conecte este repositório:**
   - Clique "+ New"
   - Escolha "GitHub Repo"
   - Selecione este repositório

4. **Adicione a variável de ambiente:**
   - Vá em "Variables"
   - Adicione: `SESSION_SECRET` = qualquer texto aleatório

### 2. No seu computador:

```bash
git add .
git commit -m "Deploy para Railway"
git push
```

### 3. Aguarde o deploy:

O Railway vai:
1. ✅ Instalar as dependências
2. ✅ **POPULAR O BANCO AUTOMATICAMENTE** (via `auto_migrate.py`)
3. ✅ Iniciar o servidor

### 4. Verifique nos logs:

Você deve ver:
```
✅ BANCO POPULADO COM SUCESSO!
📊 DADOS CRIADOS:
   • Especialidades: 9
   • Médicos: 5
   • Agenda: 990 slots
```

### 5. Teste:

Acesse seu app e faça login:
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

---

## ⚡ Como funciona a mágica?

O arquivo `nixpacks.toml` tem esta linha:

```toml
cmd = "python scripts/auto_migrate.py && gunicorn --bind 0.0.0.0:$PORT ..."
```

Isso significa:
1. Primeiro roda `auto_migrate.py` (popula o banco)
2. Depois inicia o servidor

**É automático!** Você não precisa fazer nada. 🎉

---

## 🚨 E se o banco não for populado?

Se por algum motivo não funcionar automaticamente, execute manualmente:

```bash
# Instale o Railway CLI
npm i -g @railway/cli

# Faça login
railway login

# Conecte ao projeto
railway link

# Execute o script
railway run python popular_railway.py
```

---

## 📚 Mais informações?

- **Guia completo**: `README_RAILWAY.md`
- **Detalhes técnicos**: `COMO_POPULAR_BANCO_RAILWAY.md`
- **Checklist**: `VERIFICACAO_RAPIDA.md`

---

## ✅ Resumo:

1. Adicione PostgreSQL no Railway ✓
2. Conecte o repositório ✓
3. Configure `SESSION_SECRET` ✓
4. Faça push ✓
5. **O banco é populado automaticamente!** ✓

**Pronto!** 🎊
