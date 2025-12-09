from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'weak_secret_key'

# Insecure database connection
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin12345')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'admin2', 'admin2345')") 
    conn.commit()
    conn.close()

# Vulnerable HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE HTML>
<html>
<title>Vulnerable App </title>
<head>
    <h1>This is a purposely made vulnerable application</h1>
    <h2>Practically applying security tools</h2>
</head>
<body>
    <h3>Login</h3>
    <form method='POST'>
    <input type="text" name="username" placeholder="Username required">
    <input type="password" name="password" placeholder="Enter password">
    <input type="submit" value="Login">
    </form>
    {% if message %}
        <p>{{ message }}</p>
    {% endif %}

    <h3>Search Users</h3>
    <form method="GET" action="/search">
       <input type="text" name="query" placeholder="Search the user">
       <input type="submit" value="Search">
    </form>

    <h3>Command Execution (Admin Only) </h3>
    <form method="POST" action="/execute">
       <input type="text" name="command" placeholder="Enter command">
       <input type="submit" value="Execute">
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# SQL Injection vulnerability
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Vulnerable direct string concatenation
    c.execute(f"SELECT * FROM users WHERE username LIKE '%{query}%'")
    results = c.fetchall()
    conn.close()

    return f"Results: {results}"

# Command Injection vulnerabilty
@app.route('/execute', methods=['POST'])
def execute_command():
    command = request.form.get('command', '')

    # Vulnerable direct command execution
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return f"Command output: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
    
# XSS vulnerability
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Vulnerable SQL Injection
    c.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    user = c.fetchone()
    conn.close()

    if user:
        # Vulnerable: Reflected XSS
        return render_template_string(HTML_TEMPLATE, message=f"Weclome {username}")
    else:
        return render_template_string(HTML_TEMPLATE, message="Login failed" )
    
if __name__ == '__main__':
    init_db()
    # Debug mode enabled in production poses a significant security risk
    app.run(debug=True, host='0.0.0.0', port=5000)