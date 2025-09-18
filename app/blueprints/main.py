# Main blueprint - Homepage and general routes
from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage com agendamento rápido"""
    from models import Especialidade, Medico
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    medicos = Medico.query.filter_by(ativo=True).limit(6).all()
    return render_template('index.html', especialidades=especialidades, medicos=medicos)

@bp.route('/sobre')
def sobre():
    """Página sobre a clínica"""
    return render_template('sobre.html')

@bp.route('/especialidades')
def especialidades():
    """Lista todas as especialidades"""
    from models import Especialidade
    especialidades = Especialidade.query.filter_by(ativo=True).all()
    return render_template('especialidades.html', especialidades=especialidades)

@bp.route('/medicos')
def medicos():
    """Lista todos os médicos"""
    from models import Medico
    medicos = Medico.query.filter_by(ativo=True).all()
    return render_template('medicos.html', medicos=medicos)