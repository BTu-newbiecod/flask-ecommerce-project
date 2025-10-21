from flask import Flask, app
from config import Config #import class/ham
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

#khoi tao cac bien ,nhung chua gan vao app
db=SQLAlchemy()
migrate=Migrate()
login_manager=LoginManager()

#dung ham _> goi gon qua trinh tao web _> de dang test thu
def create_app(config_class=Config):

        app=Flask(__name__)
        app.config.from_object(config_class)

        #gắn các công cụ vào app
        db.init_app(app)          
        migrate.init_app(app,db)
        login_manager.init_app(app)

        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)

        from app.auth import bp as auth_bp #DANG KY BLUEPRINT CHO AUTH
        app.register_blueprint(auth_bp,url_prefix='/auth')

        return app

from app import models

from app.models import User
@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))


