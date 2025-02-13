// 데이터 수집 함수
async function collectData(dataType) {
    try {
        const response = await fetch(`/policy/collect/${dataType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                // TODO: 실제 방화벽 정보 추가
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 다운로드 버튼 활성화
            const downloadBtn = document.querySelector(`[data-task="${dataType}"] .download`);
            downloadBtn.disabled = false;
            downloadBtn.dataset.filename = result.filename;
        }
        
        alert(result.message);
    } catch (error) {
        alert('데이터 수집 중 오류가 발생했습니다.');
        console.error(error);
    }
}

// 파일 다운로드 함수
function downloadData(dataType) {
    const downloadBtn = document.querySelector(`[data-task="${dataType}"] .download`);
    const filename = downloadBtn.dataset.filename;
    
    if (filename) {
        window.location.href = `/policy/download/${filename}`;
    }
}

// 방화벽 연결 테스트
async function testConnection() {
    const form = document.getElementById('firewallConnectionForm');
    const formData = {
        vendor: form.vendor.value,
        primary_ip: form.primary_ip.value,
        secondary_ip: form.secondary_ip.value,
        username: form.username.value,
        password: form.password.value
    };

    try {
        const response = await fetch('/policy/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('연결 테스트 성공');
            document.querySelector('.save-connection').disabled = false;
        } else {
            alert(`연결 테스트 실패: ${result.message}`);
        }
    } catch (error) {
        alert('연결 테스트 중 오류가 발생했습니다.');
        console.error(error);
    }
}

// 방화벽 설정 저장
async function saveConnection() {
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
            alert('설정이 저장되었습니다.');
            // Phase 1 완료 표시
            document.querySelector('#phase1 .task-status').textContent = '완료';
            document.getElementById('phase1').classList.add('completed');
        } else {
            alert(`저장 실패: ${result.message}`);
        }
    } catch (error) {
        alert('설정 저장 중 오류가 발생했습니다.');
        console.error(error);
    }
} 