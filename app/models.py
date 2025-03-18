from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

class Admin(db.Model, UserMixin):  # ✅ UserMixin for Flask-Login support
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')  # ✅ Hash password before saving

class Voter(db.Model, UserMixin):
    voter_id = db.Column(db.Integer, primary_key=True)  # Corrected to voter_id
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Nominee(db.Model):
    nominee_id = db.Column(db.Integer, primary_key=True)  # This is the primary key column
    full_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    aadhaar_number = db.Column(db.String(20), unique=True, nullable=False)
    face_data = db.Column(db.Text, nullable=False)
    party_name = db.Column(db.String(100), nullable=False)
    party_symbol = db.Column(db.String(255), nullable=False)
    candidate_photo = db.Column(db.Text, nullable=False)

class Votes(db.Model):
    vote_id = db.Column(db.Integer, primary_key=True)  # Changed to vote_id for clarity
    voter_id = db.Column(db.Integer, db.ForeignKey('voter.voter_id'), nullable=False)  # Corrected foreign key reference
    nominee_id = db.Column(db.Integer, db.ForeignKey('nominee.nominee_id'), nullable=False)  # Corrected foreign key reference

    # Relationship fields (optional, to simplify access to related data)
    voter = db.relationship('Voter', backref='votes')  # Optional relationship to Voter
    nominee = db.relationship('Nominee', backref='votes')  # Optional relationship to Nominee
