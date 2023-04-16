from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class submitform(FlaskForm):
    submit = StringField('Submit', 
                validators = [DataRequired(), Length(min=2, max=20)])