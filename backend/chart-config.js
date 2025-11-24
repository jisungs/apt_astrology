/**
 * Chart.js 설정 및 애니메이션 로직
 * 점성술사 컨셉에 맞는 차트 설정
 */

// Chart.js 기본 설정
const chartConfig = {
    // 애니메이션 설정
    animation: {
        duration: 1500,
        easing: 'easeInOutQuart',
        delay: (context) => context.dataIndex * 50
    },
    
    // 점성술사 컨셉 색상 팔레트
    colors: {
        primary: '#FFD700',      // 금색
        secondary: '#9370DB',    // 보라색
        accent: '#FF69B4',       // 핑크
        background: 'rgba(0, 0, 0, 0.5)',
        grid: 'rgba(147, 112, 219, 0.2)'
    },
    
    // 플러그인 설정
    plugins: {
        legend: {
            labels: {
                color: '#FFD700',
                font: {
                    family: 'Arial, sans-serif',
                    size: 12
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#FFD700',
            bodyColor: '#9370DB',
            borderColor: '#9370DB',
            borderWidth: 1
        }
    },
    
    // 스케일 설정
    scales: {
        x: {
            ticks: {
                color: '#9370DB'
            },
            grid: {
                color: 'rgba(147, 112, 219, 0.2)'
            }
        },
        y: {
            ticks: {
                color: '#9370DB'
            },
            grid: {
                color: 'rgba(147, 112, 219, 0.2)'
            }
        }
    }
};

// 라인 차트 설정
function createLineChartConfig(data, labels) {
    return {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '가격',
                data: data,
                borderColor: chartConfig.colors.primary,
                backgroundColor: 'rgba(255, 215, 0, 0.1)',
                borderWidth: 3,
                pointRadius: 5,
                pointBackgroundColor: chartConfig.colors.primary,
                pointBorderColor: chartConfig.colors.secondary,
                pointBorderWidth: 2,
                tension: 0.4, // 부드러운 곡선
                fill: true
            }]
        },
        options: {
            ...chartConfig,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                ...chartConfig.plugins,
                title: {
                    display: true,
                    text: '🔮 가격 예측',
                    color: chartConfig.colors.primary,
                    font: {
                        size: 18
                    }
                }
            }
        }
    };
}

// 바 차트 설정 (거래량)
function createBarChartConfig(data, labels) {
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '거래량',
                data: data,
                backgroundColor: chartConfig.colors.secondary,
                borderColor: chartConfig.colors.primary,
                borderWidth: 2
            }]
        },
        options: {
            ...chartConfig,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                ...chartConfig.plugins,
                title: {
                    display: true,
                    text: '📊 거래량 추이',
                    color: chartConfig.colors.primary,
                    font: {
                        size: 18
                    }
                }
            }
        }
    };
}

// 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        chartConfig,
        createLineChartConfig,
        createBarChartConfig
    };
}

