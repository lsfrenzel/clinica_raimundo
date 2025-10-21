# Correção de Timezone via URL (Rota Administrativa)

## 🎯 Propósito

Esta rota permite corrigir agendamentos antigos diretamente pela interface web, sem necessidade de executar scripts via linha de comando.

## 🔐 Acesso

**Somente administradores** podem acessar esta rota. Você precisa estar logado como admin.

## 📋 Como Usar

### Passo 1: Fazer Deploy do Código Corrigido

Antes de corrigir os dados, certifique-se de ter feito o deploy do código corrigido no Railway.

### Passo 2: Anotar a Data/Hora do Deploy

Anote a data e hora em UTC do deploy. Por exemplo:
- **Data:** 2025-10-21
- **Hora:** 22:30:00
- **Formato para URL:** `2025-10-21-22-30-00`

### Passo 3: Visualizar as Correções (Preview)

Acesse a URL (substitua `SEU_DOMINIO` pelo seu domínio do Railway):

```
https://SEU_DOMINIO/admin/corrigir-timezone-agendamentos?cutoff_date=2025-10-21-22-30-00
```

Exemplo completo:
```
https://clinica-production.up.railway.app/admin/corrigir-timezone-agendamentos?cutoff_date=2025-10-21-22-30-00
```

Esta página mostrará:
- ✅ Quantos agendamentos serão corrigidos
- ✅ Horários atuais vs. horários corrigidos
- ✅ Informações sobre cada agendamento

### Passo 4: Aplicar as Correções

Se tudo estiver correto na prévia, clique no botão **"✅ Aplicar Correções"** na página.

**IMPORTANTE:** As correções são aplicadas via formulário POST com CSRF token para segurança. Não é possível aplicar diretamente via URL.

## ⚙️ Parâmetros da URL

| Parâmetro | Obrigatório | Formato | Exemplo | Descrição |
|-----------|-------------|---------|---------|-----------|
| `cutoff_date` | **SIM** | `YYYY-MM-DD-HH-MM-SS` | `2025-10-21-22-30-00` | Data/hora do deploy (UTC) |

## 🛡️ Proteções de Segurança

A rota possui múltiplas proteções:

1. ✅ **Acesso restrito**: Somente administradores
2. ✅ **Data de corte obrigatória**: Previne correções acidentais
3. ✅ **Filtro por origem**: Apenas agendamentos de API/chatbot
4. ✅ **Filtro por data de criação**: Apenas antes da data de corte
5. ✅ **Marcação de correção**: Adiciona `[TIMEZONE_CORRIGIDO]` nas observações
6. ✅ **Proteção contra duplicação**: Não corrige agendamentos já marcados

## 🔍 O Que a Correção Faz

Para cada agendamento elegível:
- Adiciona 3 horas ao `inicio` (converte Brasília UTC-3 para UTC)
- Adiciona 3 horas ao `fim`
- Adiciona marcador `[TIMEZONE_CORRIGIDO]` nas observações

## ⚠️ Importante

- Execute apenas **UMA VEZ** após o deploy
- Certifique-se de que a **cutoff_date está correta**
- Use o **modo preview** antes de aplicar
- **Não é possível desfazer** as correções depois de aplicar

## ❓ Solução de Problemas

### Erro: "cutoff_date é obrigatória"
**Solução:** Adicione `?cutoff_date=YYYY-MM-DD-HH-MM-SS` na URL

### Erro: "Formato de data inválido"
**Solução:** Use o formato correto com hífens: `2025-10-21-22-30-00`

### Mensagem: "Nenhum agendamento para corrigir"
**Possíveis causas:**
1. Todos os agendamentos já foram corrigidos
2. A cutoff_date está muito antiga
3. Não há agendamentos de API/chatbot antes da cutoff_date

## 📝 Exemplo Completo

```bash
# 1. Fazer deploy no Railway em 2025-10-21 às 22:30:00 UTC

# 2. Acessar para visualizar preview
https://clinica-production.up.railway.app/admin/corrigir-timezone-agendamentos?cutoff_date=2025-10-21-22-30-00

# 3. Revisar as correções na tela

# 4. Clicar no botão "✅ Aplicar Correções" (formulário POST protegido por CSRF)

# 5. Verificar mensagem de sucesso no painel admin
```

## ✅ Após a Correção

Depois de aplicar as correções:
1. Os agendamentos antigos aparecerão no painel do médico
2. Novos agendamentos via API/chatbot já usarão UTC automaticamente
3. Não é necessário executar novamente

---

**Última atualização:** 21/10/2025
