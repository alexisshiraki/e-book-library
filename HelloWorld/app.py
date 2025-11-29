"""Simple Flask web app for CRUD operations on User model.

Run with: python app.py
Then visit http://localhost:5000 in your browser.

Database configuration:
- Default: SQLite (sqlite:///data.db)
- PostgreSQL: Set DATABASE_URL environment variable
  Example: $env:DATABASE_URL = "postgresql://user:pass@localhost:5432/dbname"
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import init_db
from db_sqlalchemy import User
from crud import create_user, get_user, update_user_age, delete_user, list_users, paginate_users

app = Flask(__name__)
app.secret_key = 'dev-secret-key'

# Initialize database with config module (supports SQLite and PostgreSQL)
engine, Session = init_db()


def get_session():
    """Return a fresh session for the request."""
    return Session()


@app.route('/')
def index():
    """List all users with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    session = get_session()
    try:
        pag = paginate_users(session, page=page, per_page=per_page)
        return render_template('list.html', users=pag['items'], page=page, total=pag['total'], per_page=per_page)
    finally:
        session.close()


@app.route('/user/<int:user_id>')
def view_user(user_id):
    """View a single user."""
    session = get_session()
    try:
        u = get_user(session, user_id)
        if u is None:
            flash(f'User {user_id} not found', 'error')
            return redirect(url_for('index'))
        return render_template('view.html', user=u)
    finally:
        session.close()


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new user."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age_str = request.form.get('age', '')
        age = int(age_str) if age_str else None

        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('create'))

        session = get_session()
        try:
            u = create_user(session, name, age)
            flash(f'User {u.name} created!', 'success')
            return redirect(url_for('view_user', user_id=u.id))
        finally:
            session.close()

    return render_template('create.html')


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    """Edit a user."""
    session = get_session()
    try:
        u = get_user(session, user_id)
        if u is None:
            flash(f'User {user_id} not found', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            age_str = request.form.get('age', '')
            age = int(age_str) if age_str else None

            if not name:
                flash('Name is required', 'error')
                return redirect(url_for('edit', user_id=user_id))

            # Update name and age
            u.name = name
            u.age = age
            session.add(u)
            session.commit()
            session.refresh(u)

            flash(f'User {u.name} updated!', 'success')
            return redirect(url_for('view_user', user_id=u.id))

        return render_template('edit.html', user=u)
    finally:
        session.close()


@app.route('/user/<int:user_id>/delete', methods=['POST'])
def delete(user_id):
    """Delete a user."""
    session = get_session()
    try:
        ok = delete_user(session, user_id)
        if ok:
            flash(f'User {user_id} deleted', 'success')
        else:
            flash(f'User {user_id} not found', 'error')
        return redirect(url_for('index'))
    finally:
        session.close()


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
