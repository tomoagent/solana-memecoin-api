"""
Railway環境テスト用 - 最小限API
問題特定のための軽量版
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Solana Risk Analyzer - Test Version",
    description="Railway環境テスト中",
    version="1.0.0"
)

class TestRequest(BaseModel):
    contract_address: str

class TestResponse(BaseModel):
    status: str
    message: str
    contract_address: str

@app.get("/")
async def root():
    return {
        "status": "Railway環境テスト成功！",
        "version": "1.0.0",
        "message": "Professional Risk Analyzer準備中"
    }

@app.post("/test")
async def test_analyze(request: TestRequest):
    return TestResponse(
        status="success",
        message="Railway環境正常稼働中",
        contract_address=request.contract_address
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "railway": "working"}