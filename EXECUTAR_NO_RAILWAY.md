# 🚀 Como Executar no Railway

## ✅ SOLUÇÃO: Banco Populado com Sucesso!

O banco de dados do Railway foi populado. Agora você pode fazer login!

## 🔑 Credenciais de Login

**URL:** `https://seu-app.railway.app/auth/login`

**Administrador:**
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

---

## 📋 O Que Foi Feito

✅ Banco de dados Railway conectado e populado
✅ Tabelas criadas
✅ Admin criado/resetado com senha: `admin123`
✅ Especialidades básicas criadas
✅ Sistema de migração automática atualizado

---

## 🔄 Para Garantir que Funcione Sempre

### Opção 1: Migração Automática (Recomendado)

Faça push deste código para o GitHub:

```bash
git add .
git commit -m "Migração automática completa"
git push
```

O Railway vai:
1. Detectar as mudanças
2. Rodar `python scripts/auto_migrate.py`
3. Criar admin + especialidades automaticamente
4. Iniciar o app

### Opção 2: Popular Manualmente (Se Necessário)

Se o banco estiver vazio novamente:

```bash
# Via Railway CLI
railway run python popular_railway.py
```

Isso vai criar:
- ✅ Todas as tabelas
- ✅ Admin (admin@clinicadrraimundonunes.com.br / admin123)
- ✅ 9 especialidades
- ✅ 5 médicos
- ✅ Agenda para 30 dias

---

## 🐛 Troubleshooting

### Login não funciona
1. Verifique se você está usando a URL correta: `/auth/login`
2. Use as credenciais corretas:
   - Email: `admin@clinicadrraimundonunes.com.br`
   - Senha: `admin123`
3. Limpe cookies do navegador

### "Usuário não encontrado"
```bash
# Execute para recriar o admin
railway run python popular_railway.py
```

### Banco vazio após redeploy
- Verifique se o `nixpacks.toml` está correto
- Verifique os logs do Railway: Dashboard → Deployments → View Logs
- Procure por: `✅ Admin criado com sucesso!`

---

## 📊 Scripts Disponíveis

| Script | O Que Faz |
|--------|-----------|
| `scripts/auto_migrate.py` | Migração automática (roda no Railway) |
| `popular_railway.py` | Popular banco completo (manual) |
| `scripts/seed_data.py` | Dados completos de exemplo |
| `scripts/fix_railway_admin.py` | Diagnóstico e correção do admin |

---

## ✅ Próximos Passos

1. ✅ **Fazer login:** `https://seu-app.railway.app/auth/login`
2. ✅ **Alterar senha do admin** após primeiro acesso
3. ✅ **Fazer push para GitHub** para ativar migração automática

**O login agora deve funcionar!** 🎉
