// Phase 1: 방화벽 설정 관련 코드
const phase1 = {
    validateIP(ip) {
        if (!ip) return true;
        const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipPattern.test(ip)) return false;
        
        const parts = ip.split('.');
        return parts.every(part => {
            const num = parseInt(part, 10);
            return num >= 0 && num <= 255;
        });
    },

    validateForm() {
        const form = document.getElementById('firewallConnectionForm');
        const fields = {
            vendor: '벤더를 선택해주세요',
            primary_ip: 'Primary IP를 입력해주세요',
            username: '계정을 입력해주세요',
            password: '비밀번호를 입력해주세요'
        };

        const status = document.querySelector('#phase1 .task-status');
        
        // 필수 필드 검증
        for (const [field, message] of Object.entries(fields)) {
            if (!form[field].value) {
                status.textContent = message;
                status.classList.add('error');
                return false;
            }
        }

        // IP 형식 검증
        if (!this.validateIP(form.primary_ip.value)) {
            status.textContent = 'Primary IP 형식이 올바르지 않습니다';
            status.classList.add('error');
            return false;
        }

        if (form.secondary_ip.value && !this.validateIP(form.secondary_ip.value)) {
            status.textContent = 'Secondary IP 형식이 올바르지 않습니다';
            status.classList.add('error');
            return false;
        }

        return true;
    },

    async saveConnection() {
        if (!this.validateForm()) return;
        
        const form = document.getElementById('firewallConnectionForm');
        const formData = {
            vendor: form.vendor.value,
            primary_ip: form.primary_ip.value,
            secondary_ip: form.secondary_ip.value,
            username: form.username.value,
            password: form.password.value
        };

        try {
            const response = await fetch('/policy/save-connection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                phaseManager.complete(1);
            } else {
                this.setStatus('저장 실패', 'error');
            }
        } catch (error) {
            console.error(error);
            this.setStatus('오류 발생', 'error');
        }
    },

    reset() {
        const form = document.getElementById('firewallConnectionForm');
        form.reset();
        this.setStatus('대기중');
        phaseManager.disable(2);
    },

    setStatus(message, type = '') {
        const status = document.querySelector('#phase1 .task-status');
        status.textContent = message;
        status.className = 'task-status';
        if (type) status.classList.add(type);
    }
};

