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
    
    try {
        const response = await fetch('/api/cities');
        const data = await response.json();
        
        if (data.success && data.cities.length > 0) {
            citySelect.innerHTML = '<option value="">시/도 선택</option>';
            data.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city.code;
                option.textContent = city.name;
                citySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('시/도 목록 로드 오류:', error);
    }
}

async function loadDistrictList(cityCode) {
    const districtSelect = document.getElementById('district');
    const loadingIndicator = document.getElementById('loading_district');
    
    districtSelect.disabled = true;
    districtSelect.innerHTML = '<option value="">로딩 중...</option>';
    loadingIndicator.style.display = 'block';
    
    try {
        const response = await fetch(`/api/districts?city_code=${cityCode}`);
        const data = await response.json();
        
        loadingIndicator.style.display = 'none';
        
        if (data.success && data.districts.length > 0) {
            districtSelect.innerHTML = '<option value="">구/군 선택</option>';
            data.districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district.code;
                option.textContent = district.name;
                districtSelect.appendChild(option);
            });
            districtSelect.disabled = false;
        } else {
            districtSelect.innerHTML = '<option value="">구/군을 찾을 수 없습니다</option>';
            districtSelect.disabled = true;
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';
        districtSelect.innerHTML = '<option value="">오류 발생</option>';
        districtSelect.disabled = true;
        console.error('구/군 목록 로드 오류:', error);
    }
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
    
    // 로딩 상태 표시
    aptSelect.disabled = true;
    aptSelect.innerHTML = '<option value="">로딩 중...</option>';
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    if (aptHint) aptHint.textContent = '아파트 목록을 불러오는 중...';
    
    try {
        const response = await fetch(`/api/apartments?address=${encodeURIComponent(address)}`);
        const data = await response.json();
        
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        
        if (data.success && data.apartments.length > 0) {
            // 아파트 목록으로 드롭다운 채우기
            aptSelect.innerHTML = '<option value="">전체 아파트 (선택 안 함)</option>';
            
            data.apartments.forEach(aptName => {
                const option = document.createElement('option');
                option.value = aptName;
                option.textContent = aptName;
                aptSelect.appendChild(option);
            });
            
            aptSelect.disabled = false;
            if (aptHint) {
                aptHint.textContent = `${data.count}개의 아파트를 찾았습니다. 선택하거나 전체로 예측할 수 있습니다.`;
                aptHint.style.color = '#9370DB';
            }
        } else {
            aptSelect.innerHTML = '<option value="">아파트를 찾을 수 없습니다</option>';
            aptSelect.disabled = true;
            if (aptHint) {
                aptHint.textContent = data.error || '해당 주소에서 아파트를 찾을 수 없습니다.';
                aptHint.style.color = '#FF6B6B';
            }
        }
    } catch (error) {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        aptSelect.innerHTML = '<option value="">오류 발생</option>';
        aptSelect.disabled = true;
        if (aptHint) {
            aptHint.textContent = '아파트 목록을 불러오는 중 오류가 발생했습니다.';
            aptHint.style.color = '#FF6B6B';
        }
        console.error('아파트 목록 로드 오류:', error);
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

