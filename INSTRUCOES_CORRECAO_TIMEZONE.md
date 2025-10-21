# Instruções para Correção de Timezone dos Agendamentos

## Problema Identificado

Agendamentos criados via API (chatbot/mobile) não apareciam no painel do médico devido a um problema de timezone:

- **Causa**: A API salvava horários em horário de Brasília (UTC-3) sem converter para UTC
- **Efeito**: O painel do médico buscava agendamentos usando UTC, fazendo com que agendamentos parecessem estar 3 horas no passado

## Correções Aplicadas

### 1. Código da Aplicação (já corrigido)

- ✅ **app/blueprints/api.py**: API agora converte horários de Brasília para UTC antes de salvar
- ✅ **chatbot_service.py**: Chatbot agora converte horários de Brasília para UTC antes de salvar
- ✅ **app/blueprints/main.py**: Painel do médico agora usa `datetime.utcnow()` para consistência

### 2. Dados Existentes no Railway (necessário executar script)

## Como Executar o Script de Correção no Railway

### Opção 1: Via Railway CLI (Recomendado)

**IMPORTANTE**: Você DEVE especificar a data/hora do deploy usando `--cutoff-date`. Use a data/hora em UTC de quando você fez o deploy da correção do código.

```bash
# 1. Instalar Railway CLI (se ainda não tiver)
npm i -g @railway/cli

# 2. Fazer login
railway login

# 3. Conectar ao projeto
railway link

# 4. Obter a data/hora atual em UTC (esta será sua cutoff-date)
# Anote este timestamp - você vai usá-lo no próximo passo!
date -u '+%Y-%m-%d %H:%M:%S'

# 5. Primeiro, executar em modo DRY RUN para ver o que será alterado
# SUBSTITUA a data abaixo pela data/hora do seu deploy!
railway run python scripts/fix_timezone_agendamentos.py \
  --cutoff-date "2025-10-21 22:30:00" \
  --dry-run

# 6. Se tudo estiver correto, aplicar as correções
# Use a MESMA data do passo anterior!
railway run python scripts/fix_timezone_agendamentos.py \
  --cutoff-date "2025-10-21 22:30:00" \
  --apply
```

**Por que a cutoff-date é importante?**

O script adiciona 3 horas aos agendamentos criados via API/chatbot. Se você não especificar a cutoff-date, agendamentos criados APÓS o deploy do código corrigido podem ser corrigidos duas vezes (uma vez pelo código novo e uma vez pelo script), resultando em horários incorretos.

### Opção 2: Via Console do Railway

1. Acesse o dashboard do Railway
2. Anote a data/hora atual em UTC antes de fazer o deploy (exemplo: 2025-10-21 22:30:00)
3. Vá para a aba "Settings" do seu serviço
4. Na seção "Deployments", clique em "Deploy"
5. Após o deploy, acesse o shell do container
6. Execute:
   ```bash
   # Primeiro em modo DRY RUN
   # SUBSTITUA a data abaixo pela data/hora que você anotou!
   python scripts/fix_timezone_agendamentos.py \
     --cutoff-date "2025-10-21 22:30:00" \
     --dry-run
   
   # Depois aplicar correções (use a MESMA data!)
   python scripts/fix_timezone_agendamentos.py \
     --cutoff-date "2025-10-21 22:30:00" \
     --apply
   ```

### Opção 3: Via Python Console ou Script

Se você preferir executar via console Python interativo ou modificar o script:

```python
from datetime import datetime
from scripts.fix_timezone_agendamentos import fix_timezone_agendamentos

# IMPORTANTE: Defina a data/hora do deploy do código corrigido
cutoff = datetime.strptime("2025-10-21 22:30:00", "%Y-%m-%d %H:%M:%S")

# Primeiro em modo DRY RUN
fix_timezone_agendamentos(dry_run=True, cutoff_date=cutoff)

# Depois aplicar (se tudo estiver correto)
# fix_timezone_agendamentos(dry_run=False, cutoff_date=cutoff)
```

**AVISO**: Não crie endpoints HTTP para executar este script em produção, pois ele deve ser executado apenas uma vez!

## O que o Script Faz

1. Busca todos os agendamentos criados via API ou chatbot (origem='mobile' ou origem='chatbot') **antes da data de corte (cutoff_date)**
2. Verifica se cada agendamento ainda precisa de correção com múltiplas verificações de segurança:
   - Ignora agendamentos já marcados como corrigidos (observacoes contém "TIMEZONE_CORRIGIDO")
   - Ignora agendamentos onde o horário de início é anterior à data de criação (já estão em UTC)
   - Apenas corrige agendamentos criados ANTES da data de corte para evitar correções duplas
3. Adiciona 3 horas aos horários de início e fim (convertendo de Brasília UTC-3 para UTC)
4. Marca os agendamentos corrigidos adicionando "TIMEZONE_CORRIGIDO" nas observações
5. Salva as mudanças no banco de dados
6. Em modo `--dry-run`, apenas mostra o que seria alterado sem fazer mudanças

### Proteções de Segurança

O script possui múltiplas camadas de proteção para evitar corrigir agendamentos duas vezes:

✅ **Filtro por data de criação**: Apenas agendamentos criados antes da data atual
✅ **Detecção de horário já em UTC**: Ignora agendamentos onde inicio < created_at  
✅ **Marcação de correção**: Agendamentos corrigidos são marcados para evitar re-correção
✅ **Modo DRY RUN padrão**: Sempre mostra o que seria alterado antes de aplicar

## Verificação Após Correção

Após executar o script:

1. ✅ Faça login como médico no sistema
2. ✅ Acesse o painel do médico
3. ✅ Verifique se os agendamentos criados aparecem corretamente
4. ✅ Confirme que os horários estão corretos (devem aparecer em horário de Brasília para o usuário)

## Prevenção de Problemas Futuros

As correções no código garantem que:

- ✅ Novos agendamentos via API/chatbot serão salvos corretamente em UTC
- ✅ O painel do médico sempre usa UTC para comparações
- ✅ A exibição para usuários converte de UTC para Brasília automaticamente

## Suporte

Se encontrar algum problema durante a execução:

1. Verifique os logs do Railway
2. Verifique se a variável de ambiente `DATABASE_URL` está configurada
3. Certifique-se de que o banco de dados está acessível
4. Em caso de erro, execute novamente em modo `--dry-run` primeiro
