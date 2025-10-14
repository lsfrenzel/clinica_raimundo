# 🌐 Popular Banco do Railway via URL

## ✅ Rota Criada

Criei uma rota especial que você pode acessar diretamente no navegador para popular o banco de dados do Railway!

## 🔗 Como Usar

### Passo 1: Fazer Deploy no Railway

Primeiro, faça o deploy da aplicação no Railway:

```bash
git add .
git commit -m "Adicionar rota para popular banco via URL"
git push
```

**OU** faça um redeploy manual no dashboard do Railway.

### Passo 2: Acessar a URL Especial

Depois que o deploy completar, abra esta URL no navegador:

```
https://SEU-APP.railway.app/setup-database
```

**Substitua `SEU-APP` pela URL real do seu app no Railway!**

### Passo 3: Verificar Resultado

Você verá uma resposta JSON com todas as informações:

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
    "✅ 315 slots de agenda criados!",
    "🎉 BANCO POPULADO COM SUCESSO!",
    "",
    "🔑 CREDENCIAIS DE LOGIN:",
    "Email: admin@clinicadrraimundonunes.com.br",
    "Senha: admin123"
  ],
  "dados_criados": {
    "especialidades": 9,
    "medicos": 5,
    "agenda": 315,
    "usuarios": 6
  }
}
```

## 📊 O Que Será Criado

A rota automaticamente cria:

✅ **9 Especialidades:**
- DIU e Implanon
- Pré-Natal de Alto Risco
- Hipertensão e Diabetes Gestacional
- Mastologia
- Uroginecologia
- Climatério e Menopausa
- PTGI
- Sexualidade
- Reprodução Humana

✅ **5 Médicos com múltiplas especialidades:**
1. **Dr. Raimundo Nunes** → DIU e Implanon, Pré-Natal de Alto Risco, Hipertensão e Diabetes Gestacional
2. **Dra. Ana Carolina Silva** → Mastologia, Uroginecologia, Sexualidade
3. **Dr. Ricardo Mendes** → Climatério e Menopausa, Reprodução Humana, PTGI
4. **Dra. Maria Santos** → Mastologia, DIU e Implanon
5. **Dra. Patrícia Lima** → Uroginecologia, Pré-Natal de Alto Risco

✅ **Agenda:** ~315 slots (próximos 30 dias, seg-sex, 8h-17h)

✅ **Admin:** admin@clinicadrraimundonunes.com.br / admin123

## 🔄 Executar Novamente

Se precisar popular novamente:

**Primeira vez:** A rota cria tudo do zero

**Já populado:** A rota detecta que já tem dados e apenas:
- Verifica se o admin existe
- Reseta a senha do admin para `admin123` se necessário
- Retorna status `"ja_populado"`

## 🧪 Testar Localmente (Opcional)

Você pode testar aqui no Replit primeiro:

```
http://localhost:5000/setup-database
```

Ou clique aqui: [/setup-database](/setup-database)

## ⚠️ Segurança

**IMPORTANTE:** Depois que popular o banco em produção, considere:

1. **Desabilitar a rota** (comentar o registro do blueprint no `main.py`)
2. **OU** adicionar proteção por senha/token
3. **Alterar a senha do admin** após o primeiro login

## 🎯 Resumo do Processo

1. ✅ Fazer `git push` ou redeploy no Railway
2. ✅ Acessar `https://seu-app.railway.app/setup-database`
3. ✅ Ver mensagem de sucesso
4. ✅ Testar: `https://seu-app.railway.app/appointments/agendar`
5. ✅ Login admin: `admin@clinicadrraimundonunes.com.br` / `admin123`

---

## 🐛 Troubleshooting

### Erro 500 na rota
- Verifique se `DATABASE_URL` está configurado no Railway
- Veja os logs do Railway para detalhes do erro

### Resposta "ja_populado" mas médicos não aparecem
- O banco já tinha dados antigos
- **Solução:** Limpe o banco do Railway e acesse a rota novamente

### Admin não consegue logar
- Acesse `/setup-database` novamente - vai resetar a senha

---

**Pronto! Agora é só fazer o push e acessar a URL!** 🚀
