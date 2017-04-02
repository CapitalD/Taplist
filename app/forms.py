from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DecimalField, SelectField, SubmitField, PasswordField
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
