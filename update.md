# 정책 삭제 프로세스 상세 로직

## 1. 신청번호 파싱 (parse_request_type)

### 기능
- Description 필드에서 신청번호 및 관련 정보 추출
- 날짜 형식 변환 및 정규화

### 처리 순서
1. 날짜 문자열을 날짜 객체로 변환 (convert_to_date)
   - 입력 형식: YYYYMMDD
   - 출력 형식: YYYY-MM-DD
   
2. 정규식을 통한 정보 추출 (parse_request_info)
   - Request Type 분류
     - P: GROUP
     - F: NORMAL
     - S: SERVER
     - M: PAM
   - Request ID
   - Ruleset ID
   - MIS ID
   - Request User
   - Start/End Date

3. 결과를 DataFrame에 저장하고 버전 업데이트하여 저장

## 2. 신청번호 추출 (extract_request_id)

### 기능
- Request Type별로 고유한 Request ID 추출
- 최대 5개 Type까지 처리

### 처리 순서
1. Unknown을 제외한 고유 Request Type 추출
2. Type별로 Request ID 중복 제거
3. 각 Type을 개별 시트로 저장

## 3. 신청정보 추가 (add_request_info)

### 기능
- 정책 파일과 신청정보 파일 매칭
- 매칭된 정보로 정책 파일 업데이트

### 매칭 로직
1. GROUP 타입인 경우:
   - REQUEST_ID와 MIS_ID 일치
   - REQUEST_ID, REQUEST_END_DATE, WRITE_PERSON_ID 일치
   - REQUEST_ID, REQUEST_END_DATE, REQUESTER_ID 일치

2. 기타 타입:
   - REQUEST_ID 일치

### 데이터 처리
- 날짜 필드: datetime 객체로 변환
- 이메일: Request User + '@gmail.com' 형식으로 생성
- 자동연장 ID 처리

## 4. 팔로알토 예외처리 (paloalto_exception)

### 예외 처리 기준
1. except_list와 REQUEST_ID 매칭
2. REQUEST_STATUS가 99인 경우
3. 3개월 이내 신규 정책
4. Deny_Std_Rule 이전 인프라 정책
5. sample_, test_ 시작 정책
6. 비활성화 정책 (Enable = 'N')
7. _Rule로 끝나는 기준정책
8. 차단정책 (Action = 'deny')

### 결과 처리
- 예외 여부 컬럼 추가
- 만료여부 판단
- 신청이력 컬럼 추가
- 미사용여부 컬럼 추가

## 5. 시큐아이 예외처리 (secui_exception)

### 예외 처리 기준
팔로알토와 유사하나 일부 차이 존재:
1. 기준정책 판단: Description에 '기준룰' 포함 여부
2. 인프라정책: Description에 'Deny_Std_Rule' 포함 여부 확인

## 6. 중복정책 분류 (organize_redundant_file)

### 처리 단계
1. 자동연장 여부 확인
2. 종료일 검증
   - 가장 늦은 종료일 체크
   - Type이 Upper인 경우 특별 처리
3. 신청자 검증
   - 동일 신청자 여부 확인
4. 작업구분 설정
   - 기본값: '유지'
   - 늦은종료일 = False인 경우: '삭제'
5. 공지여부 설정
   - 신청자 불일치 시 True
6. 미사용예외 설정
   - 날짜검증 = False & 늦은종료일 = True

### 예외 처리
1. GROUP 타입 자동연장 정책
2. 비GROUP 타입 자동연장 정책
3. PAM, SERVER, Unknown, GROUP 타입 제외

## 7. 공지파일 분류 (notice_file_organization)

### 분류 기준
1. 만료_사용정책
   - 예외 없음 또는 신규정책
   - 중복여부 없음
   - Unknown 아님
   - 만료됨
   - 사용중

2. 만료_미사용정책
   - 만료됨
   - 미사용

3. 미만료_미사용정책
   - 만료되지 않음
   - 미사용

4. 이력없는_미사용정책
   - 신청이력 Unknown
   - 만료됨
   - 미사용

### 결과 파일
- 각 분류별 개별 엑셀 파일 생성
- 번역된 컬럼명 적용
- 날짜 형식 통일 (YYYY-MM-DD)

## 8. MIS ID 추가 (add_mis_id)

### 처리 로직
1. MIS ID 파일에서 ruleset_id별 첫 번째 mis_id 추출
2. 정책 파일의 Ruleset ID와 매칭
3. 기존 MIS ID가 없는 경우에만 업데이트 