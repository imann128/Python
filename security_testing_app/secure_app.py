from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
import subprocess
import html
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Secure database setup
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin12345')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'admin2', 'admin2345')") 
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('secure_template.html')

# Parameterized query to prevent SQL Injection
@app.route('/search')
def search():
    query = request.args.get('query', '')
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()

    # Secure: Parameterized query
    c.execute("SELECT * FROM users WHERE username LIKE ?", (f'%{query}%',))
    results = c.fetchall()
    conn.close()

    # Secure: HTML escape output
    escaped_results = html.escape(str(results))
    return f"Results: {escaped_results}"

# Fixed input validation and restricted commands
@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.form.get('command', '')

    # Secure: Input validation and command restriction
    allowed_commands = ['ls', 'pwd', 'whoami']
    if command.split()[0] not in allowed_commands:
        return "Error: Command not allowed"

    try:
        # Without shell=True and with input validation
        result = subprocess.check_output(command.split(), text=True, stderr=subprocess.STDOUT)
        escaped_result = html.escape(result)
        return f"Command output: {escaped_result}"
    except Exception as e:
        escaped_error = html.escape(str(e))
        return f"Error: {escaped_error}"
    
# Fixed: Secure authentication with parameterized queries
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # Input validation
    if not username or not password:
        return render_template('secure_template.html', message="Username and password required")
    
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()

    # Secure: Paramterized query
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        # Secure: No XSS vulnerability
        return render_template('secure_template.html', message=f"Welcome {html.escape(username)}")
    else:
        return render_template('secure_template.html', message="Login failed")
    
if __name__ == '__main__':
    init_db()
    # Debug mode disabled
    app.run(debug=False, host='0.0.0.0', port=5000)
