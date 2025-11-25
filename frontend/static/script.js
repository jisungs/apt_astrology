// 점성술사 컨셉 인터랙션

document.addEventListener('DOMContentLoaded', function() {
    // 플로팅 로딩 오버레이 관리
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // 폼 제출 시 플로팅 로딩 애니메이션 표시
    const form = document.querySelector('.prediction-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('.submit-btn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="btn-icon">🔮</span><span class="btn-text">별을 읽는 중...</span>';
                
                // 플로팅 로딩 오버레이 표시
                if (loadingOverlay) {
                    loadingOverlay.style.display = 'flex';
                    // 약간의 지연 후 opacity 전환 (부드러운 등장)
                    setTimeout(() => {
                        loadingOverlay.classList.add('show');
                    }, 10);
                }
            }
        });
    }
    
    // 페이지 로드 시 로딩 오버레이 숨김 (결과 페이지에서)
    if (loadingOverlay) {
        loadingOverlay.classList.remove('show');
        setTimeout(() => {
            loadingOverlay.style.display = 'none';
        }, 300);
    }
    
    // 입력 필드 포커스 효과
    const inputs = document.querySelectorAll('.input-field');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // 시/도 및 구/군 드롭다운 설정
    setupAddressDropdowns();
    
    // 별 애니메이션 효과 (배경)
    createStarAnimation();
});

async function setupAddressDropdowns() {
    // 시/도 목록 로드
    await loadCityList();
    
    // 시/도 선택 시 구/군 목록 로드
    const citySelect = document.getElementById('city');
    citySelect.addEventListener('change', async function() {
        const cityCode = this.value;
        if (cityCode) {
            await loadDistrictList(cityCode);
        } else {
            resetDistrictDropdown();
            resetApartmentDropdown();
        }
    });
    
    // 구/군 선택 시 아파트 목록 로드
    const districtSelect = document.getElementById('district');
    districtSelect.addEventListener('change', async function() {
        const citySelect = document.getElementById('city');
        const districtSelect = document.getElementById('district');
        const addressInput = document.getElementById('address');
        
        if (citySelect.value && districtSelect.value) {
            const cityName = citySelect.options[citySelect.selectedIndex].text;
            const districtName = districtSelect.options[districtSelect.selectedIndex].text;
            const fullAddress = `${cityName} ${districtName}`;
            addressInput.value = fullAddress;
            await loadApartmentList(fullAddress);
        } else {
            resetApartmentDropdown();
        }
    });
}

async function loadCityList() {
    const citySelect = document.getElementById('city');
    
    // 서초구 배포 버전: 서울특별시만 표시
    citySelect.innerHTML = '<option value="">시/도 선택</option>';
    const option = document.createElement('option');
    option.value = '11'; // 서울특별시 코드
    option.textContent = '서울특별시';
    citySelect.appendChild(option);
    
    // 서울특별시 자동 선택
    citySelect.value = '11';
    await loadDistrictList('11');
}

async function loadDistrictList(cityCode) {
    const districtSelect = document.getElementById('district');
    const loadingIndicator = document.getElementById('loading_district');
    const addressInput = document.getElementById('address');
    
    // 서초구 배포 버전: 서초구만 표시
    loadingIndicator.style.display = 'none';
    districtSelect.innerHTML = '<option value="">구/군 선택</option>';
    const option = document.createElement('option');
    option.value = '11650'; // 서초구 코드
    option.textContent = '서초구';
    districtSelect.appendChild(option);
    
    // 서초구 자동 선택
    districtSelect.value = '11650';
    districtSelect.disabled = false;
    
    // 주소 설정
    if (addressInput) {
        addressInput.value = '서울특별시 서초구';
    }
    
    // 아파트 목록 로드
    await loadApartmentList('서울특별시 서초구');
}

function resetDistrictDropdown() {
    const districtSelect = document.getElementById('district');
    const loadingIndicator = document.getElementById('loading_district');
    
    districtSelect.innerHTML = '<option value="">먼저 시/도를 선택하세요</option>';
    districtSelect.disabled = true;
    loadingIndicator.style.display = 'none';
}

function setupApartmentDropdown() {
    // 이 함수는 더 이상 사용되지 않음 (구/군 선택 시 자동으로 호출됨)
}

async function loadApartmentList(address) {
    const aptSelect = document.getElementById('apt_name');
    const aptHint = document.getElementById('apt_hint');
    const loadingIndicator = document.getElementById('loading_apt');
    
    if (!aptSelect || !address) {
        return;
    }
    
    // 서초구 배포 버전: 지정된 5개 아파트만 표시
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    
    const allowedApartments = [
        { name: '대림서초시리온', value: '대림서초리시온' },
        { name: '디에이치반포클라스', value: '디에이치반포라클라스' },
        { name: '래미안 리더스원', value: '래미안_리더스원' },
        { name: '롯데캐슬갤럭시', value: '롯데캐슬갤럭시' },
        { name: '대우아이빌', value: '대우아이빌' }
    ];
    
    aptSelect.innerHTML = '<option value="">아파트 선택</option>';
    
    allowedApartments.forEach(apt => {
        const option = document.createElement('option');
        option.value = apt.value; // 모델 파일명과 일치하는 값
        option.textContent = apt.name; // 사용자에게 보여줄 이름
        aptSelect.appendChild(option);
    });
    
    aptSelect.disabled = false;
    if (aptHint) {
        aptHint.textContent = `${allowedApartments.length}개의 아파트를 선택할 수 있습니다.`;
        aptHint.style.color = '#9370DB';
    }
}

function resetApartmentDropdown() {
    const aptSelect = document.getElementById('apt_name');
    const aptHint = document.getElementById('apt_hint');
    const loadingIndicator = document.getElementById('loading_apt');
    
    aptSelect.innerHTML = '<option value="">먼저 주소를 입력하세요</option>';
    aptSelect.disabled = true;
    loadingIndicator.style.display = 'none';
    aptHint.textContent = '주소를 입력하면 해당 지역의 아파트 목록이 표시됩니다';
    aptHint.style.color = '#9370DB';
}

function createStarAnimation() {
    // 간단한 별 깜빡임 효과
    const stars = ['✨', '⭐', '🌟', '💫'];
    const container = document.body;
    
    // 배경에 별 아이콘 추가 (선택사항)
    // 실제로는 CSS 애니메이션으로 처리하는 것이 더 효율적
}

// Chart.js 설정 (향후 사용)
function setupChartJS() {
    // Chart.js 애니메이션 설정은 별도 파일로 분리 예정
}

