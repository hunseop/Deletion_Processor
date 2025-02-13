import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

class PolicyService:
    def __init__(self):
        self.config_file = 'firewall_config.json'
        # 프로젝트 루트 디렉토리 기준으로 downloads 폴더 생성
        self.download_dir = Path('downloads')
        self.download_dir.mkdir(exist_ok=True)

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
            # 시작 시간 기록
            start_time = time.time()
            
            # 3초 지연
            time.sleep(3)
            
            # 더미 데이터 생성
            dummy_data = {
                'policy': {
                    'total_count': 1250,
                    'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'sample': ['정책1', '정책2', '정책3']
                },
                'usage': {
                    'total_count': 850,
                    'period': '최근 30일',
                    'sample': ['사용이력1', '사용이력2', '사용이력3']
                },
                'duplicate': {
                    'total_count': 45,
                    'criteria': '규칙 일치도 80% 이상',
                    'sample': ['중복1', '중복2', '중복3']
                }
            }

            # 엑셀 파일 생성
            filename = self.create_excel(data_type, dummy_data[data_type])
            elapsed_time = round(time.time() - start_time, 1)
            
            data_type_names = {
                'policy': '방화벽 정책',
                'usage': '사용이력',
                'duplicate': '중복 정책'
            }

            return {
                'success': True,
                'message': f'{data_type_names.get(data_type, data_type)} 수집 완료',
                'data': dummy_data.get(data_type, {}),
                'elapsed_time': elapsed_time,
                'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filename': filename
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'데이터 수집 실패: {str(e)}'
            }

    def create_excel(self, data_type, data):
        """엑셀 파일 생성"""
        filename = f"{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = self.download_dir / filename

        # 데이터 타입별 엑셀 생성 로직
        if data_type == 'policy':
            df = pd.DataFrame({
                '정책ID': range(1, 11),
                '정책명': [f'정책{i}' for i in range(1, 11)],
                '출발지': ['192.168.1.1' for _ in range(10)],
                '목적지': ['10.0.0.1' for _ in range(10)],
                '서비스': ['HTTP' for _ in range(10)],
                '작성일자': [datetime.now().strftime('%Y-%m-%d') for _ in range(10)]
            })
        elif data_type == 'usage':
            df = pd.DataFrame({
                '정책ID': range(1, 11),
                '히트수': [i * 100 for i in range(1, 11)],
                '마지막사용일': [datetime.now().strftime('%Y-%m-%d') for _ in range(10)]
            })
        else:  # duplicate
            df = pd.DataFrame({
                '정책ID': range(1, 11),
                '중복정책ID': range(101, 111),
                '일치도': [f'{i}%' for i in range(80, 90)],
                '비고': ['검토필요' for _ in range(10)]
            })

        df.to_excel(filepath, index=False)
        return filename

    def get_download_path(self, filename):
        """다운로드 파일 경로 반환"""
        # 프로젝트 루트 디렉토리 기준으로 경로 반환
        root_dir = Path(os.getcwd())
        return root_dir / self.download_dir / filename 