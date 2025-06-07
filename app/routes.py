from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import app, db
from .models import User, Post, Comment
from .forms import RegisterForm, LoginForm, PostForm, CommentForm

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post_id))
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_created.desc()).all()
    return render_template('post_detail.html', post=post, form=form, comments=comments)
