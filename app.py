from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'smartmeter2024secretkey'  # Fixed secret key

# Fixed credentials
ADMIN_USERNAME = "smartmeter"
ADMIN_PASSWORD = "meter2024"

latest_readings = {}

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
    return render_template('index.html', readings=latest_readings)

@app.route('/update', methods=['GET'])
@login_required
def update():
    meter_id = request.args.get('meter')
    kwh = request.args.get('kWh')
    power = request.args.get('P')
    
    if all([meter_id, kwh, power]):
        latest_readings[meter_id] = {
            'kwh': float(kwh),
            'power': float(power),
            'timestamp': 'Last updated: ' + datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        }
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

@app.route('/get_readings')
@login_required
def get_readings():
    return jsonify(latest_readings)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
