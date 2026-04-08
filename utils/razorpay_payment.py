"""
Razorpay Payment Integration for Agent X
Real-time payment processing for ticket bookings
"""

import razorpay
import os
from datetime import datetime
import hashlib
import hmac

# Razorpay credentials (use environment variables in production)
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')

# Initialize Razorpay client
client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def create_order(amount: float, currency: str = 'INR', receipt: str = None, notes: dict = None) -> dict:
    """
    Create a Razorpay order for payment
    
    Args:
        amount: Amount in rupees (will be converted to paise)
        currency: Currency code (default INR)
        receipt: Optional receipt ID
        notes: Optional notes dict
        
    Returns:
        Order details from Razorpay
    """
    if not client:
        return {'error': 'Razorpay not configured. Please add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to environment.'}
    
    try:
        # Convert to paise (Razorpay expects amount in smallest currency unit)
        amount_paise = int(amount * 100)
        
        order_data = {
            'amount': amount_paise,
            'currency': currency,
            'receipt': receipt or f'order_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'notes': notes or {}
        }
        
        order = client.order.create(data=order_data)
        
        return {
            'success': True,
            'order_id': order['id'],
            'amount': amount,
            'amount_paise': amount_paise,
            'currency': currency,
            'key_id': RAZORPAY_KEY_ID,  # Frontend needs this to open checkout
            'receipt': order_data['receipt']
        }
        
    except Exception as e:
        return {'error': str(e), 'success': False}


def verify_payment(order_id: str, payment_id: str, signature: str) -> dict:
    """
    Verify payment signature from Razorpay
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID  
        signature: Razorpay signature
        
    Returns:
        Verification result
    """
    if not client:
        return {'error': 'Razorpay not configured', 'verified': False}
    
    try:
        # Create signature verification string
        message = f"{order_id}|{payment_id}"
        
        # Generate expected signature
        expected_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        if hmac.compare_digest(expected_signature, signature):
            # Fetch payment details
            payment = client.payment.fetch(payment_id)
            
            return {
                'verified': True,
                'payment_id': payment_id,
                'order_id': order_id,
                'amount': payment['amount'] / 100,  # Convert paise to rupees
                'currency': payment['currency'],
                'status': payment['status'],
                'method': payment['method'],
                'email': payment.get('email'),
                'contact': payment.get('contact'),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {'verified': False, 'error': 'Invalid signature'}
            
    except Exception as e:
        return {'verified': False, 'error': str(e)}


def get_payment_details(payment_id: str) -> dict:
    """Get details of a specific payment"""
    if not client:
        return {'error': 'Razorpay not configured'}
    
    try:
        payment = client.payment.fetch(payment_id)
        return {
            'success': True,
            'payment_id': payment['id'],
            'amount': payment['amount'] / 100,
            'currency': payment['currency'],
            'status': payment['status'],
            'method': payment['method'],
            'email': payment.get('email'),
            'contact': payment.get('contact')
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def refund_payment(payment_id: str, amount: float = None) -> dict:
    """
    Initiate refund for a payment
    
    Args:
        payment_id: Razorpay payment ID
        amount: Amount to refund (None for full refund)
    """
    if not client:
        return {'error': 'Razorpay not configured'}
    
    try:
        refund_data = {'payment_id': payment_id}
        if amount:
            refund_data['amount'] = int(amount * 100)
        
        refund = client.payment.refund(payment_id, refund_data)
        return {
            'success': True,
            'refund_id': refund['id'],
            'amount': refund['amount'] / 100,
            'status': refund['status']
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def is_configured() -> bool:
    """Check if Razorpay is properly configured"""
    return bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET)
