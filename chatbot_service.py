# Medical clinic chatbot service - OpenAI integration
# Based on blueprint:python_openai integration
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI
from models import Especialidade, Medico, Agendamento, User
from extensions import db

# Using GPT-5 - the newest OpenAI model released August 7, 2025
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class ChatbotService:
    def __init__(self):
        if not openai_client:
            raise Exception("OPENAI_API_KEY não configurada")
        self.client = openai_client
        
    def get_system_prompt(self):
        """Define o contexto e comportamento do chatbot"""
        return """Você é um assistente virtual inteligente da Clínica Dr. Raimundo Nunes, especializada em ginecologia e obstetrícia.

Seu objetivo é ajudar pacientes a agendarem consultas de forma natural e eficiente.

DIRETRIZES:
1. Seja sempre cordial, empático e profissional
2. Use linguagem clara e acessível
3. Guie o paciente passo a passo no processo de agendamento
4. Explique as especialidades quando solicitado
5. Apresente os médicos disponíveis com seus horários
6. Confirme todos os dados antes de finalizar o agendamento
7. Responda SEMPRE em português brasileiro
8. Use JSON estruturado conforme especificado para ações específicas

FLUXO DE AGENDAMENTO:
1. Cumprimente e pergunte como pode ajudar
2. Identifique a especialidade desejada
3. Apresente os médicos disponíveis
4. Mostre os horários disponíveis
5. Colete dados do paciente se necessário
6. Confirme o agendamento

ESPECIALIDADES DISPONÍVEIS:
- Ginecologia
- Obstetrícia
- Consulta Pré-natal
- Planejamento Familiar
- Medicina Preventiva

Responda sempre em formato JSON com esta estrutura:
{
    "message": "sua resposta amigável",
    "action": "get_specialties|show_doctors|show_schedules|collect_data|confirm_booking|general_chat",
    "data": {objeto com dados específicos da ação, se aplicável}
}"""

    def chat_response(self, user_message, context=None):
        """Gera resposta do chatbot baseada na mensagem do usuário"""
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            
            # Adicionar contexto se fornecido
            if context:
                context_msg = f"Contexto da conversa: {json.dumps(context, ensure_ascii=False)}"
                messages.append({"role": "assistant", "content": context_msg})
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
            else:
                raise Exception("Resposta vazia do modelo")
            
            # Processar ações específicas
            if result.get("action") == "get_specialties":
                result["data"] = self.get_specialties()
            elif result.get("action") == "show_doctors":
                specialty_id = result.get("data", {}).get("specialty_id")
                result["data"] = self.get_doctors_by_specialty(specialty_id)
            elif result.get("action") == "show_schedules":
                doctor_id = result.get("data", {}).get("doctor_id")
                result["data"] = self.get_doctor_schedules(doctor_id)
            
            return result
            
        except Exception as e:
            return {
                "message": f"Desculpe, ocorreu um erro inesperado. Tente novamente. Erro: {str(e)}",
                "action": "error",
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

    def create_appointment(self, appointment_data, user_id=None):
        """Cria um novo agendamento"""
        try:
            # Validar dados obrigatórios
            required_fields = ['medico_id', 'especialidade_id', 'datetime_inicio', 'duracao']
            for field in required_fields:
                if field not in appointment_data:
                    return {"success": False, "message": f"Campo obrigatório: {field}"}
            
            # Converter datetime
            inicio = datetime.fromisoformat(appointment_data['datetime_inicio'].replace('Z', '+00:00'))
            fim = inicio + timedelta(minutes=appointment_data['duracao'])
            
            # Verificar se horário ainda está disponível
            conflito = Agendamento.query.filter(
                Agendamento.medico_id == appointment_data['medico_id'],
                Agendamento.inicio <= inicio,
                Agendamento.fim > inicio
            ).first()
            
            if conflito:
                return {"success": False, "message": "Este horário não está mais disponível."}
            
            # Criar agendamento
            agendamento = Agendamento()
            agendamento.medico_id = appointment_data['medico_id']
            agendamento.especialidade_id = appointment_data['especialidade_id']
            agendamento.inicio = inicio
            agendamento.fim = fim
            agendamento.origem = 'chatbot'
            
            # Dados do paciente
            if user_id:
                agendamento.paciente_id = user_id
            else:
                agendamento.nome_convidado = appointment_data.get('nome')
                agendamento.email_convidado = appointment_data.get('email')
                agendamento.telefone_convidado = appointment_data.get('telefone')
            
            if appointment_data.get('observacoes'):
                agendamento.observacoes = appointment_data['observacoes']
            
            db.session.add(agendamento)
            db.session.commit()
            
            return {
                "success": True, 
                "message": "Agendamento realizado com sucesso!",
                "agendamento_id": agendamento.id
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar agendamento: {e}")
            return {"success": False, "message": "Erro interno. Tente novamente."}

# Instância global do serviço
chatbot_service = ChatbotService()