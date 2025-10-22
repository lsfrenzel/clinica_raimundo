# 🔧 Guia: Corrigir Agendamentos no Railway

## Problema
Os pacientes fazem agendamentos, mas os médicos não veem no painel médico.

## Causa Provável
O médico pode não ter um perfil na tabela `medicos` vinculado ao seu usuário, ou há inconsistências no banco de dados.

---

## ✅ PASSO 1: Executar Diagnóstico no Railway

1. **Acesse o Railway**
   - Vá para seu projeto no Railway
   - Acesse a aba "Deployments"
   - Clique no deployment ativo

2. **Execute o script de diagnóstico**
   ```bash
   python diagnostico_agendamentos.py
   ```

3. **Analise o resultado**
   - O script mostrará:
     - Total de médicos cadastrados
     - Total de agendamentos
     - Agendamentos por médico
     - Problemas encontrados

---

## ✅ PASSO 2: Verificar Problemas Comuns

### Problema A: Médico sem perfil na tabela `medicos`

**Sintoma**: O script mostra "Nenhum médico cadastrado" ou médicos faltando

**Solução**: Criar perfil médico para o usuário

Execute este SQL no banco do Railway:

```sql
-- 1. Verificar usuários com role='medico' que não têm perfil
SELECT u.id, u.nome, u.email 
FROM users u 
LEFT JOIN medicos m ON u.id = m.user_id 
WHERE u.role = 'medico' AND m.id IS NULL;

-- 2. Criar perfil médico para usuário específico
-- SUBSTITUA os valores abaixo:
INSERT INTO medicos (user_id, crm, bio, ativo) 
VALUES (
    123,  -- ID do usuário médico (veja query acima)
    'CRM12345',  -- CRM do médico
    'Médico especialista',  -- Bio
    true
);
```

### Problema B: Agendamentos sem `medico_id`

**Sintoma**: Script mostra "Agendamentos sem medico_id"

**Solução**: NÃO DEVE ACONTECER com o código atual, pois `medico_id` é NOT NULL.

Se acontecer, há um problema sério que precisa ser investigado.

### Problema C: Agendamentos com `medico_id` inválido

**Sintoma**: Script mostra "Agendamentos com medico_id inválido"

**Solução**: Corrigir os IDs

```sql
-- Verificar agendamentos órfãos
SELECT a.id, a.medico_id, a.nome_paciente, a.inicio
FROM agendamentos a
LEFT JOIN medicos m ON a.medico_id = m.id
WHERE m.id IS NULL;

-- Se necessário, deletar agendamentos órfãos (CUIDADO!)
-- DELETE FROM agendamentos WHERE medico_id NOT IN (SELECT id FROM medicos);
```

---

## ✅ PASSO 3: Atualizar o Código no Railway

Certifique-se que o código corrigido está implantado no Railway:

1. **Commit e Push**
   ```bash
   git add .
   git commit -m "Fix: Remover limite de 30 dias no painel médico"
   git push origin main
   ```

2. **Verificar Deploy**
   - Railway deve fazer deploy automaticamente
   - Aguarde o deploy completar

3. **Reiniciar o serviço (se necessário)**
   - No Railway, vá em Settings
   - Clique em "Restart"

---

## ✅ PASSO 4: Teste Manual

1. **Login como médico**
   - Acesse: `https://seu-app.railway.app/auth/login`
   - Faça login com credenciais de médico

2. **Acessar Painel Médico**
   - Vá em: `https://seu-app.railway.app/painel-medico`
   - Verifique se os agendamentos aparecem

3. **Verificar Logs**
   ```bash
   # No Railway, veja os logs em tempo real
   # Procure por linhas como:
   # "Médico encontrado: ID=X"
   # "Total de agendamentos encontrados: Y"
   # "Agendamentos futuros: Z"
   ```

---

## ✅ PASSO 5: Criar Teste Completo

Execute este teste no Railway:

```python
# teste_agendamentos_railway.py
from main import app
from models import User, Medico, Agendamento
from datetime import datetime, timedelta

with app.app_context():
    # 1. Buscar um médico
    medico = Medico.query.first()
    if not medico:
        print("❌ Nenhum médico encontrado!")
    else:
        print(f"✅ Médico: {medico.usuario.nome} (ID: {medico.id})")
        
        # 2. Buscar agendamentos deste médico
        agendamentos = Agendamento.query.filter_by(medico_id=medico.id).all()
        print(f"✅ Total de agendamentos: {len(agendamentos)}")
        
        # 3. Filtrar futuros
        agora = datetime.utcnow()
        futuros = [a for a in agendamentos if a.inicio >= agora]
        print(f"✅ Agendamentos futuros: {len(futuros)}")
        
        if futuros:
            for ag in futuros[:3]:
                print(f"   - {ag.inicio} | {ag.nome_paciente}")
```

---

## 📊 Queries Úteis para Railway

### Ver todos os agendamentos com informações completas
```sql
SELECT 
    a.id,
    a.medico_id,
    m.crm,
    u.nome as medico_nome,
    a.nome_convidado as paciente,
    a.inicio,
    a.status,
    a.origem
FROM agendamentos a
LEFT JOIN medicos m ON a.medico_id = m.id
LEFT JOIN users u ON m.user_id = u.id
ORDER BY a.inicio DESC
LIMIT 20;
```

### Ver médicos e quantidade de agendamentos
```sql
SELECT 
    m.id,
    m.crm,
    u.nome,
    COUNT(a.id) as total_agendamentos,
    COUNT(CASE WHEN a.inicio >= NOW() THEN 1 END) as futuros
FROM medicos m
JOIN users u ON m.user_id = u.id
LEFT JOIN agendamentos a ON a.medico_id = m.id
GROUP BY m.id, m.crm, u.nome
ORDER BY total_agendamentos DESC;
```

---

## 🚨 Checklist Final

- [ ] Script de diagnóstico executado
- [ ] Médicos têm perfis na tabela `medicos`
- [ ] Agendamentos têm `medico_id` válido
- [ ] Código atualizado implantado no Railway
- [ ] Teste manual realizado com sucesso
- [ ] Médico consegue ver agendamentos no painel

---

## 💡 Dica

Se após todos os passos ainda não funcionar, verifique:

1. **Sessão do médico**: Faça logout e login novamente
2. **Cache**: Limpe o cache do navegador (Ctrl+Shift+Delete)
3. **Banco correto**: Certifique-se que está conectando no banco do Railway
4. **Variável DATABASE_URL**: Verifique se está configurada corretamente no Railway

---

## 📞 Precisa de Ajuda?

Execute o diagnóstico e me envie a saída completa para análise detalhada.
