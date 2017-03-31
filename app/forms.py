from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class NewLocationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
