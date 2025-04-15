from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, UTC
from functools import wraps
import ephem
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'moonphase.db')

app.config.update(
    SECRET_KEY='dev-key-123',
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime)
    calculations = db.Column(db.Integer, default=0)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
            return f(current_user, *args, **kwargs)
        except:
            return jsonify({'message': 'Invalid token'}), 401
    return decorated

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing username or password'}), 400
            
        username = data['username'].strip()
        password = data['password']
        
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 400
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=data['username'].strip()).first()
        
        if user and check_password_hash(user.password, data['password']):
            user.last_login = datetime.now(UTC)
            db.session.commit()
            
            token = jwt.encode({
                'username': user.username,
                'exp': datetime.now(UTC) + timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'token': token,
                'username': user.username,
                'calculations': user.calculations,
                'last_login': user.last_login.isoformat()
            })
        
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@app.route('/get-moon-phase', methods=['POST'])
@token_required
def get_moon_phase(current_user):
    try:
        date_str = request.json.get('date')
        if not date_str:
            return jsonify({'error': 'Date is required'}), 400

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        moon = ephem.Moon()
        moon.compute(date_obj)
        
        phase_percent = moon.phase
        
        plt.ioff()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_aspect('equal')
        ax.axis('off')
        
        circle = plt.Circle((0.5, 0.5), 0.4, color='white')
        ax.add_patch(circle)
        
        if phase_percent <= 50:
            shadow = plt.Circle((0.5 + 0.4 * (1 - 2 * phase_percent/100), 0.5), 
                              0.4, color='black')
        else:
            shadow = plt.Circle((0.5 - 0.4 * (2 * (phase_percent-50)/100), 0.5), 
                              0.4, color='black')
        ax.add_patch(shadow)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        fig.patch.set_facecolor('black')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='black', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close('all')
        
        moon_image = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        current_user.calculations += 1
        db.session.commit()
        
        return jsonify({
            'phase_name': get_phase_name(phase_percent),
            'illumination': phase_percent,
            'moon_image': moon_image,
            'calculations': current_user.calculations
        })
        
    except Exception as e:
        plt.close('all')
        return jsonify({'error': str(e)}), 500

def get_phase_name(phase_percent):
    if phase_percent < 6.25:
        return "New Moon"
    elif phase_percent < 43.75:
        return "Waxing Crescent"
    elif phase_percent < 56.25:
        return "First Quarter"
    elif phase_percent < 93.75:
        return "Waxing Gibbous"
    elif phase_percent < 96.25:
        return "Full Moon"
    elif phase_percent < 143.75:
        return "Waning Gibbous"
    elif phase_percent < 156.25:
        return "Last Quarter"
    elif phase_percent < 193.75:
        return "Waning Crescent"
    else:
        return "New Moon"

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print(f"Database created at: {db_path}")
        except Exception as e:
            print(f"Database error: {str(e)}")
    app.run(debug=True, host='127.0.0.1', port=5000)