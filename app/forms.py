from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, BooleanField, DecimalField, SelectField, SubmitField, PasswordField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, EqualTo
from models import Person
from flask_login import current_user
from flask_wtf.file import FileField
from . import bcrypt

class NewLocation(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    private = BooleanField('private')
    add_location = SubmitField('Add location')
    save_changes = SubmitField('Save changes')


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    login = SubmitField('Log in')

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
    add_person = SubmitField('Add person')
    save_changes = SubmitField('Save changes')

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
        if self.add_person.data and not all([self.password.data,self.confirm_password.data]):
            msg = 'Both password fields are required'
            self.password.errors.append(msg)
            self.confirm_password.errors.append(msg)
            return False
        if self.save_changes.data and any([self.current_password.data,self.password.data,self.confirm_password.data]) and not all([self.current_password.data,self.password.data,self.confirm_password.data]):
            msg = 'All three password fields are all required to change your password'
            self.current_password.errors.append(msg)
            self.password.errors.append(msg)
            self.confirm_password.errors.append(msg)
            return False
        if self.save_changes.data and all([self.current_password.data,self.password.data,self.confirm_password.data]):
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

    def validate(self):
        if not super(TapKeg, self).validate():
            return False
        if self.tap_keg.data and not all([self.brewery.data, self.beer.data]):
            msg = 'You must choose both a brewery and a beer'
            self.brewery.errors.append(msg)
            self.beer.errors.append(msg)
            return False
        return True

class NewTap(FlaskForm):
    label = StringField('label', validators=[DataRequired()])
    add_tap = SubmitField('Add tap')

class NewBrewery(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    add_brewery = SubmitField('Add brewery')
    save_changes = SubmitField('Save changes')

class UploadBeerXML(FlaskForm):
    file = FileField('Beer XML')

class NewBeer(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    style = StringField('style', validators=[DataRequired()])
    abv = DecimalField('abv', validators=[DataRequired()])
    colour = DecimalField('colour', validators=[Optional()])
    add_beer = SubmitField('Add beer')
    save_changes = SubmitField('Save changes')
