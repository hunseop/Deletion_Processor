from flask import Blueprint, render_template, request, jsonify, send_file
from app.services.policy_service import PolicyService
import os

bp = Blueprint('policy', __name__, url_prefix='/policy')
policy_service = PolicyService()

@bp.route('/')
def index():
    return render_template('policy/index.html')

@bp.route('/parse/<file_type>', methods=['POST'])
def parse_policy(file_type):
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'message': '파일이 없습니다.'})
            
        result = policy_service.parse_description(file, file_type)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@bp.route('/collect/<data_type>', methods=['POST'])
def collect_data(data_type):
    try:
        firewall_info = request.get_json()
        
        if data_type == 'policy':
            result = policy_service.collect_policy_data(firewall_info)
        elif data_type == 'usage':
            result = policy_service.collect_usage_data(firewall_info)
        elif data_type == 'duplicate':
            result = policy_service.collect_duplicate_data(firewall_info)
        else:
            return jsonify({
                'success': False,
                'message': '잘못된 데이터 타입'
            })
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@bp.route('/validate-files', methods=['POST'])
def validate_files():
    try:
        request_file = request.files.get('request_file')
        mis_file = request.files.get('mis_file')
        
        result = policy_service.validate_files(request_file, mis_file)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@bp.route('/integrate', methods=['POST'])
def integrate_data():
    try:
        data = request.get_json()
        result = policy_service.integrate_data(
            integration_type=data.get('type'),
            vendor=data.get('vendor')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@bp.route('/generate-result', methods=['POST'])
def generate_result():
    try:
        data = request.get_json()
        result = policy_service.generate_result(
            result_type=data.get('type'),
            vendor=data.get('vendor')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@bp.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = policy_service.get_file_path(filename)
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': '파일을 찾을 수 없습니다.'
            })
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }) 