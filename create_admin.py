# create_admin.py
from app import app
from models import db, User
from werkzeug.security import generate_password_hash

def create_admin(username, password):
    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists.")
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            print(f"User {username} created successfully.")

if __name__ == "__main__":
    username = 'admin'  # Замініть за потреби
    password = 'your_secure_password'  # Замініть на складний пароль
    create_admin(username, password)
