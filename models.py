# Medical clinic management system - Database models
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import bcrypt

# Association table for many-to-many relationship between medicos and especialidades
medico_especialidade = db.Table('medico_especialidade',
    db.Column('medico_id', db.Integer, db.ForeignKey('medicos.id'), primary_key=True),
    db.Column('especialidade_id', db.Integer, db.ForeignKey('especialidades.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """Modelo de usuário base para o sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(20), nullable=True)
    senha_hash = db.Column(db.String(128), nullable=True)  # Nullable para convidados
    role = db.Column(db.String(20), default='paciente')  # admin, staff, medico, paciente
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    medico = db.relationship('Medico', backref='usuario', uselist=False)
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy='dynamic')
    
    def set_password(self, password):
        """Define a senha do usuário com hash bcrypt"""
        if password:
            self.senha_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        if not self.senha_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_medico(self):
        return self.role == 'medico'
    
    def __repr__(self):
        return f'<User {self.email}>'

class Especialidade(db.Model):
    """Especialidades médicas disponíveis"""
    __tablename__ = 'especialidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    duracao_padrao = db.Column(db.Integer, default=30)  # Duração em minutos
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='especialidade', lazy='dynamic')
    
    def __repr__(self):
        return f'<Especialidade {self.nome}>'

class Medico(db.Model):
    """Médicos da clínica"""
    __tablename__ = 'medicos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crm = db.Column(db.String(20), unique=True, nullable=False)
    bio = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    especialidades = db.relationship('Especialidade', secondary=medico_especialidade, 
                                   backref=db.backref('medicos', lazy='dynamic'))
    agendas = db.relationship('Agenda', backref='medico', lazy='dynamic')
    agendamentos = db.relationship('Agendamento', backref='medico', lazy='dynamic')
    
    def get_proximos_horarios_livres(self, data_inicio=None, limite=10):
        """Retorna os próximos horários disponíveis para este médico"""
        if not data_inicio:
            data_inicio = datetime.now()
        
        # Buscar agendas futuras
        agendas = self.agendas.filter(
            Agenda.data >= data_inicio.date()
        ).order_by(Agenda.data, Agenda.hora_inicio).all()
        
        horarios_livres = []
        for agenda in agendas:
            # Verificar se já tem agendamento neste horário
            agendamento_existente = Agendamento.query.filter_by(
                medico_id=self.id,
                inicio=datetime.combine(agenda.data, agenda.hora_inicio)
            ).first()
            
            if not agendamento_existente and len(horarios_livres) < limite:
                horarios_livres.append({
                    'data': agenda.data,
                    'hora': agenda.hora_inicio,
                    'duracao': agenda.duracao_minutos
                })
        
        return horarios_livres
    
    def __repr__(self):
        return f'<Medico {self.usuario.nome if hasattr(self, "usuario") and self.usuario else "Unknown"} - CRM: {self.crm}>'

class Agenda(db.Model):
    """Agenda dos médicos - define quando estão disponíveis"""
    __tablename__ = 'agendas'
    
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    duracao_minutos = db.Column(db.Integer, default=30)
    tipo = db.Column(db.String(20), default='presencial')  # presencial, teleconsulta
    ativo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Agenda Medico ID: {self.medico_id} - {self.data} {self.hora_inicio}>'

class Agendamento(db.Model):
    """Agendamentos de consultas"""
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados do paciente (pode ser convidado ou usuário registrado)
    paciente_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nome_convidado = db.Column(db.String(100), nullable=True)
    email_convidado = db.Column(db.String(120), nullable=True)
    telefone_convidado = db.Column(db.String(20), nullable=True)
    
    # Dados do agendamento
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=False)
    especialidade_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    fim = db.Column(db.DateTime, nullable=False)
    
    # Status e controle
    status = db.Column(db.String(20), default='agendado')  # agendado, confirmado, realizado, cancelado
    origem = db.Column(db.String(20), default='site')  # site, mobile, admin
    reservado_ate = db.Column(db.DateTime, nullable=True)  # Tempo limite para confirmação
    
    # Dados adicionais
    observacoes = db.Column(db.Text)
    confirmado_em = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notificacoes = db.relationship('Notificacao', backref='agendamento', lazy='dynamic')
    pagamentos = db.relationship('Pagamento', backref='agendamento', lazy='dynamic')
    
    @property
    def nome_paciente(self):
        """Retorna o nome do paciente (registrado ou convidado)"""
        if hasattr(self, 'paciente') and self.paciente:
            return self.paciente.nome
        return self.nome_convidado
    
    @property
    def email_paciente(self):
        """Retorna o email do paciente (registrado ou convidado)"""
        if hasattr(self, 'paciente') and self.paciente:
            return self.paciente.email
        return self.email_convidado
    
    @property
    def telefone_paciente(self):
        """Retorna o telefone do paciente (registrado ou convidado)"""
        if hasattr(self, 'paciente') and self.paciente:
            return self.paciente.telefone
        return self.telefone_convidado
    
    def pode_ser_cancelado(self):
        """Verifica se o agendamento pode ser cancelado (24h de antecedência)"""
        return self.inicio > datetime.utcnow() + timedelta(hours=24)
    
    def __repr__(self):
        return f'<Agendamento {self.nome_paciente} - {self.inicio}>'

class DisponibilidadeExcecao(db.Model):
    """Exceções na disponibilidade (feriados, folgas)"""
    __tablename__ = 'disponibilidade_excecoes'
    
    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=True)  # Se None, afeta todos
    data = db.Column(db.Date, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), default='feriado')  # feriado, folga, ausencia
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notificacao(db.Model):
    """Notificações enviadas para pacientes"""
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # confirmacao, lembrete_24h, lembrete_1h
    enviado_em = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pendente')  # pendente, enviado, falhou
    tentativas = db.Column(db.Integer, default=0)
    erro = db.Column(db.Text, nullable=True)

class Pagamento(db.Model):
    """Pagamentos das consultas"""
    __tablename__ = 'pagamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=False)
    metodo = db.Column(db.String(20), nullable=False)  # cartao, pix, dinheiro
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, rejeitado
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    transacao_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LogAudit(db.Model):
    """Logs de auditoria para ações críticas"""
    __tablename__ = 'logs_audit'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    acao = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)