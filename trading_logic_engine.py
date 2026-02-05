#!/usr/bin/env python3
"""
Trading Logic Engine v1.0 - Phase 4
Advanced automated trading logic with risk management and position sizing
Integrates: Smart Scanner + Risk Filter + Smart Money + (Flow Prediction when available)
Target: $999/month complete auto-trading system
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingSignal(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    NO_TRADE = "NO_TRADE"

class RiskLevel(Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

@dataclass
class TradingDecision:
    signal: TradingSignal
    confidence: float  # 0.0 - 1.0
    position_size: float  # 0.0 - 1.0 (percentage of portfolio)
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    reasoning: str
    risk_factors: List[str]
    expected_return: Optional[float]
    holding_period: str  # "SHORT" (< 1 day), "MEDIUM" (1-7 days), "LONG" (> 7 days)

@dataclass
class MarketConditions:
    overall_sentiment: str  # "BULL", "BEAR", "SIDEWAYS", "UNCERTAIN"
    volatility_level: str   # "LOW", "MEDIUM", "HIGH", "EXTREME"
    liquidity_condition: str # "EXCELLENT", "GOOD", "FAIR", "POOR"
    whale_activity: str     # "ACCUMULATING", "DISTRIBUTING", "NEUTRAL", "UNKNOWN"

class TradingLogicEngine:
    def __init__(self, api_base_url: str = "https://solana-memecoin-api.onrender.com"):
        self.api_base_url = api_base_url
        self.session = None
        
        # Risk Management Parameters
        self.max_position_size = 0.05  # 5% max per position
        self.max_daily_loss = 0.10     # 10% max daily loss
        self.min_liquidity = 50000     # $50K minimum liquidity
        self.max_risk_score = 65       # Maximum acceptable risk score
        
        # Trading Thresholds
        self.strong_buy_threshold = 0.85  # 85% confidence
        self.buy_threshold = 0.70         # 70% confidence
        self.sell_threshold = 0.30        # 30% confidence (inverse)
        
        # Position Sizing Factors
        self.base_position_size = 0.02    # 2% base position
        self.confidence_multiplier = 2.0  # Multiply by confidence
        self.risk_adjustment = 0.5        # Reduce by risk
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_comprehensive_analysis(self, contract_address: str) -> Dict[str, Any]:
        """Get complete analysis from all available APIs"""
        try:
            # Base risk analysis
            async with self.session.post(
                f"{self.api_base_url}/analyze",
                json={"contract_address": contract_address, "include_smart_money": True}
            ) as resp:
                base_analysis = await resp.json()
            
            # Smart Money specific analysis
            try:
                async with self.session.post(
                    f"{self.api_base_url}/smart-money",
                    json={"contract_address": contract_address}
                ) as resp:
                    smart_money_analysis = await resp.json()
            except:
                smart_money_analysis = {"error": "Smart Money API unavailable"}
            
            # Flow prediction (if available)
            try:
                async with self.session.post(
                    f"{self.api_base_url}/flow-prediction", 
                    json={"contract_address": contract_address}
                ) as resp:
                    flow_analysis = await resp.json()
            except:
                flow_analysis = {"error": "Flow Prediction unavailable"}
            
            return {
                "base_analysis": base_analysis,
                "smart_money_analysis": smart_money_analysis, 
                "flow_analysis": flow_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analysis: {e}")
            raise
    
    def calculate_market_conditions(self, analysis: Dict[str, Any]) -> MarketConditions:
        """Analyze current market conditions from data"""
        base = analysis.get("base_analysis", {})
        smart_money = analysis.get("smart_money_analysis", {})
        
        # Overall sentiment from risk score and smart money
        risk_score = base.get("risk_score", 50)
        smart_money_score = smart_money.get("smart_money_score", 50) if "error" not in smart_money else 50
        
        if risk_score < 30 and smart_money_score > 70:
            sentiment = "BULL"
        elif risk_score > 70 or smart_money_score < 30:
            sentiment = "BEAR" 
        elif 30 <= risk_score <= 50 and smart_money_score >= 50:
            sentiment = "SIDEWAYS"
        else:
            sentiment = "UNCERTAIN"
        
        # Volatility from price data
        market_data = base.get("market_data", {})
        price_vol = market_data.get("price_volatility", {}).get("risk_score", 2.5)
        
        if price_vol < 1:
            volatility = "LOW"
        elif price_vol < 3:
            volatility = "MEDIUM"
        elif price_vol < 4:
            volatility = "HIGH"
        else:
            volatility = "EXTREME"
        
        # Liquidity condition
        liquidity_info = base.get("liquidity_info", {})
        liquidity_risk = liquidity_info.get("risk_score", 35)
        
        if liquidity_risk < 10:
            liquidity_condition = "EXCELLENT"
        elif liquidity_risk < 20:
            liquidity_condition = "GOOD"
        elif liquidity_risk < 30:
            liquidity_condition = "FAIR"
        else:
            liquidity_condition = "POOR"
        
        # Whale activity from Smart Money
        whale_signals = smart_money.get("whale_activity", {}) if "error" not in smart_money else {}
        net_flow = whale_signals.get("net_flow_24h", 0)
        
        if net_flow > 15:
            whale_activity = "ACCUMULATING"
        elif net_flow < -15:
            whale_activity = "DISTRIBUTING"
        elif abs(net_flow) <= 15:
            whale_activity = "NEUTRAL"
        else:
            whale_activity = "UNKNOWN"
        
        return MarketConditions(
            overall_sentiment=sentiment,
            volatility_level=volatility,
            liquidity_condition=liquidity_condition,
            whale_activity=whale_activity
        )
    
    def calculate_position_size(self, analysis: Dict[str, Any], confidence: float, risk_score: float) -> float:
        """Calculate optimal position size based on risk and confidence"""
        
        # Base position adjusted by confidence
        confidence_adjusted = self.base_position_size * (1 + confidence * self.confidence_multiplier)
        
        # Risk adjustment (higher risk = smaller position)
        risk_factor = max(0.1, 1 - (risk_score / 100) * self.risk_adjustment)
        risk_adjusted = confidence_adjusted * risk_factor
        
        # Liquidity adjustment
        base = analysis.get("base_analysis", {})
        liquidity_risk = base.get("liquidity_info", {}).get("risk_score", 35)
        
        if liquidity_risk > 30:  # Poor liquidity
            risk_adjusted *= 0.5
        elif liquidity_risk < 10:  # Excellent liquidity  
            risk_adjusted *= 1.2
        
        # Cap at maximum position size
        final_position = min(risk_adjusted, self.max_position_size)
        
        # Ensure minimum viable position
        return max(final_position, 0.005)  # 0.5% minimum
    
    def calculate_stop_loss_take_profit(self, current_price: float, risk_score: float, volatility: str) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels"""
        
        # Base stop loss: 15-25% based on risk
        base_stop_loss_pct = 0.15 + (risk_score / 100) * 0.10  # 15-25%
        
        # Volatility adjustment
        volatility_multipliers = {
            "LOW": 0.8,
            "MEDIUM": 1.0,
            "HIGH": 1.3,
            "EXTREME": 1.6
        }
        
        stop_loss_pct = base_stop_loss_pct * volatility_multipliers.get(volatility, 1.0)
        stop_loss = current_price * (1 - stop_loss_pct)
        
        # Take profit: Risk-reward ratio 1:2 to 1:4
        risk_reward_ratio = 3.0 - (risk_score / 100)  # Higher risk = lower reward target
        take_profit_pct = stop_loss_pct * risk_reward_ratio
        take_profit = current_price * (1 + take_profit_pct)
        
        return stop_loss, take_profit
    
    def generate_trading_decision(self, analysis: Dict[str, Any]) -> TradingDecision:
        """Generate final trading decision based on comprehensive analysis"""
        
        base = analysis.get("base_analysis", {})
        smart_money = analysis.get("smart_money_analysis", {})
        flow = analysis.get("flow_analysis", {})
        
        # Extract key metrics
        risk_score = base.get("risk_score", 100)  # Default to high risk
        risk_level = base.get("risk_level", "VERY_HIGH")
        confidence_score = base.get("confidence_score", 0.5)
        
        # Smart Money score
        smart_money_score = smart_money.get("smart_money_score", 50) if "error" not in smart_money else 50
        smart_money_confidence = smart_money.get("confidence", 0.5) if "error" not in smart_money else 0.5
        
        # Market conditions
        market_conditions = self.calculate_market_conditions(analysis)
        
        # Calculate composite confidence
        base_confidence = confidence_score
        smart_confidence_boost = (smart_money_score - 50) / 50 * 0.3  # -0.3 to +0.3
        flow_confidence_boost = 0  # TODO: Implement when Flow Prediction available
        
        composite_confidence = max(0.0, min(1.0, base_confidence + smart_confidence_boost + flow_confidence_boost))
        
        # Risk filters
        risk_factors = []
        
        if risk_score > self.max_risk_score:
            risk_factors.append(f"High risk score: {risk_score}/100")
        
        liquidity_risk = base.get("liquidity_info", {}).get("risk_score", 35)
        if liquidity_risk > 30:
            risk_factors.append("Poor liquidity conditions")
        
        if market_conditions.whale_activity == "DISTRIBUTING":
            risk_factors.append("Whales are distributing")
        
        if market_conditions.volatility_level == "EXTREME":
            risk_factors.append("Extreme volatility detected")
        
        # Decision logic
        signal = TradingSignal.NO_TRADE
        reasoning = "Analysis inconclusive"
        
        # Strong filters first
        if len(risk_factors) >= 3:
            signal = TradingSignal.NO_TRADE
            reasoning = f"Too many risk factors: {', '.join(risk_factors)}"
            
        elif risk_score > 80:
            signal = TradingSignal.NO_TRADE  
            reasoning = f"Risk score too high: {risk_score}/100"
            
        elif composite_confidence >= self.strong_buy_threshold and risk_score <= 40:
            signal = TradingSignal.STRONG_BUY
            reasoning = f"High confidence ({composite_confidence:.2f}) + Low risk ({risk_score})"
            
        elif composite_confidence >= self.buy_threshold and risk_score <= 60:
            signal = TradingSignal.BUY
            reasoning = f"Good confidence ({composite_confidence:.2f}) + Acceptable risk ({risk_score})"
            
        elif composite_confidence <= self.sell_threshold or risk_score > 75:
            signal = TradingSignal.SELL
            reasoning = f"Low confidence ({composite_confidence:.2f}) or High risk ({risk_score})"
            
        else:
            signal = TradingSignal.HOLD
            reasoning = f"Neutral conditions - confidence: {composite_confidence:.2f}, risk: {risk_score}"
        
        # Position sizing
        position_size = 0.0
        if signal in [TradingSignal.STRONG_BUY, TradingSignal.BUY]:
            position_size = self.calculate_position_size(analysis, composite_confidence, risk_score)
        
        # Stop loss / Take profit
        current_price = 1.0  # TODO: Extract from market data
        stop_loss = None
        take_profit = None
        
        if signal in [TradingSignal.STRONG_BUY, TradingSignal.BUY]:
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(
                current_price, risk_score, market_conditions.volatility_level
            )
        
        # Expected return estimate
        expected_return = None
        if signal in [TradingSignal.STRONG_BUY, TradingSignal.BUY]:
            if signal == TradingSignal.STRONG_BUY:
                expected_return = 0.50 + (1 - risk_score/100) * 0.30  # 50-80% target
            else:
                expected_return = 0.30 + (1 - risk_score/100) * 0.20  # 30-50% target
        
        # Holding period
        holding_period = "MEDIUM"  # Default
        if market_conditions.volatility_level == "EXTREME":
            holding_period = "SHORT"
        elif risk_score < 30 and composite_confidence > 0.8:
            holding_period = "LONG"
        
        return TradingDecision(
            signal=signal,
            confidence=composite_confidence,
            position_size=position_size,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reasoning=reasoning,
            risk_factors=risk_factors,
            expected_return=expected_return,
            holding_period=holding_period
        )

    async def process_trading_analysis(self, contract_address: str) -> Dict[str, Any]:
        """Complete trading analysis and decision generation"""
        start_time = time.time()
        
        try:
            # Get comprehensive analysis
            analysis = await self.get_comprehensive_analysis(contract_address)
            
            # Generate market conditions
            market_conditions = self.calculate_market_conditions(analysis)
            
            # Generate trading decision
            trading_decision = self.generate_trading_decision(analysis)
            
            processing_time = time.time() - start_time
            
            result = {
                "contract_address": contract_address,
                "timestamp": datetime.now().isoformat(),
                "processing_time": round(processing_time, 2),
                "market_conditions": asdict(market_conditions),
                "trading_decision": asdict(trading_decision),
                "raw_analysis": analysis,
                "engine_version": "1.0",
                "status": "completed"
            }
            
            # Save result
            filename = f"trading_analysis_{contract_address[:8]}_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2, default=str)
                
            logger.info(f"Trading analysis completed in {processing_time:.2f}s: {trading_decision.signal.value}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in trading analysis: {e}")
            raise

