# app.py
from telegram.ext import Application
import logging
import sys
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from config import Config
from models import db, Group, User, MessageTemplate, MessageHistory, message_groups
from forms import (LoginForm, SendMessageForm, AddGroupForm, DeleteGroupForm, 
                  MessageTemplateForm)
from flask_login import (LoginManager, login_user, login_required, logout_user, 
                        current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_migrate import Migrate
from telegram.constants import ParseMode
import asyncio
import os
from datetime import datetime

load_dotenv()

async def send_telegram_message(bot, chat_id, text, format_type='text', image=None):
    """Utility function to send messages with proper formatting and optional image"""
    try:
        logging.info(f"Sending message with format_type: {format_type}")
        
        # Create a new application and bot for each message
        application = Application.builder().token(bot.token).build()
        new_bot = application.bot
        await new_bot.initialize()
        
        try:
            if image:
                # Параметри для підпису зображення
                caption_params = {
                    'caption': text,
                }

                # Set parse mode for caption
                if format_type == 'html':
                    logging.info("Using HTML parse mode")
                    caption_params['parse_mode'] = ParseMode.HTML
                elif format_type == 'markdown':
                    logging.info("Using Markdown parse mode")
                    caption_params['parse_mode'] = ParseMode.MARKDOWN_V2

                logging.info("Sending message with image...")
                result = await new_bot.send_photo(
                    chat_id=chat_id,
                    photo=image,
                    **caption_params
                )
                logging.info(f"Message with image sent successfully. Message ID: {result.message_id}")
            else:
                # Regular message without image
                message_params = {
                    'chat_id': chat_id,
                    'text': text,
                    'disable_web_page_preview': False,
                    'allow_sending_without_reply': True
                }

                if format_type == 'html':
                    logging.info("Using HTML parse mode")
                    message_params['parse_mode'] = ParseMode.HTML
                elif format_type == 'markdown':
                    logging.info("Using Markdown parse mode")
                    message_params['parse_mode'] = ParseMode.MARKDOWN_V2

                logging.info(f"Sending message with params: {message_params}")
                result = await new_bot.send_message(**message_params)
                logging.info(f"Message sent successfully. Message ID: {result.message_id}")

            return result

        finally:
            # Cleanup
            await new_bot.shutdown()
            await application.shutdown()

    except Exception as e:
        logging.error(f"Error sending message: {str(e)}")
        raise

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Налаштування UTF-8 для логування
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
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
        # Заповнення списку груп
        form.groups.choices = [(group.id, group.title) for group in Group.query.filter_by(is_active=True).all()]
        # Заповнення списку шаблонів
        templates = MessageTemplate.query.filter_by(user_id=current_user.id, is_active=True).all()
        if templates:
            form.template.choices = [(0, '-- Select Template --')] + [(t.id, t.name) for t in templates]
        else:
            form.template.choices = [(0, '-- No Templates Available --')]
        
        if form.validate_on_submit():
            logging.info(f"Form submitted with format_type: {form.format_type.data}")
            selected_groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
            
            # Обробка зображення
            image = None
            if form.image.data:
                logging.info("Processing uploaded image")
                image = form.image.data.read()
                logging.info(f"Image size: {len(image)} bytes")
            
            message_history = MessageHistory(
                message=form.message.data,
                user_id=current_user.id,
                template_id=form.template.data if form.template.data != 0 else None,
                status='pending'
            )
            db.session.add(message_history)
            db.session.commit()
            
            success_count = 0
            for group in selected_groups:
                status = 'failed'
                try:
                    logging.info(f"Sending message to {group.title} ({group.chat_id})")
                    
                    # Try to send message with image if provided
                    if image:
                        # Конвертація зображення в BytesIO для повторного використання
                        from io import BytesIO
                        image_stream = BytesIO(image)
                        image_stream.seek(0)
                        
                        logging.info("Sending message with image")
                        await send_telegram_message(
                            app.bot,
                            group.chat_id,
                            form.message.data,
                            form.format_type.data,
                            image=image_stream
                        )
                    else:
                        await send_telegram_message(
                            app.bot,
                            group.chat_id,
                            form.message.data,
                            form.format_type.data
                        )
                    
                    status = 'success'
                    success_count += 1
                    group.last_message_at = datetime.utcnow()
                    logging.info(f"Message sent to {group.title} ({group.chat_id})")
                    
                except Exception as e:
                    error_msg = str(e)
                    logging.error(f"Failed to send message to {group.title}: {error_msg}")
                    message_history.error_message = error_msg
                    flash(f"Failed to send message to {group.title}: {error_msg}", 'danger')
                
                finally:
                    # Record attempt in any case
                    db.session.execute(
                        message_groups.insert().values(
                            message_id=message_history.id,
                            group_id=group.id,
                            sent_at=datetime.utcnow(),
                            status=status
                        )
                    )
            
            # Update message history status
            if success_count == len(selected_groups):
                message_history.status = 'sent'
            elif success_count == 0:
                message_history.status = 'failed'
            else:
                message_history.status = 'partial'
                
            message_history.sent_at = datetime.utcnow()
            db.session.commit()
            
            if success_count > 0:
                flash(f'Messages sent successfully to {success_count} group(s).', 'success')
            
            return redirect(url_for('send_message'))
            
        return render_template('send_message.html', form=form)
    
    @app.route('/manage_groups', methods=['GET', 'POST'])
    @login_required
    def manage_groups():
        add_form = AddGroupForm(prefix='add')
        delete_form = DeleteGroupForm(prefix='delete')
        
        delete_form.group_id.choices = [(group.id, group.title) 
                                      for group in Group.query.filter_by(is_active=True).all()]
        
        if add_form.validate_on_submit() and add_form.submit.data:
            new_group = Group(chat_id=add_form.chat_id.data, 
                            title=add_form.title.data)
            db.session.add(new_group)
            db.session.commit()
            flash(f'Group {new_group.title} added successfully.', 'success')
            return redirect(url_for('manage_groups'))
        
        if delete_form.validate_on_submit() and delete_form.submit.data:
            groups_to_delete = Group.query.filter(
                Group.id.in_(delete_form.group_id.data)
            ).all()
            for group in groups_to_delete:
                group.is_active = False  # М'яке видалення
            db.session.commit()
            flash('Selected groups deleted successfully.', 'success')
            return redirect(url_for('manage_groups'))
        
        return render_template('manage_groups.html', 
                             add_form=add_form, 
                             delete_form=delete_form)

    @app.route('/templates', methods=['GET'])
    @login_required
    def manage_templates():
        templates = MessageTemplate.query.filter_by(
            user_id=current_user.id, is_active=True
        ).order_by(MessageTemplate.created_at.desc()).all()
        form = MessageTemplateForm()
        return render_template('manage_templates.html', 
                             templates=templates, 
                             form=form)

    @app.route('/template/create', methods=['POST'])
    @login_required
    def create_template():
        form = MessageTemplateForm()
        if form.validate_on_submit():
            template = MessageTemplate(
                name=form.name.data,
                description=form.description.data,
                content=form.content.data,
                format_type=form.format_type.data,
                user_id=current_user.id
            )
            db.session.add(template)
            db.session.commit()
            flash('Template created successfully!', 'success')
        return redirect(url_for('manage_templates'))

    @app.route('/template/<int:template_id>', methods=['GET'])
    @login_required
    def get_template(template_id):
        template = MessageTemplate.query.get_or_404(template_id)
        if template.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        return jsonify({
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'content': template.content,
            'format_type': template.format_type
        })

    @app.route('/template/<int:template_id>/update', methods=['POST'])
    @login_required
    def update_template(template_id):
        template = MessageTemplate.query.get_or_404(template_id)
        if template.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        form = MessageTemplateForm()
        if form.validate_on_submit():
            template.name = form.name.data
            template.description = form.description.data
            template.content = form.content.data
            template.format_type = form.format_type.data
            template.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Template updated successfully!', 'success')
        return redirect(url_for('manage_templates'))

    @app.route('/template/<int:template_id>/delete', methods=['POST'])
    @login_required
    def delete_template(template_id):
        template = MessageTemplate.query.get_or_404(template_id)
        if template.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        template.is_active = False  # Soft delete
        db.session.commit()
        return jsonify({'status': 'success'})

    @app.route('/messages/history')
    @login_required
    def message_history():
        messages = MessageHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(MessageHistory.sent_at.desc()).all()
        return render_template('message_history.html', messages=messages)
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app