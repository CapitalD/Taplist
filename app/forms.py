from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, BooleanField, DecimalField, SelectField, SubmitField, PasswordField, HiddenField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, EqualTo

class NewLocationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    submit = SubmitField('Add location')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log in')

class EditProfile(FlaskForm):
    email = StringField('email', validators=[Email()])
    password = PasswordField('password', validators=[EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('confirm_password')
    is_admin = BooleanField('is_admin')
    is_manager = BooleanField('is_manager')
    is_brewer = BooleanField('is_brewer')
    submit = SubmitField('Save changes')

class TapKeg(FlaskForm):
    tap_id = HiddenField('tap_id', validators=[DataRequired()])
    brewery = QuerySelectField(get_label='name', allow_blank=True, blank_text='Choose a brewery')
    beer = QuerySelectField(get_label='name', allow_blank=True, blank_text='Choose a brewery before choosing a beer')
    tap_keg = SubmitField('Tap keg')

class NewTap(FlaskForm):
    location_id = HiddenField('location_id', validators=[DataRequired()])
    label = StringField('label', validators=[DataRequired()])
    add_tap = SubmitField('Add tap')

class NewBrewery(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    submit = SubmitField('Add brewery')
