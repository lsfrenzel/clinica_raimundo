# 🚀 Instruções para Popular o Banco de Dados no Railway

## ✅ Como Popular o Banco de Dados via URL

Para criar todos os usuários, médicos, especialidades e agenda no banco de dados PostgreSQL do Railway, siga estas etapas:

### 1. Acesse a URL de Setup

No seu navegador, acesse a seguinte URL (substitua pela URL do seu app no Railway):

```
https://seu-app.railway.app/setup-database
```

**Exemplo:** Se seu app está em `https://clinica-production.up.railway.app`, acesse:
```
https://clinica-production.up.railway.app/setup-database
```

### 2. O que será criado?

Ao acessar essa URL, o sistema irá automaticamente criar:

- ✅ **1 Administrador**
- ✅ **5 Médicos** (incluindo Dr. Raimundo Nunes)
- ✅ **1 Paciente** (Ana Silva)
- ✅ **9 Especialidades médicas**
- ✅ **990 Slots de agenda** (próximos 30 dias úteis)

### 3. Você verá uma resposta JSON como esta:

```json
{
  "status": "sucesso",
  "mensagens": [
    "📦 Criando tabelas...",
    "✅ Tabelas criadas!",
    "👤 Verificando administrador...",
    "✅ Admin criado!",
    "📋 Criando especialidades...",
    "✅ 9 especialidades criadas!",
    "👨‍⚕️ Criando médicos...",
    "✅ 5 médicos criados!",
    "📅 Criando agenda dos médicos...",
    "✅ 990 slots de agenda criados!",
    "👥 Criando paciente Ana Silva...",
    "✅ Paciente Ana Silva criada!",
    "🎉 BANCO POPULADO COM SUCESSO!"
  ],
  "dados_criados": {
    "especialidades": 9,
    "medicos": 5,
    "agenda": 990,
    "usuarios": 7
  }
}
```

---

## 🔑 Credenciais de Login

Após popular o banco de dados, você pode fazer login com as seguintes credenciais:

### 👨‍💼 Administrador
- **Email:** admin@clinicadrraimundonunes.com.br
- **Senha:** admin123

### 👨‍⚕️ Dr. Raimundo Nunes (Médico)
- **Email:** raimundo@clinicadrraimundonunes.com.br
- **Senha:** medico123

### 👥 Ana Silva (Paciente)
- **Email:** ana.silva@email.com
- **Senha:** paciente123

### Outros Médicos Criados:
Todos os médicos abaixo usam a senha: **medico123**

1. **Dra. Ana Carolina Silva**
   - Email: ana@clinicadrraimundonunes.com.br

2. **Dr. Ricardo Mendes**
   - Email: ricardo@clinicadrraimundonunes.com.br

3. **Dra. Maria Santos**
   - Email: maria@clinicadrraimundonunes.com.br

4. **Dra. Patrícia Lima**
   - Email: patricia@clinicadrraimundonunes.com.br

---

## ⚠️ Observações Importantes

1. **Executar apenas uma vez:** A rota `/setup-database` detecta se o banco já foi populado. Se já existirem dados, ela não criará duplicatas.

2. **Resetar senha:** Se você já criou os usuários antes mas as senhas não estão funcionando, a rota automaticamente reseta as senhas para os valores padrão acima.

3. **Railway Database URL:** Certifique-se de que a variável de ambiente `DATABASE_URL` está configurada corretamente no Railway apontando para o banco PostgreSQL.

4. **Ambiente de Produção:** Este é o banco de dados de produção do Railway. Todas as alterações são permanentes.

---

## 🔍 Como Testar o Login

1. Acesse: `https://seu-app.railway.app/auth/login`
2. Use uma das credenciais acima
3. Clique em "Entrar"
4. Você deve ser redirecionado para a página apropriada conforme o tipo de usuário

---

## ❓ Problemas Comuns

### "Email ou senha inválidos"
- Verifique se você executou a URL `/setup-database` primeiro
- Confirme que está usando o email e senha exatamente como mostrado acima
- Tente acessar novamente a URL `/setup-database` para resetar as senhas

### "Erro ao conectar ao banco"
- Verifique se a variável `DATABASE_URL` está configurada no Railway
- Confirme que o banco PostgreSQL está ativo no Railway

### "Banco já populado"
- Isso é normal! Significa que os dados já foram criados anteriormente
- Você pode fazer login normalmente com as credenciais acima

---

## 📞 Suporte

Se tiver algum problema, verifique os logs da aplicação no Railway para mais detalhes.
