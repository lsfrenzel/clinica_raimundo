# 🚀 Como Inicializar o Banco no Railway - SUPER SIMPLES

## ✅ Solução em 2 Passos:

### 1️⃣ Faça o push do código atualizado:

```bash
git add .
git commit -m "Adiciona rota de inicialização do banco"
git push
```

### 2️⃣ Acesse esta URL no seu navegador:

```
https://SEU-APP.up.railway.app/admin/init-database
```

**Troque `SEU-APP` pela URL real do seu projeto no Railway.**

---

## 🎯 O que vai acontecer:

Quando você acessar essa URL, o sistema vai:

1. ✅ Criar todas as tabelas do banco
2. ✅ Criar 9 especialidades médicas
3. ✅ Criar o administrador
4. ✅ Criar 5 médicos
5. ✅ Criar 990 slots de agenda

Você vai ver uma mensagem JSON na tela tipo:

```json
{
  "status": "success",
  "message": "Banco de dados inicializado com sucesso!",
  "credenciais": {
    "admin_email": "admin@clinicadrraimundonunes.com.br",
    "admin_password": "admin123"
  }
}
```

---

## 🔑 Depois, faça login:

1. Vá para: `https://SEU-APP.up.railway.app/auth/login`
2. Use:
   - **Email:** `admin@clinicadrraimundonunes.com.br`
   - **Senha:** `admin123`

**Pronto!** ✨

---

## ⚠️ IMPORTANTE:

- **Use essa URL apenas UMA VEZ!**
- Depois que funcionar, não precisa acessar de novo
- Se acessar novamente, vai aparecer mensagem dizendo que já existe

---

## 🔒 Segurança:

**Depois que funcionar, você deve:**

1. Fazer login como admin
2. Alterar a senha do admin
3. (Opcional) Desabilitar essa rota removendo-a do código

---

**É isso!** Simples assim. Acesse a URL e pronto! 🎊
