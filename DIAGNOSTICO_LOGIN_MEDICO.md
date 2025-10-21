# 🔍 Diagnóstico e Solução - Login do Médico no Railway

## 🎯 Teste Específico para o Dr. Raimundo Nunes

Execute esta URL no seu navegador Railway para diagnosticar o problema:

```
https://seu-app.railway.app/testar-login/raimundo.nunes@clinicadrraimundonunes.com.br/medico123
```

### O que você deve ver:

#### ✅ **Se estiver funcionando:**
```json
{
  "status": "login_ok",
  "mensagem": "✅ Login funcionaria!",
  "detalhes": {
    "senha_correta": true,
    "ativo": true,
    "role": "medico"
  }
}
```

#### ❌ **Se a senha estiver incorreta:**
```json
{
  "status": "senha_incorreta",
  "mensagem": "❌ Senha incorreta - Senha resetada! Tente novamente."
}
```
**IMPORTANTE:** Se vir esta mensagem, a senha foi resetada automaticamente! Tente fazer login novamente.

#### ❌ **Se o usuário não existir:**
```json
{
  "status": "usuario_nao_encontrado"
}
```
**Solução:** Execute `/setup-database` primeiro.

---

## 🔧 Solução em 3 Passos

### **PASSO 1: Diagnóstico**
```
https://seu-app.railway.app/testar-login/raimundo.nunes@clinicadrraimundonunes.com.br/medico123
```

### **PASSO 2: Reset (se necessário)**
```
https://seu-app.railway.app/reset-senhas
```

### **PASSO 3: Verificação Final**
```
https://seu-app.railway.app/verificar-usuarios
```

---

## 🧪 Testar TODOS os Logins

### Testar Ana Silva (Paciente):
```
https://seu-app.railway.app/testar-login/ana.silva@email.com/paciente123
```

### Testar Dr. Raimundo (Médico):
```
https://seu-app.railway.app/testar-login/raimundo.nunes@clinicadrraimundonunes.com.br/medico123
```

### Testar Admin:
```
https://seu-app.railway.app/testar-login/admin@clinicadrraimundonunes.com.br/admin123
```

---

## 📋 Checklist de Resolução

Execute na ordem:

- [ ] **1.** Acesse `/testar-login/raimundo.nunes@clinicadrraimundonunes.com.br/medico123`
- [ ] **2.** Se mostrar "senha_incorreta", a senha foi resetada automaticamente
- [ ] **3.** Aguarde 10 segundos
- [ ] **4.** Tente fazer login em `/auth/login` com:
  - Email: `raimundo.nunes@clinicadrraimundonunes.com.br`
  - Senha: `medico123`
- [ ] **5.** Se ainda não funcionar, execute `/reset-senhas`
- [ ] **6.** Repita os passos 1-4

---

## ⚠️ Problemas Comuns

### 1. "Senha incorreta" mesmo após reset
**Causa:** Cache do navegador ou sessão antiga  
**Solução:** 
- Limpe cookies do site
- Tente em aba anônima
- Aguarde 10-30 segundos após o reset

### 2. "Usuário não encontrado"
**Causa:** Banco não foi populado  
**Solução:** Execute `/setup-database` primeiro

### 3. Login funciona no teste mas não na página
**Causa:** Problema com sessões ou cookies  
**Solução:**
- Verifique se `SESSION_SECRET` está configurado no Railway
- Limpe cookies e cache
- Tente em navegador diferente

---

## 🔐 Credenciais Corretas

### Dr. Raimundo Nunes
```
Email: raimundo.nunes@clinicadrraimundonunes.com.br
Senha: medico123
Role: medico
```

### Ana Silva
```
Email: ana.silva@email.com
Senha: paciente123
Role: paciente
```

### Admin
```
Email: admin@clinicadrraimundonunes.com.br
Senha: admin123
Role: admin
```

---

## 💡 Dica Extra

A rota `/testar-login` automaticamente **reseta a senha** se detectar que está incorreta. Então:

1. Execute o teste
2. Se mostrar "senha_incorreta", ela já foi corrigida
3. Tente fazer login normalmente

---

## 🆘 Se Nada Funcionar

Execute estas 3 URLs na ordem e me envie os resultados:

1. `/setup-database`
2. `/reset-senhas`
3. `/verificar-usuarios`

Copie e cole a resposta JSON de cada uma para que eu possa ajudar!
