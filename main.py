# Medical clinic management system - main.py
# Based on blueprint:python_database integration

import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, migrate, login_manager, mail, cors, csrf

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    # create the app
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    
    # Configure proxy fix for Replit
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Load configuration
    # SECRET_KEY é obrigatório para sessões e CSRF
    # Em produção, sempre configure SESSION_SECRET no ambiente
    secret_key = os.environ.get('SESSION_SECRET')
    if not secret_key:
        import secrets
        secret_key = secrets.token_hex(32)
        app.logger.warning('⚠️  SESSION_SECRET não configurado! Usando chave temporária. Configure SESSION_SECRET para produção!')
    app.config['SECRET_KEY'] = secret_key
    
    # configure the database, relative to the app instance folder
    # Fix Railway DATABASE_URL: postgres:// -> postgresql://
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Mail configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@clinicadrraimundonunes.com.br')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    csrf.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'  # type: ignore[assignment]
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.blueprints.appointments import bp as appointments_bp
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    
    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.blueprints.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    with app.app_context():
        # Import all models to register them
        import models  # noqa: F401
        
        db.create_all()
    
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    # Railway ou local - usa PORT do ambiente ou 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)