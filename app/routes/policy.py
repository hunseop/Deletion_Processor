from flask import Blueprint, request, jsonify, send_file, render_template
from app.services.policy_service import PolicyService
import os

bp = Blueprint('policy', __name__, url_prefix='/policy')
policy_service = PolicyService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/save-connection', methods=['POST'])
def save_connection():
    try:
        firewall_info = request.get_json()
        result = policy_service.save_connection(firewall_info)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/collect-firewall-data/<data_type>', methods=['POST'])
def collect_firewall_data(data_type):
    try:
        result = policy_service.collect_firewall_data(data_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}) 