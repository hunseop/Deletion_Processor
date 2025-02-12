import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 컬럼 설정
COLUMNS = [
    'Rule Name', 'Source', 'User', 'Destination', 'Service', 'Application', 'Description',
    'REQUEST_ID', 'REQUEST_START_DATE', 'REQUEST_END_DATE', 'TITLE', 'REQUESTER_ID',
    'REQUESTER_EMAIL', 'REQUESTER_NAME', 'REQUESTER_DEPT', 'WRITE_PERSON_ID', 'WRITE_PERSON_EMAIL',
    'WRITE_PERSON_NAME', 'WRITE_PERSON_DEPT', 'APPROVAL_PERSON_ID', 'APPROVAL_PERSON_EMAIL',
    'APPROVAL_PERSON_NAME', 'APPROVAL_PERSON_DEPT_NAME'
]

COLUMNS_NO_HISTORY = [
    'Rule Name', 'Source', 'User', 'Destination', 'Service', 'Application', 'Description'
]

DATE_COLUMNS = ['REQUEST_START_DATE', 'REQUEST_END_DATE']

TRANSLATED_COLUMNS = {
    'REQUEST_ID': '신청번호',
    'REQUEST_START_DATE': '시작일',
    'REQUEST_END_DATE': '종료일',
    'TITLE': '제목',
    'REQUESTER_ID': '신청자 ID',
    'REQUESTER_EMAIL': '신청자 이메일',
    'REQUESTER_NAME': '신청자명',
    'REQUESTER_DEPT': '신청자 부서',
    'WRITE_PERSON_ID': '기안자 ID',
    'WRITE_PERSON_EMAIL': '기안자 이메일',
    'WRITE_PERSON_NAME': '기안자명',
    'WRITE_PERSON_DEPT': '기안자 부서',
    'APPROVAL_PERSON_ID': '결재자 ID',
    'APPROVAL_PERSON_EMAIL': '결재자 이메일',
    'APPROVAL_PERSON_NAME': '결재자명',
    'APPROVAL_PERSON_DEPT_NAME': '결재자 부서',
}

# 예외 리스트
EXCEPT_LIST = [
    'test',
    'sample',
    'test_',
    'sample_',
    'deny_rule',
    'deny_rule_1',
    'deny_rule_2',
    'deny_rule_3',
    'deny_rule_4',
    'deny_rule_5',
    'deny_rule_6',
    'deny_rule_7',
    'deny_rule_8',
    'deny_rule_9',
    'deny_rule_10',
]

# 작업 메뉴
TASK_MENU = {
    1: "Description에서 신청번호 파싱하기",
    2: "정책파일에서 신청번호 추출하기",
    3: "정책파일에서 신청정보 추가하기",
    4: "팔로알토 정책에서 예외처리하기",
    5: "시큐아이 정책에서 예외처리하기",
    6: "중복정책 공지/삭제 분류하기",
    7: "정리대상 별 공지파일 분류하기",
    8: "정책파일에서 MIS ID 추가하기",
    0: "종료"
} 