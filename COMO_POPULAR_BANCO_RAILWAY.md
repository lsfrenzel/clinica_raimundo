# 🗄️ Como Popular o Banco de Dados no Railway

## ✅ Método 1: Automático (Recomendado)

O banco de dados será populado **automaticamente** quando você fizer o deploy no Railway!

### Como funciona:

1. Quando você faz **push** para o Railway
2. O Railway executa o arquivo `nixpacks.toml`
3. Esse arquivo roda o script `scripts/auto_migrate.py` antes de iniciar o servidor
4. O script:
   - ✅ Cria todas as tabelas
   - ✅ Popula com dados iniciais (se o banco estiver vazio)
   - ✅ Garante que o admin existe

### ⚠️ IMPORTANTE: Verificar no Railway

Certifique-se de que a variável de ambiente `DATABASE_URL` está configurada no Railway apontando para o seu banco PostgreSQL.

---

## 🔧 Método 2: Popular Manualmente (se necessário)

Se por algum motivo o método automático não funcionar, você pode executar manualmente:

### No Railway CLI:

```bash
railway run python popular_railway.py
```

### Ou conectar ao banco e executar:

1. Faça login no Railway
2. Vá em seu projeto
3. Abra o terminal do Railway
4. Execute:
   ```bash
   python popular_railway.py
   ```

---

## 📊 Dados que serão criados:

- ✅ **9 especialidades médicas**
  - DIU e Implanon
  - Pré-Natal de Alto Risco
  - Hipertensão e Diabetes Gestacional
  - Mastologia
  - Uroginecologia
  - Climatério e Menopausa
  - PTGI
  - Sexualidade
  - Reprodução Humana

- ✅ **6 usuários:**
  - 1 Administrador
  - 5 Médicos

- ✅ **990 slots de agenda** (próximos 30 dias úteis)

---

## 🔑 Credenciais de Login:

### Administrador:
- **Email:** `admin@clinicadrraimundonunes.com.br`
- **Senha:** `admin123`

### Médicos (todos com senha `medico123`):
- Dr. Raimundo Nunes - `raimundo.nunes@clinicadrraimundonunes.com.br`
- Dra. Ana Silva - `ana.silva@clinicadrraimundonunes.com.br`
- Dr. Carlos Oliveira - `carlos.oliveira@clinicadrraimundonunes.com.br`
- Dra. Maria Santos - `maria.santos@clinicadrraimundonunes.com.br`
- Dr. Ricardo Mendes - `ricardo.mendes@clinicadrraimundonunes.com.br`

---

## 🔍 Como Verificar se o Banco foi Populado:

### Opção 1: Pelo Railway Dashboard
1. Acesse o Railway
2. Vá em "Deployments"
3. Veja os logs do último deploy
4. Procure pelas mensagens:
   ```
   ✅ BANCO POPULADO COM SUCESSO!
   📊 DADOS CRIADOS:
      • Especialidades: 9
      • Médicos: 5
      • Agenda: 990 slots
   ```

### Opção 2: Pelo Sistema
1. Acesse sua aplicação no Railway
2. Vá para `/auth/login`
3. Tente fazer login com: `admin@clinicadrraimundonunes.com.br` / `admin123`
4. Se conseguir, o banco foi populado!

---

## 🚨 Problemas Comuns:

### "Tabelas vazias mesmo após deploy"

**Solução:**
1. Verifique os logs do Railway
2. Execute manualmente: `railway run python popular_railway.py`
3. Verifique se `DATABASE_URL` está configurado corretamente

### "Erro ao conectar ao banco"

**Solução:**
1. Confirme que o banco PostgreSQL está ativo no Railway
2. Verifique a variável `DATABASE_URL` nas configurações
3. O formato deve ser: `postgresql://user:password@host:port/database`

### "Admin não consegue fazer login"

**Solução:**
Execute para resetar a senha do admin:
```bash
railway run python popular_railway.py
```
(O script detecta se o admin existe e reseta a senha para `admin123`)

---

## 📝 Notas Importantes:

1. **O script é seguro**: Se o banco já tiver dados, ele NÃO apaga nada
2. **Pode executar múltiplas vezes**: O script detecta dados existentes
3. **Idempotente**: Executar várias vezes não duplica dados
4. **Logs detalhados**: Sempre mostra o que está fazendo

---

## 🎯 Próximos Passos Após Popular:

1. ✅ Faça login como admin
2. ✅ Verifique as especialidades em `/admin/especialidades`
3. ✅ Verifique os médicos em `/admin/medicos`
4. ✅ Teste o agendamento de consultas
5. ✅ Configure variáveis de ambiente adicionais (email, etc.)

---

**Dúvidas?** Verifique os logs do deploy no Railway ou execute manualmente `popular_railway.py`.
