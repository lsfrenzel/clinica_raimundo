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
        import sys
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Debug logging
        print(f"[LOGIN] Tentativa de login: {email}", file=sys.stderr)
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"[LOGIN] Usuário não encontrado: {email}", file=sys.stderr)
            flash('Email ou senha inválidos.', 'error')
        elif not user.ativo:
            print(f"[LOGIN] Usuário inativo: {email}", file=sys.stderr)
            flash('Usuário inativo. Contate o administrador.', 'error')
        elif user.check_password(password):
            print(f"[LOGIN] Login bem-sucedido: {email}", file=sys.stderr)
            remember_me = bool(request.form.get('remember'))
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirecionar baseado na role do usuário
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_medico():
                return redirect(url_for('main.painel_medico'))
            else:
                # Pacientes vão para o chatbot
                return redirect(url_for('main.chatbot'))
        else:
            print(f"[LOGIN] Senha incorreta para: {email}", file=sys.stderr)
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
        return redirect(url_for('main.chatbot'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.index'))