import logging
from flask import Flask, render_template, redirect, url_for, flash
from config import Config
from models import db, Group, User
from forms import LoginForm, SendMessageForm, AddGroupForm, DeleteGroupForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_migrate import Migrate
from telegram.constants import ParseMode
import asyncio
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    app.bot = None
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            new_user = User(username='admin', password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            logging.info("Admin user created.")
        else:
            logging.info("Admin user already exists.")
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('send_message'))
            
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('send_message'))
            else:
                flash('Invalid username or password.', 'danger')
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/', methods=['GET', 'POST'])
    @login_required
    async def send_message():
        form = SendMessageForm()
        form.groups.choices = [(group.id, group.title) for group in Group.query.all()]
        
        if form.validate_on_submit():
            if not app.bot:
                flash('Telegram bot is not initialized.', 'danger')
                return redirect(url_for('send_message'))
                
            selected_groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
            success_count = 0
            
            for group in selected_groups:
                try:
                    logging.info(f"Sending message to {group.title} ({group.chat_id})")
                    await app.bot.send_message(
                        chat_id=group.chat_id,
                        text=form.message.data,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=False
                    )
                    success_count += 1
                    logging.info(f"Message sent to {group.title}")
                except Exception as e:
                    logging.error(f"Failed to send message to {group.title}: {e}")
                    flash(f"Failed to send message to {group.title}: {str(e)}", 'danger')
            
            if success_count > 0:
                flash(f'Messages sent successfully to {success_count} group(s).', 'success')
            
            return redirect(url_for('send_message'))
            
        return render_template('send_message.html', form=form)
    
    @app.route('/manage_groups', methods=['GET', 'POST'])
    @login_required
    def manage_groups():
        add_form = AddGroupForm(prefix='add')
        delete_form = DeleteGroupForm(prefix='delete')
        
        delete_form.group_id.choices = [(group.id, group.title) for group in Group.query.all()]
        
        if add_form.validate_on_submit() and add_form.submit.data:
            new_group = Group(chat_id=add_form.chat_id.data, title=add_form.title.data)
            db.session.add(new_group)
            db.session.commit()
            flash(f'Group {new_group.title} added successfully.', 'success')
            return redirect(url_for('manage_groups'))
        
        if delete_form.validate_on_submit() and delete_form.submit.data:
            groups_to_delete = Group.query.filter(Group.id.in_(delete_form.group_id.data)).all()
            for group in groups_to_delete:
                db.session.delete(group)
            db.session.commit()
            flash('Selected groups deleted successfully.', 'success')
            return redirect(url_for('manage_groups'))
        
        return render_template('manage_groups.html', add_form=add_form, delete_form=delete_form)
    
    return app