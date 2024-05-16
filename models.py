from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define User model
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(100), nullable=False)

# Define Tour model
class Tour(db.Model):
    __tablename__="tour"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(150), index=True, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    # Add more fields as needed

# Define Booking model
class Booking(db.Model):
    __tablename__="booking"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tour_id = db.Column(db.Integer, db.ForeignKey('tour.id'), nullable=False)
    # Add more fields as needed
    