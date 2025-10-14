# 🔧 Correção: Médicos não aparecem no agendamento

## Problema
Os médicos não estão aparecendo nas páginas de agendamento porque:
1. Os médicos não estão associados às especialidades no banco do Railway
2. Ou não existem médicos cadastrados no banco

## Solução Rápida

### Opção 1: Executar script de diagnóstico e correção (RECOMENDADO)

1. **No Railway, adicione a variável de ambiente DATABASE_URL**
   - Vá em Variables
   - Copie a URL do PostgreSQL (exemplo: `postgresql://postgres:senha@servidor.railway.app:5432/railway`)

2. **Execute o script de diagnóstico**
   ```bash
   export DATABASE_URL="sua-url-do-railway-postgres-aqui"
   python diagnosticar_railway.py
   ```

3. **O script vai:**
   - ✅ Verificar todas as tabelas
   - ✅ Mostrar quantos médicos existem
   - ✅ Corrigir associações entre médicos e especialidades
   - ✅ Criar agendas futuras se necessário

### Opção 2: Popular banco do zero

Se o banco estiver vazio, execute:

```bash
export DATABASE_URL="sua-url-do-railway-postgres-aqui"
python popular_railway.py
```

Este script vai criar:
- ✅ 9 especialidades
- ✅ 5 médicos
- ✅ Associações corretas
- ✅ 30 dias de agenda para cada médico

## URLs para testar depois

Após executar o script, teste estas URLs:

- https://clinicaraimundo-production.up.railway.app/appointments/medicos/1
- https://clinicaraimundo-production.up.railway.app/appointments/medicos/2
- https://clinicaraimundo-production.up.railway.app/appointments/medicos/3

Cada especialidade deve mostrar os médicos disponíveis!

## Credenciais de Acesso

**Admin:**
- Email: admin@clinicadrraimundonunes.com.br
- Senha: admin123

**Médicos:**
- Email: raimundo.nunes@clinicadrraimundonunes.com.br
- Senha: medico123

(E outros médicos com padrão similar)

## Se ainda não funcionar

Verifique se:
1. A variável DATABASE_URL está correta
2. O banco PostgreSQL do Railway está ativo
3. As tabelas foram criadas (o script cria automaticamente)
