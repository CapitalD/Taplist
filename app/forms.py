from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, BooleanField, DecimalField, SelectField, SubmitField, PasswordField, HiddenField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, EqualTo
from models import Person
from flask_login import current_user
from . import bcrypt

class NewLocationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    submit = SubmitField('Add location')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Log in')

class ProfileForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    email = StringField('email', validators=[Email()])
    current_password = PasswordField('confirm_password')
    password = PasswordField('password', validators=[EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('confirm_password')
    is_admin = BooleanField('is_admin')
    is_manager = BooleanField('is_manager')
    location = QuerySelectField(get_label='name', allow_blank=True, blank_text='Choose a location to manage')
    is_brewer = BooleanField('is_brewer')
    brewery = QuerySelectField(get_label='name', allow_blank=True, blank_text='Choose a brewery to manage')
    submit = SubmitField('Save changes')

    def validate(self):
        if not super(ProfileForm, self).validate():
            return False
        if self.is_manager.data and not self.location.data:
            msg = 'A location must be selected if the person is a bar manager'
            self.location.errors.append(msg)
            return False
        if self.is_brewer.data and not self.brewery.data:
            msg = 'A brewery must be selected if the person is a brewer'
            self.brewery.errors.append(msg)
            return False
        if self.current_password.data:
            current = Person.query.get(current_user.id)
            if not bcrypt.check_password_hash(current.password, self.current_password.data):
                msg = 'Current password is incorrect.  Please try again.'
                self.current_password.errors.append(msg)
                return False
        return True

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

class NewBeer(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    style = StringField('style', validators=[DataRequired()])
    abv = DecimalField('abv', validators=[DataRequired()])
    colour = DecimalField('colour', validators=[Optional()])
    submit = SubmitField('Add beer')
