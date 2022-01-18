from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('incorrect password', category='error')
        else:
            flash('username does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = request.form.get('first-name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmed_pass = request.form.get('password-confirm')

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Username already exists', category='error')
        if len(first_name) < 2 or len(first_name) > 25:
            flash("Name must be between 2 and 25 chars long", category='error')
        elif len(username) < 2 or len(username) > 25:
            flash("Username must be between 2 and 25 chars long", category='error')
        elif len(password) < 8 or len(password) > 25:
            flash("password must be between 8 and 25 chars long", category='error')
        elif password != confirmed_pass:
            flash("Passwords do not match", category='error')
        else:
            new_user = User(first_name=first_name, username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Success", category='success')
            return redirect(url_for('views.index'))



    return render_template("sign_up.html", user=current_user)
