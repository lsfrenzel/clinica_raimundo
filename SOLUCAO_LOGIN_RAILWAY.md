# 🔧 Solução para Problema de Login no Railway

## ❌ Problema Identificado

O login não estava funcionando porque a paciente **Ana Silva** não foi criada no banco de dados do Railway durante o setup inicial.

## ✅ Solução - Execute estas URLs no Railway

### **PASSO 1: Verificar o Problema**

Acesse esta URL no seu navegador (substitua pela URL do seu app):

```
https://seu-app.railway.app/verificar-usuarios
```

Isso mostrará quais usuários existem e se as senhas estão corretas.

---

### **PASSO 2: Resetar e Criar Usuários** (SOLUÇÃO)

Acesse esta URL para forçar a criação dos usuários e resetar as senhas:

```
https://seu-app.railway.app/reset-senhas
```

Esta rota irá:
- ✅ Criar a paciente Ana Silva (se não existir)
- ✅ Resetar a senha do Dr. Raimundo Nunes para `medico123`
- ✅ Resetar a senha do Admin para `admin123`
- ✅ Ativar todos os usuários

---

### **PASSO 3: Verificar Novamente**

Após executar o reset, acesse novamente:

```
https://seu-app.railway.app/verificar-usuarios
```

Você deve ver algo como:

```json
{
  "usuarios_verificados": [
    {
      "email": "ana.silva@email.com",
      "existe": true,
      "ativo": true,
      "role": "paciente",
      "senha_correta": true
    },
    {
      "email": "raimundo@clinicadrraimundonunes.com.br",
      "existe": true,
      "ativo": true,
      "role": "medico",
      "senha_correta": true
    },
    {
      "email": "admin@clinicadrraimundonunes.com.br",
      "existe": true,
      "ativo": true,
      "role": "admin",
      "senha_correta": true
    }
  ]
}
```

---

## 🔑 Credenciais Após o Reset

### 👥 **Ana Silva (Paciente)**
- **Email:** ana.silva@email.com
- **Senha:** paciente123

### 👨‍⚕️ **Dr. Raimundo Nunes (Médico)**
- **Email:** raimundo@clinicadrraimundonunes.com.br
- **Senha:** medico123

### 👨‍💼 **Administrador**
- **Email:** admin@clinicadrraimundonunes.com.br
- **Senha:** admin123

---

## 🧪 Como Testar o Login

1. Acesse: `https://seu-app.railway.app/auth/login`
2. Use **ana.silva@email.com** / **paciente123**
3. Clique em "Entrar"
4. ✅ O login deve funcionar!

---

## 📋 Resumo das URLs Disponíveis

### 1. `/setup-database`
Popula o banco de dados inicial (médicos, especialidades, agenda)

### 2. `/verificar-usuarios` ⭐ NOVO
Diagnóstico: verifica se usuários existem e se senhas estão corretas

### 3. `/reset-senhas` ⭐ NOVO (SOLUÇÃO)
**USE ESTA!** - Força criação/reset de usuários e senhas

---

## 🎯 O Que Fazer Agora

**EXECUTE IMEDIATAMENTE:**

```
1. Acesse: https://seu-app.railway.app/reset-senhas
2. Aguarde a confirmação (verá JSON com "status": "sucesso")
3. Faça login com: ana.silva@email.com / paciente123
```

**PRONTO!** O login funcionará! 🎉

---

## ⚠️ Se Ainda Não Funcionar

Se após executar `/reset-senhas` o login ainda não funcionar:

1. Acesse `/verificar-usuarios` e envie-me a resposta completa
2. Verifique os logs do Railway para erros
3. Certifique-se que a variável `DATABASE_URL` está configurada

---

## 📝 Diferença entre as Rotas

| Rota | Quando Usar |
|------|-------------|
| `/setup-database` | Primeira vez - cria todos os médicos, especialidades e agenda |
| `/verificar-usuarios` | Diagnosticar problemas de login |
| `/reset-senhas` | **Solução rápida** - corrige senhas e cria usuários faltantes |

---

**💡 DICA:** A rota `/reset-senhas` é idempotente - pode executar quantas vezes quiser sem problemas!
