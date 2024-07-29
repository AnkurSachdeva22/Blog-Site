from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField, URLField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
    button_style = {'style': "margin:20px 0px; background-color: black; border: solid 3px #007189; padding: 10px"}
    field_style = {'style': "margin-bottom: 10px; border-radius: 10px;"}
    email = EmailField(label='Email', render_kw=field_style, validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', render_kw=field_style,
                             validators=[DataRequired(),Length(min=8, max=16, message='Please enter a valid password')])
    submit = SubmitField(label='Login', render_kw=button_style)

class SignUpForm(FlaskForm):
    button_style = {'style': "margin:20px 0px; background-color: black; border: solid 3px #007189; padding: 10px"}
    field_style = {'style': "margin-bottom: 10px; border-radius: 10px;"}
    first_name = StringField(label='First Name', render_kw=field_style, validators=[DataRequired()])
    last_name = StringField(label='Last Name', render_kw=field_style, validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired(), Email()], render_kw=field_style)
    password = PasswordField(label='Password', render_kw=field_style,
                             validators=[DataRequired(), Length(min=8, max=16,message='Please enter a valid password')])
    submit = SubmitField(label='Sign Up', render_kw=button_style)

class CommentForm(FlaskForm):
    field_style = {'style': "margin-bottom: 10px; border-radius: 10px;"}
    button_style = {'style': "margin:20px 0px; background-color: black; border: solid 3px #007189; padding: 10px"}
    comment = CKEditorField(label='Comment', validators=[DataRequired()], render_kw=field_style)
    submit = SubmitField(label='Post Comment', render_kw=button_style)

class ContactForm(FlaskForm):
    button_style = {'style': "margin:20px 0px; background-color: black; border: solid 3px #007189; padding: 10px"}
    field_style = {'style': "margin-bottom: 10px; border-radius: 15px; border-top: 0px; border-left:0px; border-right: 0px"}
    name = StringField(label='Full Name', validators=[DataRequired()], render_kw=field_style)
    email = EmailField(label='Email', validators=[DataRequired(), Email()], render_kw=field_style)
    contact = StringField(label='Contact No.', validators=[DataRequired()], render_kw=field_style)
    message = TextAreaField(label='Message', validators=[DataRequired()], render_kw=field_style, )
    submit = SubmitField(label='Submit Request', render_kw=button_style)


class PostForm(FlaskForm):
    button_style = {'style': "margin:20px 0px; background-color: black; border: solid 3px #007189; padding: 10px"}
    field_style = {'style': "margin-bottom: 15px; border-radius: 10px; border-top: 0px; border-left:0px; border-right: 0px"}
    title = StringField(label='Blog Title', validators=[DataRequired()], render_kw=field_style)
    subtitle = StringField(label='Blog Subtitle', validators=[DataRequired()], render_kw=field_style)
    image_url = URLField(label='Blog Image', validators=[DataRequired(), URL()], render_kw=field_style)
    body = CKEditorField(label='Blog Content', validators=[DataRequired()], render_kw=field_style)
    submit = SubmitField(label='Post', render_kw=button_style)
