
from flask import Flask
from app.database import db


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import register_routes
    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