# Main execution function
async def analyze_trading_opportunity(contract_address: str) -> Dict[str, Any]:
    """Analyze a trading opportunity and return comprehensive decision"""
    async with TradingLogicEngine() as engine:
        return await engine.process_trading_analysis(contract_address)

# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Test with SOL
        contract_address = "So11111111111111111111111111111111111111112"
        
        print(f"🤖 Trading Logic Engine v1.0")
        print(f"📊 Analyzing: {contract_address}")
        print("=" * 60)
        
        result = await analyze_trading_opportunity(contract_address)
        
        decision = result["trading_decision"]
        market = result["market_conditions"]
        
        print(f"🎯 TRADING SIGNAL: {decision['signal']}")
        print(f"🎲 Confidence: {decision['confidence']:.2f}")
        print(f"💰 Position Size: {decision['position_size']:.3f} ({decision['position_size']*100:.1f}%)")
        print(f"📈 Expected Return: {decision.get('expected_return', 'N/A')}")
        print(f"⏱️  Holding Period: {decision['holding_period']}")
        print(f"🧠 Reasoning: {decision['reasoning']}")
        
        if decision['risk_factors']:
            print(f"⚠️  Risk Factors: {', '.join(decision['risk_factors'])}")
        
        print(f"\n📊 Market Conditions:")
        print(f"   Sentiment: {market['overall_sentiment']}")
        print(f"   Volatility: {market['volatility_level']}")
        print(f"   Liquidity: {market['liquidity_condition']}")
        print(f"   Whale Activity: {market['whale_activity']}")
        
        print(f"\n⚡ Processing Time: {result['processing_time']}s")
        
    # Run the test
    asyncio.run(main())