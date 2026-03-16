from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 1. Define db OUTSIDE the function
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yalamanchili_fuels.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Link db to this specific app
    db.init_app(app)

    with app.app_context():
        # 3. Import routes and models INSIDE the context to avoid circularity
        from . import models, routes
        db.create_all()
        routes.register_routes(app)

    return app