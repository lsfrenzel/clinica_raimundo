# Medical clinic management system - Flask extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Initialize Flask extensions as singletons
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
cors = CORS()