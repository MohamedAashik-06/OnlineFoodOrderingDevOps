
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text, nullable=False)

    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(50), default="Pending")

    def __repr__(self):
        return f"<Order {self.id}>"
