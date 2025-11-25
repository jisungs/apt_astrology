"""
Pydantic 스키마 모듈
- 입력 검증 및 데이터 모델 정의
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
import re


class PredictionRequest(BaseModel):
    """예측 요청 모델"""
    address: str
    apt_name: Optional[str] = None
    
    @validator('address')
    def validate_address(cls, v):
        """주소 검증 및 정제"""
        if not v or len(v.strip()) < 2:
            raise ValueError('주소는 최소 2자 이상이어야 합니다')
        
        # 특수문자 제거 (SQL injection, XSS 방지)
        v = re.sub(r'[<>"\']', '', v)
        v = v.strip()
        
        # 길이 제한 (200자)
        if len(v) > 200:
            raise ValueError('주소는 200자 이하여야 합니다')
        
        return v
    
    @validator('apt_name')
    def validate_apt_name(cls, v):
        """아파트명 검증 및 정제"""
        if v:
            # 특수문자 제거
            v = re.sub(r'[<>"\']', '', v)
            v = v.strip()
            
            # 빈 문자열이면 None으로 변환
            if not v:
                return None
            
            # 길이 제한 (100자)
            if len(v) > 100:
                raise ValueError('아파트명은 100자 이하여야 합니다')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "address": "서울특별시 종로구",
                "apt_name": "경희궁자이"
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error_code: str
    message: str
    detail: Optional[str] = None
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "error_code": "PREDICTION_ERROR",
                "message": "예측 중 오류가 발생했습니다",
                "detail": "데이터 수집 실패",
                "timestamp": "2025-11-24T10:00:00"
            }
        }

