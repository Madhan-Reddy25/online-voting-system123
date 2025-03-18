from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  # Import text() for raw SQL queries
from config import Config  # Import Config class

app = Flask(__name__)
app.config.from_object(Config)  # Load configurations from config.py

db = SQLAlchemy(app)

try:
    with app.app_context():
        db.session.execute(text("SELECT 1"))  # Use text() for raw SQL queries
        print("✅ Database Connection Successful!")
except Exception as e:
    print(f"❌ Database Connection Failed: {e}")
