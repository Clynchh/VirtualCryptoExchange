from flask import Flask
from flask_login import LoginManager
import sqlite3


DB_NAME = "exchange.db"

def create_app():
    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'f6e0h7a9d5b43m2'
    application.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'


    from .app import app

    application.register_blueprint(app, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = 'app.login'
    login_manager.init_app(application)

    
    @login_manager.user_loader
    def load_user(id):
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute("""
        SELECT user_id FROM users WHERE user_id = ?
        """, (id))
        user_id = cursor.fetchone()
        return user_id[0]
        

    return application



