# API blueprint - REST endpoints for mobile integration
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from extensions import db

bp = Blueprint('api', __name__)
api = Api(bp)

class EspecialidadesAPI(Resource):
    def get(self):
        """Lista todas as especialidades ativas"""
        from models import Especialidade
        especialidades = Especialidade.query.filter_by(ativo=True).all()
        return {
            'especialidades': [
                {
                    'id': esp.id,
                    'nome': esp.nome,
                    'descricao': esp.descricao,
                    'duracao_padrao': esp.duracao_padrao
                }
                for esp in especialidades
            ]
        }

class MedicosAPI(Resource):
    def get(self):
        """Lista médicos por especialidade"""
        from models import Especialidade, Medico
        especialidade_id = request.args.get('especialidade_id')
        
        if especialidade_id:
            especialidade = Especialidade.query.get_or_404(especialidade_id)
            medicos = especialidade.medicos.filter_by(ativo=True).all()
        else:
            medicos = Medico.query.filter_by(ativo=True).all()
        
        return {
            'medicos': [
                {
                    'id': medico.id,
                    'nome': medico.usuario.nome,
                    'crm': medico.crm,
                    'bio': medico.bio,
                    'foto_url': medico.foto_url,
                    'especialidades': [esp.nome for esp in medico.especialidades]
                }
                for medico in medicos
            ]
        }

class DisponibilidadeAPI(Resource):
    def post(self):
        """Retorna próximos horários livres por médico/especialidade"""
        data = request.get_json()
        medico_id = data.get('medico_id')
        especialidade_id = data.get('especialidade_id')
        data_inicio = data.get('data_inicio')
        limite = data.get('limite', 10)
        
        if data_inicio:
            try:
                data_inicio = datetime.fromisoformat(data_inicio)
            except ValueError:
                data_inicio = datetime.now()
        else:
            data_inicio = datetime.now()
        
        from models import Medico, Especialidade
        if medico_id:
            medico = Medico.query.get_or_404(medico_id)
            horarios = medico.get_proximos_horarios_livres(data_inicio, limite)
            return {
                'medico_id': medico.id,
                'medico_nome': medico.usuario.nome,
                'horarios_disponiveis': horarios
            }
        
        elif especialidade_id:
            especialidade = Especialidade.query.get_or_404(especialidade_id)
            medicos = especialidade.medicos.filter_by(ativo=True).all()
            
            resultado = []
            for medico in medicos:
                horarios = medico.get_proximos_horarios_livres(data_inicio, limite)
                if horarios:
                    resultado.append({
                        'medico_id': medico.id,
                        'medico_nome': medico.usuario.nome,
                        'horarios_disponiveis': horarios[:3]  # Máximo 3 por médico
                    })
            
            return {'medicos_disponiveis': resultado}
        
        return {'error': 'medico_id ou especialidade_id são obrigatórios'}, 400

class AgendamentoAPI(Resource):
    def post(self):
        """Cria novo agendamento"""
        data = request.get_json()
        
        try:
            medico_id = data['medico_id']
            especialidade_id = data['especialidade_id']
            inicio = datetime.fromisoformat(data['inicio'])
            fim = datetime.fromisoformat(data['fim'])
            
            # Dados do paciente
            nome = data['nome']
            email = data['email']
            telefone = data.get('telefone')
            
            from models import Agendamento
            # Verificar se horário ainda está disponível
            agendamento_existente = Agendamento.query.filter_by(
                medico_id=medico_id,
                inicio=inicio
            ).first()
            
            if agendamento_existente:
                return {'error': 'Horário não está mais disponível'}, 409
            
            # Criar agendamento
            agendamento = Agendamento()
            agendamento.medico_id = medico_id
            agendamento.especialidade_id = especialidade_id
            agendamento.inicio = inicio
            agendamento.fim = fim
            agendamento.nome_convidado = nome
            agendamento.email_convidado = email
            agendamento.telefone_convidado = telefone
            agendamento.origem = 'mobile'
            
            db.session.add(agendamento)
            db.session.commit()
            
            return {
                'agendamento_id': agendamento.id,
                'status': 'agendado',
                'mensagem': 'Agendamento criado com sucesso'
            }, 201
            
        except KeyError as e:
            return {'error': f'Campo obrigatório ausente: {str(e)}'}, 400
        except Exception as e:
            return {'error': 'Erro interno do servidor'}, 500

class ConfirmarAgendamentoAPI(Resource):
    def post(self):
        """Confirma agendamento com OTP (mock)"""
        data = request.get_json()
        from models import Agendamento
        agendamento_id = data.get('agendamento_id')
        otp = data.get('otp')
        
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        # Mock OTP validation (em produção, usar Twilio ou similar)
        if otp == '123456':
            agendamento.status = 'confirmado'
            agendamento.confirmado_em = datetime.utcnow()
            db.session.commit()
            
            return {
                'status': 'confirmado',
                'mensagem': 'Agendamento confirmado com sucesso'
            }
        else:
            return {'error': 'OTP inválido'}, 400

class CancelarAgendamentoAPI(Resource):
    def post(self):
        """Cancela agendamento"""
        data = request.get_json()
        from models import Agendamento
        agendamento_id = data.get('agendamento_id')
        motivo = data.get('motivo', '')
        
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        if not agendamento.pode_ser_cancelado():
            return {'error': 'Agendamento não pode ser cancelado (menos de 24h)'}, 400
        
        agendamento.status = 'cancelado'
        agendamento.observacoes = f'Cancelado: {motivo}'
        
        db.session.commit()
        
        return {
            'status': 'cancelado',
            'mensagem': 'Agendamento cancelado com sucesso'
        }

# Endpoint de health check para evitar 404s
@bp.route('/', methods=['HEAD', 'GET'])
def api_health():
    """Health check da API"""
    return jsonify({'status': 'ok', 'service': 'Medical Clinic API'})

# Endpoint para chatbot (não REST, endpoint direto)
@bp.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    """Endpoint para interação com chatbot inteligente"""
    try:
        from chatbot_service import chatbot_service
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Mensagem é obrigatória'}), 400
        
        user_message = data['message']
        context = data.get('context', {})
        
        # Adicionar informações do usuário logado ao contexto
        context['user_id'] = current_user.id
        context['user_name'] = current_user.nome
        context['user_email'] = current_user.email
        
        # Processar mensagem no chatbot
        response = chatbot_service.chat_response(user_message, context)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        print(f"Erro no chatbot: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# Registrar recursos da API
api.add_resource(EspecialidadesAPI, '/especialidades')
api.add_resource(MedicosAPI, '/medicos')
api.add_resource(DisponibilidadeAPI, '/availability')
api.add_resource(AgendamentoAPI, '/book')
api.add_resource(ConfirmarAgendamentoAPI, '/confirm')
api.add_resource(CancelarAgendamentoAPI, '/cancel')