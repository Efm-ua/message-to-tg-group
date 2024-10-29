# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Regexp

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SendMessageForm(FlaskForm):
    groups = SelectMultipleField('Select Groups', validators=[DataRequired()], coerce=int)
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class AddGroupForm(FlaskForm):
    chat_id = StringField('Chat ID', validators=[
        DataRequired(),
        Regexp(r'^-100\d{10,}$', message="Chat ID має бути у форматі -100XXXXXXXXXX")
    ])
    title = StringField('Group Title', validators=[DataRequired()])
    submit = SubmitField('Add Group')

class DeleteGroupForm(FlaskForm):
    group_id = SelectMultipleField('Select Groups to Delete', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Delete Groups')
