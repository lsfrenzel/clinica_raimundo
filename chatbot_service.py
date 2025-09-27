# Medical clinic chatbot service - Gemini and OpenAI integration
# Based on blueprint:python_gemini and python_openai integrations
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI
from models import Especialidade, Medico, Agendamento, User
from extensions import db

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
    def __init__(self):
        # Preferir Gemini, depois OpenAI, senão usar versão baseada em regras
        self.gemini_client = gemini_client
        self.openai_client = openai_client
        self.use_gemini = gemini_client is not None
        self.use_openai = openai_client is not None  # OpenAI disponível como fallback mesmo com Gemini ativo
        
    def get_system_prompt(self):
        """Define o contexto e comportamento do chatbot"""
        return """Você é um assistente virtual inteligente da Clínica Dr. Raimundo Nunes, especializada em ginecologia e obstetrícia.

Seu objetivo é ajudar pacientes a agendarem consultas de forma natural e eficiente, guiando-os através de todo o processo.

DIRETRIZES:
1. Seja sempre cordial, empático e profissional
2. Use linguagem clara e acessível
3. Guie o paciente passo a passo no processo de agendamento
4. Explique as especialidades quando solicitado
5. Apresente os médicos disponíveis com seus horários
6. Confirme todos os dados antes de finalizar o agendamento
7. Responda SEMPRE em português brasileiro
8. Use JSON estruturado conforme especificado para ações específicas

FLUXO COMPLETO DE AGENDAMENTO:
1. Cumprimente e identifique a necessidade de agendamento
2. Mostre especialidades disponíveis se solicitado
3. Colete especialidade desejada
4. Apresente médicos da especialidade escolhida
5. Colete médico desejado
6. Mostre horários disponíveis do médico
7. Colete horário desejado
8. Colete dados do paciente (nome, email, telefone)
9. Confirme todos os dados
10. Crie o agendamento no sistema
11. Confirme o sucesso do agendamento

AÇÕES DISPONÍVEIS:
- get_specialties: Mostrar especialidades disponíveis
- select_specialty: Processar especialidade escolhida
- show_doctors: Mostrar médicos de uma especialidade
- select_doctor: Processar médico escolhido
- show_schedules: Mostrar horários disponíveis
- select_schedule: Processar horário escolhido
- collect_patient_data: Coletar dados do paciente
- confirm_booking: Confirmar todos os dados antes do agendamento
- create_booking: Criar agendamento no sistema
- general_chat: Conversa geral

Responda sempre em formato JSON com esta estrutura:
{
    "message": "sua resposta amigável",
    "action": "uma das ações acima",
    "data": {objeto com dados específicos da ação, se aplicável}
}"""

    def chat_response(self, user_message, context=None):
        """Gera resposta do chatbot baseada na mensagem do usuário"""
        try:
            if self.use_gemini and self.gemini_client:
                result = self._gemini_response(user_message, context)
            elif self.use_openai and self.openai_client:
                result = self._openai_response(user_message, context)
            else:
                result = self._rule_based_response(user_message, context)
            
            # Sempre processar ações específicas, independente do engine usado
            result, updated_context = self._process_action(result, context)
            
            # Retornar resultado e contexto atualizado
            return {
                **result,
                '_updated_context': updated_context
            }
            
        except Exception as e:
            # Fallback seguro para qualquer erro - não expor detalhes internos
            try:
                result = self._rule_based_response(user_message, context)
                result, updated_context = self._process_action(result, context)
                return {
                    **result,
                    '_updated_context': updated_context
                }
            except Exception:
                # Último recurso - resposta genérica segura
                return {
                    "message": "Olá! Estou aqui para ajudar você a agendar sua consulta na Clínica Dr. Raimundo Nunes. Como posso ajudá-lo hoje?",
                    "action": "general_chat",
                    "data": {},
                    "_updated_context": context or {}
                }

    def _openai_response(self, user_message, context=None):
        """Resposta usando OpenAI (quando disponível)"""
        messages = []
        messages.append({"role": "system", "content": self.get_system_prompt()})
        
        # Adicionar contexto se fornecido
        if context:
            context_msg = f"Contexto da conversa: {json.dumps(context, ensure_ascii=False)}"
            messages.append({"role": "assistant", "content": context_msg})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.openai_client.chat.completions.create(  # type: ignore
            model="gpt-3.5-turbo",
            messages=messages,  # type: ignore
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        if content:
            result = json.loads(content)
        else:
            raise Exception("Resposta vazia do modelo")
        
        return result

    def _gemini_response(self, user_message, context=None):
        """Resposta usando Gemini API (preferida quando disponível)"""
        try:
            # Preparar o prompt do sistema para Gemini
            system_prompt = self.get_system_prompt()
            
            # Adicionar contexto se fornecido
            context_info = ""
            if context:
                context_info = f"\n\nContexto da conversa: {json.dumps(context, ensure_ascii=False)}"
            
            # Criar prompt completo
            full_prompt = f"{system_prompt}{context_info}\n\nUsuário: {user_message}\n\nResponda em formato JSON conforme especificado:"
            
            # Fazer chamada para Gemini
            if not types:
                raise Exception("Gemini types não disponível")
                
            if not self.gemini_client:
                raise Exception("Gemini client não disponível")
                
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    response_mime_type="application/json"
                )
            )
            
            if not response.text:
                raise Exception("Resposta vazia do Gemini")
            
            # Parse da resposta JSON
            result = json.loads(response.text)
            
            return result
            
        except Exception as e:
            # Em caso de erro no Gemini, tentar OpenAI como fallback
            if self.use_openai and self.openai_client:
                try:
                    return self._openai_response(user_message, context)
                except Exception:
                    # Se OpenAI também falhar, usar sistema baseado em regras
                    return self._rule_based_response(user_message, context)
            else:
                # Se não há OpenAI, usar sistema baseado em regras
                return self._rule_based_response(user_message, context)

    def _process_action(self, result, context=None):
        """Processa as ações específicas do chatbot"""
        action = result.get("action")
        
        # Inicializar contexto se necessário
        if context is None:
            context = {}
        
        # Criar cópia do contexto para atualização
        updated_context = context.copy()
        
        # Rastrear etapa da conversa
        current_step = updated_context.get('conversation_step', 'start')
        
        if action == "get_specialties":
            result["data"] = self.get_specialties()
            updated_context['conversation_step'] = 'selecting_specialty'
            
        elif action == "show_doctors" or action == "select_specialty":
            # Sempre definir que estamos mostrando médicos
            updated_context['conversation_step'] = 'selecting_doctor'
            
            # Verificar se data é dict ou list  
            data = result.get("data", {})
            if isinstance(data, dict):
                specialty_id = data.get("specialty_id")
                specialty_name = data.get("specialty_name")
                
                # Se o Gemini retornou um nome em vez de ID, tentar encontrar o ID
                if specialty_name and not specialty_id:
                    try:
                        from models import Especialidade
                        especialidade = Especialidade.query.filter(Especialidade.nome.ilike(f"%{specialty_name}%")).first()
                        if especialidade:
                            specialty_id = especialidade.id
                            specialty_name = especialidade.nome
                    except Exception as e:
                        print(f"Erro ao buscar especialidade por nome: {e}")
                
                # Se recebeu um valor que não é numérico como specialty_id, tentar converter nome
                if specialty_id and isinstance(specialty_id, str) and not specialty_id.isdigit():
                    try:
                        from models import Especialidade
                        especialidade = Especialidade.query.filter(Especialidade.nome.ilike(f"%{specialty_id}%")).first()
                        if especialidade:
                            specialty_id = especialidade.id
                            specialty_name = especialidade.nome
                    except Exception as e:
                        print(f"Erro ao converter nome da especialidade para ID: {e}")
                        specialty_id = None
                
                # Salvar especialidade selecionada no contexto
                if specialty_id:
                    updated_context['especialidade_id'] = specialty_id
                    updated_context['especialidade_nome'] = specialty_name
                
                result["data"] = self.get_doctors_by_specialty(specialty_id)
            else:
                # Para ginecologia, usar ID 7 como padrão
                updated_context['especialidade_id'] = 7
                updated_context['especialidade_nome'] = 'Ginecologia'
                result["data"] = self.get_doctors_by_specialty(7)
            # Se data já é uma lista, não processar IDs
            
        elif action == "show_schedules" or action == "select_doctor":
            # Verificar se data é dict ou list
            data = result.get("data", {})
            if isinstance(data, dict):
                doctor_id = data.get("doctor_id")
                doctor_name = data.get("doctor_name")
                
                # Se o Gemini retornou um nome em vez de ID, tentar encontrar o ID
                if doctor_name and not doctor_id:
                    try:
                        from models import Medico, User
                        # Buscar médico pelo nome
                        user = User.query.filter(User.nome.ilike(f"%{doctor_name}%")).first()
                        if user:
                            medico = Medico.query.filter_by(user_id=user.id).first()
                            if medico:
                                doctor_id = medico.id
                                doctor_name = user.nome
                    except Exception as e:
                        print(f"Erro ao buscar médico por nome: {e}")
                
                # Se recebeu um valor que não é numérico como doctor_id, tentar converter nome
                if doctor_id and isinstance(doctor_id, str) and not doctor_id.isdigit():
                    try:
                        from models import Medico, User
                        # Buscar médico pelo nome
                        user = User.query.filter(User.nome.ilike(f"%{doctor_id}%")).first()
                        if user:
                            medico = Medico.query.filter_by(user_id=user.id).first()
                            if medico:
                                doctor_id = medico.id
                                doctor_name = user.nome
                    except Exception as e:
                        print(f"Erro ao converter nome para ID: {e}")
                        doctor_id = None
                
                # Salvar médico selecionado no contexto
                if doctor_id:
                    updated_context['medico_id'] = doctor_id
                    updated_context['medico_nome'] = doctor_name
                    updated_context['conversation_step'] = 'selecting_time'
                    
                    result["data"] = self.get_doctor_schedules(doctor_id)
                else:
                    result["data"] = []
            # Se data já é uma lista, não processar IDs
            
        elif action == "select_schedule":
            # Salvar horário selecionado no contexto
            schedule_data = result.get("data", {})
            if schedule_data.get('datetime'):
                updated_context['datetime_slot'] = schedule_data['datetime']
            
        elif action == "confirm_booking" or action == "collect_patient_data":
            # Salvar dados do paciente no contexto
            booking_data = result.get("data", {})
            if booking_data.get('patient_name'):
                updated_context['patient_name'] = booking_data['patient_name']
            if booking_data.get('patient_email'):
                updated_context['patient_email'] = booking_data['patient_email']
            if booking_data.get('patient_phone'):
                updated_context['patient_phone'] = booking_data['patient_phone']
            if booking_data.get('datetime'):
                updated_context['datetime_slot'] = booking_data['datetime']
                
        elif action == "create_booking":
            booking_data = result.get("data", {})
            
            # DEBUG: Log dos dados recebidos
            print(f"[DEBUG create_booking] Dados recebidos:")
            print(f"  booking_data: {booking_data}")
            print(f"  updated_context: {updated_context}")
            
            # Mesclar dados do booking com contexto salvado
            merged_booking_data = {
                'medico_id': updated_context.get('medico_id'),
                'especialidade_id': updated_context.get('especialidade_id'),
                'data_hora': updated_context.get('datetime_slot'),
                'nome': updated_context.get('patient_name'),
                'email': updated_context.get('patient_email'),
                'telefone': updated_context.get('patient_phone', ''),
            }
            
            # Sobrescrever com dados do booking se disponíveis
            merged_booking_data.update({k: v for k, v in booking_data.items() if v})
            
            # DEBUG: Log dos dados mesclados
            print(f"[DEBUG create_booking] Dados mesclados para create_appointment:")
            print(f"  merged_booking_data: {merged_booking_data}")
            
            result["data"] = self.create_appointment(merged_booking_data, context)
            
            # DEBUG: Log do resultado
            print(f"[DEBUG create_booking] Resultado do create_appointment:")
            print(f"  result: {result['data']}")
            
            # Limpar contexto após agendamento bem-sucedido
            if result["data"].get("success"):
                updated_context = {'user_id': context.get('user_id'), 'authenticated': context.get('authenticated'), 'user_name': context.get('user_name')}
            
        return result, updated_context

    def create_appointment(self, booking_data, context=None):
        """Cria um agendamento no banco de dados"""
        try:
            from models import Agendamento
            from datetime import datetime, timedelta
            
            # Auto-preencher dados do usuário autenticado se necessário
            if context and context.get('authenticated') and context.get('user_id'):
                if not booking_data.get('nome'):
                    booking_data['nome'] = context.get('user_name', '')
                if not booking_data.get('email'):
                    booking_data['email'] = context.get('user_email', '')
            
            # Validar dados obrigatórios
            required_fields = ['medico_id', 'especialidade_id', 'data_hora']
            for field in required_fields:
                if field not in booking_data or not booking_data[field]:
                    return {
                        'success': False,
                        'error': f'Campo obrigatório ausente: {field}'
                    }
            
            # Para usuários não autenticados, nome e email são obrigatórios
            if not context or not context.get('authenticated'):
                guest_fields = ['nome', 'email']
                for field in guest_fields:
                    if field not in booking_data or not booking_data[field]:
                        return {
                            'success': False,
                            'error': f'Campo obrigatório para visitantes: {field}'
                        }
            
            # Converter data_hora para datetime
            try:
                inicio = datetime.fromisoformat(booking_data['data_hora'])
                fim = inicio + timedelta(minutes=30)  # Duração padrão
            except ValueError:
                return {
                    'success': False,
                    'error': 'Formato de data/hora inválido'
                }
            
            # Verificar se horário ainda está disponível
            agendamento_existente = Agendamento.query.filter_by(
                medico_id=booking_data['medico_id'],
                inicio=inicio
            ).first()
            
            if agendamento_existente:
                return {
                    'success': False,
                    'error': 'Horário não está mais disponível'
                }
            
            # Criar agendamento
            agendamento = Agendamento()
            agendamento.medico_id = booking_data['medico_id']
            agendamento.especialidade_id = booking_data['especialidade_id']
            agendamento.inicio = inicio
            agendamento.fim = fim
            agendamento.origem = 'chatbot'
            agendamento.observacoes = booking_data.get('observacoes', '')
            
            # Verificar se é usuário autenticado ou visitante
            if context and context.get('authenticated') and context.get('user_id'):
                agendamento.paciente_id = context['user_id']
                # Para usuários autenticados, salvar também o email para referência cruzada
                if context.get('user_email'):
                    agendamento.email_convidado = context['user_email']
                if booking_data.get('nome'):
                    agendamento.observacoes = f"Agendado por: {booking_data['nome']} | {agendamento.observacoes}"
            else:
                agendamento.nome_convidado = booking_data['nome']
                agendamento.email_convidado = booking_data['email']
                agendamento.telefone_convidado = booking_data.get('telefone', '')
            
            db.session.add(agendamento)
            db.session.commit()
            
            return {
                'success': True,
                'agendamento_id': agendamento.id,
                'message': 'Agendamento criado com sucesso!'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Erro ao criar agendamento: {str(e)}'
            }

    def _rule_based_response(self, user_message, context=None):
        """Resposta baseada em regras (quando OpenAI não está disponível)"""
        import re
        
        message_lower = user_message.lower()
        user_name = context.get('user_name', 'Paciente') if context else 'Paciente'
        
        # Cumprimentos e saudações
        if any(word in message_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'alo', 'alô']):
            return {
                "message": f"Olá, {user_name}! Seja muito bem-vindo(a) à Clínica Dr. Raimundo Nunes! 👋\n\n🏥 **Especialista em Ginecologia e Obstetrícia**\n\nSou seu assistente virtual e estou aqui para tornar seu atendimento mais ágil e conveniente.\n\n📋 **Como posso ajudar você hoje?**\n\n🔹 **Agendar uma consulta** - Vamos encontrar o melhor horário para você\n🔹 **Conhecer especialidades** - Descubra todos os nossos serviços\n🔹 **Ver nossos médicos** - Conheça nossa equipe especializada\n🔹 **Horários disponíveis** - Consulte as próximas vagas\n\nDigite sua necessidade ou escolha uma das opções acima! ✨",
                "action": "general_chat",
                "data": {}
            }
        
        # Perguntas sobre especialidades
        elif any(word in message_lower for word in ['especialidade', 'especialidades', 'atendimento', 'área', 'area', 'tipo', 'serviço', 'servico', 'tratamento']):
            especialidades_data = self.get_specialties()
            especialidades_text = "\n".join([f"🔹 **{esp['nome']}** - {esp.get('descricao', 'Atendimento especializado')}" for esp in especialidades_data])
            return {
                "message": f"🏥 **Especialidades da Clínica Dr. Raimundo Nunes:**\n\n{especialidades_text}\n\n✨ **Todos os nossos atendimentos são realizados por profissionais altamente qualificados!**\n\n💬 Qual especialidade você precisa? Posso te ajudar a encontrar o médico ideal e agendar sua consulta!",
                "action": "get_specialties",
                "data": especialidades_data
            }
        
        # Seleção de especialidades específicas
        elif any(specialty in message_lower for specialty in ['ginecologia', 'obstetrícia', 'obstetricia', 'pré-natal', 'prenatal']):
            if 'ginecologia' in message_lower:
                specialty_id = 4  # Mastologia (relacionada à ginecologia)
                specialty_name = 'Ginecologia'
            elif any(word in message_lower for word in ['obstetrícia', 'obstetricia']):
                specialty_id = 2  # Pré-Natal de Alto Risco
                specialty_name = 'Obstetrícia'
            else:
                specialty_id = 2  # Pré-Natal de Alto Risco
                specialty_name = 'Pré-natal'
            
            doctors_data = self.get_doctors_by_specialty(specialty_id)
            if doctors_data:
                doctors_text = "\n".join([f"👨‍⚕️ **Dr(a). {doc['nome']}** - CRM: {doc['crm']}\n   📝 {doc.get('bio', 'Médico especialista')[:100]}..." for doc in doctors_data])
                return {
                    "message": f"🏥 **Médicos disponíveis para {specialty_name}:**\n\n{doctors_text}\n\n💬 **Digite o nome do médico** que você gostaria de consultar ou digite \"qualquer\" para ver horários de todos!",
                    "action": "show_doctors",
                    "data": {
                        "specialty_id": specialty_id,
                        "specialty_name": specialty_name,
                        "doctors": doctors_data
                    }
                }
            else:
                return {
                    "message": f"😊 **Especialidade {specialty_name} selecionada!**\n\nVou buscar nossos médicos especialistas...",
                    "action": "select_specialty",
                    "data": {"specialty_id": specialty_id, "specialty_name": specialty_name}
                }
                
        # Seleção de médicos específicos
        elif any(doctor in message_lower for doctor in ['dr. ricardo', 'ricardo mendes', 'dra. ana', 'ana silva', 'raimundo', 'dr. raimundo']):
            if any(name in message_lower for name in ['ricardo', 'ricardo mendes']):
                doctor_id = 3
                doctor_name = "Dr. Ricardo Mendes"
            elif any(name in message_lower for name in ['ana', 'ana silva']):
                doctor_id = 2  
                doctor_name = "Dra. Ana Carolina Silva"
            elif any(name in message_lower for name in ['raimundo']):
                doctor_id = 1
                doctor_name = "Dr. Raimundo Nunes"
            else:
                doctor_id = 3  # Default
                doctor_name = "Dr. Ricardo Mendes"
                
            schedules = self.get_doctor_schedules(doctor_id)
            schedules_text = "\n".join([f"📅 **{sch['data']}** às **{sch['hora']}**" for sch in schedules[:5]])
            
            return {
                "message": f"👨‍⚕️ **Excelente escolha! {doctor_name}**\n\n⏰ **Próximos horários disponíveis:**\n\n{schedules_text}\n\n💬 **Digite a data e hora** que prefere (exemplo: \"30/09/2025 às 08:00\") ou digite \"mais horários\" para ver outras opções!",
                "action": "select_doctor",
                "data": {
                    "doctor_id": doctor_id,
                    "doctor_name": doctor_name,
                    "schedules": schedules
                }
            }
            
        # Seleção de horários específicos
        elif any(pattern in message_lower for pattern in ['30/09', '01/10', '02/10', 'às 08:00', 'às 09:00', 'às 14:00']):
            # Extrair data e hora da mensagem
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', user_message)
            time_match = re.search(r'às (\d{1,2}:\d{2})', user_message)
            
            if date_match and time_match:
                date_str = date_match.group(1)
                time_str = time_match.group(1)
                datetime_str = f"{date_str.split('/')[2]}-{date_str.split('/')[1]:0>2}-{date_str.split('/')[0]:0>2}T{time_str}:00"
                
                return {
                    "message": f"⏰ **Horário selecionado: {date_str} às {time_str}**\n\n📋 **Agora preciso confirmar seus dados:**\n\n• Nome: {context.get('user_name', '[Por favor, informe seu nome]')}\n• Email: {context.get('user_email', '[Por favor, informe seu email]')}\n\n💬 **Digite seu telefone para contato** (exemplo: 11 99999-9999):",
                    "action": "select_schedule",
                    "data": {
                        "datetime": datetime_str,
                        "date_str": date_str,
                        "time_str": time_str
                    }
                }
            else:
                return {
                    "message": "⏰ **Para selecionar um horário, digite no formato:**\n\n📅 **\"30/09/2025 às 08:00\"**\n\nOu escolha uma das opções mostradas anteriormente.",
                    "action": "general_chat",
                    "data": {}
                }
                
        # Coleta de telefone
        elif re.search(r'\b\d{2}\s?\d{4,5}-?\d{4}\b', user_message) or re.search(r'\(\d{2}\)\s?\d{4,5}-?\d{4}', user_message):
            phone_match = re.search(r'(\(?\d{2}\)?\s?\d{4,5}-?\d{4})', user_message)
            if phone_match:
                phone = phone_match.group(1)
                return {
                    "message": f"📞 **Telefone confirmado: {phone}**\n\n✅ **Resumo do seu agendamento:**\n\n• **Médico:** {context.get('medico_nome', 'Médico selecionado')}\n• **Data/Hora:** {context.get('datetime_slot', 'Horário selecionado')}\n• **Nome:** {context.get('user_name', 'Nome informado')}\n• **Email:** {context.get('user_email', 'Email informado')}\n• **Telefone:** {phone}\n\n🎉 **Digite \"CONFIRMAR\" para finalizar o agendamento!**",
                    "action": "confirm_booking",
                    "data": {
                        "patient_phone": phone
                    }
                }
        
        # Perguntas sobre médicos
        elif any(word in message_lower for word in ['médico', 'medico', 'doutor', 'doutora', 'profissional', 'equipe', 'staff']):
            doctors_data = self.get_doctors_by_specialty()
            if doctors_data:
                doctors_text = "\n".join([f"👨‍⚕️ **Dr(a). {doc['nome']}** - CRM: {doc['crm']}\n   📋 {', '.join(doc['especialidades'])}\n   📝 {doc.get('bio', 'Médico especialista em ginecologia e obstetrícia')}\n" for doc in doctors_data[:3]])
                return {
                    "message": f"👨‍⚕️ **Nossa Equipe Médica Especializada:**\n\n{doctors_text}\n✨ **E temos mais profissionais disponíveis!**\n\n🎯 **Para ver médicos de uma especialidade específica**, me diga qual área você precisa:\n🔹 Ginecologia\n🔹 Obstetrícia\n🔹 Consulta Pré-natal\n🔹 Planejamento Familiar\n🔹 Medicina Preventiva\n\n📅 Quer agendar com algum médico específico?",
                    "action": "show_doctors", 
                    "data": doctors_data
                }
            else:
                return {
                    "message": "👨‍⚕️ **Nossa equipe médica especializada está pronta para atendê-lo!**\n\n🎯 Para mostrar os médicos disponíveis, me diga qual especialidade você precisa:\n🔹 Ginecologia\n🔹 Obstetrícia\n🔹 Consulta Pré-natal\n🔹 Planejamento Familiar\n🔹 Medicina Preventiva",
                    "action": "show_doctors", 
                    "data": []
                }
        
        # Agendamento
        elif any(word in message_lower for word in ['agendar', 'consulta', 'horário', 'horario', 'marcar', 'appointment', 'reservar', 'agendar']):
            return {
                "message": f"🎉 **Ótimo, {user_name}! Vou ajudar você a agendar sua consulta de forma rápida e fácil!**\n\n📋 **Primeiro passo**: Qual especialidade você precisa?\n\n🔹 **Ginecologia** - Consultas preventivas, exames, tratamentos\n🔹 **Obstetrícia** - Acompanhamento da gravidez\n🔹 **Consulta Pré-natal** - Cuidados durante a gestação\n🔹 **Planejamento Familiar** - Métodos contraceptivos, orientações\n🔹 **Medicina Preventiva** - Check-ups e prevenção\n\n💬 **Digite o nome da especialidade** ou **clique em uma das opções** acima!\n\n⚡ Em seguida, vou mostrar nossos médicos e horários disponíveis para você escolher o que for mais conveniente!",
                "action": "get_specialties",
                "data": self.get_specialties()
            }
            
        # Confirmação de agendamento (adicionar lógica para rule-based)
        elif any(word in message_lower for word in ['confirmar', 'sim', 'confirmo', 'ok', 'agendar agora', 'finalizar']):
            # Verificar se temos contexto completo para agendamento
            if (context and context.get('medico_id') and context.get('datetime_slot') and 
                (context.get('patient_name') or context.get('user_name')) and 
                (context.get('patient_email') or context.get('user_email'))):
                
                # Criar dados completos para o agendamento
                booking_data = {
                    'medico_id': context.get('medico_id'),
                    'especialidade_id': context.get('especialidade_id'),
                    'data_hora': context.get('datetime_slot'),
                    'nome': context.get('patient_name') or context.get('user_name'),
                    'email': context.get('patient_email') or context.get('user_email'),
                    'telefone': context.get('patient_phone', ''),
                }
                
                return {
                    "message": "🎉 **Perfeito! Finalizando seu agendamento...**\n\nAguarde um momento enquanto confirmo sua consulta no sistema.",
                    "action": "create_booking",
                    "data": booking_data
                }
            else:
                missing_data = []
                if not context or not context.get('medico_id'):
                    missing_data.append("médico")
                if not context or not context.get('datetime_slot'):
                    missing_data.append("horário")
                if not context or not (context.get('patient_name') or context.get('user_name')):
                    missing_data.append("nome")
                if not context or not (context.get('patient_email') or context.get('user_email')):
                    missing_data.append("email")
                    
                return {
                    "message": f"📋 **Para confirmar o agendamento, ainda preciso de:** {', '.join(missing_data)}\n\n💬 Digite \"agendar\" para começar o processo completo!",
                    "action": "get_specialties",
                    "data": self.get_specialties()
                }
        
        # Horários
        elif any(word in message_lower for word in ['horário', 'horario', 'disponível', 'disponivel', 'livre', 'vaga', 'vagas', 'quando']):
            return {
                "message": "⏰ **Vamos encontrar o melhor horário para você!**\n\n📋 Para mostrar os horários mais adequados, preciso de algumas informações rápidas:\n\n1️⃣ **Qual especialidade você precisa?**\n   🔹 Ginecologia | 🔹 Obstetrícia | 🔹 Pré-natal\n   🔹 Planejamento Familiar | 🔹 Medicina Preventiva\n\n2️⃣ **Tem preferência por algum médico específico?**\n   (ou posso sugerir o próximo disponível)\n\n3️⃣ **Prefere que período?**\n   🌅 Manhã | 🌞 Tarde | 🌙 Qualquer horário\n\n💬 **Me conte essas informações** e vou buscar as melhores opções de horários para você!",
                "action": "general_chat",
                "data": {}
            }
        
        # Perguntas sobre preços/valores
        elif any(word in message_lower for word in ['preço', 'preco', 'valor', 'custo', 'quanto', 'custa', 'pagamento', 'convênio', 'convenio', 'plano']):
            return {
                "message": "💰 **Informações sobre Valores e Pagamento:**\n\n🏥 Para informações detalhadas sobre:\n   • Valores das consultas\n   • Formas de pagamento aceitas\n   • Convênios médicos\n   • Promoções especiais\n\n📞 **Recomendo entrar em contato com nossa recepção**, onde nossa equipe pode dar informações atualizadas e personalizadas para seu caso.\n\n✨ **Enquanto isso, posso ajudar você a:**\n🔹 Agendar sua consulta\n🔹 Conhecer nossas especialidades\n🔹 Ver horários disponíveis\n\n💬 O que você gostaria de fazer?",
                "action": "general_chat", 
                "data": {}
            }
        
        # Localização
        elif any(word in message_lower for word in ['onde', 'endereço', 'endereco', 'localização', 'localizacao', 'local', 'chegar', 'fica']):
            return {
                "message": "📍 **Localização da Clínica Dr. Raimundo Nunes:**\n\n🏥 Nossa clínica está estrategicamente localizada em um **endereço de fácil acesso**, pensando no seu conforto e conveniência.\n\n🚗 **Facilidades:**\n   • Estacionamento disponível\n   • Transporte público próximo\n   • Fácil acesso para pessoas com mobilidade reduzida\n\n📞 **Para informações detalhadas sobre:**\n   • Endereço completo\n   • Como chegar de sua região\n   • Pontos de referência\n   • Estacionamento\n\n**Entre em contato com nossa recepção** - eles terão prazer em orientá-lo!\n\n📅 **Enquanto isso, quer agendar sua consulta?**",
                "action": "general_chat",
                "data": {}
            }
        
        # Informações sobre exames
        elif any(word in message_lower for word in ['exame', 'exames', 'ultrassom', 'papanicolau', 'preventivo', 'laboratório', 'laboratorio']):
            return {
                "message": "🔬 **Exames e Procedimentos:**\n\nNossa clínica realiza diversos exames importantes para sua saúde:\n\n🔹 **Exame Preventivo (Papanicolau)**\n🔹 **Ultrassom Ginecológico/Obstétrico**\n🔹 **Exames de rotina ginecológica**\n🔹 **Acompanhamento pré-natal completo**\n\n📋 **Para informações específicas sobre:**\n   • Preparação para exames\n   • Procedimentos realizados\n   • Agendamento de exames\n\n💬 **Me diga qual exame você precisa** ou posso ajudar você a agendar uma consulta para avaliação médica!\n\n🎯 Qual especialidade você gostaria de consultar?",
                "action": "general_chat",
                "data": {}
            }
        
        # Urgência e emergência
        elif any(word in message_lower for word in ['urgente', 'urgência', 'urgencia', 'emergência', 'emergencia', 'rápido', 'rapido', 'hoje']):
            return {
                "message": "🚨 **Atendimento Urgente:**\n\n⚠️ **Para emergências médicas**, procure imediatamente:\n   • Pronto Socorro mais próximo\n   • SAMU: 192\n   • Hospital de referência\n\n🏥 **Para consultas com urgência** (não emergência):\n   • Entre em contato diretamente com nossa recepção\n   • Podemos verificar encaixes na agenda\n   • Orientação por telefone se necessário\n\n📞 **Nossa equipe pode te orientar** sobre a melhor forma de atendimento para seu caso específico.\n\n💬 **Se não for emergência**, posso ajudar você a agendar uma consulta. Qual especialidade você precisa?",
                "action": "general_chat",
                "data": {}
            }
        
        # Gravidez e pré-natal
        elif any(word in message_lower for word in ['grávida', 'gravida', 'gravidez', 'gestante', 'bebê', 'bebe', 'pré-natal', 'prenatal', 'gestação', 'gestacao']):
            return {
                "message": "🤱 **Acompanhamento da Gravidez - Bem-vinda!**\n\n💖 **Parabéns por essa fase especial!** Nossa equipe está preparada para cuidar de você e seu bebê com todo carinho e expertise.\n\n🏥 **Nossos serviços incluem:**\n\n🔹 **Consultas de Pré-natal**\n   • Acompanhamento completo da gestação\n   • Orientações nutricionais e de cuidados\n   • Exames de rotina\n\n🔹 **Obstetrícia Especializada**\n   • Médicos experientes em gestação\n   • Ultrassom obstétrico\n   • Preparação para o parto\n\n🔹 **Consultas Preventivas**\n   • Planejamento da gravidez\n   • Cuidados pós-parto\n\n📅 **Quer agendar sua consulta de pré-natal?** Posso te ajudar a encontrar o melhor horário com nossos obstetras!\n\n💬 Me diga se prefere algum médico específico ou posso sugerir o próximo disponível!",
                "action": "get_specialties",
                "data": self.get_specialties()
            }
        
        # Primeira consulta
        elif any(word in message_lower for word in ['primeira', 'primeiro', 'primeira vez', 'nunca', 'novo', 'nova', 'paciente novo']):
            return {
                "message": "🌟 **Seja muito bem-vindo(a) como novo(a) paciente!**\n\n✨ **Para sua primeira consulta**, vamos tornar tudo mais fácil e acolhedor:\n\n📋 **O que trazer:**\n   • Documento de identidade\n   • Cartão do convênio (se tiver)\n   • Exames anteriores (se houver)\n   • Lista de medicamentos em uso\n\n⏰ **Recomendamos chegar 15 minutos antes** para fazer seu cadastro tranquilamente.\n\n🏥 **Nossas especialidades principais:**\n🔹 **Ginecologia** - Consultas preventivas e tratamentos\n🔹 **Obstetrícia** - Acompanhamento da gravidez\n🔹 **Pré-natal** - Cuidados durante a gestação\n🔹 **Planejamento Familiar** - Orientações contraceptivas\n🔹 **Medicina Preventiva** - Check-ups e prevenção\n\n💬 **Qual especialidade você precisa para sua primeira consulta?**\n\n📅 Posso te ajudar a agendar no melhor horário para você!",
                "action": "get_specialties",
                "data": self.get_specialties()
            }
        
        # Cancelar/remarcar
        elif any(word in message_lower for word in ['cancelar', 'remarcar', 'mudar', 'alterar', 'trocar', 'adiar']):
            return {
                "message": "📅 **Alteração de Consulta:**\n\n🔄 **Para cancelar ou remarcar sua consulta:**\n\n📞 **Entre em contato diretamente com nossa recepção** - eles podem:\n   • Cancelar sua consulta atual\n   • Remarcar para nova data/horário\n   • Verificar disponibilidade\n   • Fazer alterações no seu agendamento\n\n⚠️ **Importante:**\n   • Cancelamentos com 24h de antecedência são mais fáceis\n   • Nossa equipe pode encontrar novos horários rapidamente\n   • Evite faltas para não prejudicar outros pacientes\n\n💬 **Se quiser agendar uma nova consulta**, posso te ajudar agora mesmo!\n\n🎯 Qual especialidade você precisa?",
                "action": "general_chat",
                "data": {}
            }
        
        # Agradecimento
        elif any(word in message_lower for word in ['obrigado', 'obrigada', 'obrigadão', 'valeu', 'brigado', 'brigada', 'thanks']):
            return {
                "message": "💖 **Por nada! Foi um prazer ajudar você!**\n\n🌟 **Estou sempre aqui quando precisar:**\n   • Agendar consultas\n   • Tirar dúvidas sobre especialidades\n   • Conhecer nossos médicos\n   • Ver horários disponíveis\n\n🏥 **Clínica Dr. Raimundo Nunes** está sempre pronta para cuidar da sua saúde com excelência e carinho.\n\n💬 **Tem mais alguma coisa que posso ajudar?**\n\n✨ Ou se quiser, pode voltar a qualquer momento - estarei aqui para você!",
                "action": "general_chat",
                "data": {}
            }
        
        # Mensagem padrão melhorada
        else:
            return {
                "message": f"💬 **Olá, {user_name}! Entendi sua mensagem.**\n\n🤖 Sou o assistente virtual da **Clínica Dr. Raimundo Nunes** e estou aqui para tornar seu atendimento mais ágil e conveniente!\n\n🎯 **Posso ajudar você com:**\n\n🔹 **Agendar consultas** - Vamos encontrar o melhor horário\n🔹 **Informações sobre especialidades** - Conheça nossos serviços\n🔹 **Conhecer nossos médicos** - Equipe especializada\n🔹 **Ver horários disponíveis** - Consulte as próximas vagas\n🔹 **Informações gerais** - Localização, valores, exames\n\n💡 **Dicas rápidas:**\n   • Digite \"agendar\" para marcar uma consulta\n   • Digite \"especialidades\" para ver nossos serviços\n   • Digite \"médicos\" para conhecer nossa equipe\n\n💬 **O que você gostaria de fazer hoje?**",
                "action": "general_chat",
                "data": {}
            }

    def get_specialties(self):
        """Busca especialidades disponíveis no banco"""
        try:
            especialidades = Especialidade.query.filter_by(ativo=True).all()
            return [
                {
                    "id": esp.id,
                    "nome": esp.nome,
                    "descricao": esp.descricao or "Especialidade médica de qualidade",
                    "duracao": esp.duracao_padrao
                }
                for esp in especialidades
            ]
        except Exception as e:
            print(f"Erro ao buscar especialidades: {e}")
            return []

    def get_doctors_by_specialty(self, specialty_id=None):
        """Busca médicos por especialidade"""
        try:
            if specialty_id:
                # Usar relacionamento SQLAlchemy para buscar médicos por especialidade
                especialidade = Especialidade.query.get(specialty_id)
                if especialidade:
                    medicos = [medico for medico in especialidade.medicos if medico.ativo]
                else:
                    medicos = []
            else:
                medicos = Medico.query.filter_by(ativo=True).all()
            
            resultado = []
            for medico in medicos:
                user = User.query.get(medico.user_id)
                if user:
                    resultado.append({
                        "id": medico.id,
                        "nome": user.nome,
                        "crm": medico.crm,
                        "bio": medico.bio or "Médico especialista em ginecologia e obstetrícia",
                        "especialidades": [esp.nome for esp in medico.especialidades]
                    })
            
            return resultado
        except Exception as e:
            print(f"Erro ao buscar médicos: {e}")
            return []

    def get_doctor_schedules(self, doctor_id, days_ahead=14):
        """Busca horários disponíveis de um médico"""
        try:
            if not doctor_id:
                return []
                
            medico = Medico.query.get(doctor_id)
            if not medico:
                return []
            
            data_inicio = datetime.now()
            data_fim = data_inicio + timedelta(days=days_ahead)
            
            # Gerar horários disponíveis simulados (8h às 17h, seg-sex)
            horarios_disponiveis = []
            for i in range(days_ahead):
                data_atual = data_inicio + timedelta(days=i)
                # Segunda a sexta-feira apenas
                if data_atual.weekday() < 5:  # 0=segunda, 4=sexta
                    for hora in range(8, 17):  # 8h às 16h (última consulta às 16h)
                        datetime_slot = datetime.combine(data_atual.date(), datetime.min.time().replace(hour=hora))
                        
                        # Verificar se já existe agendamento
                        agendamento_existente = Agendamento.query.filter_by(
                            medico_id=doctor_id,
                            inicio=datetime_slot
                        ).first()
                        
                        if not agendamento_existente and datetime_slot > datetime.now():
                            horarios_disponiveis.append({
                                "data": datetime_slot.strftime("%d/%m/%Y"),
                                "hora": datetime_slot.strftime("%H:%M"),
                                "duracao": 60,  # 60 minutos padrão
                                "tipo": "consulta",
                                "datetime": datetime_slot.isoformat()
                            })
            
            return horarios_disponiveis[:20]  # Limitar a 20 horários
            
        except Exception as e:
            print(f"Erro ao buscar horários: {e}")
            return []


# Instância global do serviço
try:
    chatbot_service = ChatbotService()
except Exception as e:
    print(f"Aviso: Chatbot inicializando sem OpenAI: {e}")
    # Criar instância básica mesmo sem OpenAI
    class BasicChatbotService:
        def __init__(self):
            self.use_openai = False
            self.client = None
        
        def chat_response(self, user_message, context=None):
            # Instanciar temporariamente para usar os métodos
            temp_service = ChatbotService()
            return temp_service._rule_based_response(user_message, context)
        
        def get_specialties(self):
            temp_service = ChatbotService()
            return temp_service.get_specialties()
        
        def get_doctors_by_specialty(self, specialty_id=None):
            temp_service = ChatbotService()
            return temp_service.get_doctors_by_specialty(specialty_id)
        
        def get_doctor_schedules(self, doctor_id, days_ahead=14):
            temp_service = ChatbotService()
            return temp_service.get_doctor_schedules(doctor_id, days_ahead)
    
    chatbot_service = BasicChatbotService()