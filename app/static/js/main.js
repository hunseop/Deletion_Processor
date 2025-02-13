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
    const primaryIP = document.getElementById('primary_ip').value;
    const secondaryIP = document.getElementById('secondary_ip').value;
    
    if (!isValidIP(primaryIP)) {
        const status = document.querySelector('#phase1 .task-status');
        status.textContent = 'Primary IP 형식 오류';
        status.classList.add('error');
        return false;
    }
    
    if (secondaryIP && !isValidIP(secondaryIP)) {
        const status = document.querySelector('#phase1 .task-status');
        status.textContent = 'Secondary IP 형식 오류';
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