from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Solana Memecoin Analyzer API", version="2.0.0")

class AnalysisRequest(BaseModel):
    contract_address: str

@app.get("/")
async def root():
    return {
        "service": "Solana Memecoin Analyzer API", 
        "version": "2.0.0",
        "price": "$3 per analysis",
        "status": "Production Ready"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/demo")
async def demo():
    return {
        "contract_address": "DEMO123",
        "risk_score": 35,
        "risk_level": "MEDIUM",
        "analysis_status": "completed",
        "message": "Demo analysis - Full version coming soon!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
