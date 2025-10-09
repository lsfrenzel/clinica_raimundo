# 🚂 Deploy no Railway - Clínica Dr. Raimundo Nunes

## 🚀 Como fazer o deploy

### Passo 1: Preparar o Railway

1. Crie uma conta no [Railway](https://railway.app/)
2. Crie um novo projeto
3. Adicione um banco de dados PostgreSQL:
   - Clique em "+ New"
   - Selecione "Database"
   - Escolha "PostgreSQL"

### Passo 2: Conectar seu repositório

1. No Railway, clique em "+ New"
2. Selecione "GitHub Repo"
3. Escolha este repositório
4. O Railway detectará automaticamente que é um projeto Python

### Passo 3: Configurar variáveis de ambiente

O Railway já cria automaticamente a variável `DATABASE_URL` quando você adiciona o PostgreSQL.

**Variáveis adicionais necessárias:**

```
SESSION_SECRET=sua-chave-secreta-aleatoria-aqui
```

**Opcional (para email):**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
MAIL_DEFAULT_SENDER=noreply@clinicadrraimundonunes.com.br
```

### Passo 4: Deploy

1. Faça commit de todas as alterações:
   ```bash
   git add .
   git commit -m "Deploy para Railway"
   git push
   ```

2. O Railway iniciará o deploy automaticamente
3. **O banco de dados será populado automaticamente!** 🎉

### Passo 5: Verificar

1. Veja os logs do deploy no Railway
2. Procure por:
   ```
   ✅ BANCO POPULADO COM SUCESSO!
   📊 DADOS CRIADOS:
      • Especialidades: 9
      • Médicos: 5
      • Agenda: 990 slots
   ```

3. Acesse sua aplicação e faça login:
   - Email: `admin@clinicadrraimundonunes.com.br`
   - Senha: `admin123`

---

## 🗄️ O que acontece automaticamente no deploy:

1. **Instalação de dependências** (requirements.txt)
2. **Criação das tabelas** do banco de dados
3. **População automática** com dados iniciais:
   - 9 especialidades médicas
   - 1 administrador
   - 5 médicos
   - 990 slots de agenda (próximos 30 dias)

Isso é feito pelo arquivo `nixpacks.toml` que executa:
```bash
python scripts/auto_migrate.py && gunicorn ...
```

---

## 🔧 Se o banco não foi populado:

Execute manualmente no terminal do Railway:

```bash
railway run python popular_railway.py
```

Ou use o script de verificação:

```bash
railway run bash railway_deploy_check.sh
```

---

## 📋 Checklist de Deploy:

- [ ] Repositório conectado ao Railway
- [ ] Banco PostgreSQL adicionado ao projeto
- [ ] Variável `DATABASE_URL` configurada (automática)
- [ ] Variável `SESSION_SECRET` configurada (manual)
- [ ] Deploy realizado com sucesso
- [ ] Logs mostram "BANCO POPULADO COM SUCESSO"
- [ ] Login do admin funciona

---

## 🔑 Credenciais Padrão:

### Admin:
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

### Médicos (senha: `medico123`):
- `raimundo.nunes@clinicadrraimundonunes.com.br`
- `ana.silva@clinicadrraimundonunes.com.br`
- `carlos.oliveira@clinicadrraimundonunes.com.br`
- `maria.santos@clinicadrraimundonunes.com.br`
- `ricardo.mendes@clinicadrraimundonunes.com.br`

---

## ⚠️ IMPORTANTE: Segurança

Após o primeiro login, **ALTERE IMEDIATAMENTE**:

1. Senha do administrador
2. Senhas dos médicos
3. Chave `SESSION_SECRET` para uma mais forte

---

## 📞 Suporte

Se tiver problemas:

1. Verifique os logs do Railway
2. Execute: `railway run python popular_railway.py`
3. Consulte: `COMO_POPULAR_BANCO_RAILWAY.md`

---

**Pronto!** Sua clínica está no ar! 🎉
