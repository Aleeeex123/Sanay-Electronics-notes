from flask import Blueprint, render_template, session, redirect, url_for, request
from app.db import get_db
import markdown

bp = Blueprint('main', __name__)

def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title, section, created_at FROM articles ORDER BY created_at DESC')
    articles = cursor.fetchall()
    cursor.close()
    return render_template('index.html', articles=articles)

@bp.route('/section/<section_name>')
def section(section_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT id, title, content, created_at FROM articles WHERE section = %s ORDER BY created_at DESC',
        (section_name,)
    )
    articles = cursor.fetchall()
    cursor.close()
    return render_template('section.html', articles=articles, section_name=section_name)

@bp.route('/article/<int:article_id>')
def article(article_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, title, content, section, created_at FROM articles WHERE id = %s', (article_id,))
    article = cursor.fetchone()

    if not article:
        cursor.close()
        return 'Статья не найдена', 404

    content_html = markdown.markdown(article[2])

    bookmarked = False
    if 'user_id' in session:
        cursor.execute(
            'SELECT id FROM bookmarks WHERE user_id = %s AND article_id = %s',
            (session['user_id'], article_id)
        )
        bookmarked = cursor.fetchone() is not None

    cursor.close()
    return render_template('article.html', article=article, content_html=content_html, bookmarked=bookmarked)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_article():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()

    if not user or not user[0]:
        return 'Доступ запрещён. Только администратор может создавать статьи.', 403

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        section = request.form['section']

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO articles (title, content, section) VALUES (%s, %s, %s)',
            (title, content, section)
        )
        cursor.close()
        return redirect(url_for('main.index'))

    return render_template('create.html')

@bp.route('/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    db = get_db()
    cursor = db.cursor()

    # Проверка прав администратора
    cursor.execute('SELECT is_admin FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    if not user or not user[0]:
        cursor.close()
        return 'Доступ запрещён', 403

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        section = request.form['section']
        cursor.execute(
            'UPDATE articles SET title = %s, content = %s, section = %s WHERE id = %s',
            (title, content, section, article_id)
        )
        cursor.close()
        return redirect(url_for('main.article', article_id=article_id))

    cursor.execute('SELECT id, title, content, section FROM articles WHERE id = %s', (article_id,))
    article = cursor.fetchone()
    cursor.close()

    if not article:
        return 'Статья не найдена', 404

    return render_template('edit.html', article=article)

@bp.route('/profile')
@login_required
def profile():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT username FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()

    cursor.execute(
        '''SELECT a.id, a.title, a.section, b.created_at
           FROM bookmarks b
           JOIN articles a ON b.article_id = a.id
           WHERE b.user_id = %s
           ORDER BY b.created_at DESC''',
        (session['user_id'],)
    )
    bookmarks = cursor.fetchall()
    cursor.close()
    return render_template('profile.html', username=user[0], bookmarks=bookmarks)

@bp.route('/bookmark/<int:article_id>', methods=['POST'])
@login_required
def toggle_bookmark(article_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT id FROM bookmarks WHERE user_id = %s AND article_id = %s',
        (session['user_id'], article_id)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute('DELETE FROM bookmarks WHERE id = %s', (existing[0],))
    else:
        cursor.execute(
            'INSERT INTO bookmarks (user_id, article_id) VALUES (%s, %s)',
            (session['user_id'], article_id)
        )
    cursor.close()
    return redirect(url_for('main.article', article_id=article_id))