from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
import sqlite3
import os
import json

app = Flask(__name__)
app.secret_key = 'smartmeter2024secretkey'

# Fixed credentials
ADMIN_USERNAME = "smartmeter"
ADMIN_PASSWORD = "meter2024"

# Database initialization
def init_db():
    conn = sqlite3.connect('meters.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (meter_id TEXT, 
                  data TEXT,
                  timestamp TEXT,
                  PRIMARY KEY (meter_id))''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('meters.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database on startup
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    db = get_db()
    cursor = db.execute('SELECT * FROM readings')
    readings = {}
    for row in cursor:
        readings[row['meter_id']] = json.loads(row['data'])
    db.close()
    return render_template('index.html', readings=readings)

@app.route('/update', methods=['GET'])
@login_required
def update():
    meter_id = request.args.get('meter')
    kwh = request.args.get('kWh')
    power = request.args.get('P')
    
    if all([meter_id, kwh, power]):
        reading_data = {
            'kwh': float(kwh),
            'power': float(power),
            'timestamp': 'Last updated: ' + datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        }
        
        db = get_db()
        db.execute('INSERT OR REPLACE INTO readings (meter_id, data, timestamp) VALUES (?, ?, ?)',
                  [meter_id, json.dumps(reading_data), datetime.now().isoformat()])
        db.commit()
        db.close()
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route('/get_readings')
@login_required
def get_readings():
    db = get_db()
    cursor = db.execute('SELECT * FROM readings')
    readings = {}
    for row in cursor:
        readings[row['meter_id']] = json.loads(row['data'])
    db.close()
    return jsonify(readings)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
