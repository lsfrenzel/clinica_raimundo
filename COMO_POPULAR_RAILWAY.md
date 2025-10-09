# 🚀 Como Popular o Banco de Dados do Railway

O banco de dados do Railway está vazio. Você precisa executar o script `seed_data.py` no Railway para criar o usuário admin e todos os dados iniciais.

## ✅ MÉTODO 1: Via Railway CLI (Mais Fácil)

### Passo 1: Instalar Railway CLI
```bash
npm i -g @railway/cli
```

### Passo 2: Fazer Login
```bash
railway login
```

### Passo 3: Conectar ao Projeto
```bash
railway link
```
Selecione o projeto da clínica quando aparecer a lista.

### Passo 4: Popular o Banco
```bash
railway run python scripts/seed_data.py
```

**Pronto!** O banco será populado e você poderá fazer login com:
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

---

## ✅ MÉTODO 2: Executar Localmente Conectado ao Railway

### Passo 1: Copiar a DATABASE_URL do Railway
1. Acesse o dashboard do Railway
2. Vá em **PostgreSQL** → **Variables** → **DATABASE_URL**
3. Copie o valor completo (começa com `postgresql://`)

### Passo 2: Executar o Script
No seu terminal local (ou Replit):
```bash
export DATABASE_URL="postgresql://usuario:senha@host:porta/banco"
python scripts/seed_data.py
```

---

## ✅ MÉTODO 3: Via Railway Shell (Dentro do Container)

```bash
# Conectar ao container do Railway
railway shell

# Dentro do container, executar:
python scripts/seed_data.py
```

---

## ✅ MÉTODO 4: Criar Endpoint Temporário (Mais Simples)

Vou criar um endpoint `/setup` que você pode acessar pelo navegador para popular o banco automaticamente.

Após popular o banco, **delete esse arquivo** por segurança!

---

## 🔑 Credenciais Após Popular

**Administrador:**
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

**Médicos (5 cadastrados):**
- Senha padrão: `medico123`

**Pacientes (5 cadastrados):**
- Senha padrão: `paciente123`

---

## ⚠️ Importante

Após fazer login como admin pela primeira vez em produção, **altere a senha** por segurança!

---

## 🆘 Se Nenhum Método Funcionar

Me avise e criarei um script de setup automático que roda no primeiro deploy do Railway.
