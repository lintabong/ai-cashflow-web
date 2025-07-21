from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()  # Load .env variables

    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}"
        f"@{os.environ.get('MYSQL_HOST')}:{os.environ.get('MYSQL_PORT')}/{os.environ.get('MYSQL_DATABASE')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # Blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.wallet_controller import wallet_bp
    from app.controllers.transaction_controller import transaction_bp
    from app.controllers.main_controller import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(transaction_bp, url_prefix='/transaction')
    app.register_blueprint(main_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
