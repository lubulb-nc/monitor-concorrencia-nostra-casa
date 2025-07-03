from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy para toda a aplicação
db = SQLAlchemy()

def init_database(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

