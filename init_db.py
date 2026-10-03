"""Create the SQLite database and tables: python init_db.py"""
from app import app
from database.db import init_db

if __name__ == "__main__":
    init_db(app)
    print("Database ready at:", app.config["DATABASE"])
