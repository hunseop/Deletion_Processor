import json

class PolicyService:
    def __init__(self):
        self.config_file = 'firewall_config.json'

    def save_connection(self, firewall_info):
        """방화벽 연결 정보 저장"""
        try:
            required_fields = ['vendor', 'primary_ip', 'username', 'password']
            if not all(field in firewall_info for field in required_fields):
                return {'success': False, 'message': '필수 정보가 누락되었습니다.'}
            
            with open(self.config_file, 'w') as f:
                json.dump(firewall_info, f, indent=2)
                
            return {
                'success': True, 
                'message': '설정이 저장되었습니다.',
                'data': {
                    'vendor': firewall_info['vendor'],
                    'primary_ip': firewall_info['primary_ip']
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'저장 실패: {str(e)}'}

    def collect_firewall_data(self, data_type):
        """Phase 2: 방화벽 데이터 수집"""
        try:
            # TODO: 실제 데이터 수집 로직 구현
            data_type_names = {
                'policy': '방화벽 정책',
                'usage': '사용이력',
                'duplicate': '중복 정책'
            }
            return {
                'success': True,
                'message': f'{data_type_names.get(data_type, data_type)} 수집 완료'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'데이터 수집 실패: {str(e)}'
            } 