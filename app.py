"""
Flask API Backend for Agent X
Provides REST API endpoints for the React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import os
import secrets
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Import existing modules
from database.db import (
    verify_user, create_user, get_user_by_username,
    get_user_settings, update_user_settings, init_db
)
from agents.orchestrator import AgentOrchestrator

# ============== App Configuration ==============
app = Flask(__name__)

# Allow Vercel deployment domains + local dev
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3002",
]

# Add Vercel domain if set
VERCEL_URL = os.environ.get('VERCEL_URL')
if VERCEL_URL:
    ALLOWED_ORIGINS.append(f"https://{VERCEL_URL}")

# Add custom frontend URL if set
FRONTEND_URL = os.environ.get('FRONTEND_URL')
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'agentx-secret-key-2026'),
    JWT_EXPIRY_DAYS=7
)

GOOGLE_CLIENT_ID = os.environ.get(
    'GOOGLE_CLIENT_ID', 
    '734804398402-qjcvn3c4dpgtdgifs7r4g8jthqra1oqf.apps.googleusercontent.com'
)

# Available agents configuration
AGENTS_CONFIG = [
    {'id': 'email', 'name': 'Email Agent', 'status': 'active'},
    {'id': 'report', 'name': 'Report Generator', 'status': 'active'},
    {'id': 'flight', 'name': 'Flight Search', 'status': 'active'},
    {'id': 'bus', 'name': 'Bus Routes', 'status': 'active'},
    {'id': 'train', 'name': 'Train Tickets', 'status': 'active'},
    {'id': 'file_organizer', 'name': 'File Organizer', 'status': 'active'},
    {'id': 'browser', 'name': 'Browser Agent', 'status': 'active'},
    {'id': 'weather', 'name': 'Weather', 'status': 'active'},
    {'id': 'news', 'name': 'News Agent', 'status': 'active'},
    {'id': 'reminder', 'name': 'Reminders', 'status': 'active'},
    {'id': 'emergency', 'name': 'Emergency', 'status': 'active'},
]

# Initialize services
init_db()
orchestrator = AgentOrchestrator()


# ============== Helper Functions ==============
def generate_token(user: dict) -> str:
    """Generate JWT token for authenticated user"""
    return jwt.encode(
        {
            'username': user['username'],
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(days=app.config['JWT_EXPIRY_DAYS'])
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )


def format_user_response(user: dict, picture: str = None) -> dict:
    """Format user data for API response"""
    return {
        'id': user['id'],
        'username': user['username'],
        'email': user.get('email'),
        'full_name': user.get('full_name'),
        **({"picture": picture} if picture else {})
    }


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token is missing or invalid format'}), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = get_user_by_username(data['username'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


# ============== Auth Routes ==============

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with username and password"""
    data = request.get_json() or {}
    username, password = data.get('username'), data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    
    user = verify_user(username, password)
    if not user:
        return jsonify({'message': 'Invalid username or password'}), 401
    
    return jsonify({
        'token': generate_token(user),
        'user': format_user_response(user)
    })


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Create new user account"""
    data = request.get_json() or {}
    username, password = data.get('username'), data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
    if len(username) < 3:
        return jsonify({'message': 'Username must be at least 3 characters'}), 400
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    if get_user_by_username(username):
        return jsonify({'message': 'Username already exists'}), 400
    
    success = create_user(username, password, data.get('email'), data.get('full_name'))
    if success:
        return jsonify({'message': 'Account created successfully'}), 201
    return jsonify({'message': 'Failed to create account'}), 500


@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Authenticate with Google OAuth"""
    data = request.get_json() or {}
    credential = data.get('credential')
    
    if not credential:
        return jsonify({'message': 'Google credential required'}), 400
    
    try:
        idinfo = id_token.verify_oauth2_token(
            credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        
        email = idinfo.get('email', '')
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')
        username = email.split('@')[0] if email else f"google_{idinfo['sub']}"
        
        user = get_user_by_username(username)
        if not user:
            if not create_user(username, secrets.token_urlsafe(16), email, name):
                return jsonify({'message': 'Failed to create user account'}), 500
            user = get_user_by_username(username)
        
        return jsonify({
            'token': generate_token(user),
            'user': format_user_response(user, picture)
        })
        
    except ValueError as e:
        return jsonify({'message': f'Invalid Google token: {str(e)}'}), 401


@app.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if token is valid"""
    return jsonify({'valid': True, 'user': format_user_response(current_user)})


# ============== Agent Routes ==============

@app.route('/api/agents/execute', methods=['POST'])
@token_required
def execute_task(current_user):
    """Execute a task using the appropriate agent"""
    data = request.get_json() or {}
    task = data.get('task', '').strip()
    agent_type = data.get('agent_type', 'auto')
    
    if not task:
        return jsonify({'message': 'Task is required'}), 400
    
    try:
        if agent_type in ('auto', '', None):
            result = orchestrator.process_request(task)
        elif agent_type in orchestrator.agents:
            result = orchestrator.agents[agent_type].execute(task)
        else:
            return jsonify({'success': False, 'message': f'Unknown agent: {agent_type}'}), 400
        
        return jsonify({
            'success': True,
            'result': {
                'success': result.success,
                'message': result.message,
                'data': getattr(result, 'data', None),
                'error': getattr(result, 'error', None)
            },
            'agent_used': agent_type,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/agents/status', methods=['GET'])
@token_required
def get_agent_status(current_user):
    """Get available agents and their status"""
    return jsonify({'agents': AGENTS_CONFIG})


@app.route('/api/agents/history', methods=['GET'])
@token_required
def get_history(current_user):
    """Get task execution history"""
    return jsonify({'history': []})  # TODO: Implement history storage


# ============== Settings Routes ==============

@app.route('/api/settings', methods=['GET'])
@token_required
def get_settings(current_user):
    """Get user settings"""
    return jsonify({'settings': get_user_settings(current_user['id']) or {}})


@app.route('/api/settings', methods=['PUT'])
@token_required
def update_settings_route(current_user):
    """Update user settings"""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Settings data required'}), 400
    
    if update_user_settings(current_user['id'], data):
        return jsonify({'message': 'Settings updated successfully'})
    return jsonify({'message': 'Failed to update settings'}), 500


@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile"""
    return jsonify({'message': 'Profile updated successfully'})  # TODO: Implement


# ============== Payment Routes (Razorpay) ==============

@app.route('/api/payment/config', methods=['GET'])
def get_payment_config():
    """Get Razorpay configuration (public key only)"""
    from utils.razorpay_payment import is_configured, RAZORPAY_KEY_ID
    
    return jsonify({
        'configured': is_configured(),
        'key_id': RAZORPAY_KEY_ID if is_configured() else None,
        'currency': 'INR'
    })


@app.route('/api/payment/create-order', methods=['POST'])
@token_required
def create_payment_order(current_user):
    """Create a Razorpay order for ticket booking"""
    from utils.razorpay_payment import create_order, is_configured
    
    if not is_configured():
        return jsonify({
            'success': False,
            'message': 'Payment gateway not configured. Please add Razorpay credentials.'
        }), 503
    
    data = request.get_json() or {}
    amount = data.get('amount')
    booking_type = data.get('booking_type', 'ticket')  # flight, bus, train
    booking_details = data.get('booking_details', {})
    
    if not amount or amount <= 0:
        return jsonify({'success': False, 'message': 'Valid amount required'}), 400
    
    # Create order with booking details in notes
    result = create_order(
        amount=float(amount),
        notes={
            'booking_type': booking_type,
            'user_id': str(current_user['id']),
            'username': current_user['username'],
            **booking_details
        }
    )
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500


@app.route('/api/payment/verify', methods=['POST'])
@token_required
def verify_payment_route(current_user):
    """Verify Razorpay payment after completion"""
    from utils.razorpay_payment import verify_payment
    
    data = request.get_json() or {}
    order_id = data.get('razorpay_order_id')
    payment_id = data.get('razorpay_payment_id')
    signature = data.get('razorpay_signature')
    
    if not all([order_id, payment_id, signature]):
        return jsonify({
            'success': False,
            'message': 'Missing payment verification details'
        }), 400
    
    result = verify_payment(order_id, payment_id, signature)
    
    if result.get('verified'):
        # TODO: Save booking to database, generate ticket, etc.
        return jsonify({
            'success': True,
            'verified': True,
            'payment_id': payment_id,
            'message': 'Payment successful! Your ticket has been booked.',
            **result
        })
    else:
        return jsonify({
            'success': False,
            'verified': False,
            'message': result.get('error', 'Payment verification failed')
        }), 400


# ============== Health Check ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


# ============== Run Server ==============
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Agent X API Server")
    print("  http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
