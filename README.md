# Telegram Group Message Sender

A web application for sending messages to multiple Telegram groups simultaneously. Built with Flask and python-telegram-bot.

## Features

- User authentication system
- Manage multiple Telegram groups
- Send messages to multiple groups simultaneously
- Support for Markdown formatting
- Modern Bootstrap UI
- Asynchronous message processing

## Requirements

- Python 3.12+
- Flask 3.0.3
- python-telegram-bot 20.3
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/telegram-group-sender.git
cd telegram-group-sender
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file with your settings:
```env
SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token
DATABASE_URL=sqlite:///app.db
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Create admin user:
```bash
python create_admin.py
```

## Usage

1. Start the server:
```bash
python run.py
```

2. Open http://127.0.0.1:5000 in your browser
3. Log in with admin credentials
4. Add Telegram groups via the Manage Groups page
5. Start sending messages!

## Development

- Built using Flask's application factory pattern
- Asynchronous message sending with python-telegram-bot
- Bootstrap 5 for the frontend
- SQLAlchemy for database management

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE.md file for details