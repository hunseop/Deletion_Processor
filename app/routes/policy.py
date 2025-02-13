from flask import Blueprint, request, jsonify, send_file, render_template
from app.services.policy_service import PolicyService
import os

bp = Blueprint('policy', __name__, url_prefix='/policy')
policy_service = PolicyService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/collect/<data_type>', methods=['POST'])
def collect_data(data_type):
    try:
        firewall_info = request.get_json()
        result = policy_service.collect_data(data_type, firewall_info)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = policy_service.get_file_path(filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'})
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/test-connection', methods=['POST'])
def test_connection():
    try:
        firewall_info = request.get_json()
        result = policy_service.test_connection(firewall_info)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/save-connection', methods=['POST'])
def save_connection():
    try:
        firewall_info = request.get_json()
        result = policy_service.save_connection(firewall_info)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}) 