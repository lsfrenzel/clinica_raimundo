# Clínica Dr. Raimundo Nunes - Sistema de Gestão Médica

## Visão Geral
Sistema completo de gestão para clínica médica especializada em ginecologia e obstetrícia, com chatbot inteligente para agendamento de consultas, painel administrativo e gestão de pacientes.

## Estado Atual do Projeto ✅
- **Sistema Totalmente Funcional**: Chatbot, agendamentos, painel admin
- **Database Populado**: 9 especialidades, 5 médicos, 448 slots de agendamento
- **Chatbot IA**: Gemini API configurado com sistema rule-based como fallback
- **Agendamentos**: Funcionando perfeitamente via chatbot
- **Replit Environment**: Configurado e funcionando com PostgreSQL integrado
- **Design Revolucionário**: Interface moderna com animações, gradientes e UX excepcional ✨

## 🎨 Design Moderno Implementado (14/10/2025)

### Melhorias de Interface
- ✅ **Template Base**: Navbar responsivo com gradientes, botão WhatsApp flutuante, footer moderno
- ✅ **Animações**: AOS (Animate On Scroll) para transições suaves em todos os elementos
- ✅ **Cores**: Paleta customizada com teal (#4B7D7B), emerald (#50C6A5) e gold (#C5A88D)
- ✅ **Tipografia**: Fontes premium (Playfair Display, Lato, Montserrat)

### Páginas Redesenhadas
1. **Homepage (index.html)**:
   - Hero section com gradientes animados e padrões de fundo
   - Cards interativos com efeitos hover 3D
   - Seção "Como Agendar" em 3 passos ilustrados
   - Grid de especialidades e médicos com animações
   - CTAs impactantes com gradientes multi-color

2. **Especialidades e Médicos**:
   - Hero sections com backgrounds animados
   - Cards com bordas gradient e hover effects
   - Layout responsivo otimizado para mobile/desktop
   - Informações organizadas e visualmente atraentes

3. **Autenticação (Login/Cadastro)**:
   - Design em 2 colunas com branding à esquerda
   - Formulários modernos com ícones inline
   - Glassmorphism effects e gradientes suaves
   - Totalmente responsivo e acessível

### Tecnologias Frontend
- **Tailwind CSS**: Framework utility-first via CDN
- **AOS Library**: Animações on-scroll suaves
- **Custom CSS**: Gradientes, hover effects, transições
- **Responsive Design**: Mobile-first com breakpoints otimizados

### Próximas Melhorias Recomendadas
1. **Performance**: Substituir Tailwind CDN por build local para produção
2. **Otimização**: Auditar densidade de animações para dispositivos móveis
3. **Caching**: Implementar lazy-loading e headers de cache para assets

## Funcionalidades Principais

### 🤖 Chatbot Inteligente
- **IA Gemini**: Resposta natural e inteligente
- **Sistema Rule-Based**: Fallback robusto para garantir funcionamento
- **Fluxo Completo**: Especialidade → Médico → Horário → Dados → Confirmação
- **Agendamento Automático**: Criação direta no banco de dados
- **Multi-contexto**: Suporte a usuários autenticados e visitantes

### 🏥 Painel Administrativo  
- **Gestão de Agendamentos**: Visualizar, editar, cancelar
- **Controle de Médicos**: Cadastro e especialidades
- **Horários**: Configuração de agenda médica
- **Relatórios**: Acompanhamento de consultas

### 👥 Gestão de Pacientes
- **Cadastro Completo**: Dados pessoais e histórico
- **Integração**: Usuários autenticados + visitantes
- **Segurança**: Senhas criptografadas com bcrypt

## Tecnologias

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados principal
- **Gemini API**: Inteligência artificial conversacional
- **Flask-Login**: Sistema de autenticação

### Frontend
- **Jinja2**: Templates dinâmicos
- **Bootstrap**: Interface responsiva
- **JavaScript**: Interatividade do chatbot
- **CSS**: Estilização personalizada

## Arquitetura do Chatbot

### Sistema Híbrido Inteligente
1. **Gemini API** (Principal): IA conversacional avançada
2. **Rule-Based** (Fallback): Sistema robusto de regras
3. **Processamento de Ações**: Unificado para ambos sistemas

### Fluxo de Agendamento
```
Usuário → Especialidade → Médico → Horário → Dados → Confirmação → DB
```

### Ações Disponíveis
- `get_specialties`: Listar especialidades
- `select_specialty`: Processar especialidade escolhida  
- `show_doctors`: Mostrar médicos
- `select_doctor`: Processar médico escolhido
- `show_schedules`: Mostrar horários
- `select_schedule`: Processar horário
- `collect_patient_data`: Coletar dados do paciente
- `confirm_booking`: Confirmar dados
- `create_booking`: Criar agendamento no sistema

## Resolução de Problemas Recentes

### ✅ Problema: Painel Médico não mostrava agendamentos (21/10/2025)
**Causa**: 
- Query com filtro de data no SQL sem considerar timezone UTC
- Ordem incorreta (mais distantes primeiro em vez de próximos)
- Falta de conversão de timezone para exibição
- Lógica diferente de "Meus Agendamentos" (que funcionava corretamente)

**Solução**:
- ✅ Replicada a lógica bem-sucedida de "Meus Agendamentos"
- ✅ Query busca TODOS os agendamentos do médico
- ✅ Filtragem de próximos 30 dias feita em memória (com UTC)
- ✅ Conversão UTC → Brasília para exibição (`inicio_local`, `fim_local`)
- ✅ Ordenação cronológica (próximos primeiro)
- ✅ Logging detalhado para diagnóstico
- ✅ Template atualizado com horários locais e indicação de fuso

**Resultados**:
- Painel médico agora mostra agendamentos corretamente
- Estatísticas precisas (próximos 30 dias)
- Horários exibidos em horário de Brasília
- Lógica consistente entre painel médico e paciente

### ✅ Problema: Agendamentos não aparecem em "Meus Agendamentos" (14/10/2025)
**Causa**: 
- Conflito de timezone entre horário local e UTC
- Agendamentos salvos com datetime naive (sem timezone) do formulário HTML
- Comparação feita com `datetime.utcnow()` causava classificação incorreta
- Agendamentos futuros apareciam como passados devido à diferença de fuso horário

**Solução**:
- ✅ Implementada conversão de horário de Brasília (UTC-3) para UTC ao salvar agendamentos
- ✅ Todos os datetimes armazenados consistentemente em UTC no banco de dados
- ✅ Conversão de UTC para horário de Brasília na exibição para o usuário
- ✅ Campos temporários `inicio_local` e `fim_local` adicionados para renderização
- ✅ Template atualizado para exibir horários no timezone correto com indicação "(horário de Brasília)"
- ✅ Logging detalhado adicionado para debug de agendamentos
- ✅ Validação e tratamento de erros melhorados

**Resultados**:
- Agendamentos agora aparecem corretamente em "Próximas Consultas"
- Horários exibidos no fuso correto para o usuário (Brasília)
- Comparações de data/hora consistentes (UTC vs UTC)
- Sistema robusto com melhor observabilidade via logs

### ✅ Problema: Erro "Internal Server Error" em "Meus Agendamentos" no Railway (14/10/2025)
**Causa**:
- Conflito de importação de `timezone` (tentativa de usar atributo em instância)
- Rotas faltantes: `appointments.detalhes` e `appointments.cancelar`
- Template `detalhes.html` não existia

**Solução**:
- ✅ Corrigido conflito de importação renomeando `timezone` para `tz`
- ✅ Criada rota `/detalhes/<int:agendamento_id>` com conversão de timezone
- ✅ Criada rota `/cancelar/<int:agendamento_id>` com validação de 24h
- ✅ Criado template `detalhes.html` completo
- ✅ Validações de segurança (verificação de propriedade do agendamento)

**Resultados**:
- Página "Meus Agendamentos" funciona corretamente
- Usuários podem visualizar detalhes completos de agendamentos
- Sistema de cancelamento funcional com regra de 24h
- Todas as rotas do template resolvem corretamente

### ✅ Problema: Chatbot não acessava banco de dados corretamente (02/10/2025)
**Causa**: 
- Função `get_doctor_schedules` gerava horários simulados em vez de buscar da tabela `agendas`
- Sistema rule-based não detectava especialidades/médicos específicos do banco
- Falta de priorização na detecção de entidades do banco de dados

**Solução**:
- ✅ Corrigida função `get_doctor_schedules` para buscar horários REAIS da tabela `agendas`
- ✅ Adicionada verificação prioritária de especialidades do banco antes de outras regras
- ✅ Adicionada verificação prioritária de médicos do banco antes de outras regras
- ✅ Melhorado logging para debug de acesso ao banco (DEBUG logs)
- ✅ Testado e validado: 18 horários disponíveis encontrados para Dr. Raimundo Nunes

**Resultados**:
- 9 especialidades carregadas corretamente do banco
- 5 médicos listados adequadamente
- 28 agendas encontradas no banco de dados
- 18 horários disponíveis retornados corretamente
- Detecção inteligente de especialidades e médicos mencionados pelo usuário

### ✅ Problema anterior: Chatbot não criava agendamentos
**Causa**: Sistema rule-based não tinha lógica completa de agendamento
**Solução**: 
- Expandido sistema rule-based com fluxo completo
- Melhorada lógica de reconhecimento de especialidades/médicos
- Implementada transição correta para `create_booking`
- Testado e validado: Agendamento ID 12 criado com sucesso

### ✅ Melhoria: Sistema de Fallback Robusto
- Rule-based agora processa agendamentos completos
- Funciona mesmo quando Gemini API falha
- Mantém qualidade de experiência
- Acessa banco de dados PostgreSQL corretamente

### ✅ API do Gemini Configurada e Funcionando (02/10/2025)
**Status**: GEMINI_API_KEY configurada e ativa ✅

**Testes realizados**:
- ✅ Inicialização: Gemini client criado com sucesso
- ✅ Processamento: Todas as mensagens processadas pelo Gemini
- ✅ Contexto: Conversação mantida corretamente
- ✅ Integração: Banco de dados PostgreSQL acessado (18 horários disponíveis)
- ✅ Fluxo completo: Agendamento funcionando do início ao fim

**Logs de confirmação**:
```
[DEBUG] ✅ API PRIMÁRIA: GEMINI
[DEBUG] 🤖 Usando GEMINI API para processar mensagem
```

**Arquitetura atual**:
- 1ª opção: Gemini API (Google AI) - **ATIVA** ✅
- 2ª opção: OpenAI API (GPT) - Fallback
- 3ª opção: Rule-based system - Backup

## Configuração e Deploy

### Opções de Hospedagem

#### 🔷 Replit (Desenvolvimento)
- **Workflow**: Flask App rodando em 0.0.0.0:5000
- **Deploy**: Configurado para autoscale com Gunicorn
- **Proxy**: ProxyFix configurado para ambiente Replit
- **Database**: PostgreSQL integrado do Replit

#### 🚂 Railway (Produção) - **Recomendado**
- **Configuração**: Veja [README_RAILWAY.md](README_RAILWAY.md) para guia completo
- **Database**: PostgreSQL gerenciado
- **Deploy**: Automático via GitHub
- **Domínio**: Gerado automaticamente (.up.railway.app)
- **População Automática**: O banco é populado automaticamente no primeiro deploy via `scripts/auto_migrate.py`
- **Script Manual**: Se necessário, execute `railway run python popular_railway.py`

### Variáveis de Ambiente Requeridas
- `DATABASE_URL`: Conexão PostgreSQL (configurado automaticamente)
- `SESSION_SECRET`: Chave para sessões Flask
- `GEMINI_API_KEY`: Chave da API Gemini (opcional - fallback rule-based ativo)
- `PORT`: Porta do servidor (configurado automaticamente)

### Comandos de Execução
```bash
# Desenvolvimento Local/Replit
uv run python main.py

# Produção (Replit)
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app

# Produção (Railway)
gunicorn --bind 0.0.0.0:$PORT main:app
```

### Banco de Dados

#### Desenvolvimento (Replit)
- **Schema**: SQLAlchemy models (criados automaticamente)
- **População**: Script `scripts/seed_data.py`
- **Conexão**: PostgreSQL via DATABASE_URL do Replit
- **Inicialização**: Execute `python scripts/seed_data.py` para popular dados

#### Produção (Railway)
- **População Automática**: O script `scripts/auto_migrate.py` roda automaticamente no deploy
- **Arquivo de Configuração**: `nixpacks.toml` define o comando de inicialização
- **População Manual**: Se necessário, execute `railway run python popular_railway.py`
- **Documentação**: Veja [README_RAILWAY.md](README_RAILWAY.md) e [COMO_POPULAR_BANCO_RAILWAY.md](COMO_POPULAR_BANCO_RAILWAY.md)

## Próximas Melhorias Sugeridas
1. **Notificações**: SMS/Email de confirmação
2. **Pagamentos**: Integração com gateway de pagamento
3. **Relatórios**: Dashboard analítico avançado
4. **Mobile**: App nativo ou PWA
5. **Telemedicina**: Consultas online integradas

## Status de Testes
- ✅ Agendamento via chatbot funcionando
- ✅ Banco de dados populado e funcional
- ✅ Painel administrativo operacional
- ✅ Sistema de fallback testado e aprovado
- ✅ Fluxo completo de usuário validado

## Credenciais de Acesso (Desenvolvimento)
- **Admin**: admin@clinicadrraimundonunes.com.br / admin123
- **Médicos**: [email do médico] / medico123
- **Pacientes**: [email do paciente] / paciente123

---
**Última atualização**: 02/10/2025 - Sistema integrado ao Replit com PostgreSQL e deploy configurado