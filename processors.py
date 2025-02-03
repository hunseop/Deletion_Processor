import pandas as pd
import logging
from datetime import datetime, timedelta
import re
from config import COLUMNS, COLUMNS_NO_HISTORY, DATE_COLUMNS, TRANSLATED_COLUMNS, EXCEPT_LIST
from utils import (
    select_xlsx_files, update_version, save_to_excel, 
    remove_extension, convert_to_date, find_auto_extension_id
)

class PolicyProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pd.options.mode.chained_assignment = None

    def parse_request_type(self, file_path):
        """Description에서 신청번호 파싱"""
        def parse_request_info(rulename, description):
            data_dict = {
                "Request Type": "Unknown",
                "Request ID": None,
                "Ruleset ID": None,
                "MIS ID": None,
                "Request User": None,
                "Start Date": convert_to_date('19000101'),
                "End Date": convert_to_date('19000101'),
            }

            if pd.isnull(description):
                return data_dict
            
            ### 마스킹 처리 시작 아래 부분의 정규 표현식은 임의로 제거함
            pattern_3 = re.compile("MASKED")
            pattern_1_rulename = re.compile("MASKED")
            pattern_1_user = r'MASKED'
            rulename_1_rulename = r'MASKED'
            rulename_1_date = r'MASKED'
            ### 마스킹 처리 끝

            match_3 = pattern_3.match(description)
            name_match = pattern_1_rulename.match(str(rulename))
            user_match = re.search(pattern_1_user, description)
            desc_match = re.search(rulename_1_rulename, description)
            date_match = re.search(rulename_1_date, description)

            if match_3:
                data_dict.update({
                    "Request Type": None,
                    "Request ID": match_3.group(5),
                    "Ruleset ID": match_3.group(1),
                    "MIS ID": match_3.group(6) if match_3.group(6) else None,
                    "Request User": match_3.group(4),
                    "Start Date": convert_to_date(match_3.group(2)),
                    "End Date": convert_to_date(match_3.group(3)),
                })
                
                type_code = data_dict["Request ID"][:1]
                data_dict["Request Type"] = {
                    "P": "GROUP",
                    "F": "NORMAL",
                    "S": "SERVER",
                    "M": "PAM"
                }.get(type_code, "Unknown")
            
            if name_match:
                data_dict.update({
                    'Request Type': "OLD",
                    'Request ID': name_match.group(1),
                    'Request User': user_match.group(1).replace("*ACL*", "") if user_match else None
                })
                if date_match:
                    dates = date_match.group().split("~")
                    data_dict.update({
                        'Start Date': convert_to_date(dates[0]),
                        'End Date': convert_to_date(dates[1])
                    })
            
            if desc_match:
                date = description.split(';')[0]
                start_date = date.split('~')[0].replace('[', '').replace('-', '')
                end_date = date.split('~')[1].replace(']', '').replace('-', '')

                data_dict.update({
                    "Request Type": "OLD",
                    "Request ID": desc_match.group(1).split('-')[1],
                    "Ruleset ID": None,
                    "MIS ID": None,
                    "Request User": user_match.group(1).replace("*ACL*", "") if user_match else None,
                    "Start Date": convert_to_date(start_date),
                    "End Date": convert_to_date(end_date),
                })
            
            return data_dict

        try:
            df = pd.read_excel(file_path)
            
            for index, row in df.iterrows():
                result = parse_request_info(row['Rule Name'], row['Description'])
                for key, value in result.items():
                    df.at[index, key] = value
            
            df.to_excel(update_version(file_path), index=False)
            self.logger.info("Successfully parsed request types")
        except Exception as e:
            self.logger.error(f"Error in parse_request_type: {str(e)}")

    def extract_request_id(self, file_path):
        """정책파일에서 신청번호 추출"""
        try:
            df = pd.read_excel(file_path)
            unique_types = df[df['Request Type'] != 'Unknown']['Request Type'].unique()
            selected_types = unique_types[:5]
            selected_data = df[df['Request Type'].isin(selected_types)]

            output_file = f"request_id_{file_path}"
            with pd.ExcelWriter(output_file) as writer:
                for request_type, group in selected_data.groupby('Request Type'):
                    group[['Request ID']].drop_duplicates().to_excel(
                        writer, sheet_name=request_type, index=False
                    )
            self.logger.info("Successfully extracted request IDs")
        except Exception as e:
            self.logger.error(f"Error in extract_request_id: {str(e)}")

    def add_request_info(self, file_path, info_file_path):
        """정책파일에 신청정보 추가"""
        def read_and_process_excel(file):
            df = pd.read_excel(file)
            df.replace({'nan': None}, inplace=True)
            return df.astype(str)
        
        def match_and_update_df(rule_df, info_df):
            total = len(rule_df)
            for idx, row in rule_df.iterrows():
                print(f"\rProgress: {idx + 1}/{total}", end='', flush=True)
                
                if row['Request Type'] == 'GROUP':
                    matched_row = info_df[
                        ((info_df['REQUEST_ID'] == row['Request ID']) & (info_df['MIS_ID'] == row['MIS ID'])) |
                        ((info_df['REQUEST_ID'] == row['Request ID']) & (info_df['REQUEST_END_DATE'] == row['End Date']) & (info_df['WRITE_PERSON_ID'] == row['Request User'])) |
                        ((info_df['REQUEST_ID'] == row['Request ID']) & (info_df['REQUEST_END_DATE'] == row['End Date']) & (info_df['REQUESTER_ID'] == row['Request User']))
                    ]
                else:
                    matched_row = info_df[info_df['REQUEST_ID'] == row['Request ID']]
                
                if not matched_row.empty:
                    for col in matched_row.columns:
                        if col in ['REQUEST_START_DATE', 'REQUEST_END_DATE', 'Start Date', 'End Date']:
                            rule_df.at[idx, col] = pd.to_datetime(matched_row[col].values[0], errors='coerce')
                        else:
                            rule_df.at[idx, col] = matched_row[col].values[0]
                elif row['Request Type'] != 'nan' and row['Request Type'] != 'Unknown':
                    rule_df.at[idx, 'REQUEST_ID'] = row['Request ID']
                    rule_df.at[idx, 'REQUEST_START_DATE'] = row['Start Date']
                    rule_df.at[idx, 'REQUEST_END_DATE'] = row['End Date']
                    rule_df.at[idx, 'REQUESTER_ID'] = row['Request User']
                    rule_df.at[idx, 'REQUESTER_EMAIL'] = row['Request User'] + '@gmail.com'

        try:
            rule_df = read_and_process_excel(file_path)
            info_df = read_and_process_excel(info_file_path)
            info_df = info_df.sort_values(by='REQUEST_END_DATE', ascending=False)
            
            auto_extension_id = find_auto_extension_id()
            match_and_update_df(rule_df, info_df)
            rule_df.replace({'nan': None}, inplace=True)
            rule_df.loc[rule_df['REQUEST_ID'].isin(auto_extension_id), 'REQUEST_STATUS'] = '99'
            
            rule_df.to_excel(update_version(file_path), index=False)
            self.logger.info("Successfully added request info")
            return True
        except Exception as e:
            self.logger.error(f"Error in add_request_info: {str(e)}")
            return False

    def process_exceptions(self, file_path, vendor='paloalto'):
        """정책 예외처리 (팔로알토/시큐아이)"""
        try:
            df = pd.read_excel(file_path)
            current_date = datetime.now()
            three_months_ago = current_date - timedelta(days=90)

            # 예외 컬럼 초기화
            df["예외"] = ''
            df['REQUEST_ID'] = df['REQUEST_ID'].fillna('')

            # 1. except list와 request id 일치 시 예외 신청정책으로 표시
            for id in EXCEPT_LIST:
                df.loc[df['REQUEST_ID'].str.startswith(id, na=False), '예외'] = '예외신청정책'
            
            # 2. 자동연장정책
            df.loc[df['REQUEST_STATUS'] == 99, '예외'] = '자동연장정책'

            if vendor == 'paloalto':
                # 3. 신규정책 (3개월 이내)
                df['날짜'] = df['Rule Name'].str.extract(r'(\d{8})', expand=False)
                df['날짜'] = pd.to_datetime(df['날짜'], format='%Y%m%d', errors='coerce')
                df.loc[(df['날짜'] >= three_months_ago) & (df['날짜'] <= current_date), '예외'] = '신규정책'

                # 4. 인프라정책
                deny_std_rule_index = df[df['Rule Name'] == 'Deny_Std_Rule'].index[0]
                df.loc[df.index < deny_std_rule_index, '예외'] = '인프라정책'

                # 5. test_group_정책
                df.loc[df['Rule Name'].str.startswith(('sample_', 'test_')), '예외'] = 'test_group_정책'

            else:  # secui
                # 3. 인프라정책
                deny_std_rule_index = df[df['Description'].str.contains('Deny_Std_Rule') == True].index[0]
                df.loc[df.index < deny_std_rule_index, '예외'] = '인프라정책'

                # 4. 신규정책
                df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
                df.loc[(df['Start Date'] >= three_months_ago) & (df['Start Date'] <= current_date), '예외'] = '신규정책'

            # 공통 예외처리
            # 6. 비활성화정책
            df.loc[df['Enable'] == 'N', '예외'] = '비활성화정책'

            # 7. 기준정책
            if vendor == 'paloalto':
                df.loc[(df['Rule Name'].str.endswith('_Rule')) & (df['Enable'] == 'N'), '예외'] = '기준정책'
            else:
                df.loc[(df['Description'].str.contains('기준룰')) & (df['Enable'] == 'N'), '예외'] = '기준정책'

            # 8. 차단정책
            df.loc[df['Action'] == 'deny', '예외'] = '차단정책'

            df['예외'].fillna('', inplace=True)

            # 컬럼 재정렬
            cols = list(df.columns)
            cols = ['예외'] + [col for col in cols if col != '예외']
            df = df[cols]

            # 만료여부 체크
            def check_date(row):
                try:
                    end_date = pd.to_datetime(row['REQUEST_END_DATE'])
                    return '미만료' if end_date > current_date else '만료'
                except:
                    return '만료'
            
            df['만료여부'] = df.apply(check_date, axis=1)

            if vendor == 'paloalto':
                df.drop(columns=['날짜'], inplace=True)

            df.rename(columns={'Request Type': '신청이력'}, inplace=True)
            df.drop(columns=['Request ID', 'Ruleset ID', 'MIS ID', 'Request User', 'Start Date', 'End Date'], inplace=True)

            # 컬럼 순서 조정
            cols = list(df.columns)
            cols.insert(cols.index('예외') + 1, cols.pop(cols.index('만료여부')))
            df = df[cols]
            cols.insert(cols.index('예외') + 1, cols.pop(cols.index('신청이력')))
            df = df[cols]
            cols.insert(cols.index('만료여부') + 1, '미사용여부')
            df = df.reindex(columns=cols)
            df['미사용여부'] = ''

            df.to_excel(update_version(file_path, True), index=False, engine='openpyxl')
            self.logger.info(f"Successfully processed {vendor} exceptions")

        except Exception as e:
            self.logger.error(f"Error in process_exceptions: {str(e)}") 

    def organize_redundant_file(self, file_path):
        """중복정책 공지/삭제 분류"""
        try:
            expected_columns = ['No', 'Type', 'Seq', 'Rule Name', 'Enable', 'Action', 'Source', 'User', 'Destination', 'Service', 'Application', 'Security Profile', 'Description', 'Request Type', 'Request ID', 'Ruleset ID', 'MIS ID', 'Request User', 'Start Date', 'End Date']
            expected_columns_2 = ['No', 'Type', 'Vsys', 'Seq', 'Rule Name', 'Enable', 'Action', 'Source', 'User', 'Destination', 'Service', 'Application', 'Security Profile', 'Description', 'Request Type', 'Request ID', 'Ruleset ID', 'MIS ID', 'Request User', 'Start Date', 'End Date']

            print('중복정책 파일을 선택')
            selected_file = select_xlsx_files()
            if not selected_file:
                return

            df = pd.read_excel(selected_file)
            current_columns = df.columns.tolist()

            if current_columns != expected_columns and current_columns != expected_columns_2:
                self.logger.warning('컬럼명이 일치하지 않습니다')
                return  # 컬럼 불일치시 처리 중단
            
            # 자동연장 ID 가져오기
            auto_extension_id = find_auto_extension_id()
            if auto_extension_id is None:
                self.logger.error("자동연장 ID를 가져오는데 실패했습니다")
                return

            # 자동연장 여부 체크
            df['자동연장'] = df['Request ID'].isin(auto_extension_id)

            # 늦은 종료일 체크
            df['늦은종료일'] = df.groupby('No')['End Date'].transform(
                lambda x: (x == x.max()) & (~x.duplicated(keep='first'))
            )

            # 신청자 검증
            df['신청자검증'] = df.groupby('No')['Request User'].transform(lambda x: x.nunique() == 1)

            # Upper 타입의 늦은 종료일이 True인 규칙 찾기
            target_rule_true = df[
                (df['Type'] == 'Upper') & 
                (df['늦은종료일'] == True)
            ]['No'].unique()

            # 날짜 검증 초기화 및 설정
            df['날짜검증'] = False
            df.loc[df['No'].isin(target_rule_true), '날짜검증'] = True

            # 작업구분 설정
            df['작업구분'] = '유지'
            df.loc[df['늦은종료일'] == False, '작업구분'] = '삭제'

            # 공지여부 설정
            df['공지여부'] = False
            df.loc[df['신청자검증'] == False, '공지여부'] = True

            # 미사용예외 설정
            df['미사용예외'] = False
            df.loc[
                (df['날짜검증'] == False) & 
                (df['늦은종료일'] == True), 
                '미사용예외'
            ] = True

            # 자동연장 정책 중 GROUP 타입 처리
            extensioned_df = df.groupby('No').filter(lambda x: x['자동연장'].any())
            extensioned_group = extensioned_df[extensioned_df['Request Type'] == 'GROUP']
            exception_target = extensioned_group.groupby('No').filter(
                lambda x: len(x['Request ID'].unique()) >= 2
            )
            exception_id = exception_target[
                (exception_target['자동연장'] == True) & 
                (exception_target['작업구분'] == '삭제')
            ]['No']

            # 예외 ID 제거
            df = df[~df['No'].isin(exception_id)]

            # GROUP이 아닌 정책 중 자동연장이면서 삭제 대상인 정책 필터링
            filtered_no = df.groupby('No').filter(
                lambda x: (x['Request Type'] != 'GROUP').any() and
                        (x['작업구분'] == '삭제').any() and
                        (x['자동연장'] == True).any()
            )['No'].unique()

            df = df[~df['No'].isin(filtered_no)]

            # 모두 삭제 대상인 정책 필터링
            filtered_no_2 = df.groupby('No').filter(
                lambda x: (x['작업구분'] != '유지').all()
            )['No'].unique()

            df = df[~df['No'].isin(filtered_no_2)]

            # 특정 타입 제외
            target_types = ["PAM", "SERVER", "Unknown", "GROUP"]
            target_nos = df[df['Request Type'].isin(target_types)]['No'].drop_duplicates()
            df = df[~df['No'].isin(target_nos)]

            # 공지여부에 따른 분류
            notice_df = df[df['공지여부'] == True].copy()  # .copy() 추가
            delete_df = df[df['공지여부'] == False].copy()  # .copy() 추가

            # 작업구분 컬럼 이동
            for target_df in [notice_df, delete_df]:
                if not target_df.empty:  # 빈 DataFrame 체크
                    column_to_move = target_df.pop('작업구분')
                    target_df.insert(0, '작업구분', column_to_move)

            # 불필요한 컬럼 제거
            columns_to_drop = [
                'Request Type', 'Ruleset ID', 'MIS ID', 'Start Date', 
                'End Date', '늦은종료일', '신청자검증', '날짜검증', 
                '공지여부', '미사용예외', '자동연장'
            ]
            
            # 안전한 컬럼 제거
            for target_df in [notice_df, delete_df]:
                if not target_df.empty:
                    existing_columns = [col for col in columns_to_drop if col in target_df.columns]
                    target_df.drop(columns=existing_columns, axis=1, inplace=True)

            # 파일 저장
            filename = remove_extension(file_path)
            df.to_excel(f'{filename}_정리.xlsx', index=False, engine='openpyxl')
            
            if not notice_df.empty:
                notice_df.to_excel(f'{filename}_공지.xlsx', index=False, engine='openpyxl')
            if not delete_df.empty:
                delete_df.to_excel(f'{filename}_삭제.xlsx', index=False, engine='openpyxl')

            self.logger.info("Successfully organized redundant files")

        except Exception as e:
            self.logger.error(f"Error in organize_redundant_file: {str(e)}")

    def notice_file_organization(self, file_path):
        """정리대상 별 공지파일 분류"""
        def expired_used(df, selected_file):
            """만료된 사용 정책 처리"""
            filtered_df = df[
                ((df['예외'].isna()) | (df['예외'] == '신규정책')) &
                (df['중복여부'].isna()) &
                (df['신청이력'] != 'Unknown') &
                (df['만료여부'] == '만료') &
                (df['미사용여부'] == '사용')
            ]

            selected_df = filtered_df[COLUMNS]
            selected_df = selected_df.astype(str)

            for date_column in DATE_COLUMNS:
                selected_df[date_column] = pd.to_datetime(selected_df[date_column]).dt.strftime('%Y-%m-%d')
            
            selected_df.rename(TRANSLATED_COLUMNS, inplace=True)
            selected_df.fillna('', inplace=True)
            selected_df.replace('nan', '', inplace=True)
            
            type = '만료_사용정책'
            filename = f"{remove_extension(selected_file)}_기간만료(공지용).xlsx"
            selected_df.to_excel(filename, index=False, na_rep='', sheet_name=type)
            save_to_excel(selected_df, type, filename)

        def expired_unused(df, selected_file):
            """만료된 미사용 정책 처리"""
            filtered_df = df[
                ((df['예외'].isna()) | (df['예외'] == '신규정책')) &
                (df['중복여부'].isna()) &
                (df['신청이력'] != 'Unknown') &
                (df['만료여부'] == '만료') &
                (df['미사용여부'] == '미사용')
            ]

            selected_df = filtered_df[COLUMNS]
            selected_df = selected_df.astype(str)

            for date_column in DATE_COLUMNS:
                selected_df[date_column] = pd.to_datetime(selected_df[date_column]).dt.strftime('%Y-%m-%d')
            
            selected_df.rename(TRANSLATED_COLUMNS, inplace=True)
            selected_df.fillna('', inplace=True)
            selected_df.replace('nan', '', inplace=True)

            type = '만료_미사용정책'
            filename = f"{remove_extension(selected_file)}_만료_미사용정책(공지용).xlsx"
            selected_df.to_excel(filename, index=False, na_rep='', sheet_name=type)
            save_to_excel(selected_df, type, filename)

        def longterm_unused_rules(df, selected_file):
            """장기 미사용 정책 처리"""
            filtered_df = df[
                (df['예외'].isna()) &
                (df['중복여부'].isna()) &
                (df['신청이력'] != 'Unknown') &
                (df['만료여부'] == '미만료') &
                (df['미사용여부'] == '미사용')
            ]

            selected_df = filtered_df[COLUMNS]
            selected_df = selected_df.astype(str)

            for date_column in DATE_COLUMNS:
                selected_df[date_column] = pd.to_datetime(selected_df[date_column]).dt.strftime('%Y-%m-%d')
            
            selected_df.rename(TRANSLATED_COLUMNS, inplace=True)
            selected_df.fillna('', inplace=True)
            selected_df.replace('nan', '', inplace=True)

            type = '미만료_미사용정책'
            filename = f"{remove_extension(selected_file)}_장기미사용정책(공지용).xlsx"
            selected_df.to_excel(filename, index=False, na_rep='', sheet_name=type)
            save_to_excel(selected_df, type, filename)

        def no_history_unused(df, selected_file):
            """이력 없는 미사용 정책 처리"""
            filtered_df = df[
                (df['예외'].isna()) &
                (df['중복여부'].isna()) &
                (df['신청이력'] == 'Unknown') &
                (df['만료여부'] == '만료') &
                (df['미사용여부'] == '미사용')
            ]

            selected_df = filtered_df[COLUMNS_NO_HISTORY]
            selected_df = selected_df.astype(str)
            selected_df.fillna('', inplace=True)
            selected_df.replace('nan', '', inplace=True)

            type = '이력없음_미사용정책'
            filename = f"{remove_extension(selected_file)}_이력없는_미사용정책.xlsx"
            selected_df.to_excel(filename, index=False, na_rep='', sheet_name=type)
            save_to_excel(selected_df, type, filename)

        try:
            print("분류할 정책파일을 선택하세요.")
            selected_file = select_xlsx_files()
            if not selected_file:
                return
            
            self.logger.info("정책 분류 시작")
            df = pd.read_excel(selected_file)

            for func in [expired_used, expired_unused, longterm_unused_rules, no_history_unused]:
                try:
                    func(df, selected_file)
                    self.logger.info(f"{func.__doc__.strip()} 분류 완료")
                except Exception as e:
                    self.logger.error(f"{func.__doc__.strip()} 분류 실패: {str(e)}")

            self.logger.info("정책 분류 완료")

        except Exception as e:
            self.logger.error(f"Error in notice_file_organization: {str(e)}")

    def add_mis_id(self, file_path, mis_file_path):
        """정책파일에 MIS ID 추가"""
        try:
            mis_df = pd.read_csv(mis_file_path)
            rule_df = pd.read_excel(file_path)

            # 중복 제거하고 첫 번째 값만 유지
            mis_df_unique = mis_df.drop_duplicates(subset=['ruleset_id'], keep='first')
            mis_id_map = mis_df_unique.set_index('ruleset_id')['mis_id']

            # MIS ID 업데이트
            rule_df['MIS ID'] = rule_df.apply(
                lambda row: mis_id_map.get(row['Ruleset ID'], row['MIS ID']) 
                if pd.isna(row['MIS ID']) or row['MIS ID'] == '' 
                else row['MIS ID'], 
                axis=1
            )

            rule_df.to_excel(update_version(file_path), index=False, engine='openpyxl')
            self.logger.info("Successfully added MIS IDs")

        except Exception as e:
            self.logger.error(f"Error in add_mis_id: {str(e)}") 