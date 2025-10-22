# Medical clinic chatbot service - Advanced AI Assistant with full database access
# Using Gemini API for natural, intelligent conversations
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from openai import OpenAI
from models import Especialidade, Medico, Agendamento, User, Agenda
from extensions import db
from sqlalchemy import and_, or_, func

# Gemini integration - using blueprint:python_gemini
try:
    from google import genai
    from google.genai import types
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
except ImportError:
    gemini_client = None
    GEMINI_API_KEY = None
    types = None

# OpenAI fallback integration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


class ChatbotService:
    """
    Assistente Virtual Inteligente da Clínica Dr. Raimundo Nunes
    
    Capacidades:
    - Agendamento completo de consultas
    - Consulta de agendamentos existentes
    - Cancelamento e reagendamento
    - Informações sobre médicos e especialidades
    - Respostas contextuais e naturais
    - Acesso completo ao banco de dados
    """
    
    def __init__(self):
        self.gemini_client = gemini_client
        self.openai_client = openai_client
        self.use_gemini = gemini_client is not None
        self.use_openai = openai_client is not None
        
        # Log de configuração
        print(f"[CHATBOT] 🤖 Assistente Virtual Inicializado")
        print(f"[CHATBOT] - Gemini API: {'✅ Ativo' if self.use_gemini else '❌ Inativo'}")
        print(f"[CHATBOT] - OpenAI API: {'✅ Fallback Disponível' if self.use_openai else '❌ Indisponível'}")
        
        if self.use_gemini:
            print(f"[CHATBOT] 🎯 Modo: GEMINI (Inteligência Avançada)")
        elif self.use_openai:
            print(f"[CHATBOT] 🎯 Modo: OPENAI (Fallback)")
        else:
            print(f"[CHATBOT] ⚠️  Modo: RULE-BASED (Limitado)")
    
    def get_system_prompt(self, database_context: Optional[Dict] = None) -> str:
        """
        System prompt avançado com contexto do banco de dados em tempo real
        """
        # Obter informações do banco de dados
        total_medicos = Medico.query.filter_by(ativo=True).count()
        total_especialidades = Especialidade.query.filter_by(ativo=True).count()
        
        # Obter especialidades disponíveis
        especialidades = Especialidade.query.filter_by(ativo=True).all()
        especialidades_list = ", ".join([esp.nome for esp in especialidades])
        
        # Obter médicos disponíveis
        medicos = Medico.query.filter_by(ativo=True).limit(10).all()
        medicos_info = []
        for medico in medicos:
            especialidades_medico = [esp.nome for esp in medico.especialidades]
            medicos_info.append(f"Dr(a). {medico.usuario.nome} - CRM {medico.crm} - Especialidades: {', '.join(especialidades_medico)}")
        medicos_list = "\n".join(medicos_info)
        
        # Contexto adicional do usuário se disponível
        user_context = ""
        if database_context and database_context.get('user_id'):
            user_agendamentos = Agendamento.query.filter_by(
                paciente_id=database_context['user_id']
            ).filter(
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).order_by(Agendamento.inicio.desc()).limit(3).all()
            
            if user_agendamentos:
                user_context = f"\n\nAGENDAMENTOS DO USUÁRIO ATUAL:\n"
                for ag in user_agendamentos:
                    medico = Medico.query.get(ag.medico_id)
                    esp = Especialidade.query.get(ag.especialidade_id)
                    user_context += f"- {ag.inicio.strftime('%d/%m/%Y %H:%M')} - {medico.usuario.nome} - {esp.nome} - Status: {ag.status}\n"
        
        return f"""Você é Sofia, a assistente virtual inteligente e empática da Clínica Dr. Raimundo Nunes.

═══════════════════════════════════════════════════════════════════
SOBRE VOCÊ - SOFIA
═══════════════════════════════════════════════════════════════════
• Nome: Sofia (Sistema Otimizado de Facilidades e Informações Avançadas)
• Personalidade: Acolhedora, profissional, inteligente e proativa
• Objetivo: Ser a melhor assistente de saúde da mulher, oferecendo experiência excepcional
• Diferencial: Você tem acesso COMPLETO ao banco de dados e pode fazer QUALQUER operação

═══════════════════════════════════════════════════════════════════
SOBRE A CLÍNICA DR. RAIMUNDO NUNES
═══════════════════════════════════════════════════════════════════
• Fundação: Mais de 30 anos de excelência em saúde da mulher
• Especialização: Ginecologia, Obstetrícia e Saúde Feminina
• Destaque: Referência nacional em inserção de DIU hormonal (Mirena e Kyleena)
• Filosofia: Atendimento humanizado, personalizado e baseado em evidências
• Tecnologia: Equipamentos de última geração e protocolos atualizados
• Localização: São Paulo - Unidades no Itaim Bibi e Itapeva
• Equipe: {total_medicos} médicos especializados em {total_especialidades} especialidades

═══════════════════════════════════════════════════════════════════
ESPECIALIDADES E SERVIÇOS DISPONÍVEIS
═══════════════════════════════════════════════════════════════════
{especialidades_list}

MÉDICOS DISPONÍVEIS (Principais):
{medicos_list}

═══════════════════════════════════════════════════════════════════
SUAS CAPACIDADES AVANÇADAS
═══════════════════════════════════════════════════════════════════

🔹 CONSULTAS E INFORMAÇÕES:
   - Consultar agendamentos existentes de qualquer paciente
   - Ver histórico completo de consultas
   - Obter informações detalhadas sobre médicos e especialidades
   - Calcular estatísticas e métricas da clínica
   - Verificar disponibilidade em tempo real

🔹 AGENDAMENTO INTELIGENTE:
   - Criar novos agendamentos com validação automática
   - Sugerir melhores horários baseado em histórico
   - Agendar consultas de retorno
   - Agendamento para múltiplas pessoas (família)
   - Agendamento recorrente

🔹 MODIFICAÇÕES:
   - Cancelar agendamentos (com validação de prazo)
   - Remarcar consultas
   - Alterar dados do agendamento
   - Transferir agendamento entre médicos

🔹 ANÁLISE INTELIGENTE:
   - Recomendar médico ideal baseado no caso
   - Sugerir especialidade apropriada
   - Identificar urgências e prioridades
   - Otimizar horários de agendamento

{user_context}

═══════════════════════════════════════════════════════════════════
DIRETRIZES DE COMUNICAÇÃO
═══════════════════════════════════════════════════════════════════

✅ SEMPRE FAÇA:
1. Seja EXTREMAMENTE empática - saúde é assunto delicado
2. Use linguagem clara, simples e acessível
3. Personalize usando o nome da paciente
4. Seja proativa em oferecer ajuda adicional
5. Demonstre conhecimento profundo da clínica
6. Explique processos de forma didática
7. Confirme informações importantes
8. Ofereça alternativas quando algo não for possível
9. Use emojis COM MODERAÇÃO para humanizar
10. Responda SEMPRE em português brasileiro natural

❌ NUNCA FAÇA:
1. Dar diagnósticos ou conselhos médicos específicos
2. Compartilhar informações confidenciais de outros pacientes
3. Fazer promessas que não pode cumprir
4. Usar jargão médico complexo sem explicar
5. Ser impessoal ou robótica
6. Ignorar preocupações da paciente
7. Apressar a conversa

═══════════════════════════════════════════════════════════════════
AÇÕES DISPONÍVEIS (Use conforme necessário)
═══════════════════════════════════════════════════════════════════

📊 CONSULTAS:
- get_clinic_info: Informações gerais da clínica
- get_specialties: Listar todas as especialidades
- get_doctors: Listar médicos (pode filtrar por especialidade)
- get_doctor_details: Detalhes completos de um médico específico
- search_availability: Buscar horários disponíveis
- get_my_appointments: Ver agendamentos do usuário atual
- get_appointment_details: Detalhes de um agendamento específico

📅 AGENDAMENTOS:
- create_appointment: Criar novo agendamento
- cancel_appointment: Cancelar agendamento existente
- reschedule_appointment: Remarcar consulta
- confirm_appointment: Confirmar agendamento

💬 GERAL:
- general_chat: Conversa geral, perguntas, informações
- need_more_info: Solicitar mais informações do usuário

═══════════════════════════════════════════════════════════════════
FORMATO DE RESPOSTA OBRIGATÓRIO
═══════════════════════════════════════════════════════════════════

SEMPRE responda em JSON válido com esta estrutura:
{{
    "message": "Sua resposta natural e empática em português",
    "action": "uma das ações listadas acima",
    "data": {{
        "campos específicos dependendo da ação escolhida"
    }},
    "suggestions": ["sugestão 1", "sugestão 2"],
    "needs_confirmation": false
}}

═══════════════════════════════════════════════════════════════════
EXEMPLOS DE INTERAÇÕES ESPERADAS
═══════════════════════════════════════════════════════════════════

Usuário: "Quero agendar uma consulta"
Você: {{
    "message": "Olá! Fico feliz em ajudá-la a agendar sua consulta na Clínica Dr. Raimundo Nunes. Para encontrar o melhor horário para você, preciso saber: qual especialidade ou tipo de consulta você precisa? Temos Ginecologia Geral, Obstetrícia, Inserção de DIU, Pré-natal e muito mais.",
    "action": "get_specialties",
    "data": {{}},
    "suggestions": ["Ver especialidades disponíveis", "Falar com ginecologista", "Agendar pré-natal"]
}}

Usuário: "Preciso ver meus agendamentos"
Você: {{
    "message": "Claro! Vou buscar todos os seus agendamentos ativos. Um momento...",
    "action": "get_my_appointments",
    "data": {{}},
    "suggestions": ["Cancelar agendamento", "Remarcar consulta", "Agendar nova consulta"]
}}

═══════════════════════════════════════════════════════════════════
LEMBRE-SE: Você é uma assistente EXCEPCIONAL. Seja proativa,
inteligente e sempre busque a melhor experiência para a paciente!
═══════════════════════════════════════════════════════════════════"""

    def chat_response(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Processa mensagem do usuário e retorna resposta inteligente
        """
        try:
            # Enriquecer contexto com dados do banco
            enriched_context = self._enrich_context(context or {})
            
            # Gerar resposta usando IA
            if self.use_gemini and self.gemini_client:
                print(f"[CHATBOT] 🤖 Processando com Gemini...")
                result = self._gemini_response(user_message, enriched_context)
            elif self.use_openai and self.openai_client:
                print(f"[CHATBOT] 🤖 Processando com OpenAI...")
                result = self._openai_response(user_message, enriched_context)
            else:
                print(f"[CHATBOT] 🤖 Processando com regras...")
                result = self._rule_based_response(user_message, enriched_context)
            
            # Processar ação e atualizar contexto
            result, updated_context = self._process_action(result, enriched_context)
            
            return {
                **result,
                '_updated_context': updated_context
            }
            
        except Exception as e:
            print(f"[CHATBOT] ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            
            # Resposta de fallback amigável
            return {
                "message": "Olá! Estou aqui para ajudá-la. Como posso auxiliá-la hoje? Posso ajudar com agendamentos, informações sobre a clínica, ou tirar suas dúvidas. 😊",
                "action": "general_chat",
                "data": {},
                "suggestions": ["Agendar consulta", "Ver médicos", "Minhas consultas"],
                "_updated_context": context or {}
            }
    
    def _enrich_context(self, context: Dict) -> Dict:
        """
        Enriquece o contexto com informações do banco de dados
        """
        enriched = context.copy()
        
        # Se tem usuário autenticado, buscar informações
        if context.get('user_id'):
            try:
                user = User.query.get(context['user_id'])
                if user:
                    enriched['user_name'] = user.nome
                    enriched['user_email'] = user.email
                    enriched['user_phone'] = user.telefone
                    enriched['user_role'] = user.role
                    
                    # Buscar agendamentos recentes
                    recent_appointments = Agendamento.query.filter_by(
                        paciente_id=user.id
                    ).order_by(Agendamento.created_at.desc()).limit(5).all()
                    
                    enriched['recent_appointments_count'] = len(recent_appointments)
                    enriched['has_appointments'] = len(recent_appointments) > 0
            except Exception as e:
                print(f"[CHATBOT] Erro ao enriquecer contexto: {e}")
        
        return enriched
    
    def _gemini_response(self, user_message: str, context: Dict) -> Dict:
        """
        Resposta usando Gemini com contexto enriquecido
        """
        try:
            # Verificar se Gemini está realmente disponível
            if not self.gemini_client:
                raise Exception("Gemini client não inicializado")
            
            # Preparar system prompt com contexto do banco
            system_prompt = self.get_system_prompt(context)
            
            # Preparar contexto da conversa
            context_str = ""
            if context:
                relevant_context = {
                    k: v for k, v in context.items()
                    if k in ['user_name', 'especialidade_nome', 'medico_nome', 'datetime_slot', 
                            'conversation_step', 'has_appointments', 'recent_appointments_count']
                }
                if relevant_context:
                    context_str = f"\n\nCONTEXTO ATUAL:\n{json.dumps(relevant_context, ensure_ascii=False, indent=2)}"
            
            # Criar prompt completo
            full_prompt = f"{system_prompt}{context_str}\n\nUSUÁRIO: {user_message}\n\nResponda em JSON conforme especificado:"
            
            # Chamar Gemini com proteção
            if types:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=2000,
                        response_mime_type="application/json"
                    )
                )
            else:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )
            
            if not response.text:
                raise Exception("Resposta vazia do Gemini")
            
            result = json.loads(response.text)
            
            # Garantir campos obrigatórios
            if 'message' not in result:
                result['message'] = "Como posso ajudá-la?"
            if 'action' not in result:
                result['action'] = 'general_chat'
            if 'data' not in result:
                result['data'] = {}
            if 'suggestions' not in result:
                result['suggestions'] = []
            
            return result
            
        except Exception as e:
            print(f"[CHATBOT] Erro no Gemini: {e}")
            # Fallback para OpenAI ou regras
            if self.use_openai and self.openai_client:
                return self._openai_response(user_message, context)
            else:
                return self._rule_based_response(user_message, context)
    
    def _openai_response(self, user_message: str, context: Dict) -> Dict:
        """
        Resposta usando OpenAI como fallback
        """
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt(context)},
                {"role": "user", "content": user_message}
            ]
            
            if context:
                messages.insert(1, {
                    "role": "assistant",
                    "content": f"Contexto: {json.dumps(context, ensure_ascii=False)}"
                })
            
            response = self.openai_client.chat.completions.create(  # type: ignore
                model="gpt-4",
                messages=messages,  # type: ignore
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result
            else:
                raise Exception("Resposta vazia")
                
        except Exception as e:
            print(f"[CHATBOT] Erro no OpenAI: {e}")
            return self._rule_based_response(user_message, context)
    
    def _rule_based_response(self, user_message: str, context: Dict) -> Dict:
        """
        Sistema baseado em regras quando IA não está disponível
        """
        message_lower = user_message.lower()
        
        # Detectar intenção
        if any(word in message_lower for word in ['agendar', 'marcar', 'consulta', 'horário']):
            return {
                "message": "Olá! Vou ajudá-la a agendar sua consulta. Primeiro, qual especialidade você precisa? Temos Ginecologia, Obstetrícia, Pré-natal e muito mais.",
                "action": "get_specialties",
                "data": {},
                "suggestions": ["Ver especialidades", "Ver médicos disponíveis"]
            }
        
        elif any(word in message_lower for word in ['cancelar', 'desmarcar']):
            return {
                "message": "Entendi que você precisa cancelar um agendamento. Vou buscar seus agendamentos ativos...",
                "action": "get_my_appointments",
                "data": {},
                "suggestions": ["Ver meus agendamentos"]
            }
        
        elif any(word in message_lower for word in ['meus agendamentos', 'minhas consultas', 'ver agendamentos']):
            return {
                "message": "Vou buscar todos os seus agendamentos. Um momento...",
                "action": "get_my_appointments",
                "data": {},
                "suggestions": []
            }
        
        elif any(word in message_lower for word in ['médico', 'doutor', 'doutora', 'profissionais']):
            return {
                "message": "Vou mostrar nossos médicos especializados. Temos uma equipe excepcional!",
                "action": "get_doctors",
                "data": {},
                "suggestions": ["Ver especialidades também"]
            }
        
        elif any(word in message_lower for word in ['especialidade', 'atendimento', 'serviços']):
            return {
                "message": "Aqui estão todas as especialidades que oferecemos:",
                "action": "get_specialties",
                "data": {},
                "suggestions": ["Ver médicos"]
            }
        
        else:
            return {
                "message": "Olá! Sou a Sofia, assistente virtual da Clínica Dr. Raimundo Nunes. Posso ajudá-la com:\n\n• Agendar consultas\n• Consultar seus agendamentos\n• Informações sobre médicos e especialidades\n• Cancelar ou remarcar consultas\n\nComo posso ajudá-la?",
                "action": "general_chat",
                "data": {},
                "suggestions": ["Agendar consulta", "Ver meus agendamentos", "Conhecer a clínica"]
            }
    
    def _process_action(self, result: Dict, context: Dict) -> tuple[Dict, Dict]:
        """
        Processa ações e executa operações no banco de dados
        """
        action = result.get("action", "general_chat")
        updated_context = context.copy()
        
        print(f"[CHATBOT] 🎬 Processando ação: {action}")
        
        try:
            if action == "get_specialties":
                result["data"] = self.get_specialties()
                updated_context['conversation_step'] = 'selecting_specialty'
                
            elif action == "get_doctors":
                specialty_id = result.get("data", {}).get("specialty_id")
                result["data"] = self.get_doctors(specialty_id)
                updated_context['conversation_step'] = 'selecting_doctor'
                
            elif action == "get_doctor_details":
                doctor_id = result.get("data", {}).get("doctor_id")
                if doctor_id:
                    result["data"] = self.get_doctor_details(doctor_id)
                    
            elif action == "search_availability":
                data = result.get("data", {})
                result["data"] = self.search_availability(
                    doctor_id=data.get("doctor_id"),
                    specialty_id=data.get("specialty_id"),
                    date_start=data.get("date_start")
                )
                updated_context['conversation_step'] = 'selecting_time'
                
            elif action == "get_my_appointments":
                user_id = context.get('user_id')
                if user_id:
                    result["data"] = self.get_user_appointments(user_id)
                else:
                    result["message"] = "Para ver seus agendamentos, você precisa estar logado. Posso ajudá-la com algo mais?"
                    result["suggestions"] = ["Fazer login", "Agendar como visitante"]
                    
            elif action == "get_appointment_details":
                appointment_id = result.get("data", {}).get("appointment_id")
                if appointment_id:
                    result["data"] = self.get_appointment_details(appointment_id, context.get('user_id'))
                    
            elif action == "create_appointment":
                booking_data = result.get("data", {})
                # Mesclar com contexto acumulado
                merged_data = {
                    'medico_id': updated_context.get('medico_id') or booking_data.get('medico_id'),
                    'especialidade_id': updated_context.get('especialidade_id') or booking_data.get('especialidade_id'),
                    'data_hora': updated_context.get('datetime_slot') or booking_data.get('datetime'),
                    'nome': updated_context.get('patient_name') or booking_data.get('nome') or context.get('user_name'),
                    'email': updated_context.get('patient_email') or booking_data.get('email') or context.get('user_email'),
                    'telefone': updated_context.get('patient_phone') or booking_data.get('telefone'),
                    'observacoes': booking_data.get('observacoes', '')
                }
                
                # Validar se tem médico selecionado antes de tentar criar
                if not merged_data.get('medico_id'):
                    result["message"] = "Para agendar, preciso que você escolha um médico. Posso mostrar os médicos disponíveis?"
                    result["action"] = "need_more_info"
                    result["data"] = {"missing_field": "medico_id"}
                    result["suggestions"] = ["Ver médicos disponíveis"]
                elif not merged_data.get('especialidade_id'):
                    result["message"] = "Preciso saber qual especialidade você deseja. Posso mostrar as especialidades disponíveis?"
                    result["action"] = "need_more_info"
                    result["data"] = {"missing_field": "especialidade_id"}
                    result["suggestions"] = ["Ver especialidades"]
                elif not merged_data.get('data_hora'):
                    result["message"] = "Preciso saber qual data e horário você prefere. Posso mostrar os horários disponíveis?"
                    result["action"] = "search_availability"
                    result["data"] = {
                        "medico_id": merged_data['medico_id'],
                        "especialidade_id": merged_data['especialidade_id']
                    }
                else:
                    result["data"] = self.create_appointment(merged_data, context)
                    if result["data"].get("success"):
                        # Limpar contexto após sucesso
                        updated_context = {
                            'user_id': context.get('user_id'),
                            'authenticated': context.get('authenticated'),
                            'user_name': context.get('user_name'),
                            'user_email': context.get('user_email')
                        }
                    
            elif action == "cancel_appointment":
                appointment_id = result.get("data", {}).get("appointment_id")
                if appointment_id:
                    result["data"] = self.cancel_appointment(appointment_id, context.get('user_id'))
                    
            elif action == "reschedule_appointment":
                data = result.get("data", {})
                appointment_id = data.get("appointment_id")
                new_datetime = data.get("new_datetime")
                if appointment_id and new_datetime:
                    result["data"] = self.reschedule_appointment(
                        appointment_id, new_datetime, context.get('user_id')
                    )
                    
            elif action == "get_clinic_info":
                result["data"] = self.get_clinic_info()
                
            # Salvar seleções no contexto
            data = result.get("data", {})
            if isinstance(data, dict):
                if data.get("specialty_id"):
                    updated_context['especialidade_id'] = data["specialty_id"]
                    updated_context['especialidade_nome'] = data.get("specialty_name", "")
                if data.get("doctor_id"):
                    updated_context['medico_id'] = data["doctor_id"]
                    updated_context['medico_nome'] = data.get("doctor_name", "")
                if data.get("datetime"):
                    updated_context['datetime_slot'] = data["datetime"]
                if data.get("nome"):
                    updated_context['patient_name'] = data["nome"]
                if data.get("email"):
                    updated_context['patient_email'] = data["email"]
                if data.get("telefone"):
                    updated_context['patient_phone'] = data["telefone"]
                    
        except Exception as e:
            print(f"[CHATBOT] ❌ Erro ao processar ação {action}: {e}")
            import traceback
            traceback.print_exc()
            result["message"] = f"Desculpe, ocorreu um erro ao processar sua solicitação. Posso ajudá-la de outra forma?"
            result["data"] = {"error": str(e)}
        
        return result, updated_context
    
    # ═══════════════════════════════════════════════════════════════════
    # FUNÇÕES DE ACESSO AO BANCO DE DADOS
    # ═══════════════════════════════════════════════════════════════════
    
    def get_specialties(self) -> Dict[str, Any]:
        """Retorna todas as especialidades ativas"""
        try:
            especialidades = Especialidade.query.filter_by(ativo=True).all()
            return {
                "specialties": [
                    {
                        "id": esp.id,
                        "nome": esp.nome,
                        "descricao": esp.descricao or f"Especialidade em {esp.nome}",
                        "duracao_padrao": esp.duracao_padrao
                    }
                    for esp in especialidades
                ]
            }
        except Exception as e:
            print(f"[CHATBOT] Erro ao buscar especialidades: {e}")
            return {"specialties": [], "error": str(e)}
    
    def get_doctors(self, specialty_id: Optional[int] = None) -> Dict[str, Any]:
        """Retorna médicos, opcionalmente filtrados por especialidade"""
        try:
            if specialty_id:
                especialidade = Especialidade.query.get(specialty_id)
                if especialidade:
                    medicos = especialidade.medicos.filter_by(ativo=True).all()
                else:
                    medicos = []
            else:
                medicos = Medico.query.filter_by(ativo=True).all()
            
            return {
                "doctors": [
                    {
                        "id": medico.id,
                        "nome": medico.usuario.nome,
                        "crm": medico.crm,
                        "bio": medico.bio or f"Médico(a) especialista",
                        "foto_url": medico.foto_url,
                        "especialidades": [esp.nome for esp in medico.especialidades]
                    }
                    for medico in medicos
                ]
            }
        except Exception as e:
            print(f"[CHATBOT] Erro ao buscar médicos: {e}")
            return {"doctors": [], "error": str(e)}
    
    def get_doctor_details(self, doctor_id: int) -> Dict[str, Any]:
        """Retorna detalhes completos de um médico"""
        try:
            medico = Medico.query.get(doctor_id)
            if not medico:
                return {"error": "Médico não encontrado"}
            
            # Calcular estatísticas
            total_consultas = Agendamento.query.filter_by(
                medico_id=doctor_id,
                status='realizado'
            ).count()
            
            proximos_horarios = medico.get_proximos_horarios_livres(limite=5)
            
            return {
                "id": medico.id,
                "nome": medico.usuario.nome,
                "crm": medico.crm,
                "bio": medico.bio,
                "foto_url": medico.foto_url,
                "especialidades": [esp.nome for esp in medico.especialidades],
                "total_consultas_realizadas": total_consultas,
                "proximos_horarios": proximos_horarios,
                "ativo": medico.ativo
            }
        except Exception as e:
            print(f"[CHATBOT] Erro ao buscar detalhes do médico: {e}")
            return {"error": str(e)}
    
    def search_availability(self, doctor_id: Optional[int] = None, 
                           specialty_id: Optional[int] = None,
                           date_start: Optional[str] = None) -> Dict[str, Any]:
        """Busca horários disponíveis"""
        try:
            if date_start:
                try:
                    data_inicio = datetime.fromisoformat(date_start)
                except:
                    data_inicio = datetime.now()
            else:
                data_inicio = datetime.now()
            
            if doctor_id:
                medico = Medico.query.get(doctor_id)
                if medico:
                    horarios = medico.get_proximos_horarios_livres(data_inicio, limite=15)
                    return {
                        "schedules": [
                            {
                                "data": h['data'].strftime('%d/%m/%Y'),
                                "hora": h['hora'].strftime('%H:%M'),
                                "datetime": f"{h['data']}T{h['hora']}",
                                "duracao": h['duracao']
                            }
                            for h in horarios
                        ],
                        "medico_id": doctor_id,
                        "medico_nome": medico.usuario.nome
                    }
                    
            elif specialty_id:
                especialidade = Especialidade.query.get(specialty_id)
                if especialidade:
                    medicos = especialidade.medicos.filter_by(ativo=True).limit(5).all()
                    all_schedules = []
                    for medico in medicos:
                        horarios = medico.get_proximos_horarios_livres(data_inicio, limite=3)
                        for h in horarios:
                            all_schedules.append({
                                "data": h['data'].strftime('%d/%m/%Y'),
                                "hora": h['hora'].strftime('%H:%M'),
                                "datetime": f"{h['data']}T{h['hora']}",
                                "duracao": h['duracao'],
                                "medico_id": medico.id,
                                "medico_nome": medico.usuario.nome
                            })
                    return {"schedules": all_schedules[:15]}
            
            return {"schedules": []}
            
        except Exception as e:
            print(f"[CHATBOT] Erro ao buscar disponibilidade: {e}")
            return {"schedules": [], "error": str(e)}
    
    def get_user_appointments(self, user_id: int) -> Dict[str, Any]:
        """Retorna agendamentos do usuário"""
        try:
            # Buscar agendamentos ativos (futuros ou pendentes)
            agendamentos = Agendamento.query.filter(
                Agendamento.paciente_id == user_id,
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).order_by(Agendamento.inicio).all()
            
            # Buscar histórico (realizados ou cancelados)
            historico = Agendamento.query.filter(
                Agendamento.paciente_id == user_id,
                Agendamento.status.in_(['realizado', 'cancelado'])
            ).order_by(Agendamento.inicio.desc()).limit(10).all()
            
            def format_appointment(ag):
                medico = Medico.query.get(ag.medico_id)
                esp = Especialidade.query.get(ag.especialidade_id)
                return {
                    "id": ag.id,
                    "data": ag.inicio.strftime('%d/%m/%Y'),
                    "hora": ag.inicio.strftime('%H:%M'),
                    "medico": medico.usuario.nome if medico else "N/A",
                    "especialidade": esp.nome if esp else "N/A",
                    "status": ag.status,
                    "pode_cancelar": ag.pode_ser_cancelado(),
                    "observacoes": ag.observacoes
                }
            
            return {
                "appointments": [format_appointment(ag) for ag in agendamentos],
                "history": [format_appointment(ag) for ag in historico],
                "total_active": len(agendamentos),
                "total_history": len(historico)
            }
            
        except Exception as e:
            print(f"[CHATBOT] Erro ao buscar agendamentos: {e}")
            return {"appointments": [], "history": [], "error": str(e)}
    
    def get_appointment_details(self, appointment_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Retorna detalhes de um agendamento específico"""
        try:
            agendamento = Agendamento.query.get(appointment_id)
            if not agendamento:
                return {"error": "Agendamento não encontrado"}
            
            # Verificar permissão
            if user_id and agendamento.paciente_id != user_id:
                return {"error": "Você não tem permissão para ver este agendamento"}
            
            medico = Medico.query.get(agendamento.medico_id)
            esp = Especialidade.query.get(agendamento.especialidade_id)
            
            return {
                "id": agendamento.id,
                "data": agendamento.inicio.strftime('%d/%m/%Y'),
                "hora": agendamento.inicio.strftime('%H:%M'),
                "duracao": (agendamento.fim - agendamento.inicio).seconds // 60,
                "medico": {
                    "id": medico.id,
                    "nome": medico.usuario.nome,
                    "crm": medico.crm
                } if medico else None,
                "especialidade": {
                    "id": esp.id,
                    "nome": esp.nome
                } if esp else None,
                "status": agendamento.status,
                "pode_cancelar": agendamento.pode_ser_cancelado(),
                "observacoes": agendamento.observacoes,
                "origem": agendamento.origem,
                "created_at": agendamento.created_at.strftime('%d/%m/%Y %H:%M')
            }
            
        except Exception as e:
            print(f"[CHATBOT] Erro ao buscar detalhes: {e}")
            return {"error": str(e)}
    
    def create_appointment(self, booking_data: Dict, context: Dict) -> Dict[str, Any]:
        """Cria um novo agendamento com validações completas"""
        try:
            # Validar dados obrigatórios
            required = ['medico_id', 'especialidade_id', 'data_hora']
            for field in required:
                if not booking_data.get(field):
                    return {
                        'success': False,
                        'error': f'Campo obrigatório ausente: {field}',
                        'missing_field': field
                    }
            
            # Para usuários não autenticados, exigir nome e email
            if not context.get('authenticated'):
                if not booking_data.get('nome') or not booking_data.get('email'):
                    return {
                        'success': False,
                        'error': 'Nome e email são obrigatórios',
                        'missing_field': 'nome ou email'
                    }
            
            # Validar se médico existe e está ativo
            medico = Medico.query.get(booking_data['medico_id'])
            if not medico or not medico.ativo:
                return {
                    'success': False,
                    'error': 'Médico não encontrado ou inativo'
                }
            
            # Validar se especialidade existe e está ativa
            especialidade = Especialidade.query.get(booking_data['especialidade_id'])
            if not especialidade or not especialidade.ativo:
                return {
                    'success': False,
                    'error': 'Especialidade não encontrada ou inativa'
                }
            
            # Validar se médico atende essa especialidade
            if especialidade not in medico.especialidades:
                return {
                    'success': False,
                    'error': f'Dr(a). {medico.usuario.nome} não atende {especialidade.nome}'
                }
            
            # Converter data/hora com tratamento correto de timezone
            try:
                inicio_str = booking_data['data_hora']
                
                # Parse ISO string (suporta com/sem timezone)
                inicio_parsed = datetime.fromisoformat(inicio_str.replace('Z', '+00:00') if 'Z' in inicio_str else inicio_str)
                
                # Se já tem timezone, converter para UTC e remover tzinfo
                if inicio_parsed.tzinfo is not None:
                    inicio = inicio_parsed.astimezone(timezone.utc).replace(tzinfo=None)
                else:
                    # Se não tem timezone, assumir Brasília (UTC-3) e converter para UTC
                    brasilia_offset = timezone(timedelta(hours=-3))
                    inicio_brasilia = inicio_parsed.replace(tzinfo=brasilia_offset)
                    inicio = inicio_brasilia.astimezone(timezone.utc).replace(tzinfo=None)
                
                # Verificar se data está no passado (comparação timezone-aware)
                now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
                if inicio < now_utc:
                    return {
                        'success': False,
                        'error': 'Não é possível agendar para uma data no passado'
                    }
                
                fim = inicio + timedelta(minutes=especialidade.duracao_padrao or 30)
            except ValueError as e:
                return {
                    'success': False,
                    'error': f'Formato de data inválido: {str(e)}'
                }
            
            # Verificar se existe agenda do médico para esse horário
            inicio_brasilia = inicio.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-3)))
            data_agendamento = inicio_brasilia.date()
            hora_agendamento = inicio_brasilia.time()
            
            agenda_disponivel = Agenda.query.filter(
                Agenda.medico_id == booking_data['medico_id'],
                Agenda.dia_semana == data_agendamento.weekday(),
                Agenda.hora_inicio <= hora_agendamento,
                Agenda.hora_fim > hora_agendamento,
                Agenda.ativo == True
            ).first()
            
            if not agenda_disponivel:
                return {
                    'success': False,
                    'error': 'Médico não possui agenda disponível para este horário'
                }
            
            # Verificar conflito de agendamento
            conflito = Agendamento.query.filter(
                Agendamento.medico_id == booking_data['medico_id'],
                Agendamento.inicio == inicio,
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).first()
            
            if conflito:
                return {
                    'success': False,
                    'error': 'Este horário não está mais disponível. Por favor, escolha outro horário.'
                }
            
            # Criar agendamento
            agendamento = Agendamento()
            agendamento.medico_id = booking_data['medico_id']
            agendamento.especialidade_id = booking_data['especialidade_id']
            agendamento.inicio = inicio
            agendamento.fim = fim
            agendamento.status = 'agendado'
            agendamento.origem = 'chatbot'
            agendamento.observacoes = booking_data.get('observacoes', '')
            
            if context.get('authenticated') and context.get('user_id'):
                agendamento.paciente_id = context['user_id']
            else:
                agendamento.nome_convidado = booking_data['nome']
                agendamento.email_convidado = booking_data['email']
                agendamento.telefone_convidado = booking_data.get('telefone', '')
            
            db.session.add(agendamento)
            db.session.commit()
            
            return {
                'success': True,
                'agendamento_id': agendamento.id,
                'message': 'Agendamento criado com sucesso!',
                'details': {
                    'id': agendamento.id,
                    'data': agendamento.inicio.strftime('%d/%m/%Y'),
                    'hora': agendamento.inicio.strftime('%H:%M'),
                    'medico': medico.usuario.nome,
                    'especialidade': especialidade.nome,
                    'paciente': agendamento.nome_paciente
                }
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[CHATBOT] Erro ao criar agendamento: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Erro ao criar agendamento: {str(e)}'
            }
    
    def cancel_appointment(self, appointment_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Cancela um agendamento com validação de prazo de 24h"""
        try:
            agendamento = Agendamento.query.get(appointment_id)
            if not agendamento:
                return {"success": False, "error": "Agendamento não encontrado"}
            
            # Verificar permissão
            if user_id and agendamento.paciente_id != user_id:
                return {"success": False, "error": "Você não tem permissão para cancelar este agendamento"}
            
            # Verificar se status permite cancelamento
            if agendamento.status not in ['agendado', 'confirmado']:
                return {
                    "success": False,
                    "error": f"Agendamento com status '{agendamento.status}' não pode ser cancelado"
                }
            
            # Verificar prazo de 24h (comparação timezone-aware)
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            hours_until = (agendamento.inicio - now_utc).total_seconds() / 3600
            
            if hours_until < 24:
                return {
                    "success": False,
                    "error": "Cancelamento deve ser feito com pelo menos 24 horas de antecedência"
                }
            
            agendamento.status = 'cancelado'
            agendamento.observacoes = f"{agendamento.observacoes}\nCancelado via chatbot em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            db.session.commit()
            
            return {
                "success": True,
                "message": "Agendamento cancelado com sucesso",
                "appointment_id": appointment_id
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[CHATBOT] Erro ao cancelar: {e}")
            return {"success": False, "error": str(e)}
    
    def reschedule_appointment(self, appointment_id: int, new_datetime: str, 
                              user_id: Optional[int] = None) -> Dict[str, Any]:
        """Remarca um agendamento com validação de prazo de 24h"""
        try:
            agendamento = Agendamento.query.get(appointment_id)
            if not agendamento:
                return {"success": False, "error": "Agendamento não encontrado"}
            
            # Verificar permissão
            if user_id and agendamento.paciente_id != user_id:
                return {"success": False, "error": "Sem permissão"}
            
            # Verificar se status permite reagendamento
            if agendamento.status not in ['agendado', 'confirmado']:
                return {
                    "success": False,
                    "error": f"Agendamento com status '{agendamento.status}' não pode ser remarcado"
                }
            
            # Verificar prazo de 24h para remarcação (comparação timezone-aware)
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            hours_until = (agendamento.inicio - now_utc).total_seconds() / 3600
            
            if hours_until < 24:
                return {
                    "success": False,
                    "error": "Reagendamento deve ser feito com pelo menos 24 horas de antecedência"
                }
            
            # Converter nova data com tratamento correto de timezone
            try:
                novo_inicio_parsed = datetime.fromisoformat(new_datetime.replace('Z', '+00:00') if 'Z' in new_datetime else new_datetime)
                
                # Se já tem timezone, converter para UTC e remover tzinfo
                if novo_inicio_parsed.tzinfo is not None:
                    novo_inicio = novo_inicio_parsed.astimezone(timezone.utc).replace(tzinfo=None)
                else:
                    # Se não tem timezone, assumir Brasília (UTC-3) e converter para UTC
                    brasilia_offset = timezone(timedelta(hours=-3))
                    novo_inicio_brasilia = novo_inicio_parsed.replace(tzinfo=brasilia_offset)
                    novo_inicio = novo_inicio_brasilia.astimezone(timezone.utc).replace(tzinfo=None)
                
                # Verificar se nova data está no passado (comparação timezone-aware)
                if novo_inicio < now_utc:
                    return {
                        "success": False,
                        "error": "Não é possível reagendar para uma data no passado"
                    }
                    
            except ValueError:
                return {"success": False, "error": "Data inválida"}
            
            # Verificar conflito no novo horário
            conflito = Agendamento.query.filter(
                Agendamento.medico_id == agendamento.medico_id,
                Agendamento.inicio == novo_inicio,
                Agendamento.id != appointment_id,
                Agendamento.status.in_(['agendado', 'confirmado'])
            ).first()
            
            if conflito:
                return {"success": False, "error": "Novo horário não disponível"}
            
            # Salvar data antiga nas observações
            data_antiga = agendamento.inicio.strftime('%d/%m/%Y %H:%M')
            agendamento.observacoes = f"{agendamento.observacoes}\nRemarcado de {data_antiga} para {novo_inicio.strftime('%d/%m/%Y %H:%M')}"
            
            # Atualizar datas
            duracao = agendamento.fim - agendamento.inicio
            agendamento.inicio = novo_inicio
            agendamento.fim = novo_inicio + duracao
            
            db.session.commit()
            
            return {
                "success": True,
                "message": "Agendamento remarcado com sucesso",
                "new_date": novo_inicio.strftime('%d/%m/%Y'),
                "new_time": novo_inicio.strftime('%H:%M')
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[CHATBOT] Erro ao remarcar: {e}")
            return {"success": False, "error": str(e)}
    
    def get_clinic_info(self) -> Dict[str, Any]:
        """Retorna informações gerais da clínica"""
        return {
            "nome": "Clínica Dr. Raimundo Nunes",
            "especialidade_principal": "Ginecologia e Obstetrícia",
            "anos_experiencia": "30+",
            "diferenciais": [
                "Referência nacional em inserção de DIU hormonal",
                "Atendimento humanizado e personalizado",
                "Equipamentos de última geração",
                "Equipe altamente qualificada"
            ],
            "unidades": [
                {"nome": "Itaim Bibi", "cidade": "São Paulo"},
                {"nome": "Itapeva", "cidade": "São Paulo"}
            ],
            "horario_funcionamento": "Segunda a Sexta: 8h às 18h",
            "total_medicos": Medico.query.filter_by(ativo=True).count(),
            "total_especialidades": Especialidade.query.filter_by(ativo=True).count()
        }


# Instância singleton do serviço de chatbot
chatbot_service = ChatbotService()
