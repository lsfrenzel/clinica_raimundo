# 🚀 Como Fazer Deploy no Railway

## ✅ O Que Foi Configurado

O sistema agora possui **migração automática completa** que cria:

- ✅ Todas as tabelas do banco de dados
- ✅ 9 especialidades médicas
- ✅ 5 médicos especializados (cada especialidade tem pelo menos 1 médico)
- ✅ Agenda para os próximos 30 dias
- ✅ Usuário administrador

## 📋 Distribuição de Médicos por Especialidade

Após o deploy, cada especialidade terá médicos:

1. **DIU e Implanon** → Dr. Raimundo Nunes, Dra. Maria Santos
2. **Pré-Natal de Alto Risco** → Dr. Raimundo Nunes, Dra. Patrícia Lima  
3. **Hipertensão e Diabetes Gestacional** → Dr. Raimundo Nunes
4. **Mastologia** → Dra. Ana Carolina Silva, Dra. Maria Santos
5. **Uroginecologia** → Dra. Ana Carolina Silva, Dra. Patrícia Lima
6. **Climatério e Menopausa** → Dr. Ricardo Mendes
7. **PTGI** → Dr. Ricardo Mendes
8. **Sexualidade** → Dra. Ana Carolina Silva
9. **Reprodução Humana** → Dr. Ricardo Mendes

## 🔄 Como Fazer o Deploy

### Opção 1: Push para GitHub (Recomendado)

Se o Railway está conectado ao GitHub:

```bash
git add .
git commit -m "Adicionar migração automática completa"
git push
```

O Railway detectará automaticamente e fará o deploy.

### Opção 2: Deploy Manual via Railway CLI

Se você tem o Railway CLI instalado:

```bash
railway up
```

### Opção 3: Redeploy no Dashboard

1. Acesse https://railway.app
2. Vá no seu projeto
3. Clique no serviço
4. Clique em **"Deploy"** ou **"Redeploy"**

## 📊 O Que Acontece Durante o Deploy

1. Railway faz build do projeto
2. **Executa automaticamente** `python scripts/auto_migrate.py`
3. O script cria:
   - Tabelas do banco
   - 9 especialidades
   - 5 médicos com múltiplas especialidades
   - Agenda dos médicos
   - Usuário admin
4. Inicia o gunicorn
5. Aplicação fica disponível

## 🔍 Verificar se Funcionou

Após o deploy, verifique nos **logs do Railway**:

```
🚀 SISTEMA DE MIGRATION AUTOMÁTICO - RAILWAY
✅ Tabelas criadas/atualizadas com sucesso!
📋 Criando especialidades...
✅ 9 especialidades criadas
👨‍⚕️ Criando médicos...
✅ 5 médicos criados
📅 Criando agenda dos médicos...
✅ [número] slots de agenda criados
✅ BANCO POPULADO COM SUCESSO!
```

## 🔑 Credenciais de Acesso

Após o deploy:

- **Email:** admin@clinicadrraimundonunes.com.br
- **Senha:** admin123
- **URL:** https://seu-app.railway.app/auth/login

## 🌐 Testar o Sistema

1. Acesse: `https://seu-app.railway.app/appointments/agendar`
2. Clique em qualquer especialidade
3. Você deverá ver os médicos disponíveis com horários

## ⚠️ Importante

- A migração roda **automaticamente** a cada deploy
- Se o banco já tiver dados, ele NÃO recria (evita duplicação)
- O script sempre garante que o admin existe com a senha correta

## 🐛 Troubleshooting

### Problema: Médicos não aparecem

**Verifique os logs do Railway:**
- Procure por erros durante a migration
- Confirme que vê "✅ 5 médicos criados"

### Problema: "Migration failed"

**Possíveis causas:**
- DATABASE_URL não configurado → Configure no Railway
- Erro de conexão com banco → Verifique o PostgreSQL

### Problema: Admin não consegue logar

**Solução:** O script reseta automaticamente a senha para `admin123` a cada deploy.

---

## ✅ Resumo

1. Faça **git push** ou **redeploy no Railway**
2. Aguarde o deploy completar (2-3 minutos)
3. Verifique os logs
4. Acesse o app e teste o agendamento

**Tudo será criado automaticamente!** 🎉
