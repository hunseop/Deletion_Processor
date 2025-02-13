from flask import Blueprint, request, jsonify, send_file, render_template
from app.services.policy_service import PolicyService
import os
from werkzeug.utils import secure_filename

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

@bp.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = policy_service.get_download_path(filename)
        if not file_path.exists():
            return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'})
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/parse-description/<file_type>', methods=['POST'])
def parse_description(file_type):
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '파일이 없습니다.'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '선택된 파일이 없습니다.'})
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'success': False, 'message': 'XLSX 파일만 허용됩니다.'})
        
        result = policy_service.parse_description(file_type, file)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/extract-request-id', methods=['POST'])
def extract_request_id():
    try:
        result = policy_service.extract_request_id()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}) 