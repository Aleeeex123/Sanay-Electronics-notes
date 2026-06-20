from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            return render_template('register.html', error='Пользователь уже существует')

        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (%s, %s)',
            (username, hashed_password)
        )
        cursor.close()
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id, password, is_admin FROM users WHERE username = %s', (username,))
        row = cursor.fetchone()
        cursor.close()

        if row and check_password_hash(row[1], password):
            session['user_id'] = row[0]
            session['username'] = username
            session['is_admin'] = row[2]  # row[2] — is_admin
            return redirect(url_for('main.profile'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))