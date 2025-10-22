# URLs para População do Banco de Dados

Este documento explica as URLs disponíveis para popular e gerenciar o banco de dados da clínica.

## 📅 Popular Horários dos Médicos

**URL:** `/popular-horarios`

**Descrição:** Cria horários das **08:00 às 20:00** para todos os médicos ativos, de segunda a sexta-feira, nos próximos 60 dias.

**Como usar:**
- Acesse: `https://seu-dominio.railway.app/popular-horarios`
- ou localmente: `http://localhost:5000/popular-horarios`

**O que faz:**
- Cria slots de 1 hora para cada médico
- Período: Segunda a Sexta (pula fins de semana)
- Horários: 08h, 09h, 10h, 11h, 12h, 13h, 14h, 15h, 16h, 17h, 18h, 19h
- Não cria horários duplicados (verifica antes de criar)

**Exemplo de resposta:**
```json
{
  "status": "sucesso",
  "horarios_criados": 1590,
  "mensagens": [
    "📅 Criando horários para 5 médicos...",
    "✅ 1590 horários criados com sucesso!",
    "📊 Total de horários no banco: 2580"
  ]
}
```

---

## 🚀 Setup Completo do Banco

**URL:** `/setup-database`

**Descrição:** Cria toda a estrutura do banco de dados incluindo especialidades, médicos, horários (08:00-20:00), admin e paciente teste.

**Como usar:**
- Acesse: `https://seu-dominio.railway.app/setup-database`
- ou localmente: `http://localhost:5000/setup-database`

**O que faz:**
1. Cria todas as tabelas
2. Cria especialidades médicas
3. Cria 5 médicos com fotos
4. Cria horários das 08:00 às 20:00 (Segunda a Sexta) para 60 dias
5. Cria usuário admin
6. Cria paciente de teste (Ana Silva)

**Credenciais criadas:**

**ADMIN:**
- Email: `admin@clinicadrraimundonunes.com.br`
- Senha: `admin123`

**MÉDICOS:**
- Email: `raimundo.nunes@clinicadrraimundonunes.com.br`
- Senha: `medico123`
- (Todos os outros médicos também usam `medico123`)

**PACIENTE TESTE:**
- Email: `ana.silva@email.com`
- Senha: `paciente123`

---

## 🔧 Outras URLs Úteis

### Verificar Usuários
**URL:** `/verificar-usuarios`

Verifica se os usuários existem e se as senhas estão funcionando.

### Resetar Senhas
**URL:** `/reset-senhas`

Reseta as senhas do admin, médicos e paciente teste para os valores padrão.

### Criar Agendamentos de Teste
**URL:** `/criar-agendamentos-teste`

Cria 5 agendamentos aleatórios para teste do sistema.

---

## 📋 Como Funciona o Sistema de Agendamento

### 1. Criação de Horários Disponíveis
Os horários são criados na tabela `agendas` com:
- Data específica
- Hora de início e fim
- Médico associado
- Status ativo

### 2. Verificação de Disponibilidade
Quando um paciente tenta agendar:
1. O sistema busca todos os horários na tabela `agendas` para aquele médico e data
2. Verifica quais horários já têm agendamentos na tabela `agendamentos` (status 'agendado' ou 'confirmado')
3. Mostra apenas os horários que estão em `agendas` MAS NÃO estão em `agendamentos`
4. Filtra para mostrar apenas horários futuros

### 3. Agendamento
Ao confirmar um agendamento:
1. Cria um registro na tabela `agendamentos`
2. O horário continua existindo na tabela `agendas`
3. Mas não aparece mais como disponível para outros pacientes
4. Outros pacientes podem agendar em outros horários livres

---

## ✅ Status dos Horários

**Total de horários criados:** 2,580 slots
- **Por dia:** 12 horários (08:00 às 19:00)
- **Por médico:** 516 horários (43 dias úteis × 12 horários)
- **Período:** 60 dias úteis (Segunda a Sexta)

**Distribuição por hora:**
- 08:00 - 215 horários
- 09:00 - 215 horários
- 10:00 - 215 horários
- 11:00 - 215 horários
- 12:00 - 215 horários
- 13:00 - 215 horários
- 14:00 - 215 horários
- 15:00 - 215 horários
- 16:00 - 215 horários
- 17:00 - 215 horários
- 18:00 - 215 horários
- 19:00 - 215 horários

---

## 🎯 Uso Recomendado

1. **Primeira vez no Railway:** Acesse `/setup-database` para criar toda a estrutura
2. **Apenas adicionar mais horários:** Acesse `/popular-horarios`
3. **Resetar senhas:** Acesse `/reset-senhas`
4. **Testar agendamentos:** Acesse `/criar-agendamentos-teste`

---

## ⚠️ Observações Importantes

- As URLs podem ser acessadas diretamente no navegador
- O sistema não cria horários duplicados
- Os horários são criados automaticamente nas primeiras 60 dias úteis
- Fins de semana são pulados automaticamente
- Para adicionar mais dias no futuro, execute `/popular-horarios` novamente
