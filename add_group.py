from app import app
from models import db, Group

def add_group(chat_id, title):
    with app.app_context():
        existing_group = Group.query.filter_by(chat_id=chat_id).first()
        if existing_group:
            print(f"Group {title} already exists.")
        else:
            new_group = Group(chat_id=chat_id, title=title)
            db.session.add(new_group)
            db.session.commit()
            print(f"Group {title} added successfully.")

if __name__ == "__main__":
    # Замініть на ваші власні chat_id та назви груп
    add_group('-1002481015165', 'DropHelper')
    add_group('-1002130714873', 'BraveCryptoUkraine')
