from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, BooleanField, DecimalField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, EqualTo

class NewLocationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])

class EditProfile(FlaskForm):
    email = StringField('email', validators=[Email()])
    password = PasswordField('password', validators=[EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('confirm_password')
    is_admin = BooleanField('is_admin')
    is_manager = BooleanField('is_manager')
    is_brewer = BooleanField('is_brewer')
