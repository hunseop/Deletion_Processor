from flask import Blueprint, request, jsonify
from app.services.firewall_service import FirewallService

bp = Blueprint('firewall', __name__, url_prefix='/firewall')
firewall_service = FirewallService()

@bp.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    
    success, message = firewall_service.create_connection(
        vendor=data.get('vendor'),
        primary_ip=data.get('primary_ip'),
        secondary_ip=data.get('secondary_ip'),
        username=data.get('username'),
        password=data.get('password')
    )
    
    return jsonify({
        'success': success,
        'message': message
    }) 