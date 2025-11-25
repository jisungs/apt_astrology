"""
커스텀 예외 클래스 모듈
- 구조화된 에러 응답 제공
"""
from fastapi import HTTPException
from datetime import datetime
from typing import Optional


class PredictionError(HTTPException):
    """예측 관련 에러"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=500,
            detail={
                "error_code": "PREDICTION_ERROR",
                "message": message,
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            }
        )


class DataCollectionError(HTTPException):
    """데이터 수집 관련 에러"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=404,
            detail={
                "error_code": "DATA_COLLECTION_ERROR",
                "message": message,
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            }
        )


class ModelTrainingError(HTTPException):
    """모델 학습 관련 에러"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=500,
            detail={
                "error_code": "MODEL_TRAINING_ERROR",
                "message": message,
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            }
        )


class ValidationError(HTTPException):
    """입력 검증 관련 에러"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            status_code=400,
            detail={
                "error_code": "VALIDATION_ERROR",
                "message": message,
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            }
        )

