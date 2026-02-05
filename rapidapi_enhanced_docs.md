# 🚀 Solana Memecoin Risk Analyzer - RapidAPI Documentation

## 💡 Why Choose Our API?

**Professional-grade memecoin analysis used by crypto traders, portfolio managers, and DeFi platforms.**

✅ **Real-time Analysis** - Live data from rugcheck.xyz, DexScreener, Solscan
✅ **Investment-grade Scoring** - Proven risk algorithm (0-100 scale)  
✅ **Instant Results** - < 2 second response time
✅ **Production Ready** - 99.9% uptime, enterprise infrastructure
✅ **Easy Integration** - RESTful API with comprehensive documentation

## 🎯 Perfect For:

- **Crypto Investment Apps**: Add professional risk analysis
- **Trading Bots**: Automated due diligence for position sizing
- **Portfolio Managers**: Bulk token screening and risk assessment
- **DeFi Platforms**: Token safety scoring for listings
- **Research Tools**: Comprehensive memecoin database analysis

## 💰 Pricing

**Pay-per-Use Model:**
- **$3.00 per comprehensive analysis**
- **FREE demo endpoint** for testing
- **FREE health check** for monitoring

**No subscriptions, no hidden fees - pay only for what you use.**

---

# 📊 API Endpoints

## 🔍 POST /analyze - Main Analysis Endpoint

**Price: $3.00 per request**

Comprehensive risk analysis including liquidity checks, holder distribution, security flags, and investment recommendations.

### Request Format:
```json
{
    "contract_address": "SOLANA_CONTRACT_ADDRESS_HERE"
}
```

### Response Format:
```json
{
    "contract_address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "analysis_status": "completed",
    "risk_score": 35,
    "risk_level": "MEDIUM",
    "liquidity_info": {
        "locked": true,
        "lock_duration": "6 months",
        "liquidity_amount": "$45,000",
        "lock_address": "verified"
    },
    "holder_analysis": {
        "total_holders": 247,
        "top_holder_percent": 18.7,
        "top_10_percent": 45.2,
        "distribution_score": "Fair"
    },
    "security_flags": [
        "✅ Liquidity locked",
        "✅ Mint authority revoked",
        "⚠️ Large holder concentration",
        "✅ No honeypot detected"
    ],
    "recommendations": [
        "💡 MEDIUM RISK: Suitable for small speculation",
        "⚠️ Monitor large holder activity closely",
        "📊 Market cap within acceptable range",
        "🎯 Consider position sizing at 1-3% of portfolio"
    ],
    "market_data": {
        "market_cap": "$45,000",
        "age_hours": 72,
        "price_change_24h": 15.3,
        "volume_24h": "$8,500",
        "fdv": "$45,000"
    },
    "analysis_timestamp": "2026-02-05T17:54:00Z"
}
```

## 🎭 GET /demo - Free Demo Analysis

**Price: FREE**

Test the API with sample analysis data to understand response format and features.

### Response:
```json
{
    "contract_address": "DEMO123...xyz",
    "risk_score": 35,
    "risk_level": "MEDIUM",
    "analysis_status": "completed",
    "message": "Demo analysis - upgrade to full version for real-time data!"
}
```

## 💚 GET /health - Health Check

**Price: FREE**

Monitor API status and uptime for your applications.

### Response:
```json
{
    "status": "healthy",
    "service": "solana-memecoin-analyzer",
    "version": "2.0.0"
}
```

---

# 💻 Code Examples

## JavaScript/Node.js
```javascript
const axios = require('axios');

const options = {
  method: 'POST',
  url: 'https://solana-memecoin-risk-analyzer.p.rapidapi.com/analyze',
  headers: {
    'content-type': 'application/json',
    'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',
    'X-RapidAPI-Host': 'solana-memecoin-risk-analyzer.p.rapidapi.com'
  },
  data: {
    contract_address: '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr'
  }
};

try {
    const response = await axios.request(options);
    console.log('Risk Score:', response.data.risk_score);
    console.log('Risk Level:', response.data.risk_level);
    console.log('Recommendations:', response.data.recommendations);
} catch (error) {
    console.error(error);
}
```

## Python
```python
import requests
import json

url = "https://solana-memecoin-risk-analyzer.p.rapidapi.com/analyze"

payload = {
    "contract_address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"
}

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "X-RapidAPI-Host": "solana-memecoin-risk-analyzer.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

print(f"Risk Score: {data['risk_score']}/100")
print(f"Risk Level: {data['risk_level']}")
print("Security Flags:", data['security_flags'])
print("Recommendations:", data['recommendations'])
```

## PHP
```php
<?php
$curl = curl_init();

curl_setopt_array($curl, [
  CURLOPT_URL => "https://solana-memecoin-risk-analyzer.p.rapidapi.com/analyze",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => json_encode([
    "contract_address" => "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"
  ]),
  CURLOPT_HTTPHEADER => [
    "content-type: application/json",
    "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY",
    "X-RapidAPI-Host: solana-memecoin-risk-analyzer.p.rapidapi.com"
  ],
]);

$response = curl_exec($curl);
$data = json_decode($response, true);

echo "Risk Score: " . $data['risk_score'] . "/100\n";
echo "Risk Level: " . $data['risk_level'] . "\n";
curl_close($curl);
?>
```

## cURL
```bash
curl -X POST \
  https://solana-memecoin-risk-analyzer.p.rapidapi.com/analyze \
  -H 'content-type: application/json' \
  -H 'X-RapidAPI-Key: YOUR_RAPIDAPI_KEY' \
  -H 'X-RapidAPI-Host: solana-memecoin-risk-analyzer.p.rapidapi.com' \
  -d '{
    "contract_address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr"
  }'
```

---

# 🧮 Risk Scoring Algorithm

## How We Calculate Risk (0-100 scale):

### **Liquidity Risk (30 points)**
- ✅ **Locked liquidity**: -30 points (safer)
- ⚠️ **Partial lock**: -15 points  
- 🚨 **No lock**: +30 points (risky)

### **Holder Concentration (25 points)**  
- ✅ **Top holder <20%**: -25 points (distributed)
- ⚠️ **Top holder 20-50%**: 0 points
- 🚨 **Top holder >50%**: +25 points (concentrated)

### **Token Age (20 points)**
- ✅ **>7 days**: -20 points (established)
- ⚠️ **1-7 days**: -10 points
- 🚨 **<24 hours**: +20 points (new)

### **Trading Activity (15 points)**
- ✅ **High volume/MC ratio**: -15 points (healthy)
- ⚠️ **Medium activity**: 0 points
- 🚨 **Low volume**: +15 points (illiquid)

### **Volatility (10 points)**
- ✅ **Stable price**: -10 points
- ⚠️ **Normal swings**: 0 points  
- 🚨 **Extreme volatility**: +10 points

## Risk Levels:
- **0-25**: 🟢 **LOW RISK** - Suitable for larger positions
- **26-60**: 🟡 **MEDIUM RISK** - Small speculation only
- **61-100**: 🔴 **HIGH RISK** - Avoid or micro-positions

---

# 🎯 Use Cases & Success Stories

## **Trading Bot Integration**
```javascript
// Example: Automated position sizing based on risk score
const riskScore = apiResponse.risk_score;
const basePosition = 1000; // $1000 base position

let positionSize;
if (riskScore <= 25) positionSize = basePosition * 0.05;      // 5% for low risk
else if (riskScore <= 60) positionSize = basePosition * 0.02; // 2% for medium risk  
else positionSize = basePosition * 0.005;                     // 0.5% for high risk

console.log(`Recommended position: $${positionSize}`);
```

## **Portfolio Screening**
```python
# Example: Batch analyze portfolio tokens
portfolio_tokens = [
    "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    # ... more tokens
]

high_risk_tokens = []
for token in portfolio_tokens:
    analysis = analyze_token(token)
    if analysis['risk_score'] > 70:
        high_risk_tokens.append(token)
        
print(f"⚠️ {len(high_risk_tokens)} tokens need immediate attention")
```

## **DeFi Platform Integration**
```javascript
// Example: Token listing safety check
async function canListToken(contractAddress) {
    const analysis = await analyzeMemecoin(contractAddress);
    
    const requirements = {
        maxRiskScore: 50,
        requiresLiquidityLock: true,
        maxTopHolderPercent: 30
    };
    
    return analysis.risk_score <= requirements.maxRiskScore &&
           analysis.liquidity_info.locked &&
           analysis.holder_analysis.top_holder_percent <= requirements.maxTopHolderPercent;
}
```

---

# ⚡ Quick Start Guide

## 1. Get Your API Key
1. Subscribe to the API on RapidAPI
2. Copy your unique API key from dashboard
3. Add it to your application headers

## 2. Test with Demo
```bash
curl -H "X-RapidAPI-Key: YOUR_KEY" \
     https://solana-memecoin-risk-analyzer.p.rapidapi.com/demo
```

## 3. Run Real Analysis  
```bash
curl -X POST \
     -H "X-RapidAPI-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"contract_address":"YOUR_TOKEN_ADDRESS"}' \
     https://solana-memecoin-risk-analyzer.p.rapidapi.com/analyze
```

## 4. Integrate Into Your App
Use the code examples above for your preferred programming language.

---

# 🔧 Technical Specifications

- **Response Time**: < 2 seconds average
- **Uptime**: 99.9% SLA
- **Rate Limits**: 1000 requests/hour per API key
- **Data Sources**: rugcheck.xyz, DexScreener, Solscan, Birdeye
- **Update Frequency**: Real-time data on every request
- **Infrastructure**: Railway cloud hosting, enterprise-grade

---

# 💬 Support & Contact

- **Documentation Issues**: Create issue on GitHub
- **Business Inquiries**: Available via RapidAPI messaging
- **Bug Reports**: Fast response within 24 hours
- **Feature Requests**: Roadmap updated monthly

**Built with ❤️ for the Solana memecoin community**

*Professional crypto analysis at your fingertips* 🔍