"""
Railway Deployment Test - Minimal Professional API
Step-by-step verification of components
"""

from fastapi import FastAPI

app = FastAPI(
    title="Railway Test - Professional API",
    description="Testing Professional Risk Analyzer deployment",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "status": "✅ Railway deployment successful",
        "version": "Professional Test",
        "message": "Basic FastAPI working on Railway"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "test": "basic_api_working"}

@app.get("/test-imports")
async def test_imports():
    """Test if all required imports work"""
    try:
        import requests
        import asyncio
        import time
        from datetime import datetime
        
        return {
            "status": "✅ All basic imports working",
            "imports": {
                "requests": "✅",
                "asyncio": "✅", 
                "time": "✅",
                "datetime": "✅"
            }
        }
    except Exception as e:
        return {
            "status": "❌ Import error",
            "error": str(e)
        }

@app.get("/test-dexscreener")
async def test_dexscreener_import():
    """Test DexScreener API import"""
    try:
        from dexscreener_api import DexScreenerAPI
        api = DexScreenerAPI()
        
        return {
            "status": "✅ DexScreener API imported successfully",
            "class": str(type(api))
        }
    except Exception as e:
        return {
            "status": "❌ DexScreener import error", 
            "error": str(e)
        }

@app.get("/test-professional")
async def test_professional_import():
    """Test Professional Risk Analyzer import"""
    try:
        from professional_risk_analyzer import ProfessionalRiskAnalyzer
        analyzer = ProfessionalRiskAnalyzer()
        
        return {
            "status": "✅ Professional Risk Analyzer imported successfully",
            "class": str(type(analyzer))
        }
    except Exception as e:
        return {
            "status": "❌ Professional Risk Analyzer import error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("🧪 Railway Test API starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)