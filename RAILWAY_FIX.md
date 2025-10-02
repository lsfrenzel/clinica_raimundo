# Correção do Login Admin no Railway

## Problema Identificado

O login do administrador não está funcionando no Railway devido a dois problemas principais:

1. **DATABASE_URL incompatível**: Railway usa `postgres://` mas SQLAlchemy 1.4+ requer `postgresql://`
2. **Senha do admin**: Pode não estar corretamente configurada no banco de produção

## ✅ Correções Aplicadas

### 1. Correção Automática de DATABASE_URL

O arquivo `main.py` foi atualizado para converter automaticamente o formato da URL:

```python
# Fix Railway DATABASE_URL: postgres:// -> postgresql://
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
```

### 2. Melhorias no Hashing de Senha

O modelo `User` foi atualizado com tratamento de erros e encoding mais robusto para produção.

## 🚀 Como Corrigir no Railway

### Opção 1: Executar Script de Diagnóstico (Recomendado)

O script `scripts/fix_railway_admin.py` irá:
- ✅ Verificar conexão com banco
- ✅ Verificar se tabelas existem
- ✅ Verificar se usuário admin existe
- ✅ Testar senha do admin
- ✅ Criar ou resetar senha do admin se necessário

**No Railway CLI:**

```bash
# 1. Instalar Railway CLI (se ainda não tiver)
npm i -g @railway/cli

# 2. Fazer login
railway login

# 3. Vincular ao projeto
railway link

# 4. Executar script de diagnóstico
railway run python scripts/fix_railway_admin.py
```

**Ou via GitHub Actions / Railway Deploy:**

Adicione ao comando de deploy no Railway:
```bash
python scripts/fix_railway_admin.py && gunicorn --bind 0.0.0.0:$PORT main:app
```

### Opção 2: Popular Banco Manualmente

Se o banco estiver vazio, execute o script de seed:

```bash
railway run python scripts/seed_data.py
```

### Opção 3: Resetar Senha via Console Python

```bash
railway run python
```

```python
from main import create_app
from extensions import db
from models import User

app = create_app()
with app.app_context():
    # Buscar admin
    admin = User.query.filter_by(email='admin@clinicadrraimundonunes.com.br').first()
    
    if admin:
        # Resetar senha
        admin.set_password('admin123')
        db.session.commit()
        print("✅ Senha resetada!")
    else:
        # Criar admin
        admin = User()
        admin.nome = "Administrador"
        admin.email = "admin@clinicadrraimundonunes.com.br"
        admin.telefone = "(11) 99999-9999"
        admin.role = "admin"
        admin.ativo = True
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin criado!")
```

## 🔑 Credenciais de Admin

Após executar qualquer uma das opções acima:

- **Email**: `admin@clinicadrraimundonunes.com.br`
- **Senha**: `admin123`

## ⚙️ Variáveis de Ambiente Necessárias

Certifique-se de que estas variáveis estão configuradas no Railway:

### Obrigatórias:
- `DATABASE_URL` → Referência: `${{Postgres.DATABASE_URL}}`
- `SESSION_SECRET` → Gere uma chave aleatória: `python -c "import secrets; print(secrets.token_hex(32))"`

### Opcionais (Database):
- `PGHOST` → `${{Postgres.PGHOST}}`
- `PGPORT` → `${{Postgres.PGPORT}}`
- `PGUSER` → `${{Postgres.PGUSER}}`
- `PGPASSWORD` → `${{Postgres.PGPASSWORD}}`
- `PGDATABASE` → `${{Postgres.PGDATABASE}}`

### Opcionais (Chatbot):
- `GEMINI_API_KEY` → Sua chave da API Gemini (opcional)

## 📋 Checklist de Verificação

- [ ] Código atualizado com correções (push para GitHub)
- [ ] Railway fez redeploy automático
- [ ] Variáveis de ambiente configuradas
- [ ] Script de diagnóstico executado
- [ ] Login testado com sucesso

## 🐛 Troubleshooting

### Erro: "relation 'users' does not exist"
```bash
railway run flask db upgrade
```

### Erro: "password authentication failed"
Verifique se DATABASE_URL está correta:
```bash
railway variables
```

### Banco vazio após deploy
```bash
railway run python scripts/seed_data.py
```

### Login falha mas senha está correta
Limpe cookies do navegador e tente novamente.

## 📞 Suporte

Se o problema persistir:
1. Execute o script de diagnóstico e copie a saída
2. Verifique os logs do Railway: Dashboard → Deployments → View Logs
3. Compartilhe os logs para análise

---

**Última atualização**: 02/10/2025
