from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gestion_stock'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration pour les sessions
    app.config['SECRET_KEY'] = os.urandom(24).hex()
    
    # Initialisation de la base de données
    db.init_app(app)
    
    # Initialisation de Flask-Migrate
    migrate = Migrate(app, db)
    
    # Importation et enregistrement des routes
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    return app