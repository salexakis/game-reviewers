from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from application.models import User
from datetime import datetime as dt
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import Optional

current_year = dt.now().year

def maxImageSize(max_size=2):
    max_bytes = max_size * 1024 * 1024
    def _check_file_size(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(f'Image size cannot be greater than {max_size} MB')
    return _check_file_size


def validate_email(form, email):
    user = User.query.filter_by(email=email.data).first()
    if user:
        raise ValidationError('This email already exist!')



class SignupForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="This field cannot be empty."),
                                       Length(min=3, max=15, message="This field must be between 3 to 15 characters")])
    email = StringField(label="Email",
                           validators=[DataRequired(message="This field cannot be empty."), 
                                       Email(message="Please enter a valid email"), validate_email])
    password = StringField(label="Password",
                           validators=[DataRequired(message="This field cannot be empty."),
                                       Length(min=3, max=15, message="This field must be between 3 to 15 characters")])
    password2 = StringField(label="Re-enter Password",
                           validators=[DataRequired(message="This field cannot be empty."),
                                       Length(min=3, max=15, message="This field must be between 3 to 15 characters"),
                                       EqualTo('password', message='Password confirmation failed')])
    submit = SubmitField('Sign up')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists!')



class AccountUpdateForm(FlaskForm):
    username = StringField(label="Username",
                           validators=[DataRequired(message="This field cannot be empty."),
                                       Length(min=3, max=15, message="This field must be between 3 to 15 characters")])
    email = StringField(label="Email",
                           validators=[DataRequired(message="This field cannot be empty."), 
                                       Email(message="Please enter a valid email")])
    image = FileField('User Image', validators=[Optional(strip_whitespace=True),
                                                    FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                    'Only jpg, jpeg και png images are allowed!'),
                                                    maxImageSize(max_size=2)])
    submit = SubmitField('Update')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists!')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists!')



class LoginForm(FlaskForm):
    email = StringField(label="Email",
                           validators=[DataRequired(message="This field cannot be empty."), 
                                       Email(message="Please enter a valid email")])
    password = StringField(label="Password",
                           validators=[DataRequired(message="This field cannot be empty.")])
    remember_me = BooleanField(label="Remember me")
    submit = SubmitField('Sign in')




class NewGameForm(FlaskForm):
    title = StringField(label="Game Title",
                           validators=[DataRequired(message="This field cannot be empty."),
                                       Length(min=3, max=50, message="This field must be between 3 to 50 characters")])
    review = TextAreaField(label="Game Review",
                           validators=[DataRequired(message="This field cannot be empty."), 
                                       Length(min=50, message="Review must be at least 50 characters")])
    image = FileField('Game Picture', validators=[Optional(strip_whitespace=True),
                                                    FileAllowed([ 'jpg', 'jpeg', 'png' ],
                                                    'Only jpg, jpeg και png images are allowed!'),
                                                    maxImageSize(max_size=2)])
    rating = FloatField(label='Game Rating', validators=[DataRequired(message="This field cannot be empty."),
                                                                        NumberRange(1, 10, message="Rating must be between 1-10")])
    submit = SubmitField(label='Publish')  
