import smtplib
from flask import Flask, render_template, redirect, url_for, request, flash
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float, ForeignKey
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, LoginManager, login_user, logout_user, current_user, UserMixin
from forms import LoginForm, SignUpForm, CommentForm, ContactForm, PostForm
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
import os
from secrets import token_hex
from datetime import date, datetime

SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

year = datetime.today().year

# Create app and contexts
app = Flask(__name__)
app.secret_key = token_hex(30)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///posts.db')


# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)


# CKEditor, SQL, Bootstrap setup
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ------------------- MODELS --------------------
class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(250), nullable=False, unique=False)
    last_name: Mapped[str] = mapped_column(String(250), nullable=False, unique=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False, unique=False)
    # Relationship with Blogs
    blogs: Mapped[List['Blogs']] = relationship(back_populates='user')
    # Relationship with Comments
    comments: Mapped[List['Comment']] = relationship(back_populates='user')
    # Relationship with Password Recovery
    password_requests: Mapped[List['RecoveryRequests']] = relationship(back_populates='user')

    def __repr__(self):
        return f"{self.first_name}{self.last_name}"

class Blogs(db.Model):
    __tablename__ = 'blogs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(String(1000), nullable=False)
    image_url: Mapped[str] = mapped_column(String(200), nullable=False)
    # Relationship with User
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['Users'] = relationship(back_populates='blogs')
    # Relationship with Comments
    comments: Mapped[List['Comment']] = relationship(back_populates='blog')

    def __repr__(self):
        return f"{self.title}"


class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_text : Mapped[int] = mapped_column(String(1000), nullable=False)
    comment_author: Mapped[str] = mapped_column(String(100), nullable=False)
    # Relation with Blog
    blog_id : Mapped[int] = mapped_column(ForeignKey('blogs.id'))
    blog: Mapped['Blogs'] = relationship(back_populates='comments')
    # Relationship with User
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['Users'] = relationship(back_populates='comments')

class RecoveryRequests(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    time_received: Mapped[str] = mapped_column(String(250), nullable=False)
    date_received: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default='In Progress')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['Users'] = relationship(back_populates='password_requests')

with app.app_context():
    db.create_all()


# -------------------- VIEWS --------------------
@app.route('/')
def home():
    posts = db.session.execute(db.select(Blogs)).scalars().all()
    return render_template('index.html', posts=posts, year=year)

@app.route('/new-post', methods=['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Blogs(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=f"{current_user.first_name} {current_user.last_name}",
            user_id=current_user.id,
            date=date.today().strftime("%b %d, %Y"),
            body=form.body.data,
            image_url=form.image_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new-post.html', form=form, year=year)

@app.route('/edit-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    current_post = db.session.execute(db.select(Blogs).where(Blogs.id == post_id)).scalar()
    form = PostForm(
        title=current_post.title,
        subtitle=current_post.subtitle,
        body=current_post.body,
        image_url=current_post.image_url,
        author=current_post.author,
        date=current_post.date
    )
    if form.validate_on_submit():
        current_post.title = form.title.data
        current_post.subtitle = form.subtitle.data
        current_post.body = form.body.data
        current_post.image_url = form.image_url.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('new-post.html', form=form, year=year)

@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            comment_text=form.comment.data,
            comment_author=f"{current_user.first_name} {current_user.last_name}",
            user_id=current_user.id,
            blog_id=post_id
        )
        db.session.add(new_comment)
        db.session.commit()
    post = db.session.execute(db.select(Blogs).where(Blogs.id == post_id)).scalar()
    return render_template('post.html', post=post, form=form, year=year)

@app.route('/delete/<int:post_id>')
@login_required
def delete(post_id):
    post_to_delete = db.session.execute(db.select(Blogs).where(Blogs.id == post_id)).scalar()
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_exists = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
        if user_exists:
            if check_password_hash(password=form.password.data, pwhash=user_exists.password):
                login_user(user_exists)
                return redirect(url_for('home'))
            else:
                flash('Wrong Password, Please try again!')
        else:
            flash('User Does not exist. Check the email or register first')
    return render_template('login.html', form=form, year=year)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user_exists = db.session.execute(db.select(Users).where(Users.email == form.email.data)).scalar()
        if user_exists:
            flash('User already Exists. Check your email')
        else:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=10)
            new_user = Users(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                password = hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('signup.html', form=form, year=year)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        contact_no = form.contact.data
        message = form.message.data
        text_to_send = f"Subject:Contact Request Received\n\nname: {name}\nemail: {email}\ncontact: {contact_no}\nyour message: {message}"
        with smtplib.SMTP('smtp.gmail.com') as connection:
            connection.starttls()
            connection.login(user=SMTP_USER, password=SMTP_PASSWORD)
            connection.sendmail(from_addr=SMTP_USER, to_addrs=email, msg=text_to_send)
        return render_template('contact.html', form=form, email_sent=True)
    return render_template('contact.html', form=form, email_sent=False, year=year)

@app.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == 'POST':
        user = db.session.execute(db.select(Users).where(Users.email == request.form.get('email'))).scalar()
        if user:
            email = request.form.get('email')
            key = token_hex(60)
            new_request = RecoveryRequests(
                email=email,
                key=key,
                time_received=datetime.today().time().strftime("%H:%M"),
                date_received=datetime.today().date().strftime("%d-%m"),
                user_id=user.id
            )
            db.session.add(new_request)
            db.session.commit()
            recovery_url = f"{url_for('recovery')}/{key}"
            text_to_send = (f"Subject:Passwrord Recovery\n\n<html><body><p>We have received a request to reset your password.</p> "
                            f"\nClick this url to recover your password\n<a href='{recovery_url}'>{recovery_url}</a>"
                            f"<p>If it wasn't you, please ignore the email</p></body></html>")
            with smtplib.SMTP('smtp.gmail.com') as connection:
                connection.starttls()
                connection.login(user=SMTP_USER, password=SMTP_PASSWORD)
                connection.sendmail(from_addr=SMTP_USER,
                                    to_addrs=email,
                                    msg=text_to_send)
        return render_template('forgot-password.html', email_sent=True)
    return render_template('forgot-password.html', email_sent=False)

@app.route('/account-recovery/<key>', methods=['POST', 'GET'])
def recovery(key):
    # key = request.args.get('key')
    if request.method == 'POST':
        # print(request.args.get('key'))
        request_details = db.session.execute(db.select(RecoveryRequests).where(RecoveryRequests.key == key)).scalar()
        if request_details:
            print('You are here')
            user = db.session.execute(db.select(Users).where(Users.id == request_details.user_id)).scalar()
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            if password1 != password2:
                flash("Passwords do not match")
            else:
                user.password = generate_password_hash(password=password1, method='pbkdf2:sha256', salt_length=10)
                print(user.password, password1)
                db.session.commit()
                flash('Password reset successfully')
                return redirect(url_for('login'))
    return render_template('recovery.html', key=key)

@app.route('/about')
def about():
    return render_template('about.html', year=year)


if __name__ == "__main__":
    app.run(debug=False)

