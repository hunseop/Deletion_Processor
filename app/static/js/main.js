// Phase 1 부분 시작
// IP 주소 검증 함수
function isValidIP(ip) {
    if (!ip) return true; // secondary IP는 선택사항이므로 빈 값 허용
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipPattern.test(ip)) return false;
    
    const parts = ip.split('.');
    return parts.every(part => {
        const num = parseInt(part, 10);
        return num >= 0 && num <= 255;
    });
}

// 폼 검증 함수
function validateForm() {
    const form = document.getElementById('firewallConnectionForm');
    const vendor = form.vendor.value;
    const primaryIP = form.primary_ip.value;
    const secondaryIP = form.secondary_ip.value;
    const username = form.username.value;
    const password = form.password.value;
    const status = document.querySelector('#phase1 .task-status');

    // 벤더 선택 검증
    if (!vendor) {
        status.textContent = '벤더를 선택해주세요';
        status.classList.add('error');
        return false;
    }

    // Primary IP 검증
    if (!primaryIP) {
        status.textContent = 'Primary IP를 입력해주세요';
        status.classList.add('error');
        return false;
    }
    if (!isValidIP(primaryIP)) {
        status.textContent = 'Primary IP 형식이 올바르지 않습니다';
        status.classList.add('error');
        return false;
    }

    // Secondary IP 검증 (입력된 경우에만)
    if (secondaryIP && !isValidIP(secondaryIP)) {
        status.textContent = 'Secondary IP 형식이 올바르지 않습니다';
        status.classList.add('error');
        return false;
    }

    // 계정 검증
    if (!username) {
        status.textContent = '계정을 입력해주세요';
        status.classList.add('error');
        return false;
    }

    // 비밀번호 검증
    if (!password) {
        status.textContent = '비밀번호를 입력해주세요';
        status.classList.add('error');
        return false;
    }

    return true;
}

// 상태 초기화 함수
function resetStatus() {
    const status = document.querySelector('#phase1 .task-status');
    status.textContent = '대기중';
    status.classList.remove('success', 'error');
}

// 리셋 함수
function resetForm() {
    const form = document.getElementById('firewallConnectionForm');
    form.reset();
    resetStatus();
}

// 저장 함수
async function saveConnection() {
    if (!validateForm()) return;
    
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
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            const status = document.querySelector('#phase1 .task-status');
            status.textContent = '저장됨';
            status.classList.remove('error');
            status.classList.add('success');
        } else {
            const status = document.querySelector('#phase1 .task-status');
            status.textContent = '저장 실패';
            status.classList.remove('success');
            status.classList.add('error');
        }
    } catch (error) {
        console.error(error);
        const status = document.querySelector('#phase1 .task-status');
        status.textContent = '오류 발생';
        status.classList.remove('success');
        status.classList.add('error');
    }
} 
// Phase 1 부분 끝