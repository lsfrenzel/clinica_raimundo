# 🚀 SOLUÇÃO DEFINITIVA - Railway Setup

## ✅ Migração Automática COMPLETA Configurada!

O script `scripts/auto_migrate.py` foi **completamente reescrito** para criar **TODOS os dados automaticamente** quando o Railway iniciar.

### 📦 O Que Será Criado Automaticamente:

✅ **Tabelas:** Todas as 10 tabelas do sistema
✅ **Admin:** 1 administrador (admin@clinicadrraimundonunes.com.br / admin123)
✅ **Especialidades:** 9 especialidades médicas completas
✅ **Médicos:** 5 médicos com suas especialidades
✅ **Agenda:** 448 slots de atendimento (30 dias, seg-sex, 8h-17h)

---

## 🎯 PASSO A PASSO (3 Minutos)

### 1️⃣ Fazer Push para GitHub

```bash
git add .
git commit -m "Migração automática completa - popula todas as tabelas"
git push
```

### 2️⃣ Aguardar Redeploy do Railway

- O Railway detecta automaticamente o push
- Faz build do projeto (1-2 minutos)
- **Executa `python scripts/auto_migrate.py` ANTES de iniciar o gunicorn**
- Popula todas as tabelas automaticamente

### 3️⃣ Verificar Logs do Railway

1. Acesse o Railway Dashboard
2. Vá em **Deployments** → último deployment → **View Logs**
3. Procure por:

```
🚀 SISTEMA DE MIGRATION AUTOMÁTICO - RAILWAY
✅ Tabelas criadas/atualizadas com sucesso!
✅ 9 especialidades criadas
✅ Admin criado - Email: admin@clinicadrraimundonunes.com.br
✅ 5 médicos criados
✅ 448 slots de agenda criados
✅ BANCO POPULADO COM SUCESSO!
```

### 4️⃣ Fazer Login

**URL:** `https://seu-app.railway.app/auth/login`

**Credenciais:**
- **Email:** `admin@clinicadrraimundonunes.com.br`
- **Senha:** `admin123`

---

## 🔄 Como Funciona a Migração Automática

### No Railway (nixpacks.toml):
```bash
python scripts/auto_migrate.py && gunicorn --bind 0.0.0.0:$PORT main:app
```

**Fluxo:**
1. Railway inicia o container
2. **Executa `auto_migrate.py`** primeiro
3. Verifica se banco está vazio
4. Se vazio: popula com todos os dados
5. Se populado: apenas garante que admin existe
6. Inicia gunicorn após migração completa

---

## 📊 Dados Criados Automaticamente

### Admin (1)
- Nome: Administrador
- Email: admin@clinicadrraimundonunes.com.br
- Senha: admin123
- Role: admin
- Status: Ativo

### Especialidades (9)
1. DIU e Implanon
2. Pré-Natal de Alto Risco
3. Hipertensão e Diabetes Gestacional
4. Mastologia
5. Uroginecologia
6. Climatério e Menopausa
7. PTGI
8. Sexualidade
9. Reprodução Humana

### Médicos (5)
| Nome | CRM | Especialidade | Senha |
|------|-----|---------------|-------|
| Dr. Raimundo Nunes | CRM/SP 123456 | Pré-Natal de Alto Risco | medico123 |
| Dra. Ana Silva | CRM/SP 234567 | Mastologia | medico123 |
| Dr. Carlos Oliveira | CRM/SP 345678 | Reprodução Humana | medico123 |
| Dra. Maria Santos | CRM/SP 456789 | Uroginecologia | medico123 |
| Dr. Ricardo Mendes | CRM/SP 567890 | Climatério e Menopausa | medico123 |

### Agenda
- 448 slots de atendimento
- Próximos 30 dias
- Segunda a sexta (pula fins de semana)
- 8h às 17h (1 hora por slot)

---

## 🐛 Troubleshooting

### "Usuário não encontrado" após deploy
**Causa:** Migração não executou
**Solução:**
1. Verifique logs do Railway
2. Procure por erros no auto_migrate.py
3. Force redeploy: Settings → Deployments → Redeploy

### Migração executou mas admin não foi criado
**Causa:** Erro no script
**Solução:**
```bash
# Via Railway CLI
railway run python scripts/auto_migrate.py
```

### Banco continua vazio
**Causa:** `nixpacks.toml` não está sendo usado
**Solução:**
1. Verifique se `nixpacks.toml` está no root
2. Confirme que o conteúdo está correto:
```toml
[phases.setup]
nixPkgs = ['python311']

[start]
cmd = "python scripts/auto_migrate.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app"
```

---

## ✅ Checklist de Verificação

Após fazer push, verifique:

- [ ] Railway detectou o push
- [ ] Build completou com sucesso
- [ ] Logs mostram "BANCO POPULADO COM SUCESSO!"
- [ ] Consegue fazer login com admin@clinicadrraimundonunes.com.br
- [ ] Dashboard admin está acessível
- [ ] Especialidades aparecem no sistema

---

## 🔐 Segurança

Após primeiro login:
1. ✅ Altere a senha do admin
2. ✅ Delete a senha padrão dos médicos se não forem usados
3. ✅ Configure SESSION_SECRET no Railway se ainda não configurou

---

## 💡 Importante

- A migração automática **roda a cada deploy**
- Se o banco já estiver populado, apenas verifica o admin
- Se o banco estiver vazio, popula tudo automaticamente
- **Não precisa executar nada manualmente!**

---

**🎉 Agora é só fazer push e aguardar! O Railway faz o resto automaticamente!**
