from app.database import db
from dataclasses import dataclass

@dataclass
class Category(db.Model):
    id: int
    name: str
    section_id: int
    
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    products = db.relationship('Product', backref='category')

    def __str__(self):
        return self.name