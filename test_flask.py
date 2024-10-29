# test_flask.py
from flask import Flask

app = Flask(__name__)

def initialize():
    print("Before first request initialization.")

# Викликаємо ініціалізацію одразу після створення об'єкта Flask
initialize()

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)
