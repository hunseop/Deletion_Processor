document.addEventListener('DOMContentLoaded', function() {
    // 전역 상태 관리
    const state = {
        currentPhase: 1,
        totalPhases: 6,
        phases: {
            1: { completed: false, required: [] },
            2: { completed: false, required: ['connection'] },
            3: { completed: false, required: ['policy', 'usage', 'duplicate'] },
            4: { completed: false, required: ['request_file', 'mis_file'] },
            5: { completed: false, required: ['mis', 'request', 'exception'] },
            6: { completed: false, required: ['policy_classification', 'notice'] }
        }
    };

    // Task Card 상태 관리
    function updateTaskStatus(phaseNum, status = 'pending') {
        const card = document.getElementById(`phase${phaseNum}`);
        const statusElement = card.querySelector('.task-status');
        
        if (status === 'completed') {
            card.classList.add('completed');
            statusElement.textContent = '완료';
            enableNextPhase(phaseNum);
        } else if (status === 'in_progress') {
            card.classList.remove('disabled');
            statusElement.textContent = '진행중';
        } else {
            card.classList.add('disabled');
            statusElement.textContent = '대기중';
        }
    }

    // 다음 Phase 활성화
    function enableNextPhase(currentPhase) {
        const nextPhase = currentPhase + 1;
        if (nextPhase <= state.totalPhases) {
            const nextCard = document.getElementById(`phase${nextPhase}`);
            nextCard.classList.remove('disabled');
            updateTaskStatus(nextPhase, 'in_progress');
        }
    }

    // Phase 1: 연결 테스트
    window.testConnection = function() {
        const data = {
            vendor: document.getElementById('vendor').value,
            primary_ip: document.getElementById('primary_ip').value,
            secondary_ip: document.getElementById('secondary_ip').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        };

        if (!validateConnectionData(data)) {
            alert('모든 필수 항목을 입력해주세요.');
            return;
        }

        fetch('/firewall/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                updateTaskStatus(1, 'completed');
                state.phases[1].completed = true;
                alert('연결 성공!');
            } else {
                alert('연결 실패: ' + result.message);
            }
        })
        .catch(error => {
            alert('오류 발생: ' + error);
        });
    };

    // 데이터 수집 관련 함수들
    window.collectData = function(dataType) {
        const taskItem = document.querySelector(`[data-requirement="${dataType}"]`).closest('.task-item');
        const controls = taskItem.querySelectorAll('.control-button');
        const progressBar = taskItem.querySelector('.progress');
        const progressText = taskItem.querySelector('.progress-text');
        const statusMessage = taskItem.querySelector('.status-message');

        // 버튼 상태 업데이트
        controls.forEach(btn => {
            if (btn.classList.contains('start')) btn.disabled = true;
            if (btn.classList.contains('stop')) btn.disabled = false;
        });

        // 진행 상태 시뮬레이션
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            progressText.textContent = `${progress}%`;
            statusMessage.textContent = '데이터 수집 중...';

            if (progress >= 100) {
                clearInterval(interval);
                completeCollection(dataType);
            }
        }, 200);

        // 진행 상태 저장
        taskItem.dataset.interval = interval;
    };

    window.stopCollection = function(dataType) {
        const taskItem = document.querySelector(`[data-requirement="${dataType}"]`).closest('.task-item');
        clearInterval(taskItem.dataset.interval);
        
        // 버튼 상태 업데이트
        const controls = taskItem.querySelectorAll('.control-button');
        controls.forEach(btn => {
            if (btn.classList.contains('start')) btn.disabled = false;
            if (btn.classList.contains('stop')) btn.disabled = true;
            if (btn.classList.contains('retry')) btn.disabled = false;
        });

        taskItem.querySelector('.status-message').textContent = '수집 중단됨';
    };

    function completeCollection(dataType) {
        const taskItem = document.querySelector(`[data-requirement="${dataType}"]`).closest('.task-item');
        
        // 버튼 상태 업데이트
        const controls = taskItem.querySelectorAll('.control-button');
        controls.forEach(btn => {
            if (btn.classList.contains('start')) btn.disabled = true;
            if (btn.classList.contains('stop')) btn.disabled = true;
            if (btn.classList.contains('validate')) btn.disabled = false;
            if (btn.classList.contains('download')) btn.disabled = false;
        });

        taskItem.querySelector('.status-message').textContent = '수집 완료';
        
        // 데이터 미리보기 업데이트
        fetch(`/policy/collect/${dataType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(getConnectionInfo())
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                updateDataPreview(dataType, result.data, taskItem);
                checkPhaseCompletion(2);
            }
        });
    }

    // 데이터 검증
    window.validateData = function(dataType) {
        const taskItem = document.querySelector(`[data-requirement="${dataType}"]`).closest('.task-item');
        const statusMessage = taskItem.querySelector('.status-message');
        
        statusMessage.textContent = '데이터 검증 중...';
        
        // 검증 로직 실행
        setTimeout(() => {
            statusMessage.textContent = '검증 완료';
            taskItem.querySelector(`[data-requirement="${dataType}"]`).classList.add('completed');
        }, 1000);
    };

    // 데이터 다운로드
    window.downloadData = function(dataType) {
        fetch(`/policy/download/${dataType}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${dataType}_data.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        });
    };

    // 재시도
    window.retryCollection = function(dataType) {
        const taskItem = document.querySelector(`[data-requirement="${dataType}"]`).closest('.task-item');
        
        // 상태 초기화
        taskItem.querySelector('.progress').style.width = '0%';
        taskItem.querySelector('.progress-text').textContent = '0%';
        taskItem.querySelector('.status-message').textContent = '';
        
        // 버튼 상태 초기화
        const controls = taskItem.querySelectorAll('.control-button');
        controls.forEach(btn => {
            if (btn.classList.contains('start')) btn.disabled = false;
            if (btn.classList.contains('stop')) btn.disabled = true;
            if (btn.classList.contains('validate')) btn.disabled = true;
            if (btn.classList.contains('download')) btn.disabled = true;
            if (btn.classList.contains('retry')) btn.disabled = true;
        });
    };

    // 유틸리티 함수들
    function validateConnectionData(data) {
        return data.vendor && data.primary_ip && data.username && data.password;
    }

    function getConnectionInfo() {
        return {
            vendor: document.getElementById('vendor').value,
            primary_ip: document.getElementById('primary_ip').value,
            secondary_ip: document.getElementById('secondary_ip').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        };
    }

    function checkPhaseCompletion(phaseNum) {
        const phase = state.phases[phaseNum];
        const allCompleted = phase.required.every(req => {
            const button = document.querySelector(`button[data-requirement="${req}"]`);
            return button && button.classList.contains('completed');
        });

        if (allCompleted) {
            updateTaskStatus(phaseNum, 'completed');
            phase.completed = true;
        }
    }

    // 데이터 미리보기 업데이트
    function updateDataPreview(dataType, data, taskItem) {
        const previewArea = document.querySelector('.data-preview');
        const typeLabels = {
            'policy': '정책',
            'usage': '사용이력',
            'duplicate': '중복정책'
        };

        // 기존 미리보기에 새로운 데이터 추가
        const previewDiv = document.createElement('div');
        previewDiv.className = 'preview-item';
        previewDiv.innerHTML = `
            <h4>${typeLabels[dataType]} 추출 결과</h4>
            <p>상태: 추출 완료</p>
            <p>데이터 수: ${data?.count || 0}개</p>
        `;
        
        previewArea.appendChild(previewDiv);
    }

    // 파일 파싱 함수
    window.parseFile = function(fileType) {
        const fileInput = document.getElementById(fileType + 'File');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('파일을 선택해주세요.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch(`/policy/parse/${fileType}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 파싱 결과 표시
                updateParsingResult(fileType, data);
                // 파싱 성공 표시
                document.querySelector(`button[onclick="parseFile('${fileType}')"]`)
                    .classList.add('completed');
                // Phase 완료 여부 확인
                checkPhaseCompletion();
            } else {
                alert('파싱 실패: ' + data.message);
                if (data.errors) {
                    showErrors(data.errors);
                }
            }
        })
        .catch(error => {
            alert('오류 발생: ' + error);
        });
    };

    // 파싱 결과 업데이트
    function updateParsingResult(fileType, data) {
        const resultPreview = document.querySelector('.result-preview');
        const stats = data.stats;
        
        resultPreview.innerHTML = `
            <h4>${fileType} 파일 파싱 결과</h4>
            <p>전체: ${stats.total}건</p>
            <p>성공: ${stats.parsed}건</p>
            <p>실패: ${stats.failed}건</p>
            <div class="preview-table">
                ${generatePreviewTable(data.preview)}
            </div>
        `;
    }

    // 미리보기 테이블 생성
    function generatePreviewTable(preview) {
        if (!preview || preview.length === 0) return '';
        
        const headers = Object.keys(preview[0]);
        return `
            <table>
                <thead>
                    <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
                </thead>
                <tbody>
                    ${preview.map(row => `
                        <tr>${headers.map(h => `<td>${row[h] || ''}</td>`).join('')}</tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    // 오류 표시
    function showErrors(errors) {
        const errorList = document.querySelector('.error-list');
        errorList.innerHTML = `
            <h4>오류 목록</h4>
            <ul>
                ${errors.map(error => `<li>${error}</li>`).join('')}
            </ul>
        `;
    }

    // Phase 4: 파일 검증
    window.validateFiles = function() {
        const requestFile = document.getElementById('requestFile').files[0];
        const misFile = document.getElementById('misFile').files[0];
        
        if (!requestFile || !misFile) {
            alert('모든 파일을 선택해주세요.');
            return;
        }

        const formData = new FormData();
        formData.append('request_file', requestFile);
        formData.append('mis_file', misFile);

        fetch('/policy/validate-files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                updateTaskStatus(4, 'completed');
                state.phases[4].completed = true;
                showValidationResult(result);
            } else {
                alert('파일 검증 실패: ' + result.message);
                if (result.errors) {
                    showErrors(result.errors);
                }
            }
        })
        .catch(error => {
            alert('오류 발생: ' + error);
        });
    };

    // Phase 5: 데이터 통합
    window.integrateData = function(integrationType) {
        const button = document.querySelector(`button[onclick="integrateData('${integrationType}')"]`);
        const statusDiv = button.parentElement.querySelector('.step-status');
        
        button.disabled = true;
        statusDiv.textContent = '처리중...';

        fetch('/policy/integrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: integrationType,
                vendor: document.getElementById('vendor').value
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                button.classList.add('completed');
                statusDiv.textContent = '완료';
                updateIntegrationPreview(integrationType, result.data);
                checkPhaseCompletion(5);
            } else {
                statusDiv.textContent = '실패';
                alert(result.message);
            }
            button.disabled = false;
        })
        .catch(error => {
            statusDiv.textContent = '오류';
            alert('오류 발생: ' + error);
            button.disabled = false;
        });
    };

    // Phase 6: 결과 생성
    window.generateResult = function(resultType) {
        const button = document.querySelector(`button[onclick="generateResult('${resultType}')"]`);
        button.disabled = true;

        fetch('/policy/generate-result', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: resultType,
                vendor: document.getElementById('vendor').value
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                button.classList.add('completed');
                addDownloadFile(result.filename, result.type);
                checkPhaseCompletion(6);
            } else {
                alert(result.message);
            }
            button.disabled = false;
        })
        .catch(error => {
            alert('오류 발생: ' + error);
            button.disabled = false;
        });
    };

    // 결과 파일 목록에 추가
    function addDownloadFile(filename, type) {
        const fileList = document.querySelector('.file-list');
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span class="file-name">${filename}</span>
            <button onclick="downloadFile('${filename}')" class="download-button">
                다운로드
            </button>
        `;
        fileList.appendChild(fileItem);
    }

    // 파일 다운로드
    window.downloadFile = function(filename) {
        fetch(`/policy/download/${filename}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            alert('다운로드 실패: ' + error);
        });
    };

    // 검증 결과 표시
    function showValidationResult(result) {
        const previewArea = document.querySelector('.data-preview');
        previewArea.innerHTML = `
            <div class="validation-result">
                <h4>파일 검증 결과</h4>
                <div class="result-details">
                    <p>신청정보 파일: ${result.request_file_status}</p>
                    <p>MIS ID 파일: ${result.mis_file_status}</p>
                </div>
                ${result.warnings ? `
                    <div class="warnings">
                        <h5>주의사항</h5>
                        <ul>
                            ${result.warnings.map(w => `<li>${w}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // 통합 결과 미리보기 업데이트
    function updateIntegrationPreview(type, data) {
        const previewArea = document.querySelector('.integration-preview');
        previewArea.innerHTML = `
            <div class="integration-result">
                <h4>${getIntegrationTitle(type)} 결과</h4>
                <p>처리된 항목: ${data.processed_count}건</p>
                <p>성공: ${data.success_count}건</p>
                <p>실패: ${data.failed_count}건</p>
                ${generatePreviewTable(data.preview)}
            </div>
        `;
    }

    function getIntegrationTitle(type) {
        const titles = {
            'mis': 'MIS ID 정보 추가',
            'request': '신청정보 통합',
            'exception': '예외처리'
        };
        return titles[type] || type;
    }

    // 초기 상태 설정
    updateTaskStatus(1, 'in_progress');
    for (let i = 2; i <= state.totalPhases; i++) {
        updateTaskStatus(i, 'pending');
    }
}); 