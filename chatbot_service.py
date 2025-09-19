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
        # Usar OpenAI se disponível, senão usar versão baseada em regras
        self.client = openai_client
        self.use_openai = openai_client is not None
        
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
            if self.use_openai and self.client:
                return self._openai_response(user_message, context)
            else:
                return self._rule_based_response(user_message, context)
            
        except Exception as e:
            # Se OpenAI falhar (quota excedida), usar versão baseada em regras
            if "insufficient_quota" in str(e) or "429" in str(e):
                return self._rule_based_response(user_message, context)
            
            return {
                "message": f"Desculpe, ocorreu um erro inesperado. Tente novamente. Erro: {str(e)}",
                "action": "error",
                "data": {}
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
        
        response = self.client.chat.completions.create(  # type: ignore
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

    def _rule_based_response(self, user_message, context=None):
        """Resposta baseada em regras (quando OpenAI não está disponível)"""
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
            return ChatbotService._rule_based_response(self, user_message, context)
        
        def get_specialties(self):
            return ChatbotService.get_specialties(self)
        
        def get_doctors_by_specialty(self, specialty_id=None):
            return ChatbotService.get_doctors_by_specialty(self, specialty_id)
        
        def get_doctor_schedules(self, doctor_id, days_ahead=14):
            return ChatbotService.get_doctor_schedules(self, doctor_id, days_ahead)
    
    chatbot_service = BasicChatbotService()