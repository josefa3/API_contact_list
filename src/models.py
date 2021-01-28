from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Contact(db.Model):
    # __tablename__ = 'Contact'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    full_name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(14), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone
            # do not serialize the password, its a security breach
        }