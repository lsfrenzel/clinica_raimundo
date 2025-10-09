# 📚 Índice - Deploy Railway e População do Banco de Dados

## 🚀 Comece Aqui!

### Para iniciantes:
👉 **[GUIA_RAILWAY_SIMPLES.md](GUIA_RAILWAY_SIMPLES.md)** ⭐ RECOMENDADO
- Passo a passo super simples
- Sem complicações técnicas
- 5 minutos de leitura

---

## 📖 Documentação Completa

### 1. Deploy no Railway
- 📄 **[README_RAILWAY.md](README_RAILWAY.md)** - Guia completo de deploy
- ✅ **[VERIFICACAO_RAPIDA.md](VERIFICACAO_RAPIDA.md)** - Checklist e verificação

### 2. População do Banco de Dados
- 🗄️ **[COMO_POPULAR_BANCO_RAILWAY.md](COMO_POPULAR_BANCO_RAILWAY.md)** - Guia detalhado de população

### 3. Projeto Geral
- 📋 **[replit.md](replit.md)** - Documentação completa do projeto

---

## ⚡ Resposta Rápida

### "Como popular o banco no Railway?"

**Resposta: É AUTOMÁTICO!** 

Quando você faz push para o Railway:
1. O arquivo `nixpacks.toml` é lido
2. O script `scripts/auto_migrate.py` é executado automaticamente
3. O banco é populado com:
   - 9 especialidades
   - 1 administrador
   - 5 médicos
   - 990 slots de agenda

### "E se não funcionar automaticamente?"

Execute manualmente:
```bash
railway run python popular_railway.py
```

Ou use o script de verificação:
```bash
railway run bash railway_deploy_check.sh
```

---

## 🔑 Credenciais Padrão

Após o deploy, use para login:

**Administrador:**
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

**Médicos:** (senha: `medico123`)
- `raimundo.nunes@clinicadrraimundonunes.com.br`
- `ana.silva@clinicadrraimundonunes.com.br`
- `carlos.oliveira@clinicadrraimundonunes.com.br`
- `maria.santos@clinicadrraimundonunes.com.br`
- `ricardo.mendes@clinicadrraimundonunes.com.br`

---

## 🛠️ Arquivos Técnicos

### Scripts:
- `scripts/auto_migrate.py` - População automática (roda no deploy)
- `popular_railway.py` - População manual
- `railway_deploy_check.sh` - Verificação do banco

### Configuração:
- `nixpacks.toml` - Configuração do Railway
- `requirements.txt` - Dependências Python
- `models.py` - Schema do banco de dados

---

## 📊 Fluxo de Deploy

```
git push
    ↓
Railway detecta nixpacks.toml
    ↓
Instala requirements.txt
    ↓
Executa auto_migrate.py ← POPULA O BANCO AQUI!
    ↓
Inicia gunicorn
    ↓
✅ App no ar com banco populado!
```

---

## ❓ FAQ

**P: O banco é populado automaticamente?**
R: Sim! Via `auto_migrate.py` no primeiro deploy.

**P: Posso rodar várias vezes?**
R: Sim! O script é idempotente (não duplica dados).

**P: E se eu quiser resetar o banco?**
R: Use o painel do Railway para resetar o PostgreSQL e faça um novo deploy.

**P: Como verificar se funcionou?**
R: Veja os logs do deploy no Railway. Deve aparecer "✅ BANCO POPULADO COM SUCESSO!"

---

## 🎯 Próximos Passos

1. Leia: **[GUIA_RAILWAY_SIMPLES.md](GUIA_RAILWAY_SIMPLES.md)**
2. Configure o PostgreSQL no Railway
3. Adicione a variável `SESSION_SECRET`
4. Faça o push
5. Verifique os logs
6. Faça login como admin

**Pronto!** 🎊

---

**Última atualização:** 09/10/2025