// Phase 2: 데이터 수집 관련 코드
const phase2 = {
    async collectData(dataType) {
        const taskRow = document.querySelector(`[data-task="${dataType}"]`);
        const status = taskRow.querySelector('.task-status');
        const button = taskRow.querySelector('.run-btn');
        
        this.setTaskStatus(dataType, '수집 중...', '');
        button.disabled = true;
        
        try {
            const response = await fetch(`/policy/collect-firewall-data/${dataType}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const timeInfo = `(${result.elapsed_time}초)`;
                this.setTaskStatus(dataType, `완료 ${timeInfo}`, 'success');
                button.disabled = true;

                // 다운로드 버튼 추가
                this.addDownloadButton(taskRow, result.filename);
                
                if (this.checkAllCompleted()) {
                    phaseManager.complete(2);
                }
            } else {
                this.setTaskStatus(dataType, '실패', 'error');
                button.disabled = false;
            }
        } catch (error) {
            console.error(error);
            this.setTaskStatus(dataType, '오류', 'error');
            button.disabled = false;
        }
    },

    addDownloadButton(taskRow, filename) {
        const controls = taskRow.querySelector('.task-controls');
        let downloadBtn = controls.querySelector('.download-btn');
        
        if (!downloadBtn) {
            downloadBtn = document.createElement('button');
            downloadBtn.className = 'btn download-btn';
            downloadBtn.textContent = '다운로드';
            controls.appendChild(downloadBtn);
        }
        
        downloadBtn.onclick = () => {
            window.location.href = `/policy/download/${filename}`;
        };
    },

    setTaskStatus(dataType, message, type = '') {
        const status = document.querySelector(`[data-task="${dataType}"] .task-status`);
        status.textContent = message;
        status.className = 'task-status';
        if (type) status.classList.add(type);
    },

    checkAllCompleted() {
        const tasks = ['policy', 'usage', 'duplicate'];
        return tasks.every(task => {
            const button = document.querySelector(`[data-task="${task}"] .run-btn`);
            return button.disabled;
        });
    }
};

// Phase 3: 정보 파싱 관련 코드
const phase3 = {
    // 파일 선택 이벤트 핸들러
    handleFileSelect(fileType) {
        const fileInput = document.getElementById(`${fileType}File`);
        const fileName = fileInput.files[0]?.name || '선택된 파일 없음';
        const fileNameSpan = fileInput.parentElement.querySelector('.file-name');
        const parseBtn = fileInput.closest('.task-row').querySelector('.run-btn');
        
        fileNameSpan.textContent = fileName;
        parseBtn.disabled = !fileInput.files[0];
        
        // 신청번호 추출 버튼 활성화 체크
        this.checkExtractButton();
    },

    // Description 파싱 실행
    async parseDescription(fileType) {
        const taskRow = document.querySelector(`[data-task="${fileType}-parse"]`);
        const fileInput = document.getElementById(`${fileType}File`);
        const button = taskRow.querySelector('.run-btn');
        
        if (!fileInput.files[0]) return;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        this.setTaskStatus(fileType, '파싱 중...', '');
        button.disabled = true;
        
        try {
            const response = await fetch(`/policy/parse-description/${fileType}`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                const timeInfo = `(${result.elapsed_time}초)`;
                this.setTaskStatus(fileType, `완료 ${timeInfo}`, 'success');
                
                // 다운로드 버튼 추가
                this.addDownloadButton(taskRow, result.filename);
                
                // 신청번호 추출 버튼 활성화 체크
                this.checkExtractButton();
            } else {
                this.setTaskStatus(fileType, '실패', 'error');
                button.disabled = false;
            }
        } catch (error) {
            console.error(error);
            this.setTaskStatus(fileType, '오류', 'error');
            button.disabled = false;
        }
    },

    // 신청번호 추출
    async extractRequestId() {
        const taskRow = document.querySelector('[data-task="request-number"]');
        const button = taskRow.querySelector('.run-btn');
        
        this.setTaskStatus('request-number', '추출 중...', '');
        button.disabled = true;
        
        try {
            const response = await fetch('/policy/extract-request-id', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                const timeInfo = `(${result.elapsed_time}초)`;
                this.setTaskStatus('request-number', `완료 ${timeInfo}`, 'success');
                this.addDownloadButton(taskRow, result.filename);
                
                if (this.checkAllCompleted()) {
                    phaseManager.complete(3);
                }
            } else {
                this.setTaskStatus('request-number', '실패', 'error');
                button.disabled = false;
            }
        } catch (error) {
            console.error(error);
            this.setTaskStatus('request-number', '오류', 'error');
            button.disabled = false;
        }
    },

    // 상태 표시 업데이트
    setTaskStatus(taskType, message, type = '') {
        const status = document.querySelector(`[data-task="${taskType}-parse"] .task-status`) ||
                      document.querySelector(`[data-task="${taskType}"] .task-status`);
        status.textContent = message;
        status.className = 'task-status';
        if (type) status.classList.add(type);
    },

    // 다운로드 버튼 추가
    addDownloadButton(taskRow, filename) {
        const controls = taskRow.querySelector('.task-controls');
        let downloadBtn = controls.querySelector('.download-btn');
        
        if (!downloadBtn) {
            downloadBtn = document.createElement('button');
            downloadBtn.className = 'btn download-btn';
            downloadBtn.textContent = '다운로드';
            controls.appendChild(downloadBtn);
        }
        
        downloadBtn.onclick = () => {
            window.location.href = `/policy/download/${filename}`;
        };
    },

    // 신청번호 추출 버튼 활성화 체크
    checkExtractButton() {
        const requestFile = document.getElementById('requestFile');
        const extractBtn = document.querySelector('[data-task="request-number"] .run-btn');
        
        extractBtn.disabled = !requestFile.files[0];
    },

    // 모든 작업 완료 체크
    checkAllCompleted() {
        const tasks = ['policy-parse', 'duplicate-parse', 'request-number'];
        return tasks.every(task => {
            const status = document.querySelector(`[data-task="${task}"] .task-status.success`);
            return status !== null;
        });
    }
};

// Phase 관리
const phaseManager = {
    complete(currentPhase) {
        const currentCard = document.getElementById(`phase${currentPhase}`);
        const nextCard = document.getElementById(`phase${currentPhase + 1}`);
        
        if (currentCard) {
            const status = currentCard.querySelector('.task-status');
            status.textContent = '완료';
            status.classList.add('success');
        }
        
        if (nextCard) {
            nextCard.classList.remove('disabled');
            const status = nextCard.querySelector('.task-status');
            status.textContent = '대기중';
        }
    },

    disable(phase) {
        const card = document.getElementById(`phase${phase}`);
        if (card) {
            card.classList.add('disabled');
        }
    }
};

// 전역 함수 바인딩
window.saveConnection = () => phase1.saveConnection();
window.resetForm = () => phase1.reset();
window.collectFirewallData = (dataType) => phase2.collectData(dataType);
window.handleFileSelect = (fileType) => phase3.handleFileSelect(fileType);
window.parseDescription = (fileType) => phase3.parseDescription(fileType);
window.extractRequestId = () => phase3.extractRequestId();