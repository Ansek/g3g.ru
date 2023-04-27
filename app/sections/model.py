from app.database import db

class Section(db.Model):
    __tablename__ = 'section'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)

    categories = db.relationship('Category', backref='section')

    def __str__(self):
        return self.name