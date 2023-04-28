from app.database import db
from dataclasses import dataclass

@dataclass
class Section(db.Model):
    id: int
    name: str

    __tablename__ = 'section'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)

    categories = db.relationship('Category', backref='section')

    def __str__(self):
        return self.name