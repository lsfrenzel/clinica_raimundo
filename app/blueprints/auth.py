# Authentication blueprint
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        from models import User
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            remember_me = bool(request.form.get('remember'))
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha inválidos.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        password = request.form.get('password')
        
        from models import User
        # Verificar se email já existe
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('auth/register.html')
        
        # Criar novo usuário
        user = User()
        user.nome = nome
        user.email = email
        user.telefone = telefone
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))