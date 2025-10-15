from flask import Flask
from config import Config #import class/ham
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#khoi tao cac bien ,nhung chua gan vao app
db=SQLAlchemy()
migrate=Migrate()

#dung ham _> goi gon qua trinh tao web _> de dang test thu
def create_app(config_class=Config):

        app=Flask(__name__)
        app.config.from_object(config_class)

        db.init_app(app)          
        migrate.init_app(app,db)

        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)

        return app

from app import models


