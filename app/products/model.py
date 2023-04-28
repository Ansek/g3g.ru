from app.database import db
from dataclasses import dataclass

@dataclass
class Product(db.Model):
    id: int
    name: str
    cost: float
    img_path: str
    category_id: int

    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    cost = db.Column(db.Float, nullable=False)
    img_path = db.Column(db.String(256), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __str__(self):
        return self.name