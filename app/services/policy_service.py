import pandas as pd
import re
import os
from datetime import datetime

class PolicyService:
    def __init__(self):
        self.current_phase = 1
        self.collected_data = {
            'policy': None,
            'usage': None,
            'duplicate': None
        }
        self.upload_folder = 'uploads'
        self.ensure_upload_folder()
        
    def ensure_upload_folder(self):
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def parse_policy_file(self, file):
        # TODO: 정책 파일 파싱 로직 구현
        pass
        
    def extract_request_ids(self, file):
        # TODO: 신청번호 추출 로직 구현
        pass
        
    def process_policy(self, file):
        # TODO: 정책 처리 로직 구현
        pass

    def collect_policy_data(self, firewall_info):
        """방화벽 정책 추출"""
        try:
            # 임시 구현: 더미 데이터 반환
            return {
                'success': True,
                'data': {
                    'count': 150,
                    'items': [
                        {'id': 1, 'rule': 'Rule1'},
                        {'id': 2, 'rule': 'Rule2'}
                    ]
                },
                'message': '정책 추출 완료'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'정책 추출 실패: {str(e)}'
            }
    
    def collect_usage_data(self, firewall_info):
        """사용이력 추출"""
        try:
            # 임시 구현: 더미 데이터 반환
            return {
                'success': True,
                'data': {
                    'count': 80,
                    'items': [
                        {'id': 1, 'usage': 'Usage1'},
                        {'id': 2, 'usage': 'Usage2'}
                    ]
                },
                'message': '사용이력 추출 완료'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'사용이력 추출 실패: {str(e)}'
            }
    
    def collect_duplicate_data(self, firewall_info):
        """중복정책 추출"""
        try:
            # 임시 구현: 더미 데이터 반환
            return {
                'success': True,
                'data': {
                    'count': 30,
                    'items': [
                        {'id': 1, 'duplicate': 'Duplicate1'},
                        {'id': 2, 'duplicate': 'Duplicate2'}
                    ]
                },
                'message': '중복정책 추출 완료'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'중복정책 추출 실패: {str(e)}'
            }

    def parse_description(self, file, file_type):
        """Description 필드에서 신청정보 파싱"""
        try:
            df = pd.read_excel(file) if file.filename.endswith('.xlsx') else pd.read_csv(file)
            
            if 'Description' not in df.columns:
                return {
                    'success': False,
                    'message': 'Description 컬럼이 없습니다.'
                }

            # 파싱 결과를 저장할 새 컬럼들
            df['Request_Type'] = None
            df['Request_ID'] = None
            df['Start_Date'] = None
            df['End_Date'] = None
            df['Request_User'] = None

            # Description 파싱
            for idx, row in df.iterrows():
                desc = str(row['Description'])
                parsed = self._parse_description_text(desc)
                
                for key, value in parsed.items():
                    df.at[idx, key] = value

            # 파싱 결과 검증
            validation_result = self._validate_parsing_result(df)
            
            if not validation_result['success']:
                return validation_result

            # 파일 저장
            output_filename = f'parsed_{file_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            df.to_excel(output_filename, index=False)

            return {
                'success': True,
                'message': '파싱 완료',
                'filename': output_filename,
                'preview': df.head().to_dict('records'),
                'stats': {
                    'total': len(df),
                    'parsed': df['Request_ID'].notna().sum(),
                    'failed': df['Request_ID'].isna().sum()
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'파싱 실패: {str(e)}'
            }

    def _parse_description_text(self, text):
        """Description 텍스트에서 정보 추출"""
        result = {
            'Request_Type': None,
            'Request_ID': None,
            'Start_Date': None,
            'End_Date': None,
            'Request_User': None
        }

        # 정규식 패턴
        patterns = {
            'Request_Type': r'([PFSM])\d{8}',  # P, F, S, M으로 시작하는 신청번호
            'Request_ID': r'[PFSM]\d{8}',      # 전체 신청번호
            'Date': r'\d{8}',                  # YYYYMMDD 형식의 날짜
            'Request_User': r'신청자[:\s]+(\w+)'  # 신청자 정보
        }

        try:
            # Request Type & ID
            if req_id_match := re.search(patterns['Request_ID'], text):
                result['Request_ID'] = req_id_match.group()
                result['Request_Type'] = req_id_match.group()[0]

            # Dates
            dates = re.findall(patterns['Date'], text)
            if len(dates) >= 2:
                result['Start_Date'] = dates[0]
                result['End_Date'] = dates[1]

            # Request User
            if user_match := re.search(patterns['Request_User'], text):
                result['Request_User'] = user_match.group(1)

        except Exception as e:
            print(f"파싱 오류: {str(e)}")

        return result

    def _validate_parsing_result(self, df):
        """파싱 결과 검증"""
        errors = []

        # 필수 값 검증
        required_fields = ['Request_ID', 'Start_Date', 'End_Date']
        for field in required_fields:
            missing = df[df[field].isna()].index.tolist()
            if missing:
                errors.append(f'{field} 누락된 행: {missing}')

        # 날짜 형식 검증
        date_fields = ['Start_Date', 'End_Date']
        for field in date_fields:
            invalid_dates = df[~df[field].str.match(r'\d{8}', na=True)].index.tolist()
            if invalid_dates:
                errors.append(f'{field} 날짜 형식 오류 행: {invalid_dates}')

        if errors:
            return {
                'success': False,
                'message': '검증 실패',
                'errors': errors
            }

        return {'success': True}

    def validate_files(self, request_file, mis_file):
        """파일 검증"""
        try:
            # 임시 구현: 파일 존재 여부만 확인
            if not request_file or not mis_file:
                return {
                    'success': False,
                    'message': '필요한 파일이 누락되었습니다.'
                }

            # 파일 저장
            request_path = self.save_file(request_file, 'request')
            mis_path = self.save_file(mis_file, 'mis')

            return {
                'success': True,
                'message': '파일 검증 완료',
                'request_file_status': '정상',
                'mis_file_status': '정상',
                'warnings': ['일부 데이터 형식 확인 필요']
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    def integrate_data(self, integration_type, vendor):
        """데이터 통합"""
        try:
            # 임시 구현: 통합 프로세스 시뮬레이션
            return {
                'success': True,
                'message': f'{integration_type} 통합 완료',
                'data': {
                    'processed_count': 100,
                    'success_count': 95,
                    'failed_count': 5,
                    'preview': [
                        {'id': 1, 'status': '성공', 'details': '정상 처리'},
                        {'id': 2, 'status': '성공', 'details': '정상 처리'}
                    ]
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    def generate_result(self, result_type, vendor):
        """결과 파일 생성"""
        try:
            # 임시 구현: 결과 파일 생성 시뮬레이션
            filename = f'{result_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            filepath = os.path.join(self.upload_folder, filename)
            
            # 더미 데이터로 엑셀 파일 생성
            df = pd.DataFrame({
                'Column1': ['Data1', 'Data2'],
                'Column2': ['Value1', 'Value2']
            })
            df.to_excel(filepath, index=False)

            return {
                'success': True,
                'message': '결과 파일 생성 완료',
                'filename': filename,
                'type': result_type
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    def save_file(self, file, prefix):
        """파일 저장"""
        filename = f'{prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file.filename}'
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath

    def get_file_path(self, filename):
        """파일 경로 조회"""
        return os.path.join(self.upload_folder, filename) 